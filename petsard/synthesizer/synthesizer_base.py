import logging
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError, UnfittedError
from petsard.metadater import Schema


class BaseSynthesizer(ABC):
    """
    Base class for all synthesizer engine implementations.
    These engines are used by the main Synthesizer to perform the actual data synthesis.
    """

    def __init__(self, config: dict, metadata: Schema = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
                - syn_method (str): The method of how you synthesize data.
                - sample_num_rows (int): The number of rows to be synthesized.
            metadata (Schema, optional): The schema metadata object.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            metadata (Schema): The schema metadata object.
            _impl (Any): The synthesizer object.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        if "syn_method" not in config:
            error_msg: str = (
                "The 'syn_method' parameter is required for the synthesizer."
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        self.config: dict = config
        self.training_data_rows: int | None = None  # Store training data size
        self.metadata: Schema = metadata  # Store metadata for subclasses to use
        self._impl: Any = None

    def update_config(self, config: dict) -> None:
        """
        Update the synthesizer configuration.

        Args:
            config (dict): The new configuration.
        """
        self.config.update(config)

    @abstractmethod
    def _fit(self, data: pd.DataFrame = None) -> None:
        """
        Fit the synthesizer.
            _impl should be initialized in this method.

        Args:
            data (pd.DataFrame, optional): The data to be fitted.

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        error_msg: str = "The '_fit' method must be implemented in the derived class."
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)

    def fit(self, data: pd.DataFrame = None) -> None:
        """
        Fit the synthesizer to the provided data.

        This method calls the implementation-specific _fit method, which should
        train the synthesizer and prepare it for generating synthetic data.

        Args:
            data (pd.DataFrame, optional): same as _fit method.
        """
        self._logger.info(f"Fitting {self.__class__.__name__}")
        self._fit(data)
        self._logger.info(f"Successfully fitting {self.__class__.__name__}")

    @abstractmethod
    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        error_msg: str = (
            "The '_sample' method must be implemented in the derived class."
        )
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)

    def sample(self) -> pd.DataFrame:
        """
        Generate synthetic data from the fitted synthesizer.

        This method checks if the synthesizer has been properly fitted,
        then calls the implementation-specific _sample method to generate data.
        If metadata is available, applies precision rounding to numeric columns.

        Returns:
            pd.DataFrame: Generated synthetic data with precision applied

        Raises:
            UnfittedError: If the synthesizer has not been fitted yet
        """
        if not hasattr(self, "_impl") or self._impl is None:
            error_msg: str = "The synthesizer has not been fitted."
            self._logger.error(error_msg)
            raise UnfittedError(error_msg)

        self._logger.info(f"Sampling {self.__class__.__name__}")
        sampled_data: pd.DataFrame = self._sample()

        # Apply precision rounding if metadata is available
        if self.metadata is not None:
            sampled_data = self._apply_precision(sampled_data)

        self._logger.info(f"Successfully sampling {self.__class__.__name__}")
        return sampled_data

    def _apply_precision(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply precision rounding to numeric columns based on metadata.

        This is a universal feature for all synthesizers to ensure
        numeric values conform to specified precision requirements.

        Args:
            data: The synthesized data

        Returns:
            DataFrame with precision applied
        """
        from petsard.utils import safe_round

        data_copy = data.copy()

        for attr_name, attribute in self.metadata.attributes.items():
            if attr_name not in data_copy.columns:
                continue

            # Handle dict or Attribute object
            if isinstance(attribute, dict):
                type_attr = attribute.get("type_attr")
                attr_type = attribute.get("type")
            else:
                type_attr = attribute.type_attr
                attr_type = attribute.type

            # Apply precision if specified
            if type_attr and "precision" in type_attr:
                precision = type_attr["precision"]

                # Only apply to numeric columns
                if attr_type and ("float" in attr_type or "int" in attr_type):
                    # Use safe_round from utils for consistent rounding behavior
                    data_copy[attr_name] = data_copy[attr_name].apply(
                        lambda x: safe_round(x, precision)
                    )

                    self._logger.debug(
                        f"Applied precision {precision} to column {attr_name}"
                    )

        return data_copy
