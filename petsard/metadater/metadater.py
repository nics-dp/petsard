from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import yaml

from petsard.exceptions import MetadataError
from petsard.metadater.metadata import Attribute, Metadata, Schema
from petsard.metadater.stats import DatasetsStats, FieldStats, TableStats


class AttributeMetadater:
    """Single column operations

    All methods are implemented here, Attribute is just configuration
    """

    @classmethod
    def from_data(
        cls,
        data: pd.Series,
        enable_stats: bool = True,
        base_attribute: Attribute = None,
        **kwargs,
    ) -> Attribute:
        """Create Attribute configuration from Series

        Args:
            data: Data Series
            enable_stats: Whether to calculate statistics
            base_attribute: Base Attribute (if any), precision not inferred if defined
            **kwargs: Other parameters
        """
        # With base_attribute: fully inherit attributes, do not re-infer from data
        # Without base_attribute: infer from data (first time creating schema)

        if base_attribute:
            # === With base_attribute: directly inherit, maintain schema definition consistency ===
            data_type = base_attribute.type
            logical_type = base_attribute.logical_type

            # Copy type_attr
            type_attr = {}
            if base_attribute.type_attr:
                # Fully inherit type_attr (including category, nullable, precision, etc.)
                type_attr = base_attribute.type_attr.copy()
            else:
                # base_attribute has no type_attr, use default values
                type_attr["category"] = False
                type_attr["nullable"] = True

        else:
            # === Without base_attribute: infer from data (first time creating schema) ===
            dtype_str = str(data.dtype)

            # Simplified type mapping: only keep int, float, str, date, datetime
            type_mapping = {
                "int8": "int",
                "int16": "int",
                "int32": "int",
                "int64": "int",
                "float32": "float",
                "float64": "float",
                "bool": "str",  # boolean treated as string category
                "object": "str",
                "datetime64[ns]": "datetime",
            }

            data_type = type_mapping.get(dtype_str, "str")

            # Infer logical type
            logical_type = cls._infer_logical_type(data)

            # Prepare type_attr
            type_attr = {}

            # Infer if it's categorical data
            is_category = dtype_str == "category" or (
                data.dtype == "object" and len(data.unique()) / len(data) < 0.05
                if len(data) > 0
                else False
            )
            type_attr["category"] = is_category

            # Infer nullable
            type_attr["nullable"] = bool(data.isnull().any())

            # Calculate precision for numeric fields (only on first inference and for float)
            if data_type == "float":
                precision = cls._infer_precision(data)
                if precision is not None:
                    type_attr["precision"] = precision

        # Calculate statistics (calculated regardless of base_attribute)
        stats = None
        if enable_stats:
            stats = cls._calculate_field_stats(
                data, data_type, type_attr.get("category", False), logical_type
            )

        # Detect constant columns (all values are the same)
        is_constant = cls._detect_constant_column(data)

        return Attribute(
            name=data.name,
            type=data_type,
            type_attr=type_attr if type_attr else None,
            logical_type=logical_type,
            enable_stats=enable_stats,
            stats=stats,
            is_constant=is_constant,
        )

    @classmethod
    def _infer_precision(cls, data: pd.Series) -> int | None:
        """Infer precision (decimal places) for numeric fields

        This method analyzes all values in the field and finds the maximum decimal places as precision.

        Args:
            data: Numeric Series

        Returns:
            Precision (decimal places), None if cannot infer
        """
        from decimal import Decimal

        import numpy as np

        # Only handle float types
        if not pd.api.types.is_float_dtype(data):
            return None

        # Remove NaN values
        non_na_data = data.dropna()
        if len(non_na_data) == 0:
            return None

        # Calculate decimal places for each value
        precisions = []
        for value in non_na_data:
            if not np.isfinite(value):  # Skip inf and -inf
                continue

            # Use Decimal for precise decimal place detection
            # This correctly handles float precision, avoiding string formatting limitations
            try:
                # Convert float to Decimal to preserve full precision
                decimal_value = Decimal(str(value))
                # Normalize to remove trailing zeros
                normalized = decimal_value.normalize()
                # Calculate decimal places
                sign, digits, exponent = normalized.as_tuple()
                if exponent < 0:
                    precisions.append(abs(exponent))
                else:
                    precisions.append(0)
            except (ValueError, OverflowError):
                # If conversion fails, skip this value
                continue

        if not precisions:
            return None

        # Return maximum precision in this field
        return max(precisions)

    @classmethod
    def _infer_logical_type(cls, data: pd.Series) -> str | None:
        """Infer logical type"""
        # Simple logical type inference
        if data.dtype == "object":
            sample = data.dropna().head(100)

            # Ensure sample is not empty
            if len(sample) == 0:
                return None

            # Check if all are string types
            try:
                # First confirm all values are strings
                all_strings = all(isinstance(x, str) for x in sample)

                if all_strings:
                    # Check if email
                    if sample.str.contains(
                        r"^[^@]+@[^@]+\.[^@]+$", regex=True, na=False
                    ).all():
                        return "email"
            except (AttributeError, TypeError):
                # If any mixed types, skip email check
                pass

        return None

    @classmethod
    def from_metadata(cls, attribute: Attribute) -> Attribute:
        """Copy Attribute configuration"""
        return Attribute(**attribute.__dict__)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Attribute:
        """Create Attribute from dictionary (v2.0 ideal format)"""
        return Attribute(**config)

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Attribute:
        """Create Attribute from existing format (v1.0 compatibility)

        This method is usually not used directly, as v1 format fields
        are converted at Schema level
        """
        return cls.from_dict(config)

    @classmethod
    def diff(cls, attribute: Attribute, data: pd.Series) -> dict[str, Any]:
        """Compare differences between Attribute and Series"""
        diff_result = {"name": attribute.name, "changes": []}

        # Check data type differences
        current_type = str(data.dtype)
        if attribute.type and current_type != attribute.type:
            diff_result["changes"].append(
                {"field": "type", "expected": attribute.type, "actual": current_type}
            )

        # Check null value differences
        has_null = data.isnull().any()
        nullable = (
            attribute.type_attr.get("nullable", True) if attribute.type_attr else True
        )
        if has_null and not nullable:
            diff_result["changes"].append(
                {
                    "field": "null_values",
                    "expected": "no nulls",
                    "actual": f"{data.isnull().sum()} nulls found",
                }
            )

        return diff_result

    @classmethod
    def align(
        cls,
        attribute: Attribute,
        data: pd.Series,
        strategy: dict[str, Any] | None = None,
    ) -> pd.Series:
        """Align Series according to Attribute

        Args:
            attribute: Field attribute definition
            data: Original data
            strategy: Alignment strategy (reserved)

        Returns:
            Aligned Series

        Raises:
            ValueError: When type conversion fails and cast_errors='raise'
        """
        from petsard.utils import safe_round

        aligned = data.copy()

        # Handle null values
        if attribute.na_values:
            aligned = aligned.replace(attribute.na_values, pd.NA)

        # Type conversion (based on simplified type system)
        if attribute.type:
            try:
                if attribute.type == "int":
                    # Integer type: use Int64 or optimized int type based on nullable
                    nullable = (
                        attribute.type_attr.get("nullable", True)
                        if attribute.type_attr
                        else True
                    )

                    # CRITICAL FIX: Round float values before converting to int
                    # This handles cases where float64 data (e.g., from synthesis)
                    # contains decimal values (e.g., 1.5, 2.3) that need to be
                    # converted to integers. Without rounding, astype("Int64") fails.
                    # Critical fix: round float values before converting to int
                    # This handles cases where float64 from synthesis contains decimal values
                    if pd.api.types.is_float_dtype(aligned):
                        aligned = aligned.round()

                    if aligned.isnull().any() or nullable:
                        # Has null or allows null: use nullable Int64
                        aligned = aligned.astype("Int64")
                    else:
                        # No null: optimize based on enable_optimize_type
                        if attribute.enable_optimize_type:
                            aligned = cls._optimize_int_dtype(aligned)
                        else:
                            aligned = aligned.astype("int64")

                elif attribute.type == "float":
                    # Float type: optimize based on enable_optimize_type
                    if attribute.enable_optimize_type:
                        aligned = cls._optimize_float_dtype(
                            aligned, attribute.type_attr
                        )
                    else:
                        aligned = aligned.astype("float64")

                elif attribute.type == "str":
                    # Special handling: if data is already numeric, keep numeric type
                    # This avoids converting Preprocessor-encoded numeric data back to string
                    if not pd.api.types.is_numeric_dtype(aligned):
                        aligned = aligned.astype("string")
                    # If already numeric type, keep unchanged

                elif attribute.type in ["date", "datetime"]:
                    aligned = pd.to_datetime(aligned, errors=attribute.cast_errors)
                else:
                    # Other types keep unchanged or try conversion
                    aligned = aligned.astype(attribute.type)

            except Exception as e:
                if attribute.cast_errors == "raise":
                    raise MetadataError(
                        f"Type conversion failed: field '{attribute.name}' "
                        f"cannot convert from {data.dtype} to {attribute.type}",
                        field_name=attribute.name,
                        source_type=str(data.dtype),
                        target_type=attribute.type,
                        error_details=str(e)
                    ) from e
                # coerce: keep original data

        # Handle numeric precision (if set)
        if attribute.type_attr and "precision" in attribute.type_attr:
            precision = attribute.type_attr["precision"]
            # Check if actual data type is numeric, not just schema definition
            if pd.api.types.is_numeric_dtype(aligned):
                # Apply precision to numeric fields
                aligned = aligned.apply(lambda x: safe_round(x, precision))

        # Apply default value
        if attribute.default_value is not None:
            aligned = aligned.fillna(attribute.default_value)

        return aligned

    @classmethod
    def _optimize_int_dtype(cls, series: pd.Series) -> pd.Series:
        """Optimize integer type, choose smallest suitable dtype

        Args:
            series: Integer Series

        Returns:
            Optimized Series
        """
        import numpy as np

        # First convert to int64 to ensure correct type
        series_int = series.astype("int64")

        # Get min and max values
        min_val = series_int.min()
        max_val = series_int.max()

        # Choose smallest dtype based on range
        if min_val >= np.iinfo(np.int8).min and max_val <= np.iinfo(np.int8).max:
            return series_int.astype("int8")
        elif min_val >= np.iinfo(np.int16).min and max_val <= np.iinfo(np.int16).max:
            return series_int.astype("int16")
        elif min_val >= np.iinfo(np.int32).min and max_val <= np.iinfo(np.int32).max:
            return series_int.astype("int32")
        else:
            return series_int  # int64

    @classmethod
    def _optimize_float_dtype(
        cls, series: pd.Series, type_attr: dict[str, Any] | None
    ) -> pd.Series:
        """Optimize float type

        Choose float32 or float64 based on precision requirements:
        - If has precision and <= 7: use float32
        - Otherwise use float64

        Args:
            series: Float Series
            type_attr: Type attributes (may contain precision)

        Returns:
            Optimized Series
        """
        # First convert to float64 to ensure correct type
        series_float = series.astype("float64")

        # Check precision setting
        if type_attr and "precision" in type_attr:
            precision = type_attr["precision"]
            # float32 significant digits ~7, float64 ~15
            if precision <= 7:
                return series_float.astype("float32")

        return series_float  # float64

    @classmethod
    def validate(cls, attribute: Attribute, data: pd.Series) -> tuple[bool, list[str]]:
        """Validate if Series conforms to Attribute definition"""
        errors = []

        # Type validation
        if attribute.type and str(data.dtype) != attribute.type:
            errors.append(f"Type mismatch: expected {attribute.type}, got {data.dtype}")

        # Null value validation
        nullable = (
            attribute.type_attr.get("nullable", True) if attribute.type_attr else True
        )
        if not nullable and data.isnull().any():
            errors.append(f"Null values not allowed, found {data.isnull().sum()}")

        # Constraint validation
        if attribute.constraints:
            if "min" in attribute.constraints:
                if (data < attribute.constraints["min"]).any():
                    errors.append(
                        f"Values below minimum {attribute.constraints['min']}"
                    )

            if "max" in attribute.constraints:
                if (data > attribute.constraints["max"]).any():
                    errors.append(
                        f"Values above maximum {attribute.constraints['max']}"
                    )

            if "pattern" in attribute.constraints:
                pattern = attribute.constraints["pattern"]
                if data.dtype == "object":
                    invalid = ~data.str.match(pattern)
                    if invalid.any():
                        errors.append(f"Values not matching pattern {pattern}")

        return len(errors) == 0, errors

    @classmethod
    def cast(cls, attribute: Attribute, data: pd.Series) -> pd.Series:
        """Convert data type according to Attribute definition"""
        return cls.align(attribute, data)

    @classmethod
    def _calculate_field_stats(
        cls,
        series: pd.Series,
        data_type: str,
        is_category: bool,
        logical_type: str | None = None,
    ) -> FieldStats:
        """Calculate field statistics

        Determine which statistics to calculate based on type and category:
        - unique_count, category_distribution: only calculated when category=True
        - min, max, mean, std: only calculated when type != 'str' and category=False

        Args:
            series: Data Series
            data_type: Simplified data type (int, float, str, date, datetime)
            is_category: Whether it's categorical data
            logical_type: Logical type

        Statistical calculation logic implemented in Metadater class
        """
        import pandas as pd

        row_count = len(series)
        na_count = series.isna().sum()
        na_percentage = (na_count / row_count) if row_count > 0 else 0.0

        # unique_count: only calculated when category=True
        unique_count = None
        if is_category:
            unique_count = series.nunique()

        # Numeric statistics: only calculated when type != 'str' and category=False
        mean = None
        std = None
        min_val = None
        max_val = None
        median = None
        q1 = None
        q3 = None

        if (
            data_type in ["int", "float", "date", "datetime"]
            and not is_category
            and not series.empty
        ):
            non_na_series = series.dropna()
            if len(non_na_series) > 0 and pd.api.types.is_numeric_dtype(non_na_series):
                mean = float(non_na_series.mean())
                std = float(non_na_series.std())
                min_val = float(non_na_series.min())
                max_val = float(non_na_series.max())
                median = float(non_na_series.median())
                q1 = float(non_na_series.quantile(0.25))
                q3 = float(non_na_series.quantile(0.75))

        # Category statistics: only calculated when category=True
        mode = None
        mode_frequency = None
        category_distribution = None

        if is_category and not series.empty:
            mode_series = series.mode()
            if not mode_series.empty:
                mode = mode_series.iloc[0]
                mode_frequency = int((series == mode).sum())

            # Calculate category distribution
            value_counts = series.value_counts()
            # Limit to top 20 categories
            top_categories = value_counts.head(20)
            category_distribution = {str(k): int(v) for k, v in top_categories.items()}

        return FieldStats(
            row_count=row_count,
            na_count=int(na_count),
            na_percentage=round(na_percentage, 4),
            unique_count=int(unique_count) if unique_count is not None else None,
            mean=mean,
            std=std,
            min=min_val,
            max=max_val,
            median=median,
            q1=q1,
            q3=q3,
            mode=mode,
            mode_frequency=mode_frequency,
            category_distribution=category_distribution,
            detected_type=str(series.dtype),
            actual_dtype=str(series.dtype),
            logical_type=logical_type,
        )

    @classmethod
    def _detect_constant_column(cls, data: pd.Series) -> bool:
        """檢測欄位是否所有值都相同（constant column）

        Args:
            data: 資料 Series

        Returns:
            bool: 如果所有非 NA 值都相同則返回 True
        """
        # 移除 NA 值
        non_na_data = data.dropna()

        # 如果所有值都是 NA，不視為 constant
        if len(non_na_data) == 0:
            return False

        # 檢查 unique 值的數量
        unique_count = non_na_data.nunique()

        # 如果只有一個唯一值，則為 constant column
        return unique_count == 1


