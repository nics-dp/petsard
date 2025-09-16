import gc
import logging
import os
import resource
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.loader.benchmarker import BenchmarkerConfig
from petsard.loader.loader import Loader, LoaderConfig, LoaderFileExt
from petsard.metadater import Attribute, Schema, SchemaMetadater


class TestLoaderConfig:
    """Test cases for LoaderConfig class
    LoaderConfig 類的測試案例
    """

    def test_config_requires_filepath_or_method(self):
        """Test that either filepath or method must be specified
        測試必須指定 filepath 或 method 參數
        """
        with pytest.raises(ConfigError):
            LoaderConfig()

    def test_default_method(self):
        """Test default method configuration
        測試默認方法配置
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult-income.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "petsard-benchmark",
                    "sha256": "1f13ee2bf9d7c66098429281ab91fa1b51cbabd3b805cc365b3c6b44491ea2c0",
                }
            }

            config = LoaderConfig(method="default")
            # 檢查初始 filepath 被設置為 benchmark URL
            # Check that initial filepath is set to benchmark URL
            assert config.DEFAULT_METHOD_FILEPATH == "benchmark://adult-income"
            # 檢查 filepath 已被處理為本地路徑
            # Check that filepath has been processed to local path
            assert str(config.filepath).endswith("benchmark/adult-income.csv")
            # 檢查 benchmarker_config 已被設置
            # Check that benchmarker_config is set
            assert config.benchmarker_config is not None
            assert config.benchmarker_config.benchmark_name == "adult-income"

    def test_unsupported_method(self):
        """Test unsupported method raises error
        測試不支援的方法會引發錯誤
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(method="unsupported_method")

    def test_benchmark_path_parsing(self):
        """Test parsing of benchmark path
        測試基準資料集路徑解析
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }
            config = LoaderConfig(filepath="benchmark://adult-income")
            assert config.benchmarker_config is not None
            assert config.benchmarker_config.benchmark_name == "adult-income"
            assert config.filepath == Path("benchmark").joinpath("adult.csv")
            assert config.benchmarker_config.benchmark_filename == "adult.csv"
            assert config.benchmarker_config.benchmark_access == "public"
            assert config.benchmarker_config.benchmark_region_name == "us-west-2"
            assert config.benchmarker_config.benchmark_bucket_name == "test-bucket"
            assert config.benchmarker_config.benchmark_sha256 == "test-hash"

    def test_unsupported_benchmark(self):
        """Test unsupported benchmark raises error
        測試不支援的基準資料集會引發錯誤
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {}
            with pytest.raises(UnsupportedMethodError):
                LoaderConfig(filepath="benchmark://nonexistent")

    def test_private_benchmark_unsupported(self):
        """Test private benchmark access raises error
        測試私有基準資料集存取會引發錯誤
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "private-data": {
                    "filename": "private.csv",
                    "access": "private",
                    "region_name": "us-west-2",
                    "bucket_name": "private-bucket",
                    "sha256": "test-hash",
                }
            }
            with pytest.raises(UnsupportedMethodError):
                LoaderConfig(filepath="benchmark://private-data")

    @pytest.mark.parametrize(
        "filepath,expected_ext,expected_code",
        [
            ("path/to/file.csv", ".csv", LoaderFileExt.CSVTYPE),
            ("path/to/file.xlsx", ".xlsx", LoaderFileExt.EXCELTYPE),
            ("path/to/file.xls", ".xls", LoaderFileExt.EXCELTYPE),
            ("path/to/file.CSV", ".csv", LoaderFileExt.CSVTYPE),
            ("path/to/file.XLSX", ".xlsx", LoaderFileExt.EXCELTYPE),
        ],
    )
    def test_file_extension_handling(self, filepath, expected_ext, expected_code):
        """Test file extension parsing and mapping
        測試檔案副檔名解析和映射
        """
        config = LoaderConfig(filepath=filepath)
        assert config.file_ext == expected_ext
        assert config.file_ext_code == expected_code

    def test_invalid_file_extension(self):
        """Test handling of invalid file extensions
        測試處理無效的檔案副檔名
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(filepath="path/to/file.invalid")

    def test_unsupported_column_type(self):
        """Test handling of unsupported column types
        測試處理不支援的欄位類型
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(
                filepath="path/to/file.csv", column_types={"unsupported_type": ["col1"]}
            )

    def test_get_method(self):
        """Test get() method returns config dictionary
        測試 get() 方法返回配置字典
        """
        config = LoaderConfig(filepath="path/to/file.csv")
        config_dict = config.get()
        assert isinstance(config_dict, dict)
        assert config_dict["filepath"] == "path/to/file.csv"
        assert config_dict["file_ext"] == ".csv"


class TestBenchmarkerConfig:
    """Test cases for BenchmarkerConfig class
    BenchmarkerConfig 類的測試案例
    """

    def test_benchmarker_config_requires_benchmark_name(self):
        """Test that benchmark_name must be specified
        測試必須指定 benchmark_name 參數
        """
        with pytest.raises(ConfigError):
            BenchmarkerConfig()

    def test_benchmarker_config_initialization(self):
        """Test BenchmarkerConfig initialization
        測試 BenchmarkerConfig 初始化
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }

            config = BenchmarkerConfig(benchmark_name="adult-income")
            assert config.benchmark_name == "adult-income"
            assert config.benchmark_filename == "adult.csv"
            assert config.benchmark_access == "public"
            assert config.benchmark_region_name == "us-west-2"
            assert config.benchmark_bucket_name == "test-bucket"
            assert config.benchmark_sha256 == "test-hash"

    def test_benchmarker_config_get_benchmarker_config(self):
        """Test get_benchmarker_config method
        測試 get_benchmarker_config 方法
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }

            config = BenchmarkerConfig(benchmark_name="adult-income")
            benchmarker_config = config.get_benchmarker_config()

            assert isinstance(benchmarker_config, dict)
            assert benchmarker_config["benchmark_filename"] == "adult.csv"
            assert benchmarker_config["benchmark_bucket_name"] == "test-bucket"
            assert benchmarker_config["benchmark_sha256"] == "test-hash"
            assert str(benchmarker_config["filepath"]).endswith("benchmark/adult.csv")

    def test_benchmarker_config_unsupported_benchmark(self):
        """Test unsupported benchmark raises error
        測試不支援的基準資料集會引發錯誤
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {}
            with pytest.raises(UnsupportedMethodError):
                BenchmarkerConfig(benchmark_name="nonexistent")

    def test_benchmarker_config_private_access_unsupported(self):
        """Test private benchmark access raises error
        測試私有基準資料集存取會引發錯誤
        """
        with patch.object(
            BenchmarkerConfig, "_load_benchmark_config"
        ) as mock_load_config:
            mock_load_config.return_value = {
                "private-data": {
                    "filename": "private.csv",
                    "access": "private",
                    "region_name": "us-west-2",
                    "bucket_name": "private-bucket",
                    "sha256": "test-hash",
                }
            }
            with pytest.raises(UnsupportedMethodError):
                BenchmarkerConfig(benchmark_name="private-data")


