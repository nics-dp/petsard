"""
Processor Registry

統一管理所有 Processor 類別及其 Schema 轉換規則
"""

from typing import Any


class ProcessorRegistry:
    """
    Processor 註冊中心

    負責管理所有 Processor 類別的註冊和查詢
    每個 Processor 可以註冊自己的 Schema 轉換資訊
    """

    _registry: dict[str, type] = {}
    _transform_rules: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, processor_class: type, name: str | None = None) -> type:
        """
        註冊一個 Processor 類別

        Args:
            processor_class: Processor 類別
            name: 註冊名稱（如果未提供，從類別名稱生成）

        Returns:
            原始的 processor_class（用於裝飾器模式）
        """
        if name is None:
            # 從類名生成名稱
            name = cls._generate_name_from_class(processor_class)

        # 註冊類別
        cls._registry[name] = processor_class

        # 如果類別有 get_schema_transform_info 方法，註冊轉換規則
        if hasattr(processor_class, "get_schema_transform_info"):
            cls._transform_rules[name] = processor_class.get_schema_transform_info()

        return processor_class

    @classmethod
    def get_processor_class(cls, name: str) -> type | None:
        """
        根據名稱獲取 Processor 類別

        Args:
            name: Processor 名稱

        Returns:
            Processor 類別，如果不存在則返回 None
        """
        return cls._registry.get(name)

    @classmethod
    def get_transform_rule(cls, name: str) -> dict[str, Any] | None:
        """
        根據名稱獲取 Schema 轉換規則

        Args:
            name: Processor 名稱

        Returns:
            轉換規則字典，如果不存在則返回 None
        """
        return cls._transform_rules.get(name)

    @classmethod
    def list_processors(cls) -> list[str]:
        """
        列出所有已註冊的 Processor 名稱

        Returns:
            Processor 名稱列表
        """
        return list(cls._registry.keys())

    @classmethod
    def list_processors_with_rules(cls) -> list[str]:
        """
        列出所有有 Schema 轉換規則的 Processor 名稱

        Returns:
            Processor 名稱列表
        """
        return list(cls._transform_rules.keys())

    @classmethod
    def clear(cls):
        """清空註冊表（主要用於測試）"""
        cls._registry.clear()
        cls._transform_rules.clear()

    @staticmethod
    def _generate_name_from_class(processor_class: type) -> str:
        """
        從類名生成 Processor 名稱

        Args:
            processor_class: Processor 類別

        Returns:
            生成的名稱（如 'encoder_label'）
        """
        import re

        name = processor_class.__name__
        # 在大寫字母前插入底線，轉小寫
        name = re.sub("([A-Z])", r"_\1", name).lower()
        # 移除開頭的底線
        name = name.lstrip("_")
        return name


def register_processor(name: str | None = None):
    """
    Processor 註冊裝飾器

    使用方式:
        @register_processor()
        class MissingMean(SchemaTransformMixin, Missing):
            SCHEMA_TRANSFORM = schema_transform(...)

    Args:
        name: 自定義名稱（可選）
    """

    def decorator(cls):
        ProcessorRegistry.register(cls, name)
        return cls

    return decorator
