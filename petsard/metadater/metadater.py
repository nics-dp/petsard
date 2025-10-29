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
        cls,
        data: pd.Series,
        enable_stats: bool = True,
        base_attribute: Attribute = None,
        **kwargs,
    ) -> Attribute:
        """從 Series 建立 Attribute 設定檔 Create Attribute configuration from Series

        Args:
            data: 資料 Series
            enable_stats: 是否計算統計資訊
            base_attribute: 基礎 Attribute（如果有），如果該 attribute 有 precision 定義則不推斷
            **kwargs: 其他參數
        """
        # 有 base_attribute 時：完全繼承屬性，不從資料重新推斷
        # 沒有 base_attribute 時：從資料推斷（首次建立 schema）

        if base_attribute:
            # === 有 base_attribute：直接繼承，保持 schema 定義的一致性 ===
            data_type = base_attribute.type
            logical_type = base_attribute.logical_type

            # 複製 type_attr
            type_attr = {}
            if base_attribute.type_attr:
                # 完整繼承 type_attr（包含 category, nullable, precision 等）
                type_attr = base_attribute.type_attr.copy()
            else:
                # base_attribute 沒有 type_attr，使用預設值
                type_attr["category"] = False
                type_attr["nullable"] = True

        else:
            # === 沒有 base_attribute：從資料推斷（首次建立 schema） ===
            dtype_str = str(data.dtype)

            # 簡化類型映射：只保留 int, float, str, date, datetime
            type_mapping = {
                "int8": "int",
                "int16": "int",
                "int32": "int",
                "int64": "int",
                "float32": "float",
                "float64": "float",
                "bool": "str",  # boolean 當作字串類別處理
                "object": "str",
                "datetime64[ns]": "datetime",
            }

            data_type = type_mapping.get(dtype_str, "str")

            # 推斷邏輯類型 Infer logical type
            logical_type = cls._infer_logical_type(data)

            # 準備 type_attr
            type_attr = {}

            # 推斷是否為分類資料
            is_category = dtype_str == "category" or (
                data.dtype == "object" and len(data.unique()) / len(data) < 0.05
                if len(data) > 0
                else False
            )
            type_attr["category"] = is_category

            # 推斷 nullable
            type_attr["nullable"] = bool(data.isnull().any())

            # 計算數值欄位的精度（只在首次推斷且為 float 時）
            if data_type == "float":
                precision = cls._infer_precision(data)
                if precision is not None:
                    type_attr["precision"] = precision

        # 計算統計資訊（無論有無 base_attribute 都要計算）
        stats = None
        if enable_stats:
            stats = cls._calculate_field_stats(
                data, data_type, type_attr.get("category", False), logical_type
            )

        return Attribute(
            name=data.name,
            type=data_type,
            type_attr=type_attr if type_attr else None,
            logical_type=logical_type,
            enable_stats=enable_stats,
            stats=stats,
        )

    @classmethod
    def _infer_precision(cls, data: pd.Series) -> int | None:
        """推斷數值欄位的精度（小數位數）

        此方法分析該欄位中所有數值，找出最大的小數位數作為精度。

        Args:
            data: 數值型 Series

        Returns:
            精度（小數位數），如果無法推斷則返回 None
        """
        from decimal import Decimal

        import numpy as np

        # 只處理浮點數類型
        if not pd.api.types.is_float_dtype(data):
            return None

        # 移除 NaN 值
        non_na_data = data.dropna()
        if len(non_na_data) == 0:
            return None

        # 計算每個值的小數位數
        precisions = []
        for value in non_na_data:
            if not np.isfinite(value):  # 跳過 inf 和 -inf
                continue

            # 使用 Decimal 進行精確的小數位數檢測
            # 這樣可以正確處理浮點數的精度，避免字串格式化的限制
            try:
                # 將浮點數轉為 Decimal 以保留完整精度
                decimal_value = Decimal(str(value))
                # 標準化以移除尾隨零
                normalized = decimal_value.normalize()
                # 計算小數位數
                sign, digits, exponent = normalized.as_tuple()
                if exponent < 0:
                    precisions.append(abs(exponent))
                else:
                    precisions.append(0)
            except (ValueError, OverflowError):
                # 如果轉換失敗，跳過該值
                continue

        if not precisions:
            return None

        # 返回該欄位中最大的精度
        return max(precisions)

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
        """根據 Attribute 對齊 Series

        Args:
            attribute: 欄位屬性定義
            data: 原始資料
            strategy: 對齊策略（預留）

        Returns:
            對齊後的 Series

        Raises:
            ValueError: 當型別轉換失敗且 cast_errors='raise' 時
        """
        from petsard.utils import safe_round

        aligned = data.copy()

        # 處理空值
        if attribute.na_values:
            aligned = aligned.replace(attribute.na_values, pd.NA)

        # 型別轉換（依據簡化後的類型系統）
        if attribute.type:
            try:
                if attribute.type == "int":
                    # 整數類型：根據 nullable 決定使用 Int64 或優化的 int 類型
                    nullable = (
                        attribute.type_attr.get("nullable", True)
                        if attribute.type_attr
                        else True
                    )

                    if aligned.isnull().any() or nullable:
                        # 有空值或允許空值：使用 nullable Int64
                        aligned = aligned.astype("Int64")
                    else:
                        # 無空值：根據 enable_optimize_type 決定是否優化
                        if attribute.enable_optimize_type:
                            aligned = cls._optimize_int_dtype(aligned)
                        else:
                            aligned = aligned.astype("int64")

                elif attribute.type == "float":
                    # 浮點數類型：根據 enable_optimize_type 決定是否優化
                    if attribute.enable_optimize_type:
                        aligned = cls._optimize_float_dtype(
                            aligned, attribute.type_attr
                        )
                    else:
                        aligned = aligned.astype("float64")

                elif attribute.type == "str":
                    # 特殊處理：如果資料已經是數值類型，保持數值類型
                    # 這避免將 Preprocessor 編碼的數值資料轉回字串
                    if not pd.api.types.is_numeric_dtype(aligned):
                        aligned = aligned.astype("string")
                    # 如果已經是數值類型，保持不變

                elif attribute.type in ["date", "datetime"]:
                    aligned = pd.to_datetime(aligned, errors=attribute.cast_errors)
                else:
                    # 其他類型保持不變或嘗試轉換
                    aligned = aligned.astype(attribute.type)

            except Exception as e:
                if attribute.cast_errors == "raise":
                    raise ValueError(
                        f"型別轉換失敗：欄位 '{attribute.name}' "
                        f"無法從 {data.dtype} 轉換為 {attribute.type}\n"
                        f"錯誤: {str(e)}"
                    ) from e
                # coerce: 保持原始資料

        # 處理數值精度（如果有設定）
        if attribute.type_attr and "precision" in attribute.type_attr:
            precision = attribute.type_attr["precision"]
            # 檢查實際資料類型是否為數值類型，而不只是檢查 schema 定義
            if pd.api.types.is_numeric_dtype(aligned):
                # 對數值欄位應用精度
                aligned = aligned.apply(lambda x: safe_round(x, precision))

        # 應用預設值
        if attribute.default_value is not None:
            aligned = aligned.fillna(attribute.default_value)

        return aligned

    @classmethod
    def _optimize_int_dtype(cls, series: pd.Series) -> pd.Series:
        """優化整數類型，選擇最小的合適 dtype

        Args:
            series: 整數 Series

        Returns:
            優化後的 Series
        """
        import numpy as np

        # 先轉為 int64 確保型別正確
        series_int = series.astype("int64")

        # 取得最小和最大值
        min_val = series_int.min()
        max_val = series_int.max()

        # 依據範圍選擇最小的 dtype
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
        """優化浮點數類型

        根據精度需求選擇 float32 或 float64：
        - 如果有 precision 且 <= 7: 使用 float32
        - 否則使用 float64

        Args:
            series: 浮點數 Series
            type_attr: 型別屬性（可能包含 precision）

        Returns:
            優化後的 Series
        """
        # 先轉為 float64 確保型別正確
        series_float = series.astype("float64")

        # 檢查精度設定
        if type_attr and "precision" in type_attr:
            precision = type_attr["precision"]
            # float32 有效數字約 7 位，float64 約 15 位
            if precision <= 7:
                return series_float.astype("float32")

        return series_float  # float64

    @classmethod
    def validate(cls, attribute: Attribute, data: pd.Series) -> tuple[bool, list[str]]:
        """驗證 Series 是否符合 Attribute 定義"""
        errors = []

        # 型別驗證
        if attribute.type and str(data.dtype) != attribute.type:
            errors.append(f"Type mismatch: expected {attribute.type}, got {data.dtype}")

        # 空值驗證
        nullable = (
            attribute.type_attr.get("nullable", True) if attribute.type_attr else True
        )
        if not nullable and data.isnull().any():
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
        cls,
        series: pd.Series,
        data_type: str,
        is_category: bool,
        logical_type: str | None = None,
    ) -> FieldStats:
        """計算欄位統計資訊

        根據 type 和 category 決定計算哪些統計值：
        - unique_count, category_distribution: 只在 category=True 時計算
        - min, max, mean, std: 只在 type != 'str' 且 category=False 時計算

        Args:
            series: 資料 Series
            data_type: 簡化後的資料類型 (int, float, str, date, datetime)
            is_category: 是否為分類資料
            logical_type: 邏輯類型

        統計計算邏輯在 Metadater 類別中實現
        """
        import pandas as pd

        row_count = len(series)
        na_count = series.isna().sum()
        na_percentage = (na_count / row_count) if row_count > 0 else 0.0

        # unique_count: 只在 category=True 時計算
        unique_count = None
        if is_category:
            unique_count = series.nunique()

        # 數值統計：只在 type != 'str' 且 category=False 時計算
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

        # 類別統計：只在 category=True 時計算
        mode = None
        mode_frequency = None
        category_distribution = None

        if is_category and not series.empty:
            mode_series = series.mode()
            if not mode_series.empty:
                mode = mode_series.iloc[0]
                mode_frequency = int((series == mode).sum())

            # 計算類別分佈
            value_counts = series.value_counts()
            # 限制最多記錄前 20 個類別
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


