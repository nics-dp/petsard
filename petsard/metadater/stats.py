"""
統計資訊相關類別 Statistics-related classes

提供三層統計資訊的純 dataclass 定義，不包含計算邏輯
All calculation logic should be in Metadater classes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldStats:
    """欄位統計資訊 Field statistics

    純資料類別，不包含任何計算邏輯
    Pure data class without any calculation logic
    """

    # 基本統計 Basic statistics
    row_count: int = 0
    na_count: int = 0
    na_percentage: float = 0.0
    unique_count: int = 0

    # 數值統計（僅數值型態）Numeric statistics
    mean: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    median: float | None = None
    q1: float | None = None  # 第一四分位數
    q3: float | None = None  # 第三四分位數

    # 類別統計（僅類別型態）Categorical statistics
    mode: Any = None
    mode_frequency: int | None = None
    category_distribution: dict[str, int] | None = None

    # 資料型態資訊 Data type info
    detected_type: str | None = None
    actual_dtype: str | None = None
    logical_type: str | None = None


@dataclass(frozen=True)
class TableStats:
    """資料表統計資訊 Table statistics

    純資料類別，不包含任何計算邏輯
    Pure data class without any calculation logic
    """

    # 基本統計 Basic statistics
    row_count: int = 0
    column_count: int = 0
    total_na_count: int = 0
    total_na_percentage: float = 0.0

    # 記憶體使用 Memory usage
    memory_usage_bytes: int | None = None

    # 重複資料 Duplicate data
    duplicated_rows: int = 0
    duplicated_columns: list[str] = field(default_factory=list)

    # 欄位統計 Field statistics
    field_stats: dict[str, FieldStats] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetsStats:
    """資料集統計資訊 Datasets statistics

    純資料類別，不包含任何計算邏輯
    Pure data class without any calculation logic
    """

    # 基本統計 Basic statistics
    table_count: int = 0
    total_row_count: int = 0
    total_column_count: int = 0

    # 記憶體使用 Memory usage
    total_memory_usage_bytes: int | None = None

    # 資料表統計 Table statistics
    table_stats: dict[str, TableStats] = field(default_factory=dict)