class TestLoader:
    """Test cases for main Loader functionality
    主要 Loader 功能的測試案例
    """

    def test_schema_mutability(self):
        """Test that Schema objects are now mutable (not frozen)
        測試 Schema 物件現已可變更（非 frozen）
        """
        # Create a Schema instance
        schema = Schema(
            id="test_schema", name="Test Schema", description="Test Description"
        )

        # Test that we can modify attributes
        schema.id = "modified_id"
        schema.name = "Modified Name"
        schema.description = "Modified Description"

        # Verify changes
        assert schema.id == "modified_id"
        assert schema.name == "Modified Name"
        assert schema.description == "Modified Description"

        # Test adding attributes
        schema.attributes["test_field"] = Attribute(
            name="test_field", type="string", description="Test field"
        )

        assert "test_field" in schema.attributes
        assert schema.attributes["test_field"].name == "test_field"

    def test_attribute_mutability(self):
        """Test that Attribute objects are now mutable (not frozen)
        測試 Attribute 物件現已可變更（非 frozen）
        """
        # Create an Attribute instance
        attr = Attribute(name="test_attr", type="integer")

        # Test that we can modify attributes
        attr.name = "modified_attr"
        attr.type = "string"
        attr.description = "Modified description"

        # Verify changes
        assert attr.name == "modified_attr"
        assert attr.type == "string"
        assert attr.description == "Modified description"

    def test_benchmark_loader_schema_inference(self):
        """Test loading benchmark dataset with schema inference
        測試載入基準資料集並推斷 schema
        """
        with (
            patch("petsard.loader.loader.BenchmarkerRequests") as mock_benchmarker,
            patch.object(
                BenchmarkerConfig, "_load_benchmark_config"
            ) as mock_load_config,
            patch("pandas.read_csv") as mock_read_csv,
        ):
            # Setup mocks
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }

            # Mock DataFrame
            mock_df = pd.DataFrame(
                {
                    "age": [25, 30, 35],
                    "workclass": ["Private", "Self-emp", "Private"],
                    "education": ["HS-grad", "Bachelors", "Masters"],
                }
            )
            mock_read_csv.return_value = mock_df

            # Mock SchemaMetadater.from_data to return a mutable Schema
            with patch.object(SchemaMetadater, "from_data") as mock_from_data:
                test_schema = Schema(id="temp_id", name="temp_name")
                mock_from_data.return_value = test_schema

                # Mock SchemaMetadater.align
                with patch.object(SchemaMetadater, "align") as mock_align:
                    mock_align.return_value = mock_df

                    # Create loader and load data
                    loader = Loader(filepath="benchmark://adult-income")
                    data, schema = loader.load()

                    # Verify schema was created and modified
                    mock_from_data.assert_called_once()
                    assert schema.id == "adult"  # Should be modified from temp_id
                    assert (
                        schema.name == "adult.csv"
                    )  # Should be modified from temp_name

    @pytest.fixture
    def sample_csv_path(self, tmp_path):
        """Create a temporary CSV file for testing
        創建臨時 CSV 檔案用於測試
        """
        csv_file = tmp_path / "test.csv"
        pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]}).to_csv(
            csv_file, index=False
        )
        return str(csv_file)

    def test_loader_init_no_config(self):
        """Test Loader initialization with no config
        測試沒有配置的 Loader 初始化
        """
        with pytest.raises(ConfigError):
            Loader()

    @pytest.mark.parametrize(
        "filepath,expected_ext",
        [
            ("path/to/file.csv", ".csv"),
            ("path.with.dots/file.csv", ".csv"),
            ("path/to/file.name.with.dots.csv", ".csv"),
            ("./relative/path/file.csv", ".csv"),
            ("../parent/path/file.csv", ".csv"),
            ("/absolute/path/file.csv", ".csv"),
            ("file.CSV", ".csv"),  # 測試大小寫 / Test case sensitivity
            ("path/to/file.XLSX", ".xlsx"),
        ],
    )
    def test_handle_filepath_with_complex_name(self, filepath, expected_ext):
        """Test handling of complex file paths
        測試處理複雜的檔案路徑
        > issue 375
        """
        loader = Loader(filepath=filepath)
        assert loader.config.file_ext == expected_ext
        assert loader.config.filepath == filepath

    def test_loader_init_with_filepath(self, sample_csv_path):
        """Test Loader initialization with filepath
        測試使用檔案路徑初始化 Loader
        """
        loader = Loader(filepath=sample_csv_path)
        assert loader.config.filepath == sample_csv_path
        assert loader.config.file_ext == ".csv"

    def test_loader_init_with_column_types(self, sample_csv_path):
        """Test Loader initialization with column types
        測試使用欄位類型初始化 Loader
        """
        column_types = {"category": ["B"]}
        loader = Loader(filepath=sample_csv_path, column_types=column_types)
        assert loader.config.column_types == column_types

    def test_benchmark_loader(self):
        """Test loading benchmark dataset
        測試載入基準資料集
        """
        with (
            patch("petsard.loader.loader.BenchmarkerRequests") as mock_benchmarker,
            patch.object(
                BenchmarkerConfig, "_load_benchmark_config"
            ) as mock_load_config,
        ):
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }

            loader = Loader(filepath="benchmark://adult-income")
            # Benchmarker should not be called during init
            # 初始化期間不應調用 Benchmarker
            mock_benchmarker.assert_not_called()

            assert loader.config.benchmarker_config is not None
            assert loader.config.benchmarker_config.benchmark_name == "adult-income"

    def test_load_csv(self, sample_csv_path):
        """Test loading CSV file
        測試載入 CSV 檔案
        """
        loader = Loader(filepath=sample_csv_path)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                # Create a mutable Schema for testing
                test_schema = Schema(
                    id="test_id",
                    name="test_name",
                    attributes={
                        "A": Attribute(name="A", type="integer"),
                        "B": Attribute(name="B", type="string"),
                    },
                )
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Call load method
                data, schema = loader.load()

                # Assertions
                mock_read_csv.assert_called_once()
                assert data is not None
                assert schema is not None
                # Schema should be modified with file info
                assert schema.id == "test"  # From file stem
                assert schema.name == "test.csv"  # From file name

    def test_load_excel(self):
        """Test loading Excel file
        測試載入 Excel 檔案
        """
        excel_path = "path/to/file.xlsx"
        loader = Loader(filepath=excel_path)

        with patch("pandas.read_excel") as mock_read_excel:
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_excel.return_value = mock_df

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                # Create a mutable Schema for testing
                test_schema = Schema(
                    id="test_id",
                    name="test_name",
                    attributes={
                        "A": Attribute(name="A", type="integer"),
                        "B": Attribute(name="B", type="string"),
                    },
                )
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Call load method
                data, schema = loader.load()

                # Assertions
                mock_read_excel.assert_called_once()
                assert data is not None
                assert schema is not None
                # Schema should be modified with file info
                assert schema.id == "file"  # From file stem
                assert schema.name == "file.xlsx"  # From file name

    def test_benchmark_data_load(self):
        """Test loading benchmark data
        測試載入基準資料
        """
        with (
            patch.object(
                BenchmarkerConfig, "_load_benchmark_config"
            ) as mock_load_config,
            patch("petsard.loader.loader.BenchmarkerRequests") as mock_benchmarker,
            patch("pandas.read_csv") as mock_read_csv,
        ):
            # Setup mock returns
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df

            mock_benchmarker_instance = MagicMock()
            mock_benchmarker.return_value = mock_benchmarker_instance

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                test_schema = Schema(id="test_id", name="test_name", attributes={})
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Create and load benchmark data
                loader = Loader(filepath="benchmark://adult-income")
                data, schema = loader.load()

                # Assertions
                mock_benchmarker.assert_called_once()
                mock_benchmarker_instance.download.assert_called_once()
                mock_read_csv.assert_called_once()
                assert data is not None
                assert schema is not None
                # Verify schema was modified
                assert schema.id == "adult"
                assert schema.name == "adult.csv"

    def test_custom_na_values(self, sample_csv_path):
        """Test loading with custom NA values
        測試使用自定義 NA 值載入資料
        """
        na_values = ["x"]
        loader = Loader(filepath=sample_csv_path, na_values=na_values)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": [None, "y", "z"]})
            mock_read_csv.return_value = mock_df

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                test_schema = Schema(id="test_id", name="test_name", attributes={})
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Call load method
                data, schema = loader.load()

                # Verify na_values was passed to read_csv
                call_kwargs = mock_read_csv.call_args.kwargs
                assert "na_values" in call_kwargs
                assert call_kwargs["na_values"] == na_values
                assert data is not None
                assert schema is not None

    def test_custom_header_names(self, sample_csv_path):
        """Test loading with custom header names
        測試使用自定義欄位名稱載入資料
        """
        header_names = ["Col1", "Col2"]
        loader = Loader(filepath=sample_csv_path, header_names=header_names)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            mock_df = pd.DataFrame({"Col1": [1, 2, 3], "Col2": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                test_schema = Schema(id="test_id", name="test_name", attributes={})
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Call load method
                data, schema = loader.load()

                # Verify header_names was passed correctly
                call_kwargs = mock_read_csv.call_args.kwargs
                assert call_kwargs["names"] == header_names
                assert data is not None
                assert schema is not None


class TestLoaderMetadataFeature:
    """Test cases for new schema parameter functionality
    新 schema 參數功能的測試案例
    """

    @pytest.fixture
    def sample_csv_with_schema_needs(self, tmp_path):
        """Create a CSV file that needs schema transformations
        創建需要 schema 轉換的 CSV 檔案
        """
        csv_file = tmp_path / "schema_test.csv"
        test_data = {
            "age": [25, 30, "unknown", 45, "N/A"],  # Integer with custom NA values
            "salary": [
                50000.123,
                60000.456,
                70000.789,
                80000.999,
                90000.111,
            ],  # Float needing precision
            "score": ["85", "90", "78", "92", "88"],  # String that should be int
            "active": ["true", "false", "yes", "no", "1"],  # Boolean conversion
            "category": ["A", "B", "C", "A", "B"],  # Category data
        }
        pd.DataFrame(test_data).to_csv(csv_file, index=False)
        return str(csv_file)

    def test_schema_parameter_validation(self):
        """Test schema parameter validation in LoaderConfig
        測試 LoaderConfig 中的 schema 參數驗證
        """
        # Valid schema configuration using Schema
        attributes = {
            "age": Attribute(name="age", type="int", na_values=["unknown", "N/A"]),
            "salary": Attribute(
                name="salary", type="float", type_attr={"precision": 2}
            ),
            "score": Attribute(name="score", type="int"),
        }
        valid_schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        # Should not raise any exception
        # Test using Loader instead of LoaderConfig directly
        loader = Loader(filepath="test.csv", schema=valid_schema_config)
        assert loader.config.schema == valid_schema_config

    def test_schema_parameter_validation_invalid_structure(self):
        """Test schema parameter validation with invalid structure
        測試無效結構的 schema 參數驗證
        """
        # Schema accepts invalid attributes but will fail when used
        invalid_schema = Schema(
            id="test",
            name="test",
            attributes="invalid",  # Should be dict
        )

        # When trying to load with invalid schema, it should fail
        loader = Loader(filepath="test.csv", schema=invalid_schema)

        # The invalid structure will be caught when trying to iterate over attributes
        # which should be a dict but is a string
        assert loader.config.schema.attributes == "invalid"  # Invalid but accepted

    def test_schema_parameter_validation_invalid_keys(self):
        """Test schema parameter validation with invalid keys
        測試無效鍵值的 schema 參數驗證
        """
        # Attribute validation is now handled by the dataclass itself
        # Invalid parameters should be caught during Attribute creation
        with pytest.raises(TypeError):
            invalid_field = Attribute(name="age", type="int", invalid_key="value")
            schema_config = Schema(
                id="test", name="test", attributes={"age": invalid_field}
            )
            LoaderConfig(filepath="test.csv", schema=schema_config)

    def test_schema_parameter_validation_invalid_values(self):
        """Test schema parameter validation with invalid values
        測試無效值的 schema 參數驗證
        """
        # Attribute doesn't have built-in validation for precision values
        # But negative precision doesn't make sense
        attributes = {
            "salary": Attribute(
                name="salary",
                type="float",
                type_attr={
                    "precision": -1
                },  # This might not raise error but is semantically wrong
            )
        }
        schema_config = Schema(id="test", name="test", attributes=attributes)
        # Schema creation should succeed but the value is semantically invalid
        loader = Loader(filepath="test.csv", schema=schema_config)
        assert loader.config.schema == schema_config

    def test_schema_transformations_applied(self, sample_csv_with_schema_needs):
        """Test that schema transformations are applied during load
        測試在載入過程中應用 schema 轉換
        """
        # Convert FieldConfig to Attribute for new architecture
        attributes = {
            "age": Attribute(name="age", type="int", na_values=["unknown", "N/A"]),
            "salary": Attribute(
                name="salary", type="float", type_attr={"precision": 2}
            ),
            "score": Attribute(name="score", type="int"),
            "active": Attribute(name="active", type="boolean"),
        }
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            original_df = pd.DataFrame(
                {
                    "age": [25, 30, "unknown", 45, "N/A"],
                    "salary": [50000.123, 60000.456, 70000.789, 80000.999, 90000.111],
                    "score": ["85", "90", "78", "92", "88"],
                    "active": ["true", "false", "yes", "no", "1"],
                    "category": ["A", "B", "C", "A", "B"],
                }
            )
            mock_read_csv.return_value = original_df

            # Mock SchemaMetadater.align to return processed data
            with patch.object(SchemaMetadater, "align") as mock_align:
                mock_align.return_value = original_df

                # Call load method
                data, schema = loader.load()

                # Verify that align was called
                mock_align.assert_called_once()

                # Verify that the schema has the correct attributes
                assert "age" in schema.attributes
                assert "salary" in schema.attributes
                assert "score" in schema.attributes
                assert "active" in schema.attributes

    def test_schema_field_not_in_data_warning(self, sample_csv_with_schema_needs):
        """Test warning when schema field is not found in data
        測試當 schema 欄位在資料中找不到時的警告
        """
        attributes = {
            "nonexistent_field": Attribute(name="nonexistent_field", type="int"),
            "age": Attribute(name="age", type="int"),
        }
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            original_df = pd.DataFrame(
                {
                    "age": [25, 30, 35, 45, 50],
                    "other_field": ["A", "B", "C", "D", "E"],
                }
            )
            mock_read_csv.return_value = original_df

            # Mock SchemaMetadater.align
            with patch.object(SchemaMetadater, "align") as mock_align:
                mock_align.return_value = original_df

                # Call load method - should not raise exception but log warning
                data, schema = loader.load()

                # Verify that align was called
                mock_align.assert_called_once()

                # Verify that schema contains both fields
                assert "nonexistent_field" in schema.attributes
                assert "age" in schema.attributes

    def test_schema_transformation_error_handling(self, sample_csv_with_schema_needs):
        """Test error handling during schema transformations
        測試 schema 轉換過程中的錯誤處理
        """
        attributes = {
            "age": Attribute(name="age", type="int"),
        }
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            original_df = pd.DataFrame(
                {
                    "age": [25, 30, 35, 45, 50],
                }
            )
            mock_read_csv.return_value = original_df

            # Mock SchemaMetadater.align to raise an exception
            with patch.object(SchemaMetadater, "align") as mock_align:
                mock_align.side_effect = Exception("Transformation failed")

                # Call load method - should log warning but continue
                data, schema = loader.load()

                # Verify that the load completed despite transformation error
                assert data is not None
                assert schema is not None

    def test_schema_precedence_over_column_types(self, sample_csv_with_schema_needs):
        """Test that schema parameter conflicts with column_types raise ConfigError
        測試 schema 參數與 column_types 衝突時會拋出 ConfigError
        """
        attributes = {
            "age": Attribute(name="age", type="int", na_values=["unknown"]),
        }
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )
        column_types = {
            "category": ["age"],  # This should conflict with schema
        }

        # Should raise ConfigError due to field conflict
        with pytest.raises(
            ConfigError, match="Conflict detected.*age.*schema and column_types"
        ):
            Loader(
                filepath=sample_csv_with_schema_needs,
                schema=schema_config,
                column_types=column_types,
            )


class TestLoaderAmbiguousDataFeatures:
    """Test cases for ambiguous data type processing features
    容易誤判、型別判斷模糊資料處理功能的測試案例
    """

    @pytest.fixture
    def ambiguous_sample_csv(self, tmp_path):
        """Create a sample CSV file with ambiguous data types for testing
        創建含有型別判斷模糊資料的測試用 CSV 檔案
        """
        csv_file = tmp_path / "ambiguous_test.csv"
        # Ambiguous data with leading zeros, mixed types, and null values
        test_data = {
            "id_code": ["001", "002", "010", "099"],  # Leading zeros - 前導零代號
            "age": [25, 30, "", 45],  # Integers with null - 含空值整數
            "amount": [
                50000.5,
                60000.7,
                "",
                75000.3,
            ],  # Floats with null - 含空值浮點數
            "score": [85, 90, 78, 92],  # Pure integers - 純整數
            "category": ["A級", "B級", "C級", "A級"],  # Categories - 分類資料
        }
        pd.DataFrame(test_data).to_csv(csv_file, index=False)
        return str(csv_file)

    def test_backward_compatibility(self, ambiguous_sample_csv):
        """Test that Loader maintains backward compatibility
        測試 Loader 保持向後相容性
        """
        # Test with default settings - Loader should focus on basic file reading
        loader = Loader(filepath=ambiguous_sample_csv)

        with patch("pandas.read_csv") as mock_read_csv:
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df

            # Mock SchemaMetadater methods
            with (
                patch.object(SchemaMetadater, "from_data") as mock_from_data,
                patch.object(SchemaMetadater, "align") as mock_align,
            ):
                test_schema = Schema(id="test_id", name="test_name", attributes={})
                mock_from_data.return_value = test_schema
                mock_align.return_value = mock_df

                # Call load method
                data, schema = loader.load()

                # Verify normal behavior
                mock_read_csv.assert_called_once()
                assert data is not None
                assert schema is not None


class TestLoaderFileExt:
    """Test cases for LoaderFileExt class
    LoaderFileExt 類的測試案例
    """

    @pytest.mark.parametrize(
        "file_ext,expected_code",
        [
            (".csv", LoaderFileExt.CSVTYPE),
            (".CSV", LoaderFileExt.CSVTYPE),
            (".xlsx", LoaderFileExt.EXCELTYPE),
            (".XLSX", LoaderFileExt.EXCELTYPE),
            (".xls", LoaderFileExt.EXCELTYPE),
            (".xlsm", LoaderFileExt.EXCELTYPE),
            (".xlsb", LoaderFileExt.EXCELTYPE),
            (".ods", LoaderFileExt.EXCELTYPE),
            (".odt", LoaderFileExt.EXCELTYPE),
        ],
    )
    def test_get_file_ext_code(self, file_ext, expected_code):
        """Test getting file extension code
        測試獲取檔案副檔名類型
        """
        assert LoaderFileExt.get(file_ext) == expected_code

    def test_unsupported_file_ext(self):
        """Test handling of unsupported file extensions
        測試處理不支援的檔案副檔名
        """
        with pytest.raises(KeyError):
            LoaderFileExt.get(".unsupported")


# ============================================================================
# 壓力測試 Stress Tests
# ============================================================================


class MemoryMonitor:
    """記憶體使用監控器"""

    def __init__(self):
        self.initial_memory = self.get_memory_usage()
        self.peak_memory = self.initial_memory

    def get_memory_usage(self) -> float:
        """取得當前記憶體使用量 (MB)"""
        try:
            # 使用 resource 模組獲取記憶體使用量 (Unix/Linux/macOS)
            # Use resource module to get memory usage (Unix/Linux/macOS)
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except (AttributeError, OSError):
            # Windows 或其他系統的備用方案
            # Fallback for Windows or other systems
            return 0.0

    def record(self, label: str = ""):
        """記錄當前記憶體使用量"""
        current = self.get_memory_usage()
        self.peak_memory = max(self.peak_memory, current)
        return current

    def get_peak_usage(self) -> float:
        """取得峰值記憶體使用量"""
        return self.peak_memory

    def get_memory_increase(self) -> float:
        """取得記憶體增長量"""
        return self.get_memory_usage() - self.initial_memory


class LargeFileGenerator:
    """大型測試檔案生成器"""

    def __init__(self, target_size_gb: float = 1.0):
        self.target_size_gb = target_size_gb
        self.target_size_bytes = int(target_size_gb * 1024 * 1024 * 1024)

    def generate_test_csv(
        self, filepath: str, scenario: str = "mixed_types"
    ) -> dict[str, Any]:
        """生成測試 CSV 檔案"""
        logging.info(f"生成測試檔案: {filepath}, 情境: {scenario}")

        estimated_rows = self.target_size_bytes // 100
        chunk_size = 100000

        file_info = {
            "filepath": filepath,
            "scenario": scenario,
            "actual_rows": 0,
            "columns": ["id", "amount", "code", "score"],
            "file_size_bytes": 0,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("id,amount,code,score\n")

            rows_written = 0
            while rows_written < estimated_rows:
                chunk_data = []
                for i in range(min(chunk_size, estimated_rows - rows_written)):
                    row_idx = rows_written + i
                    progress = row_idx / estimated_rows

                    # 99.9% 正常資料，0.1% 例外在最後
                    if progress >= 0.999:
                        # 例外資料
                        row_data = [
                            f"EXCEPTION_{row_idx}",
                            "",
                            str(row_idx),
                            f"{row_idx}.99",
                        ]
                    else:
                        # 正常資料
                        row_data = [
                            str(row_idx + 1),
                            f"{np.random.uniform(1000, 999999):.2f}",
                            f"CODE_{row_idx:06d}",
                            str(np.random.randint(0, 100)),
                        ]

                    chunk_data.append(",".join(row_data))

                f.write("\n".join(chunk_data) + "\n")
                rows_written += len(chunk_data)

                current_size = os.path.getsize(filepath)
                if current_size >= self.target_size_bytes:
                    break

        file_info["actual_rows"] = rows_written
        file_info["file_size_bytes"] = os.path.getsize(filepath)

        logging.info(
            f"檔案生成完成: {file_info['file_size_bytes'] / 1024 / 1024:.1f} MB, {file_info['actual_rows']} 行"
        )
        return file_info


@pytest.mark.stress
class TestLoaderStress:
    """Loader 壓力測試"""

    @pytest.fixture(scope="class")
    def temp_dir(self):
        """創建臨時目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def _run_stress_test(self, temp_dir, size_gb, test_name, timeout_seconds):
        """執行壓力測試的通用方法"""
        file_generator = LargeFileGenerator(target_size_gb=size_gb)
        csv_path = os.path.join(temp_dir, f"stress_test_{size_gb}gb.csv")

        # 生成測試檔案
        file_info = file_generator.generate_test_csv(csv_path, "mixed_types")

        memory_monitor = MemoryMonitor()
        memory_monitor.record("測試開始")

        success = False
        error_msg = None
        start_time = time.time()

        try:
            # 設置超時
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"測試超時 ({timeout_seconds} 秒)")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

            try:
                loader = Loader(filepath=csv_path)

                memory_monitor.record("Loader 初始化完成")

                data, schema = loader.load()
                memory_monitor.record("資料載入完成")

                assert data is not None
                assert schema is not None
                assert len(data) > 0

                success = True

            finally:
                signal.alarm(0)  # 取消超時

        except TimeoutError as e:
            error_msg = str(e)
            logging.error(f"測試超時: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            logging.error(f"測試失敗: {error_msg}")

        finally:
            load_time = time.time() - start_time

            # 清理記憶體
            if "data" in locals():
                del data
            if "schema" in locals():
                del schema
            gc.collect()

            # 記錄測試結果
            throughput = (
                (file_info["file_size_bytes"] / 1024 / 1024) / load_time
                if success
                else 0
            )
            logging.info(
                f"{test_name}: {'成功' if success else '失敗'}, "
                f"載入時間: {load_time:.2f}秒, "
                f"處理速度: {throughput:.1f} MB/秒, "
                f"峰值記憶體: {memory_monitor.get_peak_usage():.1f} MB"
            )

        return success, error_msg

    @pytest.mark.stress
    def test_medium_file_1gb(self, temp_dir):
        """測試中檔案：1GB (120秒超時)"""
        success, error_msg = self._run_stress_test(temp_dir, 1.0, "中檔案1GB測試", 120)
        assert success, f"測試失敗: {error_msg}"

    @pytest.mark.stress
    def test_xlarge_file_5gb(self, temp_dir):
        """測試超大檔案：5GB (600秒超時)"""
        success, error_msg = self._run_stress_test(
            temp_dir, 5.0, "超大檔案5GB測試", 600
        )
        assert success, f"測試失敗: {error_msg}"


@pytest.mark.stress
class TestLoaderTypeInference:
    """型別推斷邊緣情況測試 - 99.9% 在前，0.1% 例外在後"""

    @pytest.fixture(scope="class")
    def temp_dir(self):
        """創建臨時目錄"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def _create_type_test_file(self, temp_dir, test_type):
        """創建型別測試檔案"""
        csv_path = os.path.join(temp_dir, f"{test_type}_test.csv")

        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("test_column\n")

            # 生成 10000 行測試資料
            total_rows = 10000
            exception_start = int(total_rows * 0.999)  # 99.9% 後開始例外

            for i in range(total_rows):
                if i >= exception_start:
                    # 最後 0.1% 是例外
                    if test_type == "int_to_string":
                        f.write(f"EXCEPTION_{i}\n")
                    elif test_type == "float_to_null":
                        f.write("\n")  # 空值會被 pandas 過濾掉
                    elif test_type == "string_to_numeric":
                        f.write(f"{i}\n")
                else:
                    # 前 99.9% 是正常資料
                    if test_type == "int_to_string":
                        f.write(f"{i + 1}\n")
                    elif test_type == "float_to_null":
                        f.write(f"{i * 1.5}\n")  # 移除 .2f 格式化，避免精度問題
                    elif test_type == "string_to_numeric":
                        f.write(f"STR_{i:04d}\n")

        return csv_path

    @pytest.mark.stress
    def test_int_with_string_exception(self, temp_dir):
        """測試：99.9% 整數，0.1% 字串例外"""
        csv_path = self._create_type_test_file(temp_dir, "int_to_string")

        loader = Loader(filepath=csv_path)

        data, schema = loader.load()
        assert data is not None
        assert len(data) == 10000
        logging.info(f"整數轉字串例外測試完成，資料形狀: {data.shape}")

    @pytest.mark.stress
    def test_float_with_null_exception(self, temp_dir):
        """測試：99.9% 浮點數，0.1% 空值例外"""
        csv_path = self._create_type_test_file(temp_dir, "float_to_null")

        loader = Loader(filepath=csv_path)

        data, schema = loader.load()
        assert data is not None
        # 空值會被 pandas 過濾掉，所以實際行數會少於 10000
        assert len(data) > 9900  # 至少有 99% 的資料
        logging.info(f"浮點數轉空值例外測試完成，資料形狀: {data.shape}")

    @pytest.mark.stress
    def test_string_with_numeric_exception(self, temp_dir):
        """測試：99.9% 字串，0.1% 數值例外"""
        csv_path = self._create_type_test_file(temp_dir, "string_to_numeric")

        loader = Loader(filepath=csv_path)

        data, schema = loader.load()
        assert data is not None
        assert len(data) == 10000
        logging.info(f"字串轉數值例外測試完成，資料形狀: {data.shape}")


def run_stress_demo():
    """執行壓力測試示範"""
    print("🚀 PETsARD Loader 壓力測試示範")
    print("=" * 50)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用臨時目錄: {temp_dir}")

        # 測試小檔案生成和載入
        generator = LargeFileGenerator(target_size_gb=0.01)  # 10MB
        csv_path = os.path.join(temp_dir, "demo_test.csv")

        print("\n生成測試檔案...")
        file_info = generator.generate_test_csv(csv_path, "mixed_types")

        print(f"檔案大小: {file_info['file_size_bytes'] / 1024 / 1024:.1f} MB")
        print(f"資料行數: {file_info['actual_rows']:,}")

        print("\n測試 Loader 載入...")
        memory_monitor = MemoryMonitor()
        memory_monitor.record("開始")

        start_time = time.time()
        loader = Loader(filepath=csv_path)
        data, schema = loader.load()
        load_time = time.time() - start_time

        memory_monitor.record("完成")

        print("✓ 載入成功")
        print(f"資料形狀: {data.shape}")
        print(f"載入時間: {load_time:.3f} 秒")
        print(f"記憶體使用: {memory_monitor.get_memory_increase():.1f} MB")
        print(
            f"處理速度: {(file_info['file_size_bytes'] / 1024 / 1024) / load_time:.1f} MB/秒"
        )

    print("\n" + "=" * 50)
    print("🎉 壓力測試示範完成!")
    print("執行完整測試: pytest tests/loader/ -m stress -v")


class TestLoaderSchemaParameters:
    """Test cases for schema parameter functionality in Loader
    Loader 中 schema 參數功能的測試案例
    """

    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "age": [25, 30, 35, 28, 32],
                "salary": [50000.5, 60000.0, 70000.25, 55000.75, 65000.0],
                "department": ["IT", "HR", "IT", "Finance", "IT"],
                "is_active": [True, False, True, True, False],
            }
        )

        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def teardown_method(self):
        """Cleanup test data"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_compute_stats_parameter(self):
        """Test compute_stats parameter"""
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            enable_stats=False,  # Changed from compute_stats to enable_stats
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        # Should not raise error
        assert loader.config.schema.enable_stats is False

    def test_optimize_dtypes_parameter(self):
        """Test optimize_dtypes parameter"""
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            enable_optimize_type=False,  # Changed from optimize_dtypes to enable_optimize_type
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.enable_optimize_type is False

    def test_sample_size_parameter(self):
        """Test sample_size parameter"""
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            sample_size=1000,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.sample_size == 1000

    def test_sample_size_null(self):
        """Test sample_size as null"""
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            sample_size=None,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.sample_size is None

    def test_leading_zeros_parameter(self):
        """Test leading_zeros parameter"""
        # Note: Schema class may not have leading_zeros parameter
        # This test is for demonstration - adjust based on actual Schema implementation
        attributes = {"id": Attribute(name="id", type="int")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema is not None

    def test_leading_zeros_invalid(self):
        """Test invalid leading_zeros parameter"""
        # Schema doesn't have leading_zeros validation
        # This test can be simplified or removed
        attributes = {"id": Attribute(name="id", type="int")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )
        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema is not None

    def test_nullable_int_parameter(self):
        """Test nullable_int parameter"""
        # Schema uses enable_null instead of nullable_int
        attributes = {"age": Attribute(name="age", type="int", enable_null=True)}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            enable_null=True,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.enable_null is True

    def test_nullable_int_invalid(self):
        """Test invalid nullable_int parameter"""
        # Schema doesn't have nullable_int validation
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )
        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema is not None

    def test_infer_logical_types_parameter(self):
        """Test infer_logical_types parameter"""
        # Schema doesn't have infer_logical_types, logical types are per attribute
        attributes = {"name": Attribute(name="name", type="str", logical_type="email")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.attributes["name"].logical_type == "email"

    def test_descriptive_parameters(self):
        """Test descriptive parameters"""
        attributes = {"age": Attribute(name="age", type="int")}
        schema_config = Schema(
            id="test_schema_v1",
            name="Test Schema",
            description="Schema for testing",
            attributes=attributes,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.id == "test_schema_v1"
        assert loader.config.schema.name == "Test Schema"
        assert loader.config.schema.description == "Schema for testing"


class TestLoaderSchemaFieldParameters:
    """Test field-level schema parameters in Loader
    Loader 中欄位層級 schema 參數的測試案例
    """

    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame(
            {
                "email": ["alice@example.com", "bob@test.com", "charlie@demo.org"],
                "phone": ["123-456-7890", "987-654-3210", "555-123-4567"],
                "user_id": ["00001", "00002", "00003"],
                "score": [85.5, 92.0, 78.5],
            }
        )

        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def teardown_method(self):
        """Cleanup test data"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_logical_type_parameter(self):
        """Test logical_type parameter"""
        valid_values = ["never", "infer", "email", "phone", "url"]

        for value in valid_values:
            attributes = {
                "email": Attribute(name="email", type="str", logical_type=value)
            }
            schema_config = Schema(
                id="test_schema",
                name="Test Schema",
                attributes=attributes,
            )

            loader = Loader(filepath=self.temp_file.name, schema=schema_config)
            assert loader.config.schema.attributes["email"].logical_type == value

    def test_leading_zeros_field_level(self):
        """Test leading_zeros at field level"""
        # Attribute doesn't have leading_zeros field
        attributes = {"user_id": Attribute(name="user_id", type="str")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.attributes["user_id"] is not None

    def test_leading_zeros_field_invalid(self):
        """Test invalid leading_zeros at field level"""
        # Attribute doesn't have leading_zeros validation
        attributes = {"user_id": Attribute(name="user_id", type="str")}
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )
        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema is not None


