"""
Statistics-related classes

Provides pure dataclass definitions for three-layer statistics without calculation logic
All calculation logic should be in Metadater classes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldStats:
    """Field statistics

    Pure data class without any calculation logic
    """

    # Basic statistics
    row_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0
    unique_count: int = 0

    # Numeric statistics (numeric types only)
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    median: float | None = None
    q1: float | None = None  # First quartile
    q3: float | None = None  # Third quartile

    # Categorical statistics (categorical types only)
    mode: Any = None
    mode_frequency: int | None = None
    category_distribution: dict[str, int] | None = None

    # Data type info
    detected_type: str | None = None
    actual_dtype: str | None = None
    logical_type: str | None = None


@dataclass(frozen=True)
class TableStats:
    """Table statistics

    Pure data class without any calculation logic
    """

    # Basic statistics
    row_count: int = 0
    column_count: int = 0
    total_na_count: int = 0
    total_na_percentage: float = 0.0

    # Memory usage
    memory_usage_bytes: int | None = None

    # Duplicate data
    duplicated_rows: int = 0
    duplicated_columns: list[str] = field(default_factory=list)

    # Field statistics
    field_stats: dict[str, FieldStats] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetsStats:
    """Datasets statistics

    Pure data class without any calculation logic
    """

    # Basic statistics
    table_count: int = 0
    total_row_count: int = 0
    total_column_count: int = 0

    # Memory usage
    total_memory_usage_bytes: int | None = None

    # Table statistics
    table_stats: dict[str, TableStats] = field(default_factory=dict)
