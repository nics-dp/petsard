"""
測試 ReporterSaveSchema 類別
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from petsard.exceptions import ConfigError
from petsard.reporter.reporter import Reporter
from petsard.reporter.reporter_save_schema import ReporterSaveSchema


@pytest.fixture
def sample_dataframe():
    """建立測試用的 DataFrame"""
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, np.nan],
            "income": [50000.0, 60000.0, 70000.0, 80000.0, 90000.0],
            "category": ["A", "B", "A", "C", "B"],
            "score": [0.85, 0.90, 0.75, 0.95, 0.88],
        }
    )


@pytest.fixture
def sample_schema_data(sample_dataframe):
    """建立測試用的 schema 資料結構"""
    return {
        ("Loader", "default"): sample_dataframe.copy(),
        ("Loader", "default", "Preprocessor", "scaler"): sample_dataframe.copy(),
        ("Loader", "default", "Synthesizer", "ctgan"): sample_dataframe.copy(),
    }


@pytest.fixture
def cleanup_files():
    """清理測試生成的檔案"""
    files_to_cleanup = []

    yield files_to_cleanup

    # 清理所有測試生成的檔案
    for filepath in files_to_cleanup:
        try:
            Path(filepath).unlink(missing_ok=True)
        except Exception:
            pass


class TestReporterSaveSchemaInitialization:
    """測試 ReporterSaveSchema 的初始化"""

    def test_init_with_string_source(self):
        """測試使用字串 source 初始化"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        assert reporter.config["source"] == ["Loader"]
        assert reporter.config["output"] == "petsard"

    def test_init_with_list_source(self):
        """測試使用列表 source 初始化"""
        config = {"method": "save_schema", "source": ["Loader", "Preprocessor"]}
        reporter = ReporterSaveSchema(config)

        assert reporter.config["source"] == ["Loader", "Preprocessor"]

    def test_init_with_custom_output(self):
        """測試自訂輸出前綴"""
        config = {
            "method": "save_schema",
            "source": "Loader",
            "output": "my_project",
        }
        reporter = ReporterSaveSchema(config)

        assert reporter.config["output"] == "my_project"

    def test_init_with_yaml_output(self):
        """測試啟用 YAML 輸出選項"""
        config = {
            "method": "save_schema",
            "source": "Loader",
            "yaml_output": True,
        }
        reporter = ReporterSaveSchema(config)

        assert reporter.config.get("yaml_output") is True

    def test_init_without_source_raises_error(self):
        """測試缺少 source 參數時拋出錯誤"""
        config = {"method": "save_schema"}

        with pytest.raises(ConfigError):
            ReporterSaveSchema(config)

    def test_init_with_invalid_source_type(self):
        """測試無效 source 類型時拋出錯誤"""
        # 測試數值類型
        config = {"method": "save_schema", "source": 123}
        with pytest.raises(ConfigError):
            ReporterSaveSchema(config)

        # 測試包含非字串的列表
        config = {"method": "save_schema", "source": ["Loader", 123]}
        with pytest.raises(ConfigError):
            ReporterSaveSchema(config)

        # 測試 tuple
        config = {"method": "save_schema", "source": ("Loader", "Preprocessor")}
        with pytest.raises(ConfigError):
            ReporterSaveSchema(config)


class TestReporterSaveSchemaCreate:
    """測試 ReporterSaveSchema 的 create 方法"""

    def test_create_with_single_source(self, sample_schema_data):
        """測試單一 source 的資料處理"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        result = reporter.create(sample_schema_data)

        # 應該只包含 Loader 的資料
        assert len(result) == 1
        assert "Loader[default]" in result

    def test_create_with_multiple_sources(self, sample_schema_data):
        """測試多個 source 的資料處理"""
        config = {"method": "save_schema", "source": ["Loader", "Preprocessor"]}
        reporter = ReporterSaveSchema(config)

        result = reporter.create(sample_schema_data)

        # 應該包含 Loader 和 Preprocessor 的資料
        assert len(result) == 2
        assert "Loader[default]" in result
        assert "Loader[default]_Preprocessor[scaler]" in result

    def test_create_with_all_sources(self, sample_schema_data):
        """測試包含所有 source 的資料處理"""
        config = {
            "method": "save_schema",
            "source": ["Loader", "Preprocessor", "Synthesizer"],
        }
        reporter = ReporterSaveSchema(config)

        result = reporter.create(sample_schema_data)

        # 應該包含所有資料
        assert len(result) == 3

    def test_create_with_nonexistent_source(self, sample_schema_data):
        """測試不存在的 source"""
        config = {"method": "save_schema", "source": "Evaluator"}
        reporter = ReporterSaveSchema(config)

        result = reporter.create(sample_schema_data)

        # 應該沒有匹配的資料
        assert len(result) == 0

    def test_create_skips_none_dataframes(self):
        """測試跳過 None 值的 DataFrame"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        data_with_none = {
            ("Loader", "default"): None,
            ("Preprocessor", "scaler"): pd.DataFrame({"a": [1, 2]}),
        }

        result = reporter.create(data_with_none)

        # 應該跳過 None 值
        assert len(result) == 0


