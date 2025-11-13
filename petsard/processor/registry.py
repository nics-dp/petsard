"""
Processor Registry

Unified management of all Processor classes and their Schema transformation rules
"""

from typing import Any


class ProcessorRegistry:
    """
    Processor Registry Center

    Manages registration and lookup of all Processor classes
    Each Processor can register its own Schema transformation information
    """

    _registry: dict[str, type] = {}
    _transform_rules: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, processor_class: type, name: str | None = None) -> type:
        """
        Register a Processor class

        Args:
            processor_class: Processor class
            name: Registration name (if not provided, generated from class name)

        Returns:
            Original processor_class (for decorator pattern)
        """
        if name is None:
            # Generate name from class name
            name = cls._generate_name_from_class(processor_class)

        # Register class
        cls._registry[name] = processor_class

        # If class has get_schema_transform_info method, register transformation rules
        if hasattr(processor_class, "get_schema_transform_info"):
            cls._transform_rules[name] = processor_class.get_schema_transform_info()

        return processor_class

    @classmethod
    def get_processor_class(cls, name: str) -> type | None:
        """
        Get Processor class by name

        Args:
            name: Processor name

        Returns:
            Processor class, returns None if not exists
        """
        return cls._registry.get(name)

    @classmethod
    def get_transform_rule(cls, name: str) -> dict[str, Any] | None:
        """
        Get Schema transformation rules by name

        Args:
            name: Processor name

        Returns:
            Transformation rules dictionary, returns None if not exists
        """
        return cls._transform_rules.get(name)

    @classmethod
    def list_processors(cls) -> list[str]:
        """
        List all registered Processor names

        Returns:
            List of Processor names
        """
        return list(cls._registry.keys())

    @classmethod
    def list_processors_with_rules(cls) -> list[str]:
        """
        List all Processor names with Schema transformation rules

        Returns:
            List of Processor names
        """
        return list(cls._transform_rules.keys())

    @classmethod
    def clear(cls):
        """Clear registry (mainly for testing)"""
        cls._registry.clear()
        cls._transform_rules.clear()

    @staticmethod
    def _generate_name_from_class(processor_class: type) -> str:
        """
        Generate Processor name from class name

        Args:
            processor_class: Processor class

        Returns:
            Generated name (e.g., 'encoder_label')
        """
        import re

        name = processor_class.__name__
        # Insert underscore before uppercase letters, convert to lowercase
        name = re.sub("([A-Z])", r"_\1", name).lower()
        # Remove leading underscore
        name = name.lstrip("_")
        return name


def register_processor(name: str | None = None):
    """
    Processor registration decorator

    Usage:
        @register_processor()
        class MissingMean(SchemaTransformMixin, Missing):
            SCHEMA_TRANSFORM = schema_transform(...)

    Args:
        name: Custom name (optional)
    """

    def decorator(cls):
        ProcessorRegistry.register(cls, name)
        return cls

    return decorator
