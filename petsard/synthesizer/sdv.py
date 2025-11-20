"""
SDV Synthesizer Wrapper Module

**IMPORTANT: Optional Dependency**

This module provides wrappers for SDV (Synthetic Data Vault) synthesizers.
SDV is an **optional dependency** and must be installed separately to use these methods.

**Installation:**
```bash
pip install 'sdv>=1.26.0,<2'
```

**Usage:**
- This module is lazy-loaded only when SDV methods are requested
- PETsARD will function normally without SDV installed
- Attempting to use SDV methods without installation will raise `MissingDependencyError`
- Use `petsard-gaussian_copula` as an alternative that doesn't require SDV

**Supported SDV Methods:**
- `sdv-single_table-gaussiancopula`: Gaussian Copula synthesizer
- `sdv-single_table-ctgan`: Conditional Tabular GAN
- `sdv-single_table-copulagan`: Copula GAN
- `sdv-single_table-tvae`: Tabular VAE

**Migration Note:**
Consider using `petsard-gaussian_copula` as a built-in alternative that doesn't
require external dependencies and provides similar functionality.

**Example:**
```python
from petsard.synthesizer import Synthesizer
from petsard.exceptions import MissingDependencyError

# This will check if SDV is installed
try:
    synthesizer = Synthesizer(method="sdv-single_table-gaussiancopula")
    synthesizer.create(metadata=schema)
    synthesizer.fit(data)
    syn_data = synthesizer.sample()
except MissingDependencyError as e:
    print(f"SDV not installed: {e.get_suggestion()}")
    # Use alternative method
    synthesizer = Synthesizer(method="petsard-gaussian_copula")
```
"""


import logging
import re
import warnings
from typing import Any

import pandas as pd
from scipy.stats._warnings_errors import FitError
from sdv.metadata import Metadata as SDV_Metadata
from sdv.single_table import (CopulaGANSynthesizer, CTGANSynthesizer,
                              GaussianCopulaSynthesizer, TVAESynthesizer)
from sdv.single_table.base import BaseSingleTableSynthesizer

from petsard.exceptions import UnableToSynthesizeError, UnsupportedMethodError
from petsard.metadater.metadata import Schema
from petsard.metadater.metadater import SchemaMetadater
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


def schema_to_sdv(schema: Schema) -> dict[str, Any]:
    """Convert PETsARD Schema to SDV (Synthetic Data Vault) format

    Args:
        schema: PETsARD Schema object

    Returns:
        dict: Dictionary in SDV metadata format
    """
    sdv_metadata = {"columns": {}, "METADATA_SPEC_VERSION": "SINGLE_TABLE_V1"}

    for attr_name, attribute in schema.attributes.items():
        sdtype = _map_attribute_to_sdv_type(attribute)
        sdv_metadata["columns"][attr_name] = {"sdtype": sdtype}

    return sdv_metadata


def _map_attribute_to_sdv_type(attribute: Any) -> str:
    """Map PETsARD Attribute to SDV sdtype

    Args:
        attribute: PETsARD Attribute object or dict

    Returns:
        str: SDV sdtype
    """
    # Handle both dict and Attribute object cases
    if isinstance(attribute, dict):
        logical_type = attribute.get("logical_type")
        attr_type = attribute.get("type")
        category = attribute.get("category", False)
    else:
        logical_type = attribute.logical_type
        attr_type = attribute.type
        # CRITICAL FIX: category is stored in type_attr, not as a direct Attribute property
        category = (
            attribute.type_attr.get("category", False) if attribute.type_attr else False
        )

    # Prioritize category flag check
    if category is True:
        return "categorical"

    # Determine by logical type
    if logical_type:
        logical = logical_type.lower()
        if logical in ["email", "phone"]:
            return "pii"
        elif logical == "category":
            return "categorical"
        elif logical in ["datetime", "date", "time"]:
            return "datetime"

    # Determine by data type
    if attr_type:
        attr_type_str = str(attr_type).lower()
        if "int" in attr_type_str or "float" in attr_type_str:
            return "numerical"
        elif "bool" in attr_type_str:
            return "boolean"
        elif "datetime" in attr_type_str:
            return "datetime"

    # Default to categorical
    return "categorical"


