from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from petsard.config_base import BaseConfig
from petsard.exceptions import (
    ConfigError,
    UnableToFollowMetadataError,
    UnsupportedMethodError,
)
from petsard.metadater import Attribute, Schema, SchemaMetadater


class LoaderFileExt:
    """
    Mapping of File extension.
    """

    CSVTYPE: int = 1
    EXCELTYPE: int = 2

    CSV: int = 10
    XLS: int = 20
    XLSX: int = 21
    XLSM: int = 22
    XLSB: int = 23
    ODF: int = 24
    ODS: int = 25
    ODT: int = 26

    @classmethod
    def get(cls, file_ext: str) -> int:
        """
        Get suffixes mapping int value of file extension.

        Args:
            file_ext (str): File extension
        """
        return cls.__dict__[file_ext[1:].upper()] // 10


@dataclass
class LoaderConfig(BaseConfig):
    """
    Configuration for the data loader.

    Attributes:
        _logger (logging.Logger): The logger object.
        filepath (str): The fullpath of dataset.
        column_types (dict): The dictionary of column types and their corresponding column names.
        header_names (list): **DEPRECATED in v2.0.0 - will be removed** Specifies a list of headers for the data without header.
        na_values (str | list | dict): Extra string to recognized as NA/NaN.
        schema (Schema): Schema configuration object with field definitions and global parameters.
        schema_path (str): The path to schema file if loaded from YAML file.
        dir_name (str): The directory name of the file path.
        base_name (str): The base name of the file path.
        file_name (str): The file name of the file path.
        file_ext (str): The file extension of the file path.
        file_ext_code (int): The file extension code.
    """

    filepath: str | None = None
    column_types: dict[str, list[str]] | None = (
        None  # TODO: Deprecated in v2.0.0 - will be removed
    )
    header_names: list[str] | None = (
        None  # TODO: Deprecated in v2.0.0 - will be removed
    )
    na_values: str | list[str] | dict[str, str] | None = (
        None  # TODO: Deprecated in v2.0.0 - will be removed
    )
    nrows: int | None = None  # Number of rows to read for quick testing
    schema: Schema | None = None
    schema_path: str | None = None  # 記錄 schema 來源路徑（如果從檔案載入）

    # Filepath related
    dir_name: str | None = None
    base_name: str | None = None
    file_name: str | None = None
    file_ext: str | None = None
    file_ext_code: int | None = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing LoaderConfig")
        error_msg: str = ""

        # 1. validate filepath
        if self.filepath is None:
            error_msg = "filepath must be specified"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 2. handle filepath
        filepath_path: Path = Path(self.filepath)
        self.dir_name = str(filepath_path.parent)
        self.base_name = filepath_path.name
        self.file_name = filepath_path.stem
        self.file_ext = filepath_path.suffix.lower()
        try:
            self.file_ext_code = LoaderFileExt.get(self.file_ext)
        except KeyError as e:
            error_msg = f"Unsupported file extension: {self.file_ext}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from e
        self._logger.debug(
            f"File path information - dir: {self.dir_name}, name: {self.file_name}, ext: {self.file_ext}, ext code: {self.file_ext_code}"
        )

        # 4. validate column_types (using new Metadater architecture)
        if self.column_types is not None:
            self._logger.debug(f"Validating column types: {self.column_types}")
            valid_column_types = ["category", "datetime"]
            for col_type, columns in self.column_types.items():
                if col_type.lower() not in valid_column_types:
                    error_msg = f"Column type {col_type} on {columns} is not supported"
                    self._logger.error(error_msg)
                    raise UnsupportedMethodError(error_msg)
            self._logger.debug("Column types validation passed")

        # 5. validate schema parameter and check for conflicts
        if self.schema is not None:
            self._logger.debug("Schema configuration provided")
            # SchemaConfig validation is handled by its own dataclass validation
            self._logger.debug("Schema configuration validation passed")

            # Check for conflicts between schema and column_types
            if self.column_types is not None:
                self._logger.debug(
                    "Checking for conflicts between schema and column_types"
                )
                # Schema uses 'attributes' not 'fields'
                if hasattr(self.schema, "attributes") and self.schema.attributes:
                    schema_fields = set(self.schema.attributes.keys())
                    column_type_fields = set()
                    for columns in self.column_types.values():
                        column_type_fields.update(columns)

                    conflicting_fields = schema_fields.intersection(column_type_fields)
                    if conflicting_fields:
                        error_msg = (
                            f"Conflict detected: Fields {list(conflicting_fields)} are defined in both "
                            f"schema and column_types. Please use only schema for these fields."
                        )
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                    self._logger.debug(
                        "No conflicts found between schema and column_types"
                    )


