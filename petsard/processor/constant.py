from __future__ import annotations

from typing import Any

import pandas as pd

from petsard.exceptions import UnfittedError


class ConstantProcessor:
    """Processor for handling constant columns

    This processor:
    1. Records constant field values during fit()
    2. Removes constant fields during transform() (to avoid affecting synthesizers)
    3. Restores constant fields during inverse_transform()

    This is a special processor that always executes before all other processors.
    """

    def __init__(self) -> None:
        """Initialize ConstantProcessor"""
        self._is_fitted: bool = False
        self._constant_columns: dict[str, Any] = {}  # Record constant field values
        self._original_columns: list[str] = []  # Record original field order

    def fit(self, data: pd.DataFrame, metadata: Any) -> None:
        """Fit the processor

        Args:
            data: Training data
            metadata: Schema metadata containing is_constant flag
        """
        self._constant_columns = {}
        self._original_columns = list(data.columns)

        # Check if each field is constant
        for col_name in data.columns:
            # Get is_constant flag from metadata
            if hasattr(metadata, "attributes") and col_name in metadata.attributes:
                attribute = metadata.attributes[col_name]
                if hasattr(attribute, "is_constant") and attribute.is_constant:
                    # Record the constant value of this field
                    non_na_values = data[col_name].dropna()
                    if len(non_na_values) > 0:
                        self._constant_columns[col_name] = non_na_values.iloc[0]

        self._is_fitted = True

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the data (remove constant columns)

        Args:
            data: Data to transform

        Returns:
            Data after removing constant columns
        """
        if not self._is_fitted:
            raise UnfittedError("ConstantProcessor must be fitted before transform")

        # Remove constant columns
        if self._constant_columns:
            remaining_cols = [
                col for col in data.columns if col not in self._constant_columns
            ]
            return data[remaining_cols].copy()

        return data.copy()

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform the data (restore constant columns)

        Args:
            data: Data to inverse transform

        Returns:
            Data after restoring constant columns
        """
        if not self._is_fitted:
            raise UnfittedError(
                "ConstantProcessor must be fitted before inverse_transform"
            )

        # Restore constant columns
        if self._constant_columns:
            result = data.copy()

            # Add constant columns back
            for col_name, const_value in self._constant_columns.items():
                result[col_name] = const_value

            # Restore original field order
            # Only keep existing fields (some fields may have been removed during processing)
            final_columns = [
                col for col in self._original_columns if col in result.columns
            ]
            # Add new fields (if any)
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
        """Get constant columns and their values"""
        return self._constant_columns.copy()
