from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import yaml

from petsard.metadater.metadata import Attribute, Metadata, Schema


class AttributeMetadater:
    """單欄層操作類別 Single column operations

    所有方法都在這裡實作，Attribute 只是設定檔
    All methods are implemented here, Attribute is just configuration
    """

    @classmethod
    def from_data(cls, data: pd.Series) -> Attribute:
        """從 Series 建立 Attribute 設定檔 Create Attribute configuration from Series"""
        # 推斷資料類型 Infer data type
        dtype_str = str(data.dtype)

        # 基本類型映射
        type_mapping = {
            "int8": "int8",
            "int16": "int16",
            "int32": "int32",
            "int64": "int64",
            "float32": "float32",
            "float64": "float64",
            "bool": "boolean",
            "object": "string",
            "datetime64[ns]": "datetime64",
            "category": "category",
        }

        data_type = type_mapping.get(dtype_str, "string")

        # 推斷邏輯類型 Infer logical type
        logical_type = cls._infer_logical_type(data)

        return Attribute(
            name=data.name,
            type=data_type,
            logical_type=logical_type,
            enable_null=data.isnull().any(),
        )

    @classmethod
    def _infer_logical_type(cls, data: pd.Series) -> str | None:
        """推斷邏輯類型"""
        # 簡單的邏輯類型推斷
        if data.dtype == "object":
            sample = data.dropna().head(100)

            # 檢查是否為 email
            if sample.str.contains(r"^[^@]+@[^@]+\.[^@]+$", regex=True).all():
                return "email"

            # 檢查是否為分類資料
            if len(data.unique()) / len(data) < 0.05:  # 唯一值比例小於 5%
                return "category"

        return None

    @classmethod
    def from_metadata(cls, attribute: Attribute) -> Attribute:
        """複製 Attribute 設定檔"""
        return Attribute(**attribute.__dict__)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Attribute:
        """從字典建立 Attribute（v2.0 理想格式）"""
        return Attribute(**config)

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Attribute:
        """從現有格式建立 Attribute（v1.0 相容性）

        此方法通常不會直接使用，因為 v1 格式的欄位
        會在 Schema 層級被轉換
        """
        return cls.from_dict(config)

    @classmethod
    def diff(cls, attribute: Attribute, data: pd.Series) -> dict[str, Any]:
        """比較 Attribute 與 Series 的差異"""
        diff_result = {"name": attribute.name, "changes": []}

        # 檢查資料類型差異
        current_type = str(data.dtype)
        if attribute.type and current_type != attribute.type:
            diff_result["changes"].append(
                {"field": "type", "expected": attribute.type, "actual": current_type}
            )

        # 檢查空值差異
        has_null = data.isnull().any()
        if has_null and not attribute.enable_null:
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
        """根據 Attribute 對齊 Series"""
        aligned = data.copy()

        # 處理空值
        if attribute.na_values:
            aligned = aligned.replace(attribute.na_values, pd.NA)

        # 型別轉換
        if attribute.type:
            try:
                if attribute.type == "int64" and aligned.isnull().any():
                    aligned = aligned.astype("Int64")  # Nullable integer
                elif attribute.type == "boolean":
                    aligned = aligned.astype("boolean")
                elif attribute.type == "category":
                    aligned = aligned.astype("category")
                elif attribute.type.startswith("datetime"):
                    aligned = pd.to_datetime(aligned, errors=attribute.cast_errors)
                else:
                    aligned = aligned.astype(attribute.type)
            except Exception as e:
                if attribute.cast_errors == "raise":
                    raise e
                # coerce: 保持原始資料

        # 應用預設值
        if attribute.default_value is not None:
            aligned = aligned.fillna(attribute.default_value)

        return aligned

    @classmethod
    def validate(cls, attribute: Attribute, data: pd.Series) -> tuple[bool, list[str]]:
        """驗證 Series 是否符合 Attribute 定義"""
        errors = []

        # 型別驗證
        if attribute.type and str(data.dtype) != attribute.type:
            errors.append(f"Type mismatch: expected {attribute.type}, got {data.dtype}")

        # 空值驗證
        if not attribute.enable_null and data.isnull().any():
            errors.append(f"Null values not allowed, found {data.isnull().sum()}")

        # 約束驗證
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
        """根據 Attribute 定義轉換資料類型"""
        return cls.align(attribute, data)


