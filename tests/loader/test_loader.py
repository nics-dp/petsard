import gc
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import psutil
import pytest

from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.loader.loader import BenchmarkerConfig, Loader, LoaderConfig, LoaderFileExt


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

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, schema = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert schema is not None

    def test_load_excel(self):
        """Test loading Excel file
        測試載入 Excel 檔案
        """
        excel_path = "path/to/file.xlsx"
        loader = Loader(filepath=excel_path)

        with (
            patch("pandas.read_excel") as mock_read_excel,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch("os.path.exists") as mock_exists,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_exists.return_value = True
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_excel.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, schema = loader.load()

            # Assertions
            # 斷言
            mock_read_excel.assert_called_once_with(
                excel_path,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert schema is not None

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
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
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
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df
            mock_benchmarker_instance = MagicMock()
            mock_benchmarker.return_value = mock_benchmarker_instance

            # Create and load benchmark data
            # 創建和載入基準資料
            loader = Loader(filepath="benchmark://adult-income")
            data, schema = loader.load()

            # Assertions
            # 斷言
            mock_benchmarker.assert_called_once()
            mock_benchmarker_instance.download.assert_called_once()
            mock_read_csv.assert_called_once()
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert schema is not None

    def test_custom_na_values(self, sample_csv_path):
        """Test loading with custom NA values
        測試使用自定義 NA 值載入資料
        """
        na_values = ["x"]
        loader = Loader(filepath=sample_csv_path, na_values=na_values)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": [None, "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, schema = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header="infer",
                names=None,
                na_values=na_values,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert schema is not None

    def test_custom_header_names(self, sample_csv_path):
        """Test loading with custom header names
        測試使用自定義欄位名稱載入資料
        """
        header_names = ["Col1", "Col2"]
        loader = Loader(filepath=sample_csv_path, header_names=header_names)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"Col1": [1, 2, 3], "Col2": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, schema = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header=0,
                names=header_names,
                na_values=loader.config.na_values,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
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
        # Valid schema configuration
        valid_schema = {
            "age": {"type": "int", "na_values": ["unknown", "N/A"]},
            "salary": {"type": "float", "precision": 2},
            "score": {"type": "int"},
        }

        # Should not raise any exception
        config = LoaderConfig(filepath="test.csv", schema=valid_schema)
        assert config.schema == valid_schema

    def test_schema_parameter_validation_invalid_structure(self):
        """Test schema parameter validation with invalid structure
        測試無效結構的 schema 參數驗證
        """
        # Invalid: schema is not a dict
        with pytest.raises(ConfigError, match="schema must be a dictionary"):
            LoaderConfig(filepath="test.csv", schema="invalid")

        # Invalid: field config is not a dict
        with pytest.raises(ConfigError, match="must be a dictionary"):
            LoaderConfig(filepath="test.csv", schema={"field1": "invalid"})

    def test_schema_parameter_validation_invalid_keys(self):
        """Test schema parameter validation with invalid keys
        測試無效鍵值的 schema 參數驗證
        """
        # Invalid: unknown key
        invalid_schema = {"age": {"type": "int", "invalid_key": "value"}}
        with pytest.raises(ConfigError, match="contains invalid keys"):
            LoaderConfig(filepath="test.csv", schema=invalid_schema)

    def test_schema_parameter_validation_invalid_values(self):
        """Test schema parameter validation with invalid values
        測試無效值的 schema 參數驗證
        """
        # Invalid: type is not string
        with pytest.raises(ConfigError, match="must be a string"):
            LoaderConfig(filepath="test.csv", schema={"age": {"type": 123}})

        # Invalid: na_values is not str or list
        with pytest.raises(ConfigError, match="must be str or list"):
            LoaderConfig(filepath="test.csv", schema={"age": {"na_values": 123}})

        # Invalid: precision is not non-negative integer
        with pytest.raises(ConfigError, match="must be a non-negative integer"):
            LoaderConfig(filepath="test.csv", schema={"salary": {"precision": -1}})

        with pytest.raises(ConfigError, match="must be a non-negative integer"):
            LoaderConfig(
                filepath="test.csv", schema={"salary": {"precision": "invalid"}}
            )

    def test_schema_transformations_applied(self, sample_csv_with_schema_needs):
        """Test that schema transformations are applied during load
        測試在載入過程中應用 schema 轉換
        """
        schema_config = {
            "age": {"type": "int", "na_values": ["unknown", "N/A"]},
            "salary": {"type": "float", "precision": 2},
            "score": {"type": "int"},
            "active": {"type": "boolean"},
        }

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch(
                "petsard.metadater.field.field_functions.apply_field_transformations"
            ) as mock_field_transform,
        ):
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
            mock_read_csv.return_value = original_df.fillna(pd.NA)

            # Mock field transformations to return modified series
            def mock_transform_side_effect(series, config, field_name):
                if field_name == "age":
                    # Simulate NA value replacement and type conversion
                    return pd.Series([25, 30, pd.NA, 45, pd.NA], dtype="Int64")
                elif field_name == "salary":
                    # Simulate precision rounding
                    return pd.Series([50000.12, 60000.46, 70000.79, 80001.00, 90000.11])
                elif field_name == "score":
                    # Simulate string to int conversion
                    return pd.Series([85, 90, 78, 92, 88], dtype="Int64")
                elif field_name == "active":
                    # Simulate boolean conversion
                    return pd.Series([True, False, True, False, True], dtype="boolean")
                return series

            mock_field_transform.side_effect = mock_transform_side_effect

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = original_df

            # Call load method
            data, schema = loader.load()

            # Verify that field transformations were called for each configured field
            assert mock_field_transform.call_count == 4  # age, salary, score, active

            # Verify the calls were made with correct field names
            called_field_names = [
                call[0][2] for call in mock_field_transform.call_args_list
            ]
            expected_fields = {"age", "salary", "score", "active"}
            assert set(called_field_names) == expected_fields

    def test_schema_field_not_in_data_warning(self, sample_csv_with_schema_needs):
        """Test warning when schema field is not found in data
        測試當 schema 欄位在資料中找不到時的警告
        """
        schema_config = {
            "nonexistent_field": {"type": "int"},
            "age": {"type": "int"},
        }

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch(
                "petsard.metadater.field.field_functions.apply_field_transformations"
            ) as mock_field_transform,
        ):
            # Setup mock returns
            original_df = pd.DataFrame(
                {
                    "age": [25, 30, 35, 45, 50],
                    "other_field": ["A", "B", "C", "D", "E"],
                }
            )
            mock_read_csv.return_value = original_df.fillna(pd.NA)
            mock_field_transform.return_value = original_df["age"]

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = original_df

            # Call load method - should not raise exception but log warning
            data, schema = loader.load()

            # Verify that field transformation was only called for existing field
            assert mock_field_transform.call_count == 1
            called_field_name = mock_field_transform.call_args_list[0][0][2]
            assert called_field_name == "age"

    def test_schema_transformation_error_handling(self, sample_csv_with_schema_needs):
        """Test error handling during schema transformations
        測試 schema 轉換過程中的錯誤處理
        """
        schema_config = {
            "age": {"type": "int"},
        }

        loader = Loader(filepath=sample_csv_with_schema_needs, schema=schema_config)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch(
                "petsard.metadater.field.field_functions.apply_field_transformations"
            ) as mock_field_transform,
        ):
            # Setup mock returns
            original_df = pd.DataFrame(
                {
                    "age": [25, 30, 35, 45, 50],
                }
            )
            mock_read_csv.return_value = original_df.fillna(pd.NA)

            # Make field transformation raise an exception
            mock_field_transform.side_effect = Exception("Transformation failed")

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = original_df

            # Call load method - should not raise exception but continue with other processing
            data, schema = loader.load()

            # Verify that the load completed despite transformation error
            assert data is not None
            assert schema is not None

    def test_schema_precedence_over_column_types(self, sample_csv_with_schema_needs):
        """Test that schema parameter takes precedence over column_types
        測試 schema 參數優先於 column_types
        """
        schema_config = {
            "age": {"type": "int", "na_values": ["unknown"]},
        }
        column_types = {
            "category": ["age"],  # This should be overridden by schema
        }

        loader = Loader(
            filepath=sample_csv_with_schema_needs,
            schema=schema_config,
            column_types=column_types,
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            original_df = pd.DataFrame({"age": [25, 30, 35]})
            mock_read_csv.return_value = original_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = original_df

            # Call load method
            data, schema = loader.load()

            # Verify that create_schema was called with schema configuration
            # The schema should override column_types for the 'age' field
            call_args = mock_create_schema.call_args
            schema_config = call_args[1]["config"]  # keyword argument 'config'

            # Check that the field config for 'age' comes from schema, not column_types
            age_field_config = schema_config.fields["age"]
            assert age_field_config.type_hint == "int"
            assert age_field_config.na_values == ["unknown"]


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

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            data, schema = loader.load()

            # Verify normal behavior (no dtype parameter when no column_types specified)
            mock_read_csv.assert_called_once_with(
                ambiguous_sample_csv,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
                # No dtype parameter should be passed when no column_types specified
            )
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
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        self.peak_memory = self.initial_memory

    def get_memory_usage(self) -> float:
        """取得當前記憶體使用量 (MB)"""
        return self.process.memory_info().rss / 1024 / 1024

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
    def test_small_file_100mb(self, temp_dir):
        """測試小檔案：100MB (30秒超時)"""
        success, error_msg = self._run_stress_test(temp_dir, 0.1, "小檔案100MB測試", 30)
        assert success, f"測試失敗: {error_msg}"

    @pytest.mark.stress
    def test_medium_file_1gb(self, temp_dir):
        """測試中檔案：1GB (120秒超時)"""
        success, error_msg = self._run_stress_test(temp_dir, 1.0, "中檔案1GB測試", 120)
        assert success, f"測試失敗: {error_msg}"

    @pytest.mark.stress
    def test_large_file_3gb(self, temp_dir):
        """測試大檔案：3GB (300秒超時)"""
        success, error_msg = self._run_stress_test(temp_dir, 3.0, "大檔案3GB測試", 300)
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


if __name__ == "__main__":
    run_stress_demo()