class SDVSingleTableMap:
    """
    Mapping of SDV.
    """

    COPULAGAN: int = 1
    CTGAN: int = 2
    GAUSSIANCOPULA: int = 3
    TVAE: int = 4

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        # accept both of "sdv-" or "sdv-single_table-" prefix
        return cls.__dict__[re.sub(r"^(sdv-single_table-|sdv-)", "", method).upper()]


class SDVSingleTableSynthesizer(BaseSynthesizer):
    """
    Factory class for SDV synthesizer.
    """

    SDV_SINGLETABLE_MAP: dict[int, BaseSynthesizer] = {
        SDVSingleTableMap.COPULAGAN: CopulaGANSynthesizer,
        SDVSingleTableMap.CTGAN: CTGANSynthesizer,
        SDVSingleTableMap.GAUSSIANCOPULA: GaussianCopulaSynthesizer,
        SDVSingleTableMap.TVAE: TVAESynthesizer,
    }

    def __init__(self, config: dict, metadata: Schema = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (Schema, optional): The metadata object.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _impl (BaseSingleTableSynthesizer): The synthesizer object if metadata is provided.
        """
        super().__init__(config, metadata)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.debug(
            f"Initializing {self.__class__.__name__} with config: {config}"
        )

        # If metadata is provided, initialize the synthesizer in the init method.
        if metadata is not None:
            self._logger.debug(
                "Metadata provided, initializing synthesizer in __init__"
            )
            # Convert Schema to SDV format using local function
            sdv_metadata_dict = schema_to_sdv(metadata)

            # DIAGNOSTIC: Log the actual metadata being sent to SDV
            self._logger.debug("=" * 80)
            self._logger.debug("[DIAGNOSTIC] Schema -> SDV Metadata Conversion")
            self._logger.debug("=" * 80)
            for col_name, col_info in sdv_metadata_dict["columns"].items():
                # Get original attribute for comparison
                orig_attr = metadata.attributes.get(col_name)
                if orig_attr:
                    category_flag = (
                        orig_attr.type_attr.get("category", False)
                        if orig_attr.type_attr
                        else False
                    )
                    self._logger.debug(
                        f"  {col_name}: "
                        f"type={orig_attr.type}, "
                        f"category={category_flag} "
                        f"→ sdtype='{col_info['sdtype']}'"
                    )
                else:
                    self._logger.debug(f"  {col_name}: sdtype='{col_info['sdtype']}'")
            self._logger.debug("=" * 80)

            # Create SDV Metadata object from the dictionary
            # Suppress the "No table name was provided" warning and log it instead
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings(
                    "always", message="No table name was provided.*"
                )
                sdv_metadata = SDV_Metadata.load_from_dict(sdv_metadata_dict)
                # Log any warnings as debug messages
                for warning in w:
                    self._logger.debug(f"SDV Metadata: {warning.message}")
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=sdv_metadata
            )
            self._logger.debug("Synthesizer initialized with provided metadata")
        else:
            self._logger.debug(
                "No metadata provided, synthesizer will be initialized during fit"
            )

    def _initialize_impl(self, metadata: SDV_Metadata) -> BaseSingleTableSynthesizer:
        """
        Initialize the synthesizer.

        Args:
            metadata (Metadata): The metadata of the data.

        Returns:
            (BaseSingleTableSynthesizer): The SDV synthesizer

        Raises:
            UnsupportedMethodError: If the synthesizer method is not supported.
        """

        self._logger.debug(
            f"Initializing synthesizer with method: {self.config['syn_method']}"
        )
        try:
            method_code = SDVSingleTableMap.map(self.config["syn_method"])
            self._logger.debug(f"Mapped method code: {method_code}")
            synthesizer_class: Any = self.SDV_SINGLETABLE_MAP[method_code]
            self._logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")
        except KeyError:
            error_msg: str = (
                f"Unsupported synthesizer method: {self.config['syn_method']}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from None

        # Prepare initialization parameters
        init_params = {
            "metadata": metadata,
            "enforce_rounding": True,  # Apply to all synthesizer types
        }

        # Add enforce_min_max_values only for TVAE and GaussianCopula
        if method_code in [SDVSingleTableMap.TVAE, SDVSingleTableMap.GAUSSIANCOPULA]:
            init_params["enforce_min_max_values"] = True
            self._logger.debug(
                f"Adding enforce_min_max_values=True for {synthesizer_class.__name__}"
            )

        # catch warnings during synthesizer initialization:
        # "We strongly recommend saving the metadata using 'save_to_json' for replicability in future SDV versions."
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            synthesizer: BaseSingleTableSynthesizer = synthesizer_class(**init_params)

            for warning in w:
                self._logger.debug(f"Warning during fit: {warning.message}")

        self._logger.debug(
            f"Successfully created {synthesizer_class.__name__} instance"
        )
        return synthesizer

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _impl should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.

        Attributes:
            _impl (BaseSingleTableSynthesizer): The synthesizer object been fitted.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't fit the data. See Issue 454.
        """
        self._logger.debug(f"Fitting synthesizer with data shape: {data.shape}")

        # If metadata is not provided, initialize the synthesizer in the fit method.
        if not hasattr(self, "_impl") or self._impl is None:
            self._logger.debug("Initializing synthesizer in _fit method")
            # Create Schema from data and convert to SDV metadata
            schema = SchemaMetadater.from_data(data)
            sdv_metadata_dict = schema_to_sdv(schema)

            # DIAGNOSTIC: Log the inferred metadata
            self._logger.debug("=" * 80)
            self._logger.debug(
                "[DIAGNOSTIC] Inferred Schema -> SDV Metadata (fit method)"
            )
            self._logger.debug("=" * 80)
            for col_name, col_info in sdv_metadata_dict["columns"].items():
                # Get inferred attribute
                attr = schema.attributes.get(col_name)
                if attr:
                    category_flag = (
                        attr.type_attr.get("category", False)
                        if attr.type_attr
                        else False
                    )
                    actual_dtype = str(data[col_name].dtype)
                    self._logger.debug(
                        f"  {col_name}: "
                        f"dtype={actual_dtype}, "
                        f"type={attr.type}, "
                        f"category={category_flag} "
                        f"→ sdtype='{col_info['sdtype']}'"
                    )
            self._logger.debug("=" * 80)

            # Create SDV Metadata object from the dictionary
            # Suppress the "No table name was provided" warning and log it instead
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings(
                    "always", message="No table name was provided.*"
                )
                sdv_metadata = SDV_Metadata.load_from_dict(sdv_metadata_dict)
                # Log any warnings as debug messages
                for warning in w:
                    self._logger.debug(f"SDV Metadata: {warning.message}")
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=sdv_metadata
            )
            self._logger.debug("Synthesizer initialized from data")

        try:
            self._logger.debug("Fitting synthesizer with data")
            self._impl.fit(data)
            self._logger.info("Successfully fitted synthesizer with data")
        except FitError as ex:
            error_msg: str = f"The synthesizer couldn't fit the data. FitError: {ex}."
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't synthesize the data.
        """
        num_rows = self.config["sample_num_rows"]
        self._logger.debug(f"Sampling {num_rows} rows from synthesizer")

        batch_size: int = None
        if "batch_size" in self.config:
            self._logger.debug(f"Using batch size: {batch_size}")
            batch_size = int(self.config["batch_size"])

        try:
            synthetic_data = self._impl.sample(
                num_rows=num_rows,
                batch_size=batch_size,
            )
            self._logger.info(f"Successfully sampled {len(synthetic_data)} rows")
            self._logger.debug(f"Generated data shape: {synthetic_data.shape}")
            # Precision rounding is now handled by the base class
            return synthetic_data
        except Exception as ex:
            error_msg: str = f"SDV synthesizer couldn't sample the data: {ex}"
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex
