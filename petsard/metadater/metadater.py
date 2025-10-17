from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import yaml

from petsard.metadater.metadata import Attribute, Metadata, Schema
from petsard.metadater.stats import DatasetsStats, FieldStats, TableStats


class AttributeMetadater:
    """單欄層操作類別 Single column operations

    所有方法都在這裡實作，Attribute 只是設定檔
    All methods are implemented here, Attribute is just configuration
    """

    @classmethod
    def from_data(
        cls, data: pd.Series, enable_stats: bool = True, **kwargs
    ) -> Attribute:
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
        }

        data_type = type_mapping.get(dtype_str, "string")

        # 推斷邏輯類型 Infer logical type
        logical_type = cls._infer_logical_type(data)

        # 推斷是否為分類資料 Infer if categorical
        is_category = dtype_str == "category" or (
            data.dtype == "object" and len(data.unique()) / len(data) < 0.05
            if len(data) > 0
            else False
        )

        # 計算統計資訊
        stats = None
        if enable_stats:
            stats = cls._calculate_field_stats(data, logical_type)

        return Attribute(
            name=data.name,
            type=data_type,
            logical_type=logical_type,
            category=is_category,
            enable_null=data.isnull().any(),
            enable_stats=enable_stats,
            stats=stats,
        )

    @classmethod
    def _infer_logical_type(cls, data: pd.Series) -> str | None:
        """推斷邏輯類型"""
        # 簡單的邏輯類型推斷
        if data.dtype == "object":
            sample = data.dropna().head(100)

            # 確保樣本不為空
            if len(sample) == 0:
                return None

            # 檢查是否全部為字串類型
            try:
                # 先確認所有值都是字串
                all_strings = all(isinstance(x, str) for x in sample)

                if all_strings:
                    # 檢查是否為 email
                    if sample.str.contains(
                        r"^[^@]+@[^@]+\.[^@]+$", regex=True, na=False
                    ).all():
                        return "email"
            except (AttributeError, TypeError):
                # 如果有任何混合類型，跳過 email 檢查
                pass

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
        from petsard.utils import safe_round

        aligned = data.copy()

        # 處理空值
        if attribute.na_values:
            aligned = aligned.replace(attribute.na_values, pd.NA)

        # 型別轉換
        if attribute.type:
            try:
                # CRITICAL FIX: Handle both "integer" (schema format) and "int64" (pandas dtype format)
                # 關鍵修復：處理 "integer"（schema 格式）和 "int64"（pandas dtype 格式）
                if attribute.type in ("integer", "int64", "int32", "int16", "int8"):
                    # For integer types, always use nullable Int64 to handle potential NaN values
                    # 對於整數類型，始終使用 nullable Int64 來處理潛在的 NaN 值
                    if aligned.isnull().any():
                        aligned = aligned.astype("Int64")
                    else:
                        # No nulls, can use regular int64
                        # 沒有空值，可以使用普通的 int64
                        try:
                            aligned = aligned.astype("int64")
                        except (ValueError, TypeError):
                            # If conversion fails, use Int64 anyway
                            # 如果轉換失敗，仍然使用 Int64
                            aligned = aligned.astype("Int64")
                elif attribute.type == "boolean":
                    aligned = aligned.astype("boolean")
                elif attribute.type.startswith("datetime"):
                    aligned = pd.to_datetime(aligned, errors=attribute.cast_errors)
                else:
                    aligned = aligned.astype(attribute.type)
            except Exception:
                if attribute.cast_errors == "raise":
                    raise  # 保留原始 traceback
                # coerce: 保持原始資料

        # 處理數值精度（如果有設定）
        if attribute.type_attr and "precision" in attribute.type_attr:
            precision = attribute.type_attr["precision"]
            if attribute.type and (
                "float" in attribute.type or "int" in attribute.type
            ):
                # 對數值欄位應用精度
                aligned = aligned.apply(lambda x: safe_round(x, precision))

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

    @classmethod
    def _calculate_field_stats(
        cls, series: pd.Series, logical_type: str | None = None
    ) -> FieldStats:
        """計算欄位統計資訊

        統計計算邏輯在 Metadater 類別中實現
        """
        import pandas as pd

        row_count = len(series)
        na_count = series.isna().sum()
        na_percentage = (na_count / row_count) if row_count > 0 else 0.0
        unique_count = series.nunique()

        # 數值統計
        mean = None
        std = None
        min_val = None
        max_val = None
        median = None
        q1 = None
        q3 = None

        if pd.api.types.is_numeric_dtype(series) and not series.empty:
            non_na_series = series.dropna()
            if len(non_na_series) > 0:
                mean = float(non_na_series.mean())
                std = float(non_na_series.std())
                min_val = float(non_na_series.min())
                max_val = float(non_na_series.max())
                median = float(non_na_series.median())
                q1 = float(non_na_series.quantile(0.25))
                q3 = float(non_na_series.quantile(0.75))

        # 類別統計
        mode = None
        mode_frequency = None
        category_distribution = None

        if not series.empty:
            mode_series = series.mode()
            if not mode_series.empty:
                mode = mode_series.iloc[0]
                mode_frequency = int((series == mode).sum())

            # 如果是類別型態，計算分佈
            if logical_type in ["string", "categorical", "boolean"]:
                value_counts = series.value_counts()
                # 限制最多記錄前 20 個類別
                top_categories = value_counts.head(20)
                category_distribution = {
                    str(k): int(v) for k, v in top_categories.items()
                }

        return FieldStats(
            row_count=row_count,
            na_count=int(na_count),
            na_percentage=round(na_percentage, 4),
            unique_count=int(unique_count),
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


class SchemaMetadater:
    """單表層操作類別 Single table operations

    所有方法都在這裡實作，Schema 只是設定檔
    All methods are implemented here, Schema is just configuration
    """

    @classmethod
    def from_data(
        cls, data: pd.DataFrame, enable_stats: bool = False, **kwargs
    ) -> Schema:
        """從 DataFrame 建立 Schema 設定檔"""
        attributes = {}

        for col in data.columns:
            attributes[col] = AttributeMetadater.from_data(
                data[col], enable_stats=enable_stats
            )

        # 計算表格統計
        stats = None
        if enable_stats:
            # 收集 field stats
            field_stats = {}
            for col_name, attr in attributes.items():
                if attr.stats:
                    field_stats[col_name] = attr.stats
            # 計算表格統計
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
        """複製 Schema 設定檔"""
        # 深度複製 attributes
        new_attributes = {}
        for name, attr in schema.attributes.items():
            new_attributes[name] = AttributeMetadater.from_metadata(attr)

        return Schema(**{**schema.__dict__, "attributes": new_attributes})

    @classmethod
    def from_dict_v1(cls, config: dict[str, Any]) -> Schema:
        """從現有 YAML 格式建立 Schema（v1.0 相容性）"""
        # 轉換 fields 為 attributes
        attributes = {}
        if "fields" in config:
            for field_name, field_config in config["fields"].items():
                # 轉換 v1 欄位格式為 v2 Attribute 格式
                attr_config = cls._convert_field_to_attribute(field_name, field_config)
                attributes[field_name] = AttributeMetadater.from_dict(attr_config)

        # 建立 v2 Schema 格式，支援 compute_stats 和 title
        return Schema(
            id=config.get("schema_id", "default"),
            name=config.get(
                "title", config.get("name", "Default Schema")
            ),  # 優先使用 title
            description=config.get("description", ""),
            attributes=attributes,
            primary_key=config.get("primary_key", []),
            foreign_keys=config.get("foreign_keys", {}),
            enable_stats=config.get("compute_stats", True),  # 支援 compute_stats
            sample_size=config.get("sample_size"),  # 支援 sample_size
        )

    @staticmethod
    def _convert_field_to_attribute(name: str, field: dict[str, Any]) -> dict[str, Any]:
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
            attr["category"] = True

        # 合併 type_attr
        type_attr = {}

        if "precision" in field:
            type_attr["precision"] = field["precision"]

        if "datetime_format" in field:
            type_attr["format"] = field["datetime_format"]

        if "leading_zeros" in field:
            leading = field["leading_zeros"]
            if leading.startswith("leading_"):
                width = int(leading.split("_")[1])
                type_attr["width"] = width

        if type_attr:
            attr["type_attr"] = type_attr

        return attr

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Schema:
        """從字典建立 Schema（v2.0 理想格式）"""
        # 處理 attributes 或 fields
        if "attributes" in config:
            # 將 attributes 中的 dict 轉換成 Attribute 物件
            attributes = {}
            for attr_name, attr_config in config["attributes"].items():
                if isinstance(attr_config, dict):
                    # 確保有 name 欄位
                    if "name" not in attr_config:
                        attr_config["name"] = attr_name
                    attributes[attr_name] = AttributeMetadater.from_dict(attr_config)
                else:
                    # 如果已經是 Attribute 物件，直接使用
                    attributes[attr_name] = attr_config
            config["attributes"] = attributes
        elif "fields" in config:
            # 向後相容：將 fields 對應到內部的 attributes
            attributes = {}
            for field_name, field_config in config["fields"].items():
                attributes[field_name] = AttributeMetadater.from_dict(field_config)
            config["attributes"] = attributes
            del config["fields"]  # 移除 fields，改用 attributes

        return Schema(**config)

    @classmethod
    def from_yaml(cls, filepath: str) -> Schema:
        """從 YAML 檔案載入 Schema"""
        with open(filepath) as f:
            config = yaml.safe_load(f)

        # 直接使用 from_dict，它會處理 fields 和 attributes 兩種格式
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
    def _calculate_table_stats(
        cls, df: pd.DataFrame, field_stats: dict[str, FieldStats]
    ) -> TableStats:
        """計算資料表統計資訊

        統計計算邏輯在 SchemaMetadater 類別中實現
        """
        row_count = len(df)
        column_count = len(df.columns)

        # 從欄位統計計算總 NA 數量
        total_na_count = sum(stats.na_count for stats in field_stats.values())
        total_cells = row_count * column_count
        total_na_percentage = (total_na_count / total_cells) if total_cells > 0 else 0.0

        # 記憶體使用
        memory_usage_bytes = int(df.memory_usage(deep=True).sum())

        # 重複資料檢查
        duplicated_rows = int(df.duplicated().sum())

        # 檢查完全相同的欄位
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
            duplicated_columns=duplicated_columns[:10],  # 限制最多記錄 10 對
            field_stats=field_stats,
        )


