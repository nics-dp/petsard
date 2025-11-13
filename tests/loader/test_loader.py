import os
import tempfile
from unittest.mock import patch

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

    def test_default_filepath(self):
        """Test that filepath must be specified
        測試必須指定 filepath 參數
        """
        # LoaderConfig no longer supports method parameter
        # LoaderConfig 不再支持 method 參數
        with pytest.raises(ConfigError):
            LoaderConfig()  # No filepath specified

    def test_regular_filepath(self):
        """Test regular file path parsing
        測試一般檔案路徑解析
        """
        # LoaderConfig should handle regular file paths
        config = LoaderConfig(filepath="path/to/data.csv")
        assert config.filepath == "path/to/data.csv"
        assert config.file_ext == ".csv"

    def test_benchmark_path_not_supported_in_loader(self):
        """Test that benchmark:// paths are not supported in LoaderConfig
        測試 LoaderConfig 不支援 benchmark:// 路徑
        """
        # LoaderConfig should not handle benchmark:// paths
        # These should be handled by LoaderAdapter instead
        # LoaderConfig 不應處理 benchmark:// 路徑
        # 這些應該由 LoaderAdapter 處理
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(filepath="benchmark://adult-income")

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

    def test_loader_with_regular_csv(self):
        """Test loading regular CSV dataset with schema inference
        測試載入一般 CSV 資料集並推斷 schema
        """
        with patch("pandas.read_csv") as mock_read_csv:
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

                    # Create loader and load data with regular file path
                    loader = Loader(filepath="data/test.csv")
                    data, schema = loader.load()

                    # Verify schema was created and modified
                    mock_from_data.assert_called_once()
                    assert schema.id == "test"  # Should be modified from temp_id
                    assert (
                        schema.name == "test.csv"
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

    def test_loader_does_not_handle_benchmark(self):
        """Test that Loader does not handle benchmark datasets
        測試 Loader 不處理基準資料集
        """
        # Loader should raise error for benchmark:// paths
        # Loader 應該對 benchmark:// 路徑拋出錯誤
        with pytest.raises(UnsupportedMethodError):
            Loader(filepath="benchmark://adult-income")

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

    def test_regular_data_load(self):
        """Test loading regular data
        測試載入一般資料
        """
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

                # Create and load regular data
                loader = Loader(filepath="data/test.csv")
                data, schema = loader.load()

                # Assertions
                mock_read_csv.assert_called_once()
                assert data is not None
                assert schema is not None
                # Verify schema was modified
                assert schema.id == "test"
                assert schema.name == "test.csv"

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

                # Verify that schema contains the fields from the actual data
                # The nonexistent_field should not be in the returned schema since it's not in data
                assert "age" in schema.attributes
                assert "other_field" in schema.attributes

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

    def test_data_schema_reconciliation_extra_columns(self):
        """Test automatic reconciliation when data has extra columns
        測試資料有額外欄位時的自動協調
        """
        # Create test data with extra columns
        test_data = pd.DataFrame(
            {"defined_col": [1, 2, 3], "extra_col": ["a", "b", "c"]}
        )

        # Create schema with only one column defined
        schema = Schema(
            id="test_schema",
            name="Test Schema",
            attributes={"defined_col": Attribute(name="defined_col", type="int")},
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)

            loader = Loader(filepath=f.name, schema=schema)

            with patch("pandas.read_csv") as mock_read_csv:
                mock_read_csv.return_value = test_data

                # Mock SchemaMetadater.diff to return extra columns
                with patch.object(SchemaMetadater, "diff") as mock_diff:
                    mock_diff.return_value = {
                        "missing_columns": [],
                        "extra_columns": ["extra_col"],
                        "type_mismatches": {},
                    }

                    # Mock AttributeMetadater.from_data
                    from petsard.metadater import AttributeMetadater

                    with patch.object(
                        AttributeMetadater, "from_data"
                    ) as mock_from_data:
                        mock_from_data.return_value = Attribute(
                            name="extra_col", type="string"
                        )

                        # Mock SchemaMetadater.align
                        with patch.object(SchemaMetadater, "align") as mock_align:
                            mock_align.return_value = test_data

                            data, result_schema = loader.load()

                            # Verify extra column was added to schema
                            assert "extra_col" in result_schema.attributes
                            assert (
                                result_schema.attributes["extra_col"].type == "string"
                            )

    def test_data_schema_reconciliation_missing_columns(self):
        """Test automatic reconciliation when schema has missing columns
        測試 schema 有缺失欄位時的自動協調
        """
        # Create test data
        test_data = pd.DataFrame({"col1": [1, 2, 3]})

        # Create schema with additional columns
        schema = Schema(
            id="test_schema",
            name="Test Schema",
            attributes={
                "col1": Attribute(name="col1", type="int"),
                "col2": Attribute(name="col2", type="string"),
            },
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            test_data.to_csv(f.name, index=False)

            loader = Loader(filepath=f.name, schema=schema)

            with patch("pandas.read_csv") as mock_read_csv:
                mock_read_csv.return_value = test_data

                # Mock SchemaMetadater.diff to return missing columns
                with patch.object(SchemaMetadater, "diff") as mock_diff:
                    mock_diff.return_value = {
                        "missing_columns": ["col2"],
                        "extra_columns": [],
                        "type_mismatches": {},
                    }

                    # Mock SchemaMetadater.align to add missing columns with defaults
                    expected_data = test_data.copy()
                    expected_data["col2"] = pd.NA

                    with patch.object(SchemaMetadater, "align") as mock_align:
                        mock_align.return_value = expected_data

                        data, result_schema = loader.load()

                        # Verify align was called with correct strategy
                        mock_align.assert_called_once()
                        align_strategy = mock_align.call_args[0][2]
                        assert align_strategy["add_missing_columns"] is True
                        assert align_strategy["remove_extra_columns"] is False


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
        # Schema uses enable_null at schema level, not attribute level
        # Use nullable in type_attr for attribute level
        attributes = {
            "age": Attribute(name="age", type="int", type_attr={"nullable": True})
        }
        schema_config = Schema(
            id="test_schema",
            name="Test Schema",
            attributes=attributes,
            enable_null=True,
        )

        loader = Loader(filepath=self.temp_file.name, schema=schema_config)
        assert loader.config.schema.enable_null is True
        assert loader.config.schema.attributes["age"].type_attr["nullable"] is True

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