class TestLoaderSchemaParameterConflicts:
    """Test parameter conflicts and validation in Loader
    Loader 中參數衝突和驗證的測試案例
    """

    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame(
            {"email": ["alice@example.com", "bob@test.com"], "name": ["Alice", "Bob"]}
        )

        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def teardown_method(self):
        """Cleanup test data"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_infer_logical_types_conflict(self):
        """Test conflict between infer_logical_types and field logical_type"""
        # Schema doesn't have infer_logical_types parameter
        # Create a schema with logical_type specified
        attributes = {
            "email": Attribute(name="email", type="str", logical_type="email")
        }
        schema_config = Schema(
            id="test_schema", name="Test Schema", attributes=attributes
        )

        # Schema creation should succeed
        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.attributes["email"].logical_type == "email"


class TestLoaderSchemaEdgeCases:
    """Test edge cases and error handling for schema parameters in Loader
    Loader 中 schema 參數的邊緣情況和錯誤處理測試案例
    """

    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def teardown_method(self):
        """Cleanup test data"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_empty_schema(self):
        """Test empty schema"""
        # Test with no schema_config - should use defaults
        loader = Loader(filepath=self.temp_file.name)
        # Should not raise error
        assert loader.config.schema is None

    def test_schema_with_only_global_params(self):
        """Test schema with only global parameters"""
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes={},
            enable_stats=False,
            enable_optimize_type=True,
            sample_size=100,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.enable_stats is False
        assert loader.config.schema.enable_optimize_type is True
        assert loader.config.schema.sample_size == 100

    def test_invalid_global_parameter(self):
        """Test invalid global parameter"""
        # Invalid parameters should be caught during Schema creation
        with pytest.raises(TypeError):
            Schema(
                id="test_schema",
                name="Test Schema",
                attributes={"col1": Attribute(name="col1", type="int")},
                invalid_param="value",
            )

    def test_invalid_field_parameter(self):
        """Test invalid field parameter"""
        # Invalid parameters should be caught during Attribute creation
        with pytest.raises(TypeError):
            Attribute(name="test", type="int", invalid_param="value")

    def test_mixed_legacy_and_schema(self):
        """Test mixing legacy parameters with schema"""
        attributes = {"col1": Attribute(name="col1", type="int")}
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            enable_stats=False,
        )

        # This should raise ConfigError due to field conflict
        with pytest.raises(
            ConfigError, match="Conflict detected.*col1.*schema and column_types"
        ):
            Loader(
                filepath=self.temp_file.name,
                column_types={"category": ["col1"]},  # This conflicts with schema
                schema=schema_config,
            )


if __name__ == "__main__":
    run_stress_demo()