class TestReporterSaveSchemaInferSchema:
    """測試 schema 推斷功能"""

    def test_infer_schema_basic_structure(self, sample_dataframe):
        """測試基本 schema 結構"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)

        # 檢查基本結構
        assert "columns" in schema
        assert "shape" in schema
        assert schema["shape"]["rows"] == 5
        assert schema["shape"]["columns"] == 4

    def test_infer_schema_column_info(self, sample_dataframe):
        """測試欄位資訊推斷"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)

        # 檢查 age 欄位（有 NaN）
        age_info = schema["columns"]["age"]
        assert "dtype" in age_info
        assert age_info["nullable"] is True
        assert "unique_count" in age_info

    def test_infer_schema_numeric_statistics(self, sample_dataframe):
        """測試數值型別的統計資訊"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)

        # 檢查 income 欄位的統計資訊
        income_info = schema["columns"]["income"]
        assert "statistics" in income_info
        assert "min" in income_info["statistics"]
        assert "max" in income_info["statistics"]
        assert "mean" in income_info["statistics"]
        assert income_info["statistics"]["min"] == 50000.0
        assert income_info["statistics"]["max"] == 90000.0

    def test_infer_schema_categorical_info(self, sample_dataframe):
        """測試類別型別的資訊"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)

        # 檢查 category 欄位的類別資訊
        category_info = schema["columns"]["category"]
        assert "categories" in category_info
        assert len(category_info["categories"]) == 3
        assert set(category_info["categories"]) == {"A", "B", "C"}