class SchemaMetadater:
    """Single table operations

    All methods are implemented here, Schema is just configuration
    """

    @classmethod
    def from_data(
        cls,
        data: pd.DataFrame,
        enable_stats: bool = False,
        base_schema: Schema = None,
        **kwargs,
    ) -> Schema:
        """Create Schema configuration from DataFrame

        Args:
            data: Data DataFrame
            enable_stats: Whether to calculate statistics
            base_schema: Base Schema (if any), precision not inferred if field has definition
            **kwargs: Other parameters
        """
        attributes = {}

        for col in data.columns:
            # Check if this field has definition in base_schema
            base_attribute = None
            if base_schema and base_schema.attributes and col in base_schema.attributes:
                base_attribute = base_schema.attributes[col]

            attributes[col] = AttributeMetadater.from_data(
                data[col], enable_stats=enable_stats, base_attribute=base_attribute
            )

        # Calculate table statistics
        stats = None
        if enable_stats:
            # Collect field stats
            field_stats = {}
            for col_name, attr in attributes.items():
                if attr.stats:
                    field_stats[col_name] = attr.stats
            # Calculate table statistics
            stats = cls._calculate_table_stats(data, field_stats)

        return Schema(
            id=kwargs.get("id", "inferred_schema"),
            name=kwargs.get("name", "Inferred Schema"),
            attributes=attributes,
            enable_stats=enable_stats,
            stats=stats,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["id", "name", "enable_stats", "stats"]
            },
        )

    @classmethod
    def from_metadata(cls, schema: Schema) -> Schema:
        """Copy Schema configuration"""
        # Deep copy attributes
        new_attributes = {}
        for name, attr in schema.attributes.items():
            new_attributes[name] = AttributeMetadater.from_metadata(attr)

        return Schema(**{**schema.__dict__, "attributes": new_attributes})

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Schema:
        """Create Schema from existing YAML format (v1.0 compatibility)"""
        # Convert fields to attributes
        attributes = {}
        if "fields" in config:
            for field_name, field_config in config["fields"].items():
                # Convert v1 field format to v2 Attribute format
                attr_config = cls._convert_field_to_attribute(field_name, field_config)
                attributes[field_name] = AttributeMetadater.from_dict(attr_config)

        # Create v2 Schema format, support compute_stats and title
        return Schema(
            id=config.get("schema_id", "default"),
            name=config.get(
                "title", config.get("name", "Default Schema")
            ),  # Prefer title
            description=config.get("description", ""),
            attributes=attributes,
            primary_key=config.get("primary_key", []),
            foreign_keys=config.get("foreign_keys", {}),
            enable_stats=config.get("compute_stats", True),  # Support compute_stats
            sample_size=config.get("sample_size"),  # Support sample_size
        )

    @staticmethod
    def _convert_field_to_attribute(name: str, field: dict[str, Any]) -> dict[str, Any]:
        """Convert v1 field format to v2 attribute format"""
        # Simplified type mapping: standardize to int, float, str, date, datetime
        type_mapping = {
            "int": "int",
            "int8": "int",
            "int16": "int",
            "int32": "int",
            "int64": "int",
            "integer": "int",
            "float": "float",
            "float32": "float",
            "float64": "float",
            "str": "str",
            "string": "str",
            "bool": "str",
            "boolean": "str",
            "date": "date",
            "datetime": "datetime",
            "datetime64": "datetime",
        }

        # Create attribute configuration
        attr = {
            "name": name,
            "type": type_mapping.get(field.get("type", "str"), "str"),
            "logical_type": field.get("logical_type", ""),
        }

        # Merge type_attr
        type_attr = {}

        # nullable (inferred from na_values)
        type_attr["nullable"] = True if field.get("na_values") else False

        # Handle category
        if field.get("category_method") == "force":
            type_attr["category"] = True

        # precision
        if "precision" in field:
            type_attr["precision"] = field["precision"]

        # datetime format
        if "datetime_format" in field:
            type_attr["format"] = field["datetime_format"]

        # leading zeros
        if "leading_zeros" in field:
            leading = field["leading_zeros"]
            if leading.startswith("leading_"):
                width = int(leading.split("_")[1])
                type_attr["width"] = width

        if type_attr:
            attr["type_attr"] = type_attr

        return attr

    @staticmethod
    def _normalize_attribute_config(config: dict[str, Any]) -> dict[str, Any]:
        """Normalize attribute configuration, move top-level type_attr related attributes into type_attr dict

        Handle attributes directly defined at top level in YAML such as:
        - category: true
        - nullable: true
        - precision: 2
        - format: "%Y-%m-%d"
        - width: 8

        Move them into type_attr dict to conform to internal structure.
        """
        config = config.copy()  # Avoid modifying original dict

        # Define attributes to move into type_attr
        type_attr_keys = ["category", "nullable", "precision", "format", "width"]

        # Check if any type_attr related attributes at top level
        has_type_attr_in_top = any(key in config for key in type_attr_keys)

        if has_type_attr_in_top:
            # Ensure type_attr dict exists
            if "type_attr" not in config:
                config["type_attr"] = {}

            # Move top-level type_attr related attributes into type_attr dict
            for key in type_attr_keys:
                if key in config:
                    # Only move if type_attr doesn't have this attribute yet
                    if key not in config["type_attr"]:
                        config["type_attr"][key] = config[key]
                    # Delete from top level
                    del config[key]

        return config

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Schema:
        """Create Schema from dictionary (v2.0 ideal format)"""
        # Handle attributes or fields
        if "attributes" in config:
            # Convert dict in attributes to Attribute objects
            attributes = {}
            for attr_name, attr_config in config["attributes"].items():
                if isinstance(attr_config, dict):
                    # Ensure name field exists
                    if "name" not in attr_config:
                        attr_config["name"] = attr_name

                    # Apply simplified type mapping (consistent with fields handling)
                    if "type" in attr_config:
                        type_mapping = {
                            "int": "int",
                            "int8": "int",
                            "int16": "int",
                            "int32": "int",
                            "int64": "int",
                            "integer": "int",
                            "float": "float",
                            "float32": "float",
                            "float64": "float",
                            "str": "str",
                            "string": "str",
                            "bool": "str",
                            "boolean": "str",
                            "date": "date",
                            "datetime": "datetime",
                            "datetime64": "datetime",
                        }
                        attr_config["type"] = type_mapping.get(
                            attr_config["type"], attr_config["type"]
                        )

                    # Handle top-level type_attr related attributes (category, nullable, precision, format, width)
                    # Move them into type_attr dict
                    attr_config = cls._normalize_attribute_config(attr_config)

                    attributes[attr_name] = AttributeMetadater.from_dict(attr_config)
                else:
                    # If already Attribute object, use directly
                    attributes[attr_name] = attr_config
            config["attributes"] = attributes
        elif "fields" in config:
            # Backward compatibility: map fields to internal attributes
            attributes = {}
            for field_name, field_config in config["fields"].items():
                if isinstance(field_config, dict):
                    # Ensure name field exists
                    if "name" not in field_config:
                        field_config["name"] = field_name
                    # Apply simplified type mapping
                    if "type" in field_config:
                        type_mapping = {
                            "int": "int",
                            "int8": "int",
                            "int16": "int",
                            "int32": "int",
                            "int64": "int",
                            "integer": "int",
                            "float": "float",
                            "float32": "float",
                            "float64": "float",
                            "str": "str",
                            "string": "str",
                            "bool": "str",
                            "boolean": "str",
                            "date": "date",
                            "datetime": "datetime",
                            "datetime64": "datetime",
                        }
                        field_config["type"] = type_mapping.get(
                            field_config["type"], field_config["type"]
                        )

                    # Normalize attribute configuration (handle top-level type_attr attributes)
                    field_config = cls._normalize_attribute_config(field_config)

                    attributes[field_name] = AttributeMetadater.from_dict(field_config)
                else:
                    # If already Attribute object, use directly
                    attributes[field_name] = field_config
            config["attributes"] = attributes
            del config["fields"]  # Remove fields, use attributes instead

        return Schema(**config)

    @classmethod
    def from_yaml(cls, filepath: str) -> Schema:
        """Load Schema from YAML file

        Raises:
            ValueError: When YAML file has duplicate field names
        """

        # Use custom loader to detect duplicate keys
        class DuplicateKeysLoader(yaml.SafeLoader):
            """Custom YAML Loader, detect duplicate keys"""

            pass

        def check_duplicate_keys(loader, node, deep=False):
            """Check and report duplicate keys"""
            mapping = {}
            duplicates = []

            for key_node, _value_node in node.value:
                # Get actual value of key
                key = loader.construct_object(key_node, deep=deep)
                if key in mapping:
                    # Record duplicate key and its line number
                    duplicates.append(
                        f"  - '{key}' (first at line {mapping[key]}, duplicate at line {key_node.start_mark.line + 1})"
                    )
                else:
                    mapping[key] = key_node.start_mark.line + 1

            if duplicates:
                error_msg = (
                    "Schema file contains duplicate attribute names:\n"
                    + "\n".join(duplicates)
                    + f"\n\nFile: {filepath}"
                )
                raise ValueError(error_msg)

            # Use parent class construct_mapping method
            return yaml.SafeLoader.construct_mapping(loader, node, deep)

        # Override construct_mapping method
        DuplicateKeysLoader.construct_mapping = check_duplicate_keys

        with open(filepath) as f:
            try:
                config = yaml.load(f, Loader=DuplicateKeysLoader)
            except MetadataError:
                # Re-raise MetadataError, keep original error message
                raise
            except yaml.YAMLError as e:
                # Other YAML parsing errors
                raise MetadataError(
                    f"Failed to parse YAML file {filepath}: {e}",
                    filepath=filepath
                ) from e

        # Use from_dict directly, it handles both fields and attributes formats
        return cls.from_dict(config)

    @classmethod
    def get(cls, schema: Schema, name: str) -> Attribute:
        """Get Attribute from Schema"""
        if name not in schema.attributes:
            raise MetadataError(
                f"Attribute '{name}' not found in schema '{schema.id}'",
                attribute_name=name,
                schema_id=schema.id
            )
        return schema.attributes[name]

    @classmethod
    def add(cls, schema: Schema, attribute: Attribute | pd.Series) -> Schema:
        """Add Attribute to Schema"""
        if isinstance(attribute, pd.Series):
            attribute = AttributeMetadater.from_data(attribute)

        new_attributes = dict(schema.attributes)
        new_attributes[attribute.name] = attribute

        return Schema(
            **{
                **schema.__dict__,
                "attributes": new_attributes,
                "updated_at": datetime.now(),
            }
        )

    @classmethod
    def update(cls, schema: Schema, attribute: Attribute | pd.Series) -> Schema:
        """Update Attribute in Schema"""
        return cls.add(schema, attribute)  # add will overwrite attribute with same name

    @classmethod
    def remove(cls, schema: Schema, name: str) -> Schema:
        """Remove Attribute from Schema"""
        new_attributes = dict(schema.attributes)
        if name in new_attributes:
            del new_attributes[name]

        return Schema(
            **{
                **schema.__dict__,
                "attributes": new_attributes,
                "updated_at": datetime.now(),
            }
        )

    @classmethod
    def diff(cls, schema: Schema, data: pd.DataFrame) -> dict[str, Any]:
        """Compare differences between Schema and DataFrame"""
        diff_result = {
            "schema_id": schema.id,
            "missing_columns": [],
            "extra_columns": [],
            "attribute_changes": {},
        }

        schema_cols = set(schema.attributes.keys())
        data_cols = set(data.columns)

        # Find missing and extra fields
        diff_result["missing_columns"] = list(schema_cols - data_cols)
        diff_result["extra_columns"] = list(data_cols - schema_cols)

        # Compare differences in common fields
        common_cols = schema_cols & data_cols
        for col in common_cols:
            attr_diff = AttributeMetadater.diff(schema.attributes[col], data[col])
            if attr_diff["changes"]:
                diff_result["attribute_changes"][col] = attr_diff

        return diff_result

    @classmethod
    def align(
        cls, schema: Schema, data: pd.DataFrame, strategy: dict[str, Any] | None = None
    ) -> pd.DataFrame:
        """Align DataFrame according to Schema"""
        strategy = strategy or {}
        aligned_df = data.copy()

        # Handle missing fields
        for col_name, attribute in schema.attributes.items():
            if col_name not in aligned_df.columns:
                # Handle missing fields based on strategy
                if strategy.get("add_missing_columns", True):
                    # Add missing field and fill with default value
                    if attribute.default_value is not None:
                        aligned_df[col_name] = attribute.default_value
                    else:
                        aligned_df[col_name] = pd.NA
            else:
                # Align existing fields
                aligned_df[col_name] = AttributeMetadater.align(
                    attribute, aligned_df[col_name], strategy
                )

        # Handle extra fields
        if strategy.get("remove_extra_columns", False):
            extra_cols = set(aligned_df.columns) - set(schema.attributes.keys())
            aligned_df = aligned_df.drop(columns=list(extra_cols))

        # Reorder fields
        if strategy.get("reorder_columns", True):
            col_order = [
                col for col in schema.attributes.keys() if col in aligned_df.columns
            ]
            # Keep fields not in schema (if not removed)
            extra_cols = [col for col in aligned_df.columns if col not in col_order]
            aligned_df = aligned_df[col_order + extra_cols]

        return aligned_df

    @classmethod
    def _calculate_table_stats(
        cls, df: pd.DataFrame, field_stats: dict[str, FieldStats]
    ) -> TableStats:
        """Calculate table statistics

        Statistical calculation logic implemented in SchemaMetadater class
        """
        row_count = len(df)
        column_count = len(df.columns)

        # Calculate total NA count from field statistics
        total_na_count = sum(stats.na_count for stats in field_stats.values())
        total_cells = row_count * column_count
        total_na_percentage = (total_na_count / total_cells) if total_cells > 0 else 0.0

        # Memory usage
        memory_usage_bytes = int(df.memory_usage(deep=True).sum())

        # Duplicate data check
        duplicated_rows = int(df.duplicated().sum())

        # Check identical fields
        duplicated_columns = []
        columns = list(df.columns)
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                if df[columns[i]].equals(df[columns[j]]):
                    duplicated_columns.append(f"{columns[i]}=={columns[j]}")

        return TableStats(
            row_count=row_count,
            column_count=column_count,
            total_na_count=total_na_count,
            total_na_percentage=round(total_na_percentage, 4),
            memory_usage_bytes=memory_usage_bytes,
            duplicated_rows=duplicated_rows,
            duplicated_columns=duplicated_columns[:10],  # Limit to max 10 pairs
            field_stats=field_stats,
        )


