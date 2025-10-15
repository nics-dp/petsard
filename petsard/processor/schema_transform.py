"""
Processor Schema Transform Mixin

為 Processor 類別提供 Schema 轉換資訊的基礎設施
每個 Processor 透過宣告類屬性來描述它如何影響 SchemaMetadata
"""

from typing import Any, ClassVar


class SchemaTransformMixin:
    """
    Schema 轉換 Mixin

    為 Processor 類別提供宣告 Schema 轉換規則的能力
    子類別應該設定以下類屬性來描述它們如何轉換 Schema
    """

    # Schema 轉換規則
    SCHEMA_TRANSFORM: ClassVar[dict[str, Any]] = {
        # 輸入類型限制 (None 表示接受所有類型)
        "input_types": None,  # list[str] | None
        # 輸入是否為類別 (None 表示不限制)
        "input_category": None,  # bool | None
        # 輸出類型 (None 表示保持不變)
        "output_type": None,  # str | None
        # 輸出邏輯類型 (None 表示保持不變)
        "output_logical_type": None,  # str | None
        # 輸出是否為類別 (None 表示保持不變)
        "output_category": None,  # bool | None
        # 是否創建新欄位 (如 OneHot)
        "creates_columns": False,  # bool
        # 是否移除原欄位
        "removes_columns": False,  # bool
        # 新欄位的命名模式 (如 OneHot 的後綴)
        "column_pattern": None,  # str | None
        # 是否影響可空性
        "affects_nullable": False,  # bool
        # 轉換後的可空性 (None 表示保持不變)
        "nullable_after": None,  # bool | None
        # 額外描述
        "description": "",  # str
    }

    @classmethod
    def get_schema_transform_info(cls) -> dict[str, Any]:
        """
        獲取此 Processor 的 Schema 轉換資訊

        Returns:
            Schema 轉換規則字典
        """
        # 如果子類別沒有定義 SCHEMA_TRANSFORM，使用預設值
        if (
            not hasattr(cls, "SCHEMA_TRANSFORM")
            or cls.SCHEMA_TRANSFORM is SchemaTransformMixin.SCHEMA_TRANSFORM
        ):
            # 返回預設規則：保持類型不變
            return {
                "input_types": None,
                "input_category": None,
                "output_type": None,
                "output_logical_type": None,
                "output_category": None,
                "creates_columns": False,
                "removes_columns": False,
                "column_pattern": None,
                "affects_nullable": False,
                "nullable_after": None,
                "description": "No schema transformation defined",
            }

        return cls.SCHEMA_TRANSFORM.copy()

    @classmethod
    def get_processor_name(cls) -> str:
        """
        獲取 Processor 的名稱（用於註冊）

        Returns:
            Processor 名稱（小寫，如 'encoder_label'）
        """
        # 從類名生成名稱，如 EncoderLabel -> encoder_label
        name = cls.__name__

        # 處理駝峰命名
        import re

        # 在大寫字母前插入底線
        name = re.sub("([A-Z])", r"_\1", name).lower()
        # 移除開頭的底線
        name = name.lstrip("_")

        return name


# Schema 轉換資訊的簡化工廠函數
def schema_transform(
    input_types: list[str] | None = None,
    input_category: bool | None = None,
    output_type: str | None = None,
    output_logical_type: str | None = None,
    output_category: bool | None = None,
    creates_columns: bool = False,
    removes_columns: bool = False,
    column_pattern: str | None = None,
    affects_nullable: bool = False,
    nullable_after: bool | None = None,
    description: str = "",
) -> dict[str, Any]:
    """
    創建 Schema 轉換規則的工廠函數

    這是一個便利函數，讓 Processor 類別可以更簡潔地定義轉換規則

    Args:
        input_types: 接受的輸入類型列表
        input_category: 輸入是否必須為類別 (None=不限制)
        output_type: 輸出類型 (None=保持不變)
        output_logical_type: 輸出邏輯類型 (None=保持不變)
        output_category: 輸出是否為類別 (None=保持不變)
        creates_columns: 是否創建新欄位
        removes_columns: 是否移除原欄位
        column_pattern: 新欄位命名模式
        affects_nullable: 是否影響可空性
        nullable_after: 轉換後的可空性
        description: 轉換描述

    Example:
        class EncoderLabel(SchemaTransformMixin, Encoder):
            SCHEMA_TRANSFORM = schema_transform(
                input_category=True,
                output_type="int64",
                output_category=False,
                description="Label encoding: 類別 -> 數值"
            )
    """
    return {
        "input_types": input_types,
        "input_category": input_category,
        "output_type": output_type,
        "output_logical_type": output_logical_type,
        "output_category": output_category,
        "creates_columns": creates_columns,
        "removes_columns": removes_columns,
        "column_pattern": column_pattern,
        "affects_nullable": affects_nullable,
        "nullable_after": nullable_after,
        "description": description,
    }
