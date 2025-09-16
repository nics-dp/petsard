"""
統計資訊相關類別 Statistics-related classes

提供三層統計資訊的 dataclass 定義與計算功能
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FieldStats:
    """欄位統計資訊 Field statistics"""

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
    """資料表統計資訊 Table statistics"""

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
    """資料集統計資訊 Datasets statistics"""

    # 基本統計 Basic statistics
    table_count: int = 0
    total_row_count: int = 0
    total_column_count: int = 0

    # 記憶體使用 Memory usage
    total_memory_usage_bytes: int | None = None

    # 資料表統計 Table statistics
    table_stats: dict[str, TableStats] = field(default_factory=dict)


class StatsCalculator:
    """統計計算工具類別 Statistics calculator utility class"""

    @classmethod
    def calculate_field_stats(cls, series: pd.Series) -> FieldStats:
        """計算欄位統計資訊"""
        row_count = len(series)
        na_count = series.isna().sum()
        na_percentage = (na_count / row_count) if row_count > 0 else 0.0
        unique_count = series.nunique()

        # 檢測邏輯型態
        logical_type = cls._detect_logical_type(series)

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

    @classmethod
    def _detect_logical_type(cls, series: pd.Series) -> str:
        """檢測欄位的邏輯型態"""
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_categorical_dtype(series):
            return "categorical"
        elif pd.api.types.is_object_dtype(series):
            # 進一步檢查是否為字串
            non_na = series.dropna()
            if len(non_na) > 0 and all(isinstance(x, str) for x in non_na.head(100)):
                return "string"
            return "object"
        else:
            return "unknown"

    @classmethod
    def calculate_table_stats(
        cls, df: pd.DataFrame, field_stats: dict[str, FieldStats] | None = None
    ) -> TableStats:
        """計算資料表統計資訊"""
        row_count = len(df)
        column_count = len(df.columns)

        # 如果沒有提供 field_stats，則計算
        if field_stats is None:
            field_stats = {}
            for col in df.columns:
                field_stats[col] = cls.calculate_field_stats(df[col])

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

    @classmethod
    def calculate_datasets_stats(
        cls,
        tables: dict[str, pd.DataFrame] | None = None,
        table_stats: dict[str, TableStats] | None = None,
    ) -> DatasetsStats:
        """計算資料集統計資訊

        Args:
            tables: 資料表字典（如果提供，會計算 table_stats）
            table_stats: 已計算的表格統計（如果沒有 tables，則使用此參數）
        """
        if table_stats is None:
            if tables is None:
                raise ValueError("Must provide either tables or table_stats")
            table_stats = {}
            for name, df in tables.items():
                table_stats[name] = cls.calculate_table_stats(df)

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
