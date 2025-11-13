"""
Processor Schema Transform Mixin

Provides infrastructure for Schema transformation information to Processor classes
Each Processor describes how it affects SchemaMetadata through declared class attributes
"""

from typing import Any, ClassVar


class SchemaTransformMixin:
    """
    Schema Transform Mixin

    Provides ability to declare Schema transformation rules for Processor classes
    Subclasses should set the following class attributes to describe how they transform Schema
    """

    # Schema transformation rules
    SCHEMA_TRANSFORM: ClassVar[dict[str, Any]] = {
        # Input type constraints (None means accept all types)
        "input_types": None,  # list[str] | None
        # Whether input must be categorical (None means no constraint)
        "input_category": None,  # bool | None
        # Output type (None means keep unchanged)
        "output_type": None,  # str | None
        # Output logical type (None means keep unchanged)
        "output_logical_type": None,  # str | None
        # Whether output is categorical (None means keep unchanged)
        "output_category": None,  # bool | None
        # Whether creates new columns (e.g., OneHot)
        "creates_columns": False,  # bool
        # Whether removes original columns
        "removes_columns": False,  # bool
        # Naming pattern for new columns (e.g., OneHot suffix)
        "column_pattern": None,  # str | None
        # Whether affects nullability
        "affects_nullable": False,  # bool
        # Nullability after transformation (None means keep unchanged)
        "nullable_after": None,  # bool | None
        # Additional description
        "description": "",  # str
    }

    @classmethod
    def get_schema_transform_info(cls) -> dict[str, Any]:
        """
        Get Schema transformation information for this Processor

        Returns:
            Schema transformation rules dictionary
        """
        # If subclass hasn't defined SCHEMA_TRANSFORM, use default values
        if (
            not hasattr(cls, "SCHEMA_TRANSFORM")
            or cls.SCHEMA_TRANSFORM is SchemaTransformMixin.SCHEMA_TRANSFORM
        ):
            # Return default rules: keep types unchanged
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
        Get Processor name (for registration)

        Returns:
            Processor name (lowercase, e.g., 'encoder_label')
        """
        # Generate name from class name, e.g., EncoderLabel -> encoder_label
        name = cls.__name__

        # Handle camelCase naming
        import re

        # Insert underscore before uppercase letters
        name = re.sub("([A-Z])", r"_\1", name).lower()
        # Remove leading underscore
        name = name.lstrip("_")

        return name


# Simplified factory function for Schema transformation information
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
    Factory function to create Schema transformation rules

    This is a convenience function allowing Processor classes to define transformation rules more concisely

    Args:
        input_types: List of accepted input types
        input_category: Whether input must be categorical (None=no constraint)
        output_type: Output type (None=keep unchanged)
        output_logical_type: Output logical type (None=keep unchanged)
        output_category: Whether output is categorical (None=keep unchanged)
        creates_columns: Whether creates new columns
        removes_columns: Whether removes original columns
        column_pattern: Naming pattern for new columns
        affects_nullable: Whether affects nullability
        nullable_after: Nullability after transformation
        description: Transformation description

    Example:
        class EncoderLabel(SchemaTransformMixin, Encoder):
            SCHEMA_TRANSFORM = schema_transform(
                input_category=True,
                output_type="int64",
                output_category=False,
                description="Label encoding: category -> numeric"
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
