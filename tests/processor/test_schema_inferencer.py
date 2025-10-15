"""
測試 Schema Inferencer 功能

驗證 SchemaInferencer 能正確推論 Processor 對 Schema 的影響
"""

import pytest

from petsard.metadater.metadata import Attribute, Schema
from petsard.metadater.schema_inferencer import (
    ProcessorTransformRules,
    SchemaInferencer,
    TransformRule,
)


class TestTransformRule:
    """測試 TransformRule 基本功能"""

    def test_transform_rule_creation(self):
        """測試創建轉換規則"""
        rule = TransformRule(
            processor_type="encoder",
            processor_method="encoder_label",
            input_types=["categorical"],
            output_type="int64",
            output_logical_type="encoded_categorical",
        )

        assert rule.processor_type == "encoder"
        assert rule.processor_method == "encoder_label"
        assert rule.output_type == "int64"


class TestProcessorTransformRules:
    """測試 ProcessorTransformRules 規則庫"""

    def test_get_rule_exists(self):
        """測試獲取存在的規則"""
        rule = ProcessorTransformRules.get_rule("encoder_label")
        assert rule is not None
        assert rule.processor_method == "encoder_label"
        assert rule.output_type == "int64"

    def test_get_rule_not_exists(self):
        """測試獲取不存在的規則"""
        rule = ProcessorTransformRules.get_rule("nonexistent_processor")
        assert rule is None

    def test_apply_rule_changes_type(self):
        """測試應用規則會改變類型"""
        # 創建一個類別型欄位
        original_attr = Attribute(
            name="category_col", type="string", logical_type="category"
        )

        # 獲取 encoder_label 規則
        rule = ProcessorTransformRules.get_rule("encoder_label")

        # 應用規則
        new_attr = ProcessorTransformRules.apply_rule(original_attr, rule)

        # 驗證類型改變
        assert new_attr.type == "int64"
        assert new_attr.logical_type == "encoded_categorical"
        assert new_attr.name == original_attr.name

    def test_apply_rule_preserves_name(self):
        """測試應用規則保留欄位名稱"""
        original_attr = Attribute(name="test_column", type="float64")

        rule = ProcessorTransformRules.get_rule("scaler_standard")
        new_attr = ProcessorTransformRules.apply_rule(original_attr, rule)

        assert new_attr.name == "test_column"

    def test_missing_processor_removes_nulls(self):
        """測試 missing processor 會影響可空性"""
        original_attr = Attribute(name="numeric_col", type="float64", enable_null=True)

        rule = ProcessorTransformRules.get_rule("missing_mean")
        new_attr = ProcessorTransformRules.apply_rule(original_attr, rule)

        # missing 處理後應該不允許 null
        assert new_attr.enable_null == False


class TestSchemaInferencer:
    """測試 SchemaInferencer 推論功能"""

    def test_inferencer_creation(self):
        """測試創建推論器"""
        inferencer = SchemaInferencer()
        assert inferencer is not None
        assert len(inferencer._inference_history) == 0

    def test_infer_preprocessor_output_simple(self):
        """測試推論簡單的 Preprocessor 輸出"""
        # 創建輸入 Schema
        input_schema = Schema(
            id="test_schema",
            name="Test Schema",
            attributes={
                "age": Attribute(name="age", type="int64"),
                "name": Attribute(name="name", type="string"),
            },
        )

        # 創建 Processor 配置
        processor_config = {"encoder": {"name": "encoder_label"}}

        # 推論
        inferencer = SchemaInferencer()
        output_schema = inferencer.infer_preprocessor_output(
            input_schema, processor_config
        )

        # 驗證結果
        assert output_schema is not None
        assert len(output_schema.attributes) == 2
        assert output_schema.parent_schema_id == "test_schema"

    def test_infer_with_scaler(self):
        """測試包含 scaler 的推論"""
        input_schema = Schema(
            id="test_schema",
            attributes={
                "value": Attribute(name="value", type="float64"),
            },
        )

        processor_config = {"scaler": {"value": "scaler_standard"}}

        inferencer = SchemaInferencer()
        output_schema = inferencer.infer_preprocessor_output(
            input_schema, processor_config
        )

        # Standard scaler 輸出應該是 float64
        assert output_schema.attributes["value"].type == "float64"
        assert output_schema.attributes["value"].logical_type == "standardized"

    def test_infer_with_multiple_processors(self):
        """測試多個 processor 的推論"""
        input_schema = Schema(
            id="test_schema",
            attributes={
                "value": Attribute(name="value", type="int64", enable_null=True),
            },
        )

        # 配置：先填充缺失值，再標準化
        processor_config = {
            "missing": {"value": "missing_mean"},
            "scaler": {"value": "scaler_standard"},
        }

        inferencer = SchemaInferencer()
        output_schema = inferencer.infer_preprocessor_output(
            input_schema, processor_config
        )

        # 應該不允許 null（因為 missing_mean）並且是 float64（因為 scaler_standard）
        assert output_schema.attributes["value"].enable_null == False
        assert output_schema.attributes["value"].type == "float64"

    def test_inference_history_recorded(self):
        """測試推論歷史被正確記錄"""
        input_schema = Schema(
            id="test_schema",
            attributes={
                "cat": Attribute(name="cat", type="string"),
            },
        )

        processor_config = {"encoder": {"cat": "encoder_label"}}

        inferencer = SchemaInferencer()
        inferencer.infer_preprocessor_output(input_schema, processor_config)

        history = inferencer.get_inference_history()
        assert len(history) == 1
        assert history[0]["stage"] == "preprocessor"
        assert len(history[0]["changes"]) > 0


class TestIntegration:
    """整合測試：模擬真實的 pipeline 流程"""

    def test_full_pipeline_inference(self):
        """測試完整的 pipeline Schema 推論"""
        # 模擬 Loader 輸出的 Schema
        loader_schema = Schema(
            id="loader_output",
            name="Loaded Data",
            attributes={
                "id": Attribute(name="id", type="int64"),
                "age": Attribute(name="age", type="int64", enable_null=True),
                "category": Attribute(name="category", type="string"),
                "value": Attribute(name="value", type="float64", enable_null=True),
            },
        )

        # 模擬完整的 Preprocessor 配置
        pipeline_config = {
            "Preprocessor": {
                "missing": {
                    "age": "missing_mean",
                    "value": "missing_median",
                },
                "encoder": {
                    "category": "encoder_label",
                },
                "scaler": {
                    "age": "scaler_standard",
                    "value": "scaler_minmax",
                },
            }
        }

        # 推論
        inferencer = SchemaInferencer()
        schemas = inferencer.infer_pipeline_schemas(loader_schema, pipeline_config)

        # 驗證
        assert "Loader" in schemas
        assert "Preprocessor" in schemas

        preprocessor_schema = schemas["Preprocessor"]

        # id 應該保持不變
        assert preprocessor_schema.attributes["id"].type == "int64"

        # age: missing_mean + scaler_standard -> float64, no null
        assert preprocessor_schema.attributes["age"].type == "float64"
        assert preprocessor_schema.attributes["age"].enable_null == False

        # category: encoder_label -> int64
        assert preprocessor_schema.attributes["category"].type == "int64"

        # value: missing_median + scaler_minmax -> float64, no null
        assert preprocessor_schema.attributes["value"].type == "float64"
        assert preprocessor_schema.attributes["value"].enable_null == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
