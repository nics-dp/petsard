"""
Schema Inferencer: 推論 pipeline 中每個階段的 Schema 變化

此模組負責在 Executor 初始化時，根據 YAML 配置推論整個 pipeline 中
每個模組（Loader → Preprocessor → Synthesizer → Postprocessor → Evaluator）
的 input 和 output SchemaMetadata。

主要功能：
1. 追蹤 Processor 的 transform 如何改變欄位的 dtype 和屬性
2. 預測每個模組的 input/output Schema
3. 提供 dtype 一致性驗證
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from petsard.metadater.metadata import Attribute, Schema


@dataclass
class TransformRule:
    """單一轉換規則

    描述一個 Processor 如何改變欄位的屬性
    """

    processor_type: str  # 'missing', 'outlier', 'encoder', 'scaler', 'discretizing'
    processor_method: str  # 具體方法，如 'encoder_onehot', 'scaler_standard'

    # 轉換規則
    input_types: list[str] | None = None  # 適用的輸入類型，None 表示全部
    output_type: str | None = None  # 輸出類型，None 表示保持不變
    output_logical_type: str | None = None  # 輸出邏輯類型

    # 特殊行為
    creates_columns: bool = False  # 是否創建新欄位（如 OneHot）
    removes_columns: bool = False  # 是否移除原欄位
    column_suffix: str | None = None  # 新欄位的後綴模式

    # 屬性變更
    affects_nullable: bool = False  # 是否影響可空性
    nullable_after: bool | None = None  # 轉換後的可空性

    context: dict[str, Any] = field(default_factory=dict)  # 額外上下文


class ProcessorTransformRules:
    """Processor 轉換規則庫

    定義每種 Processor 如何改變 Schema
    """

    # 定義所有已知的轉換規則
    RULES: dict[str, TransformRule] = {
        # === Missing Handlers ===
        "missing_drop": TransformRule(
            processor_type="missing",
            processor_method="missing_drop",
            affects_nullable=True,
            nullable_after=False,
            context={"description": "移除包含缺失值的行，欄位不再有 null"},
        ),
        "missing_mean": TransformRule(
            processor_type="missing",
            processor_method="missing_mean",
            input_types=["numerical"],
            affects_nullable=True,
            nullable_after=False,
            context={"description": "用均值填充，欄位不再有 null"},
        ),
        "missing_median": TransformRule(
            processor_type="missing",
            processor_method="missing_median",
            input_types=["numerical"],
            affects_nullable=True,
            nullable_after=False,
            context={"description": "用中位數填充，欄位不再有 null"},
        ),
        "missing_mode": TransformRule(
            processor_type="missing",
            processor_method="missing_mode",
            affects_nullable=True,
            nullable_after=False,
            context={"description": "用眾數填充，欄位不再有 null"},
        ),
        "missing_simple": TransformRule(
            processor_type="missing",
            processor_method="missing_simple",
            affects_nullable=True,
            nullable_after=False,
            context={"description": "簡單填充策略，欄位不再有 null"},
        ),
        # === Outlier Handlers ===
        # Outlier 處理通常保持類型不變，但可能移除一些行
        "outlier_iqr": TransformRule(
            processor_type="outlier",
            processor_method="outlier_iqr",
            input_types=["numerical", "datetime"],
            context={"description": "IQR 離群值處理，保持類型不變"},
        ),
        "outlier_zscore": TransformRule(
            processor_type="outlier",
            processor_method="outlier_zscore",
            input_types=["numerical"],
            context={"description": "Z-Score 離群值處理，保持類型不變"},
        ),
        "outlier_lof": TransformRule(
            processor_type="outlier",
            processor_method="outlier_lof",
            input_types=["numerical"],
            context={"description": "LOF 離群值處理，保持類型不變"},
        ),
        "outlier_isolationforest": TransformRule(
            processor_type="outlier",
            processor_method="outlier_isolationforest",
            input_types=["numerical"],
            context={"description": "Isolation Forest 離群值處理，保持類型不變"},
        ),
        # === Encoders ===
        "encoder_label": TransformRule(
            processor_type="encoder",
            processor_method="encoder_label",
            input_types=["categorical", "string"],
            output_type="int64",
            output_logical_type="encoded_categorical",
            context={"description": "Label 編碼，類別轉為整數"},
        ),
        "encoder_onehot": TransformRule(
            processor_type="encoder",
            processor_method="encoder_onehot",
            input_types=["categorical", "string"],
            output_type="int64",
            output_logical_type="onehot_encoded",
            creates_columns=True,
            removes_columns=True,
            context={"description": "One-Hot 編碼，創建多個二元欄位"},
        ),
        "encoder_uniform": TransformRule(
            processor_type="encoder",
            processor_method="encoder_uniform",
            input_types=["categorical", "string"],
            output_type="float64",
            output_logical_type="uniform_encoded",
            context={"description": "Uniform 編碼，類別轉為均勻分布的浮點數"},
        ),
        "encoder_minguodate": TransformRule(
            processor_type="encoder",
            processor_method="encoder_minguodate",
            input_types=["datetime", "string"],
            output_type="int64",
            output_logical_type="minguo_year",
            context={"description": "民國年編碼，日期轉為民國年整數"},
        ),
        "encoder_datediff": TransformRule(
            processor_type="encoder",
            processor_method="encoder_datediff",
            input_types=["datetime"],
            output_type="int64",
            output_logical_type="date_diff_days",
            context={"description": "日期差異編碼，計算與參考日期的天數差"},
        ),
        # === Scalers ===
        "scaler_standard": TransformRule(
            processor_type="scaler",
            processor_method="scaler_standard",
            input_types=["numerical", "datetime"],
            output_type="float64",
            output_logical_type="standardized",
            context={"description": "標準化，轉為均值0標準差1的浮點數"},
        ),
        "scaler_minmax": TransformRule(
            processor_type="scaler",
            processor_method="scaler_minmax",
            input_types=["numerical", "datetime"],
            output_type="float64",
            output_logical_type="normalized",
            context={"description": "Min-Max 正規化，轉為 [0,1] 範圍的浮點數"},
        ),
        "scaler_log": TransformRule(
            processor_type="scaler",
            processor_method="scaler_log",
            input_types=["numerical"],
            output_type="float64",
            output_logical_type="log_transformed",
            context={"description": "對數轉換"},
        ),
        "scaler_log1p": TransformRule(
            processor_type="scaler",
            processor_method="scaler_log1p",
            input_types=["numerical"],
            output_type="float64",
            output_logical_type="log1p_transformed",
            context={"description": "Log(1+x) 轉換"},
        ),
        "scaler_zerocenter": TransformRule(
            processor_type="scaler",
            processor_method="scaler_zerocenter",
            input_types=["numerical", "datetime"],
            output_type="float64",
            output_logical_type="zero_centered",
            context={"description": "零中心化"},
        ),
        "scaler_timeanchor": TransformRule(
            processor_type="scaler",
            processor_method="scaler_timeanchor",
            input_types=["datetime"],
            output_type="float64",
            output_logical_type="time_anchored",
            context={"description": "時間錨點標準化"},
        ),
        # === Discretizing ===
        "discretizing_kbins": TransformRule(
            processor_type="discretizing",
            processor_method="discretizing_kbins",
            input_types=["numerical", "datetime"],
            output_type="int64",
            output_logical_type="discretized",
            context={"description": "K-Bins 離散化，連續值轉為離散區間"},
        ),
    }

    @classmethod
    def get_rule(cls, processor_method: str) -> TransformRule | None:
        """獲取指定處理器的轉換規則"""
        return cls.RULES.get(processor_method)

    @classmethod
    def apply_rule(cls, attribute: Attribute, rule: TransformRule) -> Attribute:
        """應用轉換規則到 Attribute

        Args:
            attribute: 原始 Attribute
            rule: 轉換規則

        Returns:
            轉換後的 Attribute（新實例）
        """
        # 創建新的 Attribute，保留大部分原始資訊
        new_attr_dict = {
            "name": attribute.name,
            "description": attribute.description,
            "type": rule.output_type if rule.output_type else attribute.type,
            "type_attr": attribute.type_attr,
            "category": attribute.category,  # 預設保持不變
            "logical_type": rule.output_logical_type
            if rule.output_logical_type
            else attribute.logical_type,
            "enable_optimize_type": attribute.enable_optimize_type,
            "enable_null": rule.nullable_after
            if rule.affects_nullable
            else attribute.enable_null,
            "enable_stats": attribute.enable_stats,
            "stats": None,  # 統計資訊在轉換後會改變，暫時設為 None
            "na_values": attribute.na_values,
            "cast_errors": attribute.cast_errors,
            "null_strategy": attribute.null_strategy,
            "default_value": attribute.default_value,
            "constraints": attribute.constraints,
            "created_at": attribute.created_at,
            "updated_at": datetime.now(),
        }

        return Attribute(**new_attr_dict)

    @classmethod
    def apply_transform_info(
        cls, attribute: Attribute, transform_info: dict[str, Any]
    ) -> Attribute:
        """應用從 Processor 類別取得的 SCHEMA_TRANSFORM 資訊

        Args:
            attribute: 原始 Attribute
            transform_info: 從 Processor.get_schema_transform_info() 獲得的轉換資訊

        Returns:
            轉換後的 Attribute（新實例）
        """
        # 創建新的 Attribute，保留大部分原始資訊
        new_attr_dict = {
            "name": attribute.name,
            "description": attribute.description,
            "type": transform_info.get("output_type") or attribute.type,
            "type_attr": attribute.type_attr,
            "category": transform_info.get("output_category")
            if transform_info.get("output_category") is not None
            else attribute.category,
            "logical_type": transform_info.get("output_logical_type")
            or attribute.logical_type,
            "enable_optimize_type": attribute.enable_optimize_type,
            "enable_null": transform_info.get("nullable_after")
            if transform_info.get("affects_nullable")
            else attribute.enable_null,
            "enable_stats": attribute.enable_stats,
            "stats": None,  # 統計資訊在轉換後會改變，暫時設為 None
            "na_values": attribute.na_values,
            "cast_errors": attribute.cast_errors,
            "null_strategy": attribute.null_strategy,
            "default_value": attribute.default_value,
            "constraints": attribute.constraints,
            "created_at": attribute.created_at,
            "updated_at": datetime.now(),
        }

        return Attribute(**new_attr_dict)


class SchemaInferencer:
    """Schema 推論器

    根據 Processor 配置推論 Schema 的變化
    """

    def __init__(self):
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._inference_history: list[dict[str, Any]] = []

    def infer_preprocessor_output(
        self, input_schema: Schema, processor_config: dict[str, dict[str, Any]]
    ) -> Schema:
        """推論 Preprocessor 的輸出 Schema

        Args:
            input_schema: 輸入的 Schema（來自 Loader）
            processor_config: Processor 配置

        Returns:
            推論出的輸出 Schema
        """
        self.logger.debug(
            f"推論 Preprocessor 輸出 Schema，輸入欄位數: {len(input_schema.attributes)}"
        )

        # 檢查是否使用 'default' 方法
        # 如果是，需要生成完整的配置（模擬 Processor._generate_config()）
        if self._is_using_default_method(processor_config):
            self.logger.info(
                "偵測到使用 'default' 方法，將根據 DefaultProcessorMap 生成配置"
            )
            processor_config = self._generate_default_config(input_schema)

        # 深拷貝輸入 Schema 作為基礎
        output_attributes = {}

        # 追蹤欄位變化
        inference_record = {
            "timestamp": datetime.now().isoformat(),
            "stage": "preprocessor",
            "changes": [],
        }

        # 遍歷每個欄位和其處理器配置
        for col_name, input_attr in input_schema.attributes.items():
            current_attr = input_attr
            col_changes = []

            # 按順序應用每個處理器類型
            for processor_type in [
                "missing",
                "outlier",
                "encoder",
                "scaler",
                "discretizing",
            ]:
                if processor_type not in processor_config:
                    continue

                col_config = processor_config[processor_type].get(col_name)
                if not col_config:
                    continue

                # 獲取處理器方法名稱
                if isinstance(col_config, str):
                    method_name = col_config
                elif isinstance(col_config, dict) and "method" in col_config:
                    method_name = col_config["method"]
                else:
                    continue

                # 優先嘗試從 Processor 類別獲取動態的 SCHEMA_TRANSFORM
                transform_info = self._get_processor_transform_info(
                    processor_type, method_name
                )

                if transform_info:
                    # 使用動態獲取的轉換資訊
                    # 檢查輸入類型和 category 是否匹配
                    if transform_info.get("input_types"):
                        current_type = self._get_data_category(current_attr)
                        if current_type not in transform_info["input_types"]:
                            self.logger.warning(
                                f"欄位 '{col_name}' 的類型 '{current_type}' "
                                f"不匹配 '{method_name}' 的預期輸入類型 {transform_info['input_types']}"
                            )
                            continue

                    if transform_info.get("input_category") is not None:
                        if current_attr.category != transform_info["input_category"]:
                            self.logger.warning(
                                f"欄位 '{col_name}' 的 category={current_attr.category} "
                                f"不匹配 '{method_name}' 的預期 input_category={transform_info['input_category']}"
                            )
                            continue

                    # 應用轉換
                    new_attr = ProcessorTransformRules.apply_transform_info(
                        current_attr, transform_info
                    )
                    col_changes.append(
                        {
                            "processor": processor_type,
                            "method": method_name,
                            "type_before": current_attr.type,
                            "type_after": new_attr.type,
                            "category_before": current_attr.category,
                            "category_after": new_attr.category,
                            "logical_type_before": current_attr.logical_type,
                            "logical_type_after": new_attr.logical_type,
                        }
                    )
                    current_attr = new_attr

                    self.logger.debug(
                        f"應用 {method_name} 到欄位 '{col_name}': "
                        f"type: {col_changes[-1]['type_before']} → {col_changes[-1]['type_after']}, "
                        f"category: {col_changes[-1]['category_before']} → {col_changes[-1]['category_after']}"
                    )
                else:
                    # 回退到靜態規則
                    rule = ProcessorTransformRules.get_rule(method_name)
                    if rule:
                        # 檢查輸入類型是否匹配
                        if rule.input_types:
                            current_type = self._get_data_category(current_attr)
                            if current_type not in rule.input_types:
                                self.logger.warning(
                                    f"欄位 '{col_name}' 的類型 '{current_type}' "
                                    f"不匹配 '{method_name}' 的預期輸入類型 {rule.input_types}"
                                )
                                continue

                        # 應用轉換
                        new_attr = ProcessorTransformRules.apply_rule(
                            current_attr, rule
                        )
                        col_changes.append(
                            {
                                "processor": processor_type,
                                "method": method_name,
                                "type_before": current_attr.type,
                                "type_after": new_attr.type,
                                "logical_type_before": current_attr.logical_type,
                                "logical_type_after": new_attr.logical_type,
                            }
                        )
                        current_attr = new_attr

                        self.logger.debug(
                            f"應用 {method_name} 到欄位 '{col_name}': "
                            f"{col_changes[-1]['type_before']} → {col_changes[-1]['type_after']}"
                        )

            output_attributes[col_name] = current_attr
            if col_changes:
                inference_record["changes"].append(
                    {"column": col_name, "transformations": col_changes}
                )

        # 記錄推論歷史
        self._inference_history.append(inference_record)

        # 創建輸出 Schema
        output_schema = Schema(
            id=f"{input_schema.id}_preprocessed",
            name=f"{input_schema.name} (Preprocessed)",
            description=f"Preprocessed schema from {input_schema.id}",
            attributes=output_attributes,
            primary_key=input_schema.primary_key,
            foreign_keys=input_schema.foreign_keys,
            indexes=input_schema.indexes,
            sample_size=input_schema.sample_size,
            stage="preprocessed",
            parent_schema_id=input_schema.id,
            enable_optimize_type=input_schema.enable_optimize_type,
            enable_null=input_schema.enable_null,
            enable_stats=False,  # 推論的 Schema 沒有統計資訊
            stats=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.logger.info(
            f"推論完成：輸入 {len(input_schema.attributes)} 欄位 → "
            f"輸出 {len(output_attributes)} 欄位"
        )

        return output_schema

    def _get_processor_transform_info(
        self, processor_type: str, method_name: str
    ) -> dict[str, Any] | None:
        """從 Processor 類別動態獲取 SCHEMA_TRANSFORM 資訊

        Args:
            processor_type: 處理器類型 (encoder, scaler, etc.)
            method_name: 處理器方法名稱

        Returns:
            SCHEMA_TRANSFORM 字典，若無法獲取則返回 None
        """
        try:
            # 動態導入 Processor 類別
            from petsard.processor.base import ProcessorClassMap

            processor_class = ProcessorClassMap.get_class(method_name)
            if processor_class and hasattr(
                processor_class, "get_schema_transform_info"
            ):
                transform_info = processor_class.get_schema_transform_info()
                self.logger.debug(
                    f"從 {processor_class.__name__} 獲取 SCHEMA_TRANSFORM: {transform_info}"
                )
                return transform_info
        except Exception as e:
            self.logger.debug(f"無法從 {method_name} 獲取動態 SCHEMA_TRANSFORM: {e}")

        return None

    def _get_data_category(self, attribute: Attribute) -> str:
        """從 Attribute 推斷資料類別

        將 Attribute 的 type 映射到處理器使用的類別：
        numerical, categorical, datetime, object
        """
        if not attribute.type:
            return "object"

        type_str = str(attribute.type).lower()

        if "int" in type_str or "float" in type_str:
            return "numerical"
        elif type_str in ["string", "str", "binary"]:
            return "categorical"
        elif type_str == "boolean":
            return "categorical"
        elif "datetime" in type_str or type_str in ["date", "time", "timestamp"]:
            return "datetime"
        elif attribute.category is True:
            return "categorical"
        else:
            return "object"

    def get_inference_history(self) -> list[dict[str, Any]]:
        """獲取推論歷史記錄"""
        return self._inference_history

    def infer_pipeline_schemas(
        self, loader_schema: Schema, pipeline_config: dict[str, Any]
    ) -> dict[str, Schema]:
        """推論整個 pipeline 的 Schema 變化

        Args:
            loader_schema: Loader 輸出的 Schema
            pipeline_config: Pipeline 配置（從 YAML 解析）

        Returns:
            各階段的 Schema 字典
        """
        schemas = {"Loader": loader_schema}

        # 推論 Preprocessor 輸出
        if "Preprocessor" in pipeline_config:
            preprocessor_config = pipeline_config["Preprocessor"]
            schemas["Preprocessor"] = self.infer_preprocessor_output(
                loader_schema, preprocessor_config
            )

        # Synthesizer 和 Postprocessor 通常保持 Schema 不變
        # （除非有特殊配置）
        if "Preprocessor" in schemas:
            schemas["Synthesizer"] = schemas["Preprocessor"]
            schemas["Postprocessor"] = schemas["Preprocessor"]

        return schemas

    def _is_using_default_method(self, processor_config: dict[str, Any]) -> bool:
        """檢查是否使用 default 方法

        Args:
            processor_config: Processor 配置

        Returns:
            True 如果使用 default 方法
        """
        # 檢查配置結構是否為 {"default": {"method": "default"}}
        if len(processor_config) == 1 and "default" in processor_config:
            default_config = processor_config["default"]
            if (
                isinstance(default_config, dict)
                and default_config.get("method") == "default"
            ):
                return True
        return False

    def _generate_default_config(self, schema: Schema) -> dict[str, dict[str, Any]]:
        """生成 default 配置（模擬 Processor._generate_config()）

        這個方法複製 Processor._generate_config() 的邏輯，
        根據 DefaultProcessorMap 為每個欄位分配 processor

        Args:
            schema: 輸入 Schema

        Returns:
            完整的 processor 配置
        """
        from petsard.processor.base import DefaultProcessorMap

        field_names = list(schema.attributes.keys())
        config: dict = {
            processor: dict.fromkeys(field_names)
            for processor in DefaultProcessorMap.VALID_TYPES
        }

        for col in field_names:
            # 使用與 Processor._get_field_infer_dtype() 相同的邏輯
            infer_dtype = self._get_field_infer_dtype(schema.attributes[col])

            for processor, obj in DefaultProcessorMap.PROCESSOR_MAP.items():
                processor_class = obj[infer_dtype]
                # 將 processor 類別轉換為方法名稱
                if processor_class is None or (
                    callable(processor_class) and processor_class() is None
                ):
                    config[processor][col] = None
                else:
                    # 從類別名稱推導方法名稱
                    # 例如：EncoderUniform → encoder_uniform
                    class_name = processor_class.__name__
                    # 轉換為 snake_case
                    method_name = self._class_name_to_method_name(class_name)
                    config[processor][col] = method_name

        self.logger.debug(f"生成的 default 配置: {config}")
        return config

    def _get_field_infer_dtype(self, attribute: Attribute) -> str:
        """獲取欄位的推斷資料類型（模擬 Processor._get_field_infer_dtype()）

        Args:
            attribute: 欄位屬性

        Returns:
            推斷的資料類型：'numerical', 'categorical', 'datetime', 'object'
        """
        # 與 Processor._get_field_infer_dtype() 使用相同的邏輯
        data_type_str = str(attribute.type).lower() if attribute.type else "object"

        # Map specific types to legacy categories
        if "int" in data_type_str or "float" in data_type_str:
            return "numerical"
        elif data_type_str in ["string", "str", "binary"]:
            return "categorical"
        elif data_type_str == "boolean":
            return "categorical"
        elif "datetime" in data_type_str or data_type_str in [
            "date",
            "time",
            "timestamp",
        ]:
            return "datetime"
        elif attribute.category is True:
            return "categorical"
        else:
            return "object"

    def _class_name_to_method_name(self, class_name: str) -> str:
        """將類別名稱轉換為方法名稱

        例如：EncoderUniform → encoder_uniform

        Args:
            class_name: 類別名稱

        Returns:
            方法名稱（snake_case）
        """
        # 將 CamelCase 轉換為 snake_case
        import re

        # 在大寫字母前插入下劃線
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        # 處理連續大寫字母
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