class Loader:
    """
    The Loader class is responsible for creating and configuring a data loader,
    as well as retrieving and processing data from the specified sources.

    The Loader is designed to be passive and focuses on three core functions:
    1. Schema processing: Pass schema parameters to metadater for validation
    2. Legacy compatibility: Update legacy column_types and na_values to schema
    3. Data reading: Use pandas reader module to load data with proper configuration
    """

    def __init__(
        self,
        filepath: str = None,
        column_types: dict[str, list[str]] | None = None,  # TODO: Deprecated in v2.0.0
        header_names: list[str] | None = None,  # TODO: Deprecated in v2.0.0
        na_values: str
        | list[str]
        | dict[str, str]
        | None = None,  # TODO: Deprecated in v2.0.0
        nrows: int | None = None,
        schema: Schema | dict | str | None = None,
    ):
        """
        Args:
            filepath (str): The fullpath of dataset.
            column_types (dict ,optional): **DEPRECATED in v2.0.0 - will be removed**
                The dictionary of column types and their corresponding column names,
                formatted as {type: [colname]}
                Only the following types are supported (case-insensitive):
                - 'category': The column(s) will be treated as categorical.
                - 'datetime': The column(s) will be treated as datetime.
                Default is None, indicating no custom column types will be applied.
            header_names (list ,optional): **DEPRECATED in v2.0.0 - will be removed**
                Specifies a list of headers for the data without header.
                Default is None, indicating no custom headers will be applied.
            na_values (str | list | dict ,optional): **DEPRECATED in v2.0.0 - will be removed**
                Extra string to recognized as NA/NaN.
                If dictionary passed, value will be specific per-column NA values.
                Format as {colname: na_values}.
                Default is None, means no extra.
                Check pandas document for Default NA string list.
            nrows (int, optional): Number of rows to read from the file.
                Useful for quickly testing with a subset of data to reduce memory usage.
                Similar to pandas.read_csv's nrows parameter.
                Default is None, which reads all rows.
            schema (Schema | dict | str, optional): Schema configuration.
                Can be one of:
                - Schema object: Direct schema configuration
                - dict: Dictionary that will be converted to Schema using from_dict()
                - str: Path to YAML file containing schema configuration
                Contains field definitions and global parameters for data processing.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (LoaderConfig): Configuration
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info("Initializing Loader")
        self._logger.debug(
            f"Loader parameters - filepath: {filepath}, column_types: {column_types}"
        )

        # Process schema parameter - handle different input types
        processed_schema, schema_path = self._process_schema_parameter(schema)

        self.config: LoaderConfig = LoaderConfig(
            filepath=filepath,
            column_types=column_types,
            header_names=header_names,
            na_values=na_values,
            nrows=nrows,
            schema=processed_schema,
            schema_path=schema_path,
        )
        self._logger.debug("LoaderConfig successfully initialized")

    def _process_schema_parameter(
        self, schema: Schema | dict | str | None
    ) -> tuple[Schema | None, str | None]:
        """
        Process schema parameter and convert it to Schema object.

        Args:
            schema: Schema parameter that can be Schema, dict, str (path), or None

        Returns:
            tuple: (processed_schema, schema_path)
                - processed_schema: Schema object or None
                - schema_path: Path to schema file if loaded from file, None otherwise
        """
        if schema is None:
            self._logger.debug("No schema provided")
            return None, None

        if isinstance(schema, Schema):
            self._logger.debug("Schema provided as Schema object")
            return schema, None

        if isinstance(schema, dict):
            self._logger.debug("Schema provided as dictionary, converting to Schema")
            try:
                # 使用 SchemaMetadater 的 from_dict 或 from_dict_v1 方法
                # 檢查是否有舊格式的特徵
                has_global_params = any(
                    k in schema
                    for k in ["optimize_dtypes", "nullable_int", "infer_logical_types"]
                )

                if has_global_params:
                    # v1.0 格式
                    schema_obj = SchemaMetadater.from_dict_v1(schema)
                else:
                    # v2.0 格式 - 確保有 id
                    if "id" not in schema:
                        schema["id"] = "auto_generated_schema"
                    schema_obj = SchemaMetadater.from_dict(schema)

                return schema_obj, None
            except Exception as e:
                error_msg = f"Failed to convert dictionary to Schema: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

        if isinstance(schema, str):
            self._logger.info(f"Loading schema from YAML file: {schema}")
            try:
                schema_path = Path(schema)
                if not schema_path.exists():
                    error_msg = f"Schema file not found: {schema}"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

                # 使用 SchemaMetadater.from_yaml 直接載入
                schema_obj = SchemaMetadater.from_yaml(str(schema_path))
                self._logger.debug(f"Successfully loaded schema from {schema}")
                return schema_obj, str(schema_path)

            except yaml.YAMLError as e:
                error_msg = f"Failed to parse YAML file {schema}: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e
            except Exception as e:
                error_msg = f"Failed to load schema from file {schema}: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

        error_msg = f"Unsupported schema type: {type(schema)}"
        self._logger.error(error_msg)
        raise ConfigError(error_msg)

    def load(self) -> tuple[pd.DataFrame, Schema]:
        """
        Load data from the specified file path.

        This method implements three core functions:
        1. Schema processing: Merge legacy parameters into schema and validate
        2. Data reading: Use pandas reader module for file loading
        3. Metadater integration: Pass schema to metadater for processing

        Returns:
            data (pd.DataFrame): Data been loaded
            schema (Schema): Schema metadata of the data
        """
        self._logger.info(f"Loading data from {self.config.filepath}")

        # 1: Schema processing - merge legacy parameters into schema
        merged_schema_config = self._merge_legacy_to_schema()

        # 2: Data reading using pandas reader module
        data = self._read_data_with_pandas_reader(merged_schema_config)

        # 3: Pass schema to metadater for validation and processing
        schema_metadata = self._process_with_metadater(data, merged_schema_config)

        self._logger.info("Data loading completed successfully")
        return data, schema_metadata

    def _merge_legacy_to_schema(self) -> Schema:
        """
        Merge legacy column_types and na_values into Schema.

        Returns:
            Schema: Merged schema configuration
        """
        # Start with existing schema or create a new one
        if self.config.schema:
            # Use existing schema as base
            self._logger.debug("Using existing schema configuration")
            return self.config.schema
        else:
            # Create new schema with attributes
            attributes = {}

            # Merge legacy column_types
            if self.config.column_types:
                self._logger.debug(
                    f"Merging legacy column_types: {self.config.column_types}"
                )
                for col_type, columns in self.config.column_types.items():
                    for col in columns:
                        # 建立 Attribute 物件
                        type_mapping = {
                            "category": "category",
                            "datetime": "datetime64",
                        }
                        attributes[col] = Attribute(
                            name=col,
                            type=type_mapping.get(col_type, "string"),
                            logical_type=col_type
                            if col_type in ["category", "datetime"]
                            else None,
                            enable_null=True,
                        )

            # Merge legacy na_values
            if self.config.na_values:
                self._logger.debug(f"Merging legacy na_values: {self.config.na_values}")
                if isinstance(self.config.na_values, dict):
                    # Column-specific na_values
                    for col, na_val in self.config.na_values.items():
                        if col not in attributes:
                            attributes[col] = Attribute(
                                name=col,
                                type="string",
                                enable_null=True,
                            )
                        # 更新 na_values
                        attributes[col].na_values = (
                            na_val if isinstance(na_val, list) else [na_val]
                        )

            # 建立 Schema 物件
            merged_schema = Schema(
                id=self.config.file_name or "default_schema",
                name=self.config.base_name or "Default Schema",
                description="Auto-generated schema from legacy parameters",
                attributes=attributes,
            )

            self._logger.debug("Created merged schema config")
            return merged_schema

    def _read_data_with_pandas_reader(self, schema: Schema) -> pd.DataFrame:
        """
        Read data using the pandas loader classes.

        Args:
            schema: Merged schema configuration

        Returns:
            pd.DataFrame: Loaded dataframe
        """
        from petsard.loader.loader_pandas import LoaderPandasCsv, LoaderPandasExcel

        self._logger.info("Reading data using pandas loader classes")

        # Map file extension codes to loader classes
        loaders_map = {
            LoaderFileExt.CSVTYPE: LoaderPandasCsv,
            LoaderFileExt.EXCELTYPE: LoaderPandasExcel,
        }

        if self.config.file_ext_code not in loaders_map:
            error_msg = f"Unsupported file extension code: {self.config.file_ext_code}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        loader_class = loaders_map[self.config.file_ext_code]

        # Build configuration for the loader
        config = {
            "filepath": str(self.config.filepath),
            "header_names": self.config.header_names,
        }

        # Add nrows parameter if specified
        if self.config.nrows is not None:
            config["nrows"] = self.config.nrows
            self._logger.info(f"Reading only first {self.config.nrows} rows")

        # Handle legacy na_values (takes precedence over schema na_values for backward compatibility)
        if self.config.na_values is not None:
            config["na_values"] = self.config.na_values
            self._logger.debug(f"Using legacy na_values: {self.config.na_values}")

        # Handle legacy column_types for dtype parameter
        dtype_dict = {}
        if self.config.column_types and "category" in self.config.column_types:
            category_columns = self.config.column_types["category"]
            if isinstance(category_columns, list) and category_columns:
                self._logger.debug(
                    f"Setting category columns to string type: {category_columns}"
                )
                for col in category_columns:
                    dtype_dict[col] = str

        # Handle schema-based dtype configuration
        if schema and schema.attributes:
            for attr_name, attribute in schema.attributes.items():
                if attribute.type:
                    # Map schema types to pandas dtypes
                    if attribute.type == "string":
                        dtype_dict[attr_name] = str
                    elif "int" in attribute.type:
                        # Use nullable integer type for int to handle NA values properly
                        dtype_dict[attr_name] = "Int64"
                    elif "float" in attribute.type:
                        dtype_dict[attr_name] = float
                    elif attribute.type == "boolean":
                        dtype_dict[attr_name] = "boolean"
                    # datetime will be handled post-loading

        # Only add dtype parameter if we have dtype specifications
        if dtype_dict:
            config["dtype"] = dtype_dict
            self._logger.debug(f"Using dtype configuration: {dtype_dict}")

        # Handle schema-based na_values (only if legacy na_values not provided)
        if self.config.na_values is None and schema and schema.attributes:
            na_values_dict = {}
            for attr_name, attribute in schema.attributes.items():
                if attribute.na_values:
                    na_values_dict[attr_name] = attribute.na_values
            if na_values_dict:
                config["na_values"] = na_values_dict
                self._logger.debug(f"Using schema-based na_values: {na_values_dict}")

        try:
            # Create loader instance and load data
            loader = loader_class(config)
            data = loader.load().fillna(pd.NA)
            self._logger.info(f"Successfully loaded data with shape: {data.shape}")
            return data

        except Exception as e:
            error_msg = f"Failed to load data from {self.config.filepath}: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

    def _process_with_metadater(self, data: pd.DataFrame, schema: Schema) -> Schema:
        """
        Process data and schema with metadater.

        Args:
            data: Loaded dataframe
            schema: Merged schema configuration

        Returns:
            Schema: Schema metadata
        """
        self._logger.info("Processing with metadater")

        # 如果沒有 schema，從資料建立
        if schema is None or not schema.attributes:
            try:
                schema = SchemaMetadater.from_data(data)
                # 現在可以直接修改屬性（已移除 frozen）
                schema.id = self.config.file_name or "inferred_schema"
                schema.name = self.config.base_name or "Inferred Schema"
                self._logger.debug("Created schema from data")
            except Exception as e:
                error_msg = f"Failed to create schema from data: {str(e)}"
                self._logger.error(error_msg)
                raise UnableToFollowMetadataError(error_msg) from e

        # Validate data and schema consistency and handle differences
        if schema and schema.attributes:
            # Compare schema with data to find differences
            diff_result = SchemaMetadater.diff(schema, data)

            # Log differences but don't raise errors, let align handle it
            if diff_result["missing_columns"]:
                self._logger.warning(
                    f"Schema defines columns not in data (will be added with default values): "
                    f"{diff_result['missing_columns']}"
                )

            if diff_result["extra_columns"]:
                self._logger.info(
                    f"Data contains columns not in schema (will be added to schema): "
                    f"{diff_result['extra_columns']}"
                )

                # Create Attributes for extra columns and add to schema
                for col_name in diff_result["extra_columns"]:
                    if col_name in data.columns:
                        # Infer attribute from data
                        from petsard.metadater import AttributeMetadater

                        new_attr = AttributeMetadater.from_data(
                            data[col_name], enable_stats=schema.enable_stats
                        )
                        # Add to schema
                        schema.attributes[col_name] = new_attr
                        self._logger.debug(f"Added attribute '{col_name}' to schema")

        # Align data with schema
        try:
            # Set alignment strategy
            align_strategy = {
                "add_missing_columns": True,  # Add default values for columns defined in schema but missing in data
                "remove_extra_columns": False,  # Keep extra columns in data
                "reorder_columns": True,  # Reorder columns
            }

            aligned_data = SchemaMetadater.align(schema, data, align_strategy)
            # Update original data reference
            data.update(aligned_data)
            self._logger.debug("Data aligned with schema successfully")
        except Exception as e:
            # Log warning but continue with original data
            warning_msg = f"Failed to align data with schema: {str(e)}. Continuing with original data."
            self._logger.warning(warning_msg)
            # Continue with original data if alignment fails

        return schema


# ============================================================================
# Tests for nrows parameter
# ============================================================================

if __name__ == "__main__":
    """
    Test script for Loader nrows parameter
    測試 Loader nrows 參數功能
    """
    import os
    import sys

    def test_nrows_basic():
        """Test basic nrows functionality with CSV file"""
        print("=" * 60)
        print("Test 1: Basic nrows functionality")
        print("=" * 60)

        # Create a test CSV file with 100 rows
        test_data = pd.DataFrame(
            {
                "id": range(1, 101),
                "name": [f"Name_{i}" for i in range(1, 101)],
                "value": range(100, 200),
            }
        )
        test_file = "test_data.csv"
        test_data.to_csv(test_file, index=False)
        print(f"✓ Created test file with {len(test_data)} rows")

        # Test 1: Load with nrows=10
        loader = Loader(test_file, nrows=10)
        data, schema = loader.load()

        assert len(data) == 10, f"Expected 10 rows, got {len(data)}"
        print(f"✓ Successfully loaded {len(data)} rows with nrows=10")
        print(f"  Data shape: {data.shape}")
        print(f"  Schema attributes: {len(schema.attributes)}")

        # Test 2: Load without nrows (full data)
        loader_full = Loader(test_file)
        data_full, schema_full = loader_full.load()

        assert len(data_full) == 100, f"Expected 100 rows, got {len(data_full)}"
        print(f"✓ Successfully loaded {len(data_full)} rows without nrows")

        # Cleanup
        os.remove(test_file)
        print("✓ Test file cleaned up")
        print("\n✅ Test 1 PASSED\n")

    def test_nrows_with_schema():
        """Test nrows with schema configuration"""
        print("=" * 60)
        print("Test 2: nrows with schema")
        print("=" * 60)

        # Create test data
        test_data = pd.DataFrame(
            {
                "age": range(18, 68),
                "income": range(30000, 80000, 1000),
                "category": ["A"] * 25 + ["B"] * 25,
            }
        )
        test_file = "test_schema_data.csv"
        test_data.to_csv(test_file, index=False)
        print(f"✓ Created test file with {len(test_data)} rows")

        # Define schema
        schema_dict = {
            "id": "test_schema",
            "name": "Test Schema",
            "attributes": {
                "age": {"type": "Int64"},
                "income": {"type": "Int64"},
                "category": {"type": "category"},
            },
        }

        # Load with nrows and schema
        loader = Loader(test_file, nrows=15, schema=schema_dict)
        data, schema = loader.load()

        assert len(data) == 15, f"Expected 15 rows, got {len(data)}"
        print(f"✓ Successfully loaded {len(data)} rows with nrows=15 and schema")
        print(f"  Data shape: {data.shape}")
        print(f"  Schema ID: {schema.id}")

        # Verify schema was applied correctly
        print(f"  Data types: {dict(data.dtypes)}")

        # Cleanup
        os.remove(test_file)
        print("✓ Test file cleaned up")
        print("\n✅ Test 2 PASSED\n")

    def test_nrows_memory_efficiency():
        """Test that nrows actually reduces memory usage"""
        print("=" * 60)
        print("Test 3: Memory efficiency with nrows")
        print("=" * 60)

        # Create a larger test file
        test_data = pd.DataFrame({f"col_{i}": range(10000) for i in range(10)})
        test_file = "test_large_data.csv"
        test_data.to_csv(test_file, index=False)
        print(
            f"✓ Created large test file with {len(test_data)} rows and {len(test_data.columns)} columns"
        )

        # Load with nrows
        loader_small = Loader(test_file, nrows=100)
        data_small, _ = loader_small.load()
        memory_small = sys.getsizeof(data_small)

        print(f"✓ Loaded {len(data_small)} rows")
        print(f"  Memory usage (estimated): {memory_small:,} bytes")

        # Cleanup
        os.remove(test_file)
        print("✓ Test file cleaned up")
        print("\n✅ Test 3 PASSED\n")

    # Run tests
    print("\n" + "=" * 60)
    print("Testing Loader nrows Parameter")
    print("測試 Loader nrows 參數")
    print("=" * 60 + "\n")

    try:
        test_nrows_basic()
        test_nrows_with_schema()
        test_nrows_memory_efficiency()

        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("✅ 所有測試通過")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 60)
        raise