class SchemaMetadater:
    """單表層操作類別 Single table operations

    所有方法都在這裡實作，Schema 只是設定檔
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
        """從 DataFrame 建立 Schema 設定檔

        Args:
            data: 資料 DataFrame
            enable_stats: 是否計算統計資訊
            base_schema: 基礎 Schema（如果有），如果欄位有 precision 定義則不推斷
            **kwargs: 其他參數
        """
        attributes = {}

        for col in data.columns:
            # 檢查 base_schema 中是否有該欄位的定義
            base_attribute = None
            if base_schema and base_schema.attributes and col in base_schema.attributes:
                base_attribute = base_schema.attributes[col]

            attributes[col] = AttributeMetadater.from_data(
                data[col], enable_stats=enable_stats, base_attribute=base_attribute
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
        # 簡化型別映射：統一為 int, float, str, date, datetime
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

        # 建立 attribute 設定
        attr = {
            "name": name,
            "type": type_mapping.get(field.get("type", "str"), "str"),
            "logical_type": field.get("logical_type", ""),
        }

        # 合併 type_attr
        type_attr = {}

        # nullable（從 na_values 推斷）
        type_attr["nullable"] = True if field.get("na_values") else False

        # 處理 category
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
        """標準化 attribute 配置，將頂層的 type_attr 相關屬性移入 type_attr 字典

        處理 YAML 中直接定義在頂層的屬性如：
        - category: true
        - nullable: true
        - precision: 2
        - format: "%Y-%m-%d"
        - width: 8

        將它們移入 type_attr 字典中以符合內部結構。
        """
        config = config.copy()  # 避免修改原始字典

        # 定義需要移入 type_attr 的屬性
        type_attr_keys = ["category", "nullable", "precision", "format", "width"]

        # 檢查是否有任何 type_attr 相關屬性在頂層
        has_type_attr_in_top = any(key in config for key in type_attr_keys)

        if has_type_attr_in_top:
            # 確保有 type_attr 字典
            if "type_attr" not in config:
                config["type_attr"] = {}

            # 將頂層的 type_attr 相關屬性移入 type_attr 字典
            for key in type_attr_keys:
                if key in config:
                    # 只有當 type_attr 中還沒有這個屬性時才移入
                    if key not in config["type_attr"]:
                        config["type_attr"][key] = config[key]
                    # 從頂層刪除
                    del config[key]

        return config

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

                    # 應用簡化類型映射（與 fields 處理保持一致）
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

                    # 處理頂層的 type_attr 相關屬性（category, nullable, precision, format, width）
                    # 將它們移入 type_attr 字典中
                    attr_config = cls._normalize_attribute_config(attr_config)

                    attributes[attr_name] = AttributeMetadater.from_dict(attr_config)
                else:
                    # 如果已經是 Attribute 物件，直接使用
                    attributes[attr_name] = attr_config
            config["attributes"] = attributes
        elif "fields" in config:
            # 向後相容：將 fields 對應到內部的 attributes
            attributes = {}
            for field_name, field_config in config["fields"].items():
                if isinstance(field_config, dict):
                    # 確保有 name 欄位
                    if "name" not in field_config:
                        field_config["name"] = field_name
                    # 應用簡化類型映射
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

                    # 標準化 attribute 配置（處理頂層的 type_attr 屬性）
                    field_config = cls._normalize_attribute_config(field_config)

                    attributes[field_name] = AttributeMetadater.from_dict(field_config)
                else:
                    # 如果已經是 Attribute 物件，直接使用
                    attributes[field_name] = field_config
            config["attributes"] = attributes
            del config["fields"]  # 移除 fields，改用 attributes

        return Schema(**config)

    @classmethod
    def from_yaml(cls, filepath: str) -> Schema:
        """從 YAML 檔案載入 Schema

        Raises:
            ValueError: 當 YAML 檔案中有重複的欄位名稱時
        """

        # 使用自定義 loader 來檢測重複的 key
        class DuplicateKeysLoader(yaml.SafeLoader):
            """自定義 YAML Loader，檢測重複的 key"""

            pass

        def check_duplicate_keys(loader, node, deep=False):
            """檢查並報告重複的 key"""
            mapping = {}
            duplicates = []

            for key_node, value_node in node.value:
                # 獲取 key 的實際值
                key = loader.construct_object(key_node, deep=deep)
                if key in mapping:
                    # 記錄重複的 key 及其行號
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

            # 使用父類的 construct_mapping 方法
            return yaml.SafeLoader.construct_mapping(loader, node, deep)

        # 覆寫 construct_mapping 方法
        DuplicateKeysLoader.construct_mapping = check_duplicate_keys

        with open(filepath) as f:
            try:
                config = yaml.load(f, Loader=DuplicateKeysLoader)
            except ValueError:
                # 重新拋出 ValueError，保持原始錯誤訊息
                raise
            except yaml.YAMLError as e:
                # 其他 YAML 解析錯誤
                raise ValueError(f"Failed to parse YAML file {filepath}: {e}")

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