class SchemaMetadater:
    """單表層操作類別 Single table operations

    所有方法都在這裡實作，Schema 只是設定檔
    All methods are implemented here, Schema is just configuration
    """

    @classmethod
    def from_data(cls, data: pd.DataFrame) -> Schema:
        """從 DataFrame 建立 Schema 設定檔"""
        attributes = {}

        for col in data.columns:
            attributes[col] = AttributeMetadater.from_data(data[col])

        return Schema(
            id="inferred_schema", name="Inferred Schema", attributes=attributes
        )

    @classmethod
    def from_metadata(cls, schema: Schema) -> Schema:
        """複製 Schema 設定檔"""
        # 深度複製 attributes
        new_attributes = {}
        for name, attr in schema.attributes.items():
            new_attributes[name] = AttributeMetadater.from_metadata(attr)

        return Schema(**{**schema.__dict__, "attributes": new_attributes})

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Schema:
        """從現有 YAML 格式建立 Schema（v1.0 相容性）"""
        # 提取全域參數
        global_params = {
            "optimize_dtypes": config.get("optimize_dtypes", "selective"),
            "nullable_int": config.get("nullable_int", "force"),
            "leading_zeros": config.get("leading_zeros", "never"),
            "infer_logical_types": config.get("infer_logical_types", "selective"),
            "sample_size": config.get("sample_size"),
        }

        # 轉換 fields 為 attributes
        attributes = {}
        if "fields" in config:
            for field_name, field_config in config["fields"].items():
                # 轉換 v1 欄位格式為 v2 Attribute 格式
                attr_config = cls._convert_field_to_attribute(
                    field_name, field_config, global_params
                )
                attributes[field_name] = AttributeMetadater.from_dict(attr_config)

        # 建立 v2 Schema 格式
        return Schema(
            id=config.get("schema_id", "default"),
            name=config.get("name", "Default Schema"),
            description=config.get("description", ""),
            attributes=attributes,
            primary_key=config.get("primary_key", []),
            foreign_keys=config.get("foreign_keys", {}),
        )

    @staticmethod
    def _convert_field_to_attribute(
        name: str, field: dict[str, Any], global_params: dict[str, Any]
    ) -> dict[str, Any]:
        """將 v1 field 格式轉換為 v2 attribute 格式"""
        # 型別映射
        type_mapping = {
            "int": "int64",
            "float": "float64",
            "str": "string",
            "bool": "boolean",
            "datetime": "datetime64",
        }

        # 建立 attribute 設定
        attr = {
            "name": name,
            "type": type_mapping.get(field.get("type", "string"), "string"),
            "logical_type": field.get("logical_type", ""),
            "enable_null": True if field.get("na_values") else False,
        }

        # 處理特殊屬性
        if field.get("category_method") == "force":
            attr["logical_type"] = "category"

        if "precision" in field:
            attr["type_attr"] = {"precision": field["precision"]}

        if "datetime_format" in field:
            attr["type_attr"] = {"format": field["datetime_format"]}

        if "leading_zeros" in field:
            leading = field["leading_zeros"]
            if leading.startswith("leading_"):
                width = int(leading.split("_")[1])
                attr["type_attr"] = {"width": width}

        return attr

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Schema:
        """從字典建立 Schema（v2.0 理想格式）"""
        # 將 fields 對應到內部的 attributes
        if "fields" in config:
            attributes = {}
            for field_name, field_config in config["fields"].items():
                attributes[field_name] = AttributeMetadater.from_dict(field_config)
            config["attributes"] = attributes
            del config["fields"]  # 移除 fields，改用 attributes

        return Schema(**config)

    @classmethod
    def from_yaml(cls, filepath: str) -> Schema:
        """智慧載入 YAML，自動判斷版本"""
        with open(filepath) as f:
            config = yaml.safe_load(f)

        # 根據其他特徵判斷版本
        has_global_params = any(
            k in config
            for k in ["optimize_dtypes", "nullable_int", "infer_logical_types"]
        )

        if has_global_params:
            # v1.0 格式（有全域參數）
            return cls.from_dict_v1(config)
        else:
            # v2.0 格式（簡潔格式）
            return cls.from_dict(config)

    @classmethod
    def get(cls, schema: Schema, name: str) -> Attribute:
        """從 Schema 取得 Attribute"""
        if name not in schema.attributes:
            raise KeyError(f"Attribute '{name}' not found in schema '{schema.id}'")
        return schema.attributes[name]

    @classmethod
    def add(cls, schema: Schema, attribute: Attribute | pd.Series) -> Schema:
        """新增 Attribute 到 Schema"""
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
        """更新 Schema 中的 Attribute"""
        return cls.add(schema, attribute)  # add 會覆蓋同名的 attribute

    @classmethod
    def remove(cls, schema: Schema, name: str) -> Schema:
        """從 Schema 移除 Attribute"""
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
        """比較 Schema 與 DataFrame 的差異"""
        diff_result = {
            "schema_id": schema.id,
            "missing_columns": [],
            "extra_columns": [],
            "attribute_changes": {},
        }

        schema_cols = set(schema.attributes.keys())
        data_cols = set(data.columns)

        # 找出缺失和額外的欄位
        diff_result["missing_columns"] = list(schema_cols - data_cols)
        diff_result["extra_columns"] = list(data_cols - schema_cols)

        # 比較共同欄位的差異
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
        """根據 Schema 對齊 DataFrame"""
        strategy = strategy or {}
        aligned_df = data.copy()

        # 處理缺失的欄位
        for col_name, attribute in schema.attributes.items():
            if col_name not in aligned_df.columns:
                # 根據策略處理缺失欄位
                if strategy.get("add_missing_columns", True):
                    # 新增缺失欄位並填充預設值
                    if attribute.default_value is not None:
                        aligned_df[col_name] = attribute.default_value
                    else:
                        aligned_df[col_name] = pd.NA
            else:
                # 對齊現有欄位
                aligned_df[col_name] = AttributeMetadater.align(
                    attribute, aligned_df[col_name], strategy
                )

        # 處理額外的欄位
        if strategy.get("remove_extra_columns", False):
            extra_cols = set(aligned_df.columns) - set(schema.attributes.keys())
            aligned_df = aligned_df.drop(columns=list(extra_cols))

        # 重新排序欄位
        if strategy.get("reorder_columns", True):
            col_order = [
                col for col in schema.attributes.keys() if col in aligned_df.columns
            ]
            # 保留未在 schema 中的欄位（如果沒有移除）
            extra_cols = [col for col in aligned_df.columns if col not in col_order]
            aligned_df = aligned_df[col_order + extra_cols]

        return aligned_df

    @classmethod
    def to_sdv(cls, schema: Schema) -> dict[str, Any]:
        """轉換 Schema 為 SDV (Synthetic Data Vault) 格式"""
        sdv_metadata = {"columns": {}, "METADATA_SPEC_VERSION": "SINGLE_TABLE_V1"}

        for attr_name, attribute in schema.attributes.items():
            sdtype = cls._map_to_sdv_type(attribute)
            sdv_metadata["columns"][attr_name] = {"sdtype": sdtype}

        return sdv_metadata

    @staticmethod
    def _map_to_sdv_type(attribute: Attribute) -> str:
        """將 PETsARD Attribute 對應到 SDV sdtype"""
        # 根據邏輯類型優先判斷
        if attribute.logical_type:
            logical = attribute.logical_type.lower()
            if logical in ["email", "phone"]:
                return "pii"
            elif logical == "category":
                return "categorical"
            elif logical in ["datetime", "date", "time"]:
                return "datetime"

        # 根據資料類型判斷
        if attribute.type:
            if "int" in attribute.type or "float" in attribute.type:
                return "numerical"
            elif "bool" in attribute.type:
                return "boolean"
            elif "datetime" in attribute.type:
                return "datetime"

        # 預設為分類
        return "categorical"

    @classmethod
    def from_sdv(
        cls, sdv_dict: dict[str, Any], schema_id: str = "imported_from_sdv"
    ) -> Schema:
        """從 SDV 格式建立 Schema"""
        attributes = {}

        for column_name, column_info in sdv_dict.get("columns", {}).items():
            sdtype = column_info.get("sdtype", "categorical")

            # 對應回 PETsARD 類型
            if sdtype == "numerical":
                data_type = "float64"
                logical_type = None
            elif sdtype == "datetime":
                data_type = "datetime64"
                logical_type = "datetime"
            elif sdtype == "boolean":
                data_type = "boolean"
                logical_type = None
            elif sdtype == "pii":
                data_type = "string"
                logical_type = "pii"
            else:  # categorical 或其他
                data_type = "string"
                logical_type = "category"

            attributes[column_name] = Attribute(
                name=column_name,
                type=data_type,
                logical_type=logical_type,
                enable_null=True,  # SDV 預設允許 null
            )

        return Schema(id=schema_id, name="Imported from SDV", attributes=attributes)


