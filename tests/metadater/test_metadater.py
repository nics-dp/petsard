"""
Metadater 完整測試套件
測試新架構的完整功能
"""

import numpy as np
import pandas as pd
import pytest

from petsard.metadater import AttributeMetadater, Metadater, SchemaMetadater
from petsard.metadater.metadata import Attribute
from petsard.metadater.stats import DatasetsStats, FieldStats, TableStats


class TestBasicWorkflow:
    """測試基本工作流程"""

    def test_create_metadata_from_data(self):
        """測試從資料建立 Metadata"""
        data = {
            "users": pd.DataFrame(
                {
                    "user_id": [1, 2, 3, 4, 5],
                    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                    "age": [25, 30, 35, 28, 32],
                    "email": [
                        "alice@test.com",
                        "bob@test.com",
                        "charlie@test.com",
                        "david@test.com",
                        "eve@test.com",
                    ],
                    "balance": [1000.50, 2500.75, 500.00, 3000.25, 1500.00],
                }
            ),
            "transactions": pd.DataFrame(
                {
                    "trans_id": [101, 102, 103, 104],
                    "user_id": [1, 2, 1, 3],
                    "amount": [50.00, 100.00, 75.50, 200.00],
                    "date": pd.to_datetime(
                        ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
                    ),
                }
            ),
        }

        metadata = Metadater.from_data(data)

        assert metadata.id == "inferred_metadata"
        assert len(metadata.schemas) == 2
        assert "users" in metadata.schemas
        assert "transactions" in metadata.schemas

        # 檢查 Schema 層級
        users_schema = metadata.schemas["users"]
        assert users_schema.id == "users"
        assert len(users_schema.attributes) == 5

        # 檢查 Attribute 層級
        age_attr = users_schema.attributes["age"]
        assert age_attr.name == "age"
        assert age_attr.type == "int64"

    def test_create_schema_from_dataframe(self):
        """測試從 DataFrame 建立 Schema"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Product A", "Product B", "Product C"],
                "price": [100.0, 200.0, 150.0],
                "in_stock": [True, False, True],
            }
        )

        schema = SchemaMetadater.from_data(df)

        assert schema.id == "inferred_schema"
        assert len(schema.attributes) == 4
        assert "id" in schema.attributes
        assert "price" in schema.attributes

        # 檢查型別推斷
        assert schema.attributes["id"].type == "int64"
        assert schema.attributes["price"].type == "float64"
        assert schema.attributes["in_stock"].type == "boolean"

    def test_create_attribute_from_series(self):
        """測試從 Series 建立 Attribute"""
        series = pd.Series([1, 2, 3, None, 5], name="test_column")

        attr = AttributeMetadater.from_data(series)

        assert attr.name == "test_column"
        assert attr.type == "float64"  # 因為有 None，pandas 會轉為 float
        assert attr.enable_null == True


class TestStatistics:
    """測試統計功能"""

    def test_field_statistics(self):
        """測試欄位統計"""
        series = pd.Series([1, 2, 3, 4, 5, None, 7, 8, 9, 10])

        attr = AttributeMetadater.from_data(series, enable_stats=True)

        assert attr.stats is not None
        assert isinstance(attr.stats, FieldStats)
        assert attr.stats.row_count == 10
        assert attr.stats.na_count == 1
        assert attr.stats.unique_count == 9
        assert attr.stats.mean == 5.5
        assert attr.stats.min == 1.0
        assert attr.stats.max == 10.0

    def test_table_statistics(self):
        """測試表格統計"""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "category": ["A", "B", "A", "C", None],
                "value": [10.5, 20.3, 15.7, None, 25.8],
                "active": [True, False, True, True, False],
            }
        )

        schema = SchemaMetadater.from_data(df, enable_stats=True)

        assert schema.stats is not None
        assert isinstance(schema.stats, TableStats)
        assert schema.stats.row_count == 5
        assert schema.stats.column_count == 4
        assert schema.stats.total_na_count == 2

        # 檢查欄位統計
        assert "id" in schema.stats.field_stats
        assert "category" in schema.stats.field_stats

    def test_datasets_statistics(self):
        """測試資料集統計"""
        data = {
            "table1": pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
            "table2": pd.DataFrame(
                {"x": [7, 8, 9, 10], "y": [11, 12, 13, 14], "z": [15, 16, 17, 18]}
            ),
        }

        metadata = Metadater.from_data(data, enable_stats=True)

        assert metadata.stats is not None
        assert isinstance(metadata.stats, DatasetsStats)
        assert metadata.stats.table_count == 2
        assert metadata.stats.total_row_count == 7  # 3 + 4
        assert metadata.stats.total_column_count == 5  # 2 + 3


class TestDiffFunctionality:
    """測試差異比較功能"""

    def test_schema_diff_missing_columns(self):
        """測試偵測缺失欄位"""
        original_df = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [10, 20, 30]}
        )
        schema = SchemaMetadater.from_data(original_df)

        # 缺少 'value' 欄位
        new_df = pd.DataFrame({"id": [4, 5, 6], "name": ["D", "E", "F"]})

        diff = SchemaMetadater.diff(schema, new_df)

        assert "value" in diff["missing_columns"]
        assert len(diff["extra_columns"]) == 0

    def test_schema_diff_extra_columns(self):
        """測試偵測額外欄位"""
        original_df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        schema = SchemaMetadater.from_data(original_df)

        # 多了 'extra' 欄位
        new_df = pd.DataFrame(
            {"id": [4, 5, 6], "name": ["D", "E", "F"], "extra": [100, 200, 300]}
        )

        diff = SchemaMetadater.diff(schema, new_df)

        assert "extra" in diff["extra_columns"]
        assert len(diff["missing_columns"]) == 0

    def test_schema_diff_type_changes(self):
        """測試偵測型別變更"""
        original_df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        schema = SchemaMetadater.from_data(original_df)

        # 'id' 從 int 變成 string
        new_df = pd.DataFrame({"id": ["1", "2", "3"], "value": [10, 20, 30]})

        diff = SchemaMetadater.diff(schema, new_df)

        assert "id" in diff["attribute_changes"]
        changes = diff["attribute_changes"]["id"]["changes"]
        assert any(c["field"] == "type" for c in changes)

    def test_metadata_diff_missing_tables(self):
        """測試偵測缺失表格"""
        original_data = {
            "users": pd.DataFrame({"id": [1, 2]}),
            "orders": pd.DataFrame({"id": [1, 2]}),
        }
        metadata = Metadater.from_data(original_data)

        # 缺少 'orders' 表
        new_data = {"users": pd.DataFrame({"id": [3, 4]})}

        diff = Metadater.diff(metadata, new_data)

        assert "orders" in diff["missing_tables"]
        assert len(diff["extra_tables"]) == 0


class TestAlignFunctionality:
    """測試資料對齊功能"""

    def test_align_add_missing_columns(self):
        """測試新增缺失欄位"""
        schema_config = {
            "id": "test_schema",
            "fields": {
                "id": {"name": "id", "type": "int64", "enable_null": False},
                "name": {"name": "name", "type": "string", "enable_null": False},
                "age": {"name": "age", "type": "int64", "enable_null": True},
            },
        }
        schema = SchemaMetadater.from_dict(schema_config)

        # 缺少 'age' 欄位
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})

        strategy = {"add_missing_columns": True}
        aligned_df = SchemaMetadater.align(schema, df, strategy)

        assert "age" in aligned_df.columns
        assert aligned_df["age"].isna().all()  # 應該都是 NA

    def test_align_remove_extra_columns(self):
        """測試移除額外欄位"""
        schema_config = {
            "id": "test_schema",
            "fields": {
                "id": {"name": "id", "type": "int64", "enable_null": False},
                "name": {"name": "name", "type": "string", "enable_null": False},
            },
        }
        schema = SchemaMetadater.from_dict(schema_config)

        # 有額外的 'extra' 欄位
        df = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["A", "B", "C"], "extra": [10, 20, 30]}
        )

        strategy = {"remove_extra_columns": True}
        aligned_df = SchemaMetadater.align(schema, df, strategy)

        assert "extra" not in aligned_df.columns
        assert list(aligned_df.columns) == ["id", "name"]

    def test_align_type_conversion(self):
        """測試型別轉換"""
        series = pd.Series(["1", "2", "3"], name="numbers")
        attr = Attribute(name="numbers", type="int64", enable_null=False)

        aligned_series = AttributeMetadater.align(attr, series)

        assert aligned_series.dtype == "int64"
        assert list(aligned_series) == [1, 2, 3]

    def test_align_reorder_columns(self):
        """測試重新排序欄位"""
        schema_config = {
            "id": "test_schema",
            "fields": {
                "id": {"name": "id", "type": "int64"},
                "name": {"name": "name", "type": "string"},
                "value": {"name": "value", "type": "float64"},
            },
        }
        schema = SchemaMetadater.from_dict(schema_config)

        # 欄位順序不同
        df = pd.DataFrame({"value": [10.5, 20.3], "id": [1, 2], "name": ["A", "B"]})

        strategy = {"reorder_columns": True}
        aligned_df = SchemaMetadater.align(schema, df, strategy)

        assert list(aligned_df.columns) == ["id", "name", "value"]


class TestYamlCompatibility:
    """測試 YAML 相容性"""

    def test_from_dict_with_fields(self):
        """測試從 YAML 格式字典建立（使用 fields）"""
        yaml_config = {
            "id": "test_metadata",
            "name": "Test Metadata",
            "schemas": {
                "users": {
                    "id": "users",
                    "name": "User Table",
                    "fields": {  # YAML 使用 fields
                        "user_id": {
                            "name": "user_id",
                            "type": "int64",
                            "enable_null": False,
                        },
                        "username": {
                            "name": "username",
                            "type": "string",
                            "enable_null": False,
                        },
                        "email": {
                            "name": "email",
                            "type": "string",
                            "logical_type": "email",
                            "enable_null": True,
                        },
                    },
                }
            },
        }

        metadata = Metadater.from_dict(yaml_config)

        assert metadata.id == "test_metadata"
        assert "users" in metadata.schemas

        users_schema = metadata.schemas["users"]
        assert "user_id" in users_schema.attributes
        assert "username" in users_schema.attributes
        assert "email" in users_schema.attributes

        # 檢查 logical_type
        email_attr = users_schema.attributes["email"]
        assert email_attr.logical_type == "email"

    def test_schema_from_dict(self):
        """測試 Schema 從字典建立"""
        config = {
            "id": "product_schema",
            "name": "Product Schema",
            "fields": {
                "product_id": {
                    "name": "product_id",
                    "type": "int64",
                    "enable_null": False,
                },
                "price": {
                    "name": "price",
                    "type": "float64",
                    "enable_null": False,
                    "default_value": 0.0,
                },
            },
        }

        schema = SchemaMetadater.from_dict(config)

        assert schema.id == "product_schema"
        assert schema.name == "Product Schema"
        assert len(schema.attributes) == 2

        price_attr = schema.attributes["price"]
        assert price_attr.default_value == 0.0


class TestSchemaOperations:
    """測試 Schema 操作"""

    def test_add_attribute_to_schema(self):
        """測試新增欄位到 Schema"""
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        schema = SchemaMetadater.from_data(df)

        # 新增欄位
        new_series = pd.Series([10, 20, 30], name="value")
        updated_schema = SchemaMetadater.add(schema, new_series)

        assert "value" in updated_schema.attributes
        assert len(updated_schema.attributes) == 3
        # 原始 schema 應該不變（immutable）
        assert "value" not in schema.attributes

    def test_remove_attribute_from_schema(self):
        """測試從 Schema 移除欄位"""
        df = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [10, 20, 30]}
        )
        schema = SchemaMetadater.from_data(df)

        # 移除欄位
        updated_schema = SchemaMetadater.remove(schema, "value")

        assert "value" not in updated_schema.attributes
        assert len(updated_schema.attributes) == 2
        # 原始 schema 應該不變
        assert "value" in schema.attributes

    def test_update_attribute_in_schema(self):
        """測試更新 Schema 中的欄位"""
        df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        schema = SchemaMetadater.from_data(df)

        # 更新欄位
        new_attr = Attribute(
            name="value", type="float64", enable_null=False, default_value=0.0
        )
        updated_schema = SchemaMetadater.update(schema, new_attr)

        assert updated_schema.attributes["value"].default_value == 0.0
        # 原始 schema 應該不變
        assert schema.attributes["value"].default_value is None

    def test_get_attribute_from_schema(self):
        """測試從 Schema 取得欄位"""
        df = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        schema = SchemaMetadater.from_data(df)

        attr = SchemaMetadater.get(schema, "name")
        assert attr is not None
        assert attr.name == "name"

        # 不存在的欄位應該拋出錯誤
        with pytest.raises(KeyError):
            SchemaMetadater.get(schema, "nonexistent")


class TestLogicalTypeInference:
    """測試邏輯型別推斷"""

    def test_infer_email_type(self):
        """測試推斷 email 型別"""
        series = pd.Series(
            ["alice@example.com", "bob@test.org", "charlie@company.net"], name="email"
        )

        attr = AttributeMetadater.from_data(series)

        assert attr.logical_type == "email"

    def test_infer_category_type(self):
        """測試推斷類別型別"""
        # 重複值多的資料
        series = pd.Series(["A", "B", "A", "C", "B", "A"] * 20, name="category")

        attr = AttributeMetadater.from_data(series)

        assert attr.logical_type == "category"

    def test_no_logical_type(self):
        """測試無特殊邏輯型別"""
        series = pd.Series(
            ["unique1", "unique2", "unique3", "unique4", "unique5"], name="text"
        )

        attr = AttributeMetadater.from_data(series)

        assert attr.logical_type is None


class TestEdgeCases:
    """測試邊界情況"""

    def test_empty_dataframe(self):
        """測試空 DataFrame"""
        df = pd.DataFrame()
        schema = SchemaMetadater.from_data(df)

        assert len(schema.attributes) == 0

    def test_dataframe_with_all_nulls(self):
        """測試全空值的 DataFrame"""
        df = pd.DataFrame(
            {"col1": [None, None, None], "col2": [np.nan, np.nan, np.nan]}
        )

        schema = SchemaMetadater.from_data(df)

        assert schema.attributes["col1"].enable_null == True
        assert schema.attributes["col2"].enable_null == True

    def test_mixed_type_series(self):
        """測試混合型別的 Series"""
        series = pd.Series([1, "two", 3.0, None], name="mixed")

        attr = AttributeMetadater.from_data(series)

        assert attr.type == "string"  # pandas 會轉為 object/string

    def test_large_dataset_stats(self):
        """測試大資料集的統計計算"""
        # 建立較大的測試資料
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "id": range(10000),
                "value": np.random.normal(100, 15, 10000),
                "category": np.random.choice(["A", "B", "C", "D"], 10000),
                "flag": np.random.choice([True, False], 10000),
            }
        )

        schema = SchemaMetadater.from_data(df, enable_stats=True)

        assert schema.stats.row_count == 10000
        assert schema.stats.column_count == 4

        # 檢查數值統計
        value_stats = schema.attributes["value"].stats
        assert 85 < value_stats.mean < 115  # 應該接近 100
        assert 10 < value_stats.std < 20  # 應該接近 15


class TestAttributeValidation:
    """測試 Attribute 驗證功能"""

    def test_validate_type_mismatch(self):
        """測試型別不符的驗證"""
        attr = Attribute(name="id", type="int64", enable_null=False)
        series = pd.Series(["a", "b", "c"], name="id")

        is_valid, errors = AttributeMetadater.validate(attr, series)

        assert not is_valid
        assert any("Type mismatch" in e for e in errors)

    def test_validate_null_violation(self):
        """測試空值違反的驗證"""
        attr = Attribute(name="required", type="int64", enable_null=False)
        series = pd.Series([1, 2, None, 4], name="required")

        is_valid, errors = AttributeMetadater.validate(attr, series)

        assert not is_valid
        assert any("Null values not allowed" in e for e in errors)

    def test_validate_constraints(self):
        """測試約束條件驗證"""
        attr = Attribute(
            name="age",
            type="int64",
            enable_null=False,
            constraints={"min": 0, "max": 120},
        )
        series = pd.Series([25, 30, 150, 40], name="age")  # 150 超過最大值

        is_valid, errors = AttributeMetadater.validate(attr, series)

        assert not is_valid
        assert any("above maximum" in e for e in errors)


class TestIntegration:
    """整合測試"""

    def test_complete_workflow(self):
        """測試完整工作流程"""
        # 1. 從資料建立
        original_data = {
            "customers": pd.DataFrame(
                {
                    "customer_id": [1, 2, 3],
                    "name": ["Alice", "Bob", "Charlie"],
                    "age": [25, 30, 35],
                    "email": ["alice@test.com", "bob@test.com", "charlie@test.com"],
                }
            ),
            "orders": pd.DataFrame(
                {
                    "order_id": [101, 102, 103],
                    "customer_id": [1, 2, 1],
                    "amount": [99.99, 149.99, 79.99],
                    "order_date": pd.to_datetime(
                        ["2024-01-01", "2024-01-02", "2024-01-03"]
                    ),
                }
            ),
        }

        metadata = Metadater.from_data(original_data, enable_stats=True)

        # 2. 檢查差異
        new_data = {
            "customers": pd.DataFrame(
                {
                    "customer_id": ["4", "5"],  # 型別改變
                    "name": ["David", "Eve"],
                    "phone": ["123-456", "789-012"],  # 新欄位，缺少 age 和 email
                }
            ),
            "orders": pd.DataFrame(
                {
                    "order_id": [104, 105],
                    "customer_id": [4, 5],
                    "amount": [199.99, 299.99],
                    "order_date": pd.to_datetime(["2024-01-04", "2024-01-05"]),
                }
            ),
        }

        diff = Metadater.diff(metadata, new_data)

        # 應該偵測到 customers 表的變化
        assert "customers" in diff["schema_changes"]
        customer_diff = diff["schema_changes"]["customers"]
        assert "age" in customer_diff["missing_columns"]
        assert "email" in customer_diff["missing_columns"]
        assert "phone" in customer_diff["extra_columns"]

        # 3. 對齊資料
        strategy = {
            "add_missing_columns": True,
            "remove_extra_columns": True,
            "reorder_columns": True,
        }
        aligned_data = Metadater.align(metadata, new_data, strategy)

        # 檢查對齊結果
        aligned_customers = aligned_data["customers"]
        assert "age" in aligned_customers.columns
        assert "email" in aligned_customers.columns
        assert "phone" not in aligned_customers.columns

        # 4. 更新 metadata
        customers_schema = metadata.schemas["customers"]
        new_attr = Attribute(
            name="vip_status", type="boolean", enable_null=False, default_value=False
        )
        updated_schema = SchemaMetadater.add(customers_schema, new_attr)

        assert "vip_status" in updated_schema.attributes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