class Metadater:
    """Multiple tables operations

    All methods are implemented here, Metadata is just configuration
    """

    @classmethod
    def from_data(
        cls, data: dict[str, pd.DataFrame], enable_stats: bool = False, **kwargs
    ) -> Metadata:
        """Create Metadata from data, including statistics

        Args:
            data: Data table dictionary
            enable_stats: Whether to calculate statistics
            **kwargs: Other Metadata parameters

        Returns:
            Metadata: Metadata containing statistics
        """

        # Create schemas
        schemas = {}
        for name, df in data.items():
            # Pass parameters directly to SchemaMetadater.from_data
            schema = SchemaMetadater.from_data(
                df, enable_stats=enable_stats, id=name, name=name
            )
            schemas[name] = schema

        # Calculate dataset statistics
        stats = None
        if enable_stats:
            # Collect already calculated table statistics
            table_stats = {
                name: schema.stats for name, schema in schemas.items() if schema.stats
            }
            stats = cls._calculate_datasets_stats(table_stats)

        # Override default values
        defaults = {
            "id": kwargs.get("id", "inferred_metadata"),
            "name": kwargs.get("name", "Inferred Metadata"),
            "schemas": schemas,
            "enable_stats": enable_stats,
            "stats": stats,
        }
        defaults.update(kwargs)

        return Metadata(**defaults)

    @classmethod
    def from_metadata(cls, metadata: Metadata) -> Metadata:
        """Copy Metadata configuration"""
        # Deep copy schemas
        new_schemas = {}
        for name, schema in metadata.schemas.items():
            new_schemas[name] = SchemaMetadater.from_metadata(schema)

        return Metadata(**{**metadata.__dict__, "schemas": new_schemas})

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Metadata:
        """Create Metadata from existing YAML format (v1.0 compatibility)

        Handle existing single Schema format
        """
        # Convert v1 format to v2 format
        schema = SchemaMetadater.from_dict_v1(config)

        return Metadata(
            id=config.get("metadata_id", "default"),
            name=config.get("name", "Default Metadata"),
            description=config.get("description", ""),
            schemas={"default": schema},
        )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Metadata:
        """Create Metadata from dictionary (v2.0 ideal format)"""
        # Recursively process schemas
        if "schemas" in config:
            schemas = {}
            for schema_id, schema_config in config["schemas"].items():
                schemas[schema_id] = SchemaMetadater.from_dict(schema_config)
            config["schemas"] = schemas

        return Metadata(**config)

    @classmethod
    def get(cls, metadata: Metadata, name: str) -> Schema:
        """Get Schema from Metadata"""
        if name not in metadata.schemas:
            raise MetadataError(
                f"Schema '{name}' not found in metadata '{metadata.id}'",
                schema_name=name,
                metadata_id=metadata.id
            )
        return metadata.schemas[name]

    @classmethod
    def add(cls, metadata: Metadata, schema: Schema | pd.DataFrame) -> Metadata:
        """Add Schema to Metadata"""
        if isinstance(schema, pd.DataFrame):
            schema = SchemaMetadater.from_data(schema)

        new_schemas = dict(metadata.schemas)
        new_schemas[schema.id] = schema

        return Metadata(
            **{
                **metadata.__dict__,
                "schemas": new_schemas,
                "updated_at": datetime.now(),
            }
        )

    @classmethod
    def update(cls, metadata: Metadata, schema: Schema | pd.DataFrame) -> Metadata:
        """Update Schema in Metadata"""
        return cls.add(metadata, schema)  # add will overwrite schema with same name

    @classmethod
    def remove(cls, metadata: Metadata, name: str) -> Metadata:
        """Remove Schema from Metadata"""
        new_schemas = dict(metadata.schemas)
        if name in new_schemas:
            del new_schemas[name]

        return Metadata(
            **{
                **metadata.__dict__,
                "schemas": new_schemas,
                "updated_at": datetime.now(),
            }
        )

    @classmethod
    def diff(cls, metadata: Metadata, data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        """Compare differences between Metadata and data"""
        diff_result = {
            "metadata_id": metadata.id,
            "missing_tables": [],
            "extra_tables": [],
            "schema_changes": {},
        }

        metadata_tables = set(metadata.schemas.keys())
        data_tables = set(data.keys())

        # Find missing and extra tables
        diff_result["missing_tables"] = list(metadata_tables - data_tables)
        diff_result["extra_tables"] = list(data_tables - metadata_tables)

        # Compare differences in common tables
        common_tables = metadata_tables & data_tables
        for table in common_tables:
            schema_diff = SchemaMetadater.diff(metadata.schemas[table], data[table])
            if (
                schema_diff["missing_columns"]
                or schema_diff["extra_columns"]
                or schema_diff["attribute_changes"]
            ):
                diff_result["schema_changes"][table] = schema_diff

        return diff_result

    @classmethod
    def align(
        cls,
        metadata: Metadata,
        data: dict[str, pd.DataFrame],
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Align data according to Metadata"""
        strategy = strategy or {}
        aligned = {}

        for schema_id, schema in metadata.schemas.items():
            if schema_id in data:
                # Call lower-level SchemaMetadater
                aligned_df = SchemaMetadater.align(schema, data[schema_id], strategy)
                aligned[schema_id] = aligned_df
            elif strategy.get("add_missing_tables", False):
                # Create empty DataFrame
                columns = list(schema.attributes.keys())
                aligned[schema_id] = pd.DataFrame(columns=columns)

        return aligned

    @classmethod
    def _calculate_datasets_stats(
        cls, table_stats: dict[str, TableStats]
    ) -> DatasetsStats:
        """Calculate dataset statistics

        Statistical calculation logic implemented in Metadater class
        """
        table_count = len(table_stats)
        total_row_count = sum(stats.row_count for stats in table_stats.values())
        total_column_count = sum(stats.column_count for stats in table_stats.values())
        total_memory_usage_bytes = sum(
            stats.memory_usage_bytes
            for stats in table_stats.values()
            if stats.memory_usage_bytes
        )

        return DatasetsStats(
            table_count=table_count,
            total_row_count=total_row_count,
            total_column_count=total_column_count,
            total_memory_usage_bytes=total_memory_usage_bytes
            if total_memory_usage_bytes
            else None,
            table_stats=table_stats,
        )