class Metadater:
    """多表層操作類別 Multiple tables operations

    所有方法都在這裡實作，Metadata 只是設定檔
    All methods are implemented here, Metadata is just configuration
    """

    @classmethod
    def from_data(cls, data: dict[str, pd.DataFrame]) -> Metadata:
        """從資料建立 Metadata 設定檔"""
        schemas = {}

        for table_name, df in data.items():
            schema = SchemaMetadater.from_data(df)
            # 更新 schema id 為表名
            schema = Schema(**{**schema.__dict__, "id": table_name, "name": table_name})
            schemas[table_name] = schema

        return Metadata(
            id="inferred_metadata", name="Inferred Metadata", schemas=schemas
        )

    @classmethod
    def from_metadata(cls, metadata: Metadata) -> Metadata:
        """複製 Metadata 設定檔"""
        # 深度複製 schemas
        new_schemas = {}
        for name, schema in metadata.schemas.items():
            new_schemas[name] = SchemaMetadater.from_metadata(schema)

        return Metadata(**{**metadata.__dict__, "schemas": new_schemas})

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Metadata:
        """從現有 YAML 格式建立 Metadata（v1.0 相容性）

        處理現有的單一 Schema 格式
        """
        # 將 v1 格式轉換為 v2 格式
        schema = SchemaMetadater.from_dict_v1(config)

        return Metadata(
            id=config.get("metadata_id", "default"),
            name=config.get("name", "Default Metadata"),
            description=config.get("description", ""),
            schemas={"default": schema},
        )

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Metadata:
        """從字典建立 Metadata（v2.0 理想格式）"""
        # 遞迴處理 schemas
        if "schemas" in config:
            schemas = {}
            for schema_id, schema_config in config["schemas"].items():
                schemas[schema_id] = SchemaMetadater.from_dict(schema_config)
            config["schemas"] = schemas

        return Metadata(**config)

    @classmethod
    def get(cls, metadata: Metadata, name: str) -> Schema:
        """從 Metadata 取得 Schema"""
        if name not in metadata.schemas:
            raise KeyError(f"Schema '{name}' not found in metadata '{metadata.id}'")
        return metadata.schemas[name]

    @classmethod
    def add(cls, metadata: Metadata, schema: Schema | pd.DataFrame) -> Metadata:
        """新增 Schema 到 Metadata"""
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
        """更新 Metadata 中的 Schema"""
        return cls.add(metadata, schema)  # add 會覆蓋同名的 schema

    @classmethod
    def remove(cls, metadata: Metadata, name: str) -> Metadata:
        """從 Metadata 移除 Schema"""
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
        """比較 Metadata 與資料的差異"""
        diff_result = {
            "metadata_id": metadata.id,
            "missing_tables": [],
            "extra_tables": [],
            "schema_changes": {},
        }

        metadata_tables = set(metadata.schemas.keys())
        data_tables = set(data.keys())

        # 找出缺失和額外的表
        diff_result["missing_tables"] = list(metadata_tables - data_tables)
        diff_result["extra_tables"] = list(data_tables - metadata_tables)

        # 比較共同表的差異
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
        """根據 Metadata 對齊資料"""
        strategy = strategy or {}
        aligned = {}

        for schema_id, schema in metadata.schemas.items():
            if schema_id in data:
                # 呼叫下層 SchemaMetadater
                aligned_df = SchemaMetadater.align(schema, data[schema_id], strategy)
                aligned[schema_id] = aligned_df
            elif strategy.get("add_missing_tables", False):
                # 建立空的 DataFrame
                columns = list(schema.attributes.keys())
                aligned[schema_id] = pd.DataFrame(columns=columns)

        return aligned