class TestReporterSaveSchemaFlatten:
    """測試 schema 攤平功能"""

    def test_flatten_source_schema_basic(self, sample_dataframe):
        """測試基本攤平功能"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)
        flattened = reporter._flatten_source_schema("Loader[default]", schema)

        # 檢查基本結構
        assert "source" in flattened
        assert flattened["source"] == "Loader[default]"

    def test_flatten_source_schema_columns(self, sample_dataframe):
        """測試欄位屬性攤平"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)
        flattened = reporter._flatten_source_schema("Loader[default]", schema)

        # 檢查數值欄位的統計資訊 - 注意欄位名稱可能被包在方括號中
        assert "[income]_dtype" in flattened or "income_dtype" in flattened
        assert "[income]_nullable" in flattened or "income_nullable" in flattened
        assert "[income]_min" in flattened or "income_min" in flattened
        assert "[income]_max" in flattened or "income_max" in flattened
        assert "[income]_mean" in flattened or "income_mean" in flattened

    def test_flatten_source_schema_categories(self, sample_dataframe):
        """測試類別資訊攤平"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        schema = reporter._infer_schema_from_dataframe(sample_dataframe)
        flattened = reporter._flatten_source_schema("Loader[default]", schema)

        # 檢查類別欄位 - 注意欄位名稱可能被包在方括號中
        category_key = (
            "[category]_categories"
            if "[category]_categories" in flattened
            else "category_categories"
        )
        assert category_key in flattened
        assert isinstance(flattened[category_key], str)
        assert "|" in flattened[category_key]


class TestReporterSaveSchemaReport:
    """測試報告生成功能"""

    def test_report_csv_output(self, sample_schema_data, cleanup_files, tmp_path):
        """測試 CSV 輸出"""
        output_file = tmp_path / "test_output"
        config = {
            "method": "save_schema",
            "source": ["Loader", "Preprocessor"],
            "output": str(output_file),
        }
        reporter = ReporterSaveSchema(config)

        processed_data = reporter.create(sample_schema_data)
        result = reporter.report(processed_data)

        # 檢查返回結果
        assert len(result) == 2

        # 檢查 CSV 檔案是否生成
        csv_file = Path(f"{output_file}_schema_Loader-Preprocessor_summary.csv")
        cleanup_files.append(str(csv_file))
        assert csv_file.exists()

        # 讀取 CSV 並驗證內容
        df = pd.read_csv(csv_file)
        assert "source" in df.columns
        assert len(df) == 2

    def test_report_yaml_output(self, sample_schema_data, cleanup_files, tmp_path):
        """測試 YAML 輸出"""
        output_file = tmp_path / "test_output"
        config = {
            "method": "save_schema",
            "source": "Loader",
            "output": str(output_file),
            "yaml_output": True,
        }
        reporter = ReporterSaveSchema(config)

        processed_data = reporter.create(sample_schema_data)
        result = reporter.report(processed_data)

        # 檢查 YAML 檔案是否生成
        yaml_file = Path(f"{output_file}_schema_Loader[default].yaml")
        cleanup_files.append(str(yaml_file))
        assert yaml_file.exists()

        # 讀取 YAML 並驗證內容
        with open(yaml_file, encoding="utf-8") as f:
            schema = yaml.safe_load(f)

        assert "columns" in schema
        assert "shape" in schema

    def test_report_filename_with_multiple_sources(
        self, sample_schema_data, cleanup_files, tmp_path
    ):
        """測試多個 source 的檔名生成"""
        output_file = tmp_path / "test_output"
        config = {
            "method": "save_schema",
            "source": ["Loader", "Preprocessor", "Synthesizer"],
            "output": str(output_file),
        }
        reporter = ReporterSaveSchema(config)

        processed_data = reporter.create(sample_schema_data)
        reporter.report(processed_data)

        # 檢查檔名包含所有 source
        csv_file = Path(
            f"{output_file}_schema_Loader-Preprocessor-Synthesizer_summary.csv"
        )
        cleanup_files.append(str(csv_file))
        assert csv_file.exists()

    def test_report_with_empty_data(self):
        """測試空資料的處理"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        result = reporter.report({})

        # 應該返回空字典
        assert result == {}

    def test_report_with_none_dataframes(self):
        """測試包含 None 的資料"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        processed_data = {
            "Loader[default]": None,
            "Loader[test]": pd.DataFrame({"a": [1, 2]}),
        }

        result = reporter.report(processed_data)

        # 應該只處理非 None 的資料
        assert "Loader[test]" in result
        assert "Loader[default]" not in result


class TestReporterFactoryIntegration:
    """測試與 Reporter 工廠的整合"""

    def test_create_via_reporter_factory(self):
        """測試透過 Reporter 工廠創建"""
        reporter = Reporter(method="save_schema", source="Loader")

        assert isinstance(reporter, ReporterSaveSchema)
        assert reporter.config["source"] == ["Loader"]

    def test_factory_with_multiple_sources(self):
        """測試工廠方法使用多個 source"""
        reporter = Reporter(
            method="save_schema", source=["Loader", "Preprocessor", "Synthesizer"]
        )

        assert isinstance(reporter, ReporterSaveSchema)
        assert reporter.config["source"] == ["Loader", "Preprocessor", "Synthesizer"]

    def test_factory_without_source_raises_error(self):
        """測試工廠方法缺少 source 時拋出錯誤"""
        with pytest.raises(ConfigError):
            Reporter(method="save_schema")


class TestReporterSaveSchemaEdgeCases:
    """測試邊界情況"""

    def test_empty_dataframe(self):
        """測試空 DataFrame"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        empty_df = pd.DataFrame()
        schema = reporter._infer_schema_from_dataframe(empty_df)

        assert schema["shape"]["rows"] == 0
        assert schema["shape"]["columns"] == 0
        assert len(schema["columns"]) == 0

    def test_dataframe_with_all_nan(self):
        """測試全為 NaN 的 DataFrame"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        nan_df = pd.DataFrame({"col1": [np.nan, np.nan], "col2": [np.nan, np.nan]})
        schema = reporter._infer_schema_from_dataframe(nan_df)

        # 應該能正常處理
        assert "col1" in schema["columns"]
        assert schema["columns"]["col1"]["nullable"] is True

    def test_dataframe_with_many_categories(self):
        """測試有大量類別的 DataFrame"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        # 創建有 20 個不同類別的 DataFrame
        many_categories_df = pd.DataFrame({"category": [f"cat_{i}" for i in range(20)]})
        schema = reporter._infer_schema_from_dataframe(many_categories_df)

        # 超過 10 個類別時不應該記錄
        assert "categories" not in schema["columns"]["category"]

    def test_save_yaml_error_handling(self, tmp_path, caplog):
        """測試 YAML 保存錯誤處理"""
        config = {"method": "save_schema", "source": "Loader"}
        reporter = ReporterSaveSchema(config)

        # 嘗試寫入無效路徑
        invalid_path = "/invalid/path/that/does/not/exist/test.yaml"

        with pytest.raises(Exception):
            reporter._save_schema_to_yaml({"test": "data"}, invalid_path)