class Metadater:
    """多表層操作類別 Multiple tables operations

    所有方法都在這裡實作，Metadata 只是設定檔
    All methods are implemented here, Metadata is just configuration
    """

    @classmethod
    def from_data(
        cls, data: dict[str, pd.DataFrame], enable_stats: bool = False, **kwargs
    ) -> Metadata:
        """從資料建立 Metadata，包含統計資訊

        Args:
            data: 資料表字典
            enable_stats: 是否計算統計資訊
            **kwargs: 其他 Metadata 參數

        Returns:
            Metadata: 包含統計資訊的 Metadata
        """

        # 建立 schemas
        schemas = {}
        for name, df in data.items():
            # 直接傳遞參數給 SchemaMetadater.from_data
            schema = SchemaMetadater.from_data(
                df, enable_stats=enable_stats, id=name, name=name
            )
            schemas[name] = schema

        # 計算資料集統計
        stats = None
        if enable_stats:
            # 收集已經計算好的表格統計
            table_stats = {
                name: schema.stats for name, schema in schemas.items() if schema.stats
            }
            stats = cls._calculate_datasets_stats(table_stats)

        # 覆寫預設值
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

    @classmethod
    def _calculate_datasets_stats(
        cls, table_stats: dict[str, TableStats]
    ) -> DatasetsStats:
        """計算資料集統計資訊

        統計計算邏輯在 Metadater 類別中實現
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
