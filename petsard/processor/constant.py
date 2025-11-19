"""Constant column processor

處理所有值都相同的欄位（constant columns）。
這類欄位在合成資料生成時可能導致某些演算法（如 Copula）出現錯誤。
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from petsard.exceptions import UnfittedError


class ConstantProcessor:
    """處理 constant columns 的 processor

    此 processor 會：
    1. 在 fit() 時記錄 constant 欄位的值
    2. 在 transform() 時將 constant 欄位移除（避免影響合成器）
    3. 在 inverse_transform() 時將 constant 欄位還原

    這是一個特殊的 processor，總是在所有其他 processor 之前執行。
    """

    def __init__(self) -> None:
        """初始化 ConstantProcessor"""
        self._is_fitted: bool = False
        self._constant_columns: dict[str, Any] = {}  # 記錄 constant 欄位的值
        self._original_columns: list[str] = []  # 記錄原始欄位順序

    def fit(self, data: pd.DataFrame, metadata: Any) -> None:
        """Fit the processor

        Args:
            data: 訓練資料
            metadata: Schema metadata，包含 is_constant 標記
        """
        self._constant_columns = {}
        self._original_columns = list(data.columns)

        # 檢查每個欄位是否為 constant
        for col_name in data.columns:
            # 從 metadata 獲取 is_constant 標記
            if hasattr(metadata, "attributes") and col_name in metadata.attributes:
                attribute = metadata.attributes[col_name]
                if hasattr(attribute, "is_constant") and attribute.is_constant:
                    # 記錄該欄位的 constant 值
                    non_na_values = data[col_name].dropna()
                    if len(non_na_values) > 0:
                        self._constant_columns[col_name] = non_na_values.iloc[0]

        self._is_fitted = True

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the data (移除 constant columns)

        Args:
            data: 要轉換的資料

        Returns:
            移除 constant columns 後的資料
        """
        if not self._is_fitted:
            raise UnfittedError("ConstantProcessor must be fitted before transform")

        # 移除 constant columns
        if self._constant_columns:
            remaining_cols = [
                col for col in data.columns if col not in self._constant_columns
            ]
            return data[remaining_cols].copy()

        return data.copy()

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform the data (還原 constant columns)

        Args:
            data: 要逆轉換的資料

        Returns:
            還原 constant columns 後的資料
        """
        if not self._is_fitted:
            raise UnfittedError(
                "ConstantProcessor must be fitted before inverse_transform"
            )

        # 還原 constant columns
        if self._constant_columns:
            result = data.copy()

            # 將 constant columns 加回去
            for col_name, const_value in self._constant_columns.items():
                result[col_name] = const_value

            # 恢復原始欄位順序
            # 只保留存在的欄位（某些欄位可能在處理過程中被移除）
            final_columns = [
                col for col in self._original_columns if col in result.columns
            ]
            # 加上新增的欄位（如果有的話）
            new_columns = [col for col in result.columns if col not in final_columns]
            result = result[final_columns + new_columns]

            return result

        return data.copy()

    @property
    def is_fitted(self) -> bool:
        """Check if the processor is fitted"""
        return self._is_fitted

    @property
    def constant_columns(self) -> dict[str, Any]:
        """獲取 constant columns 及其值"""
        return self._constant_columns.copy()
