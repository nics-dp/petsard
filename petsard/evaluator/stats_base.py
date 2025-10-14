import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)

from petsard.utils import safe_round


class BaseStats(ABC):
    """
    Base class for statistics evaluation.
    """

    def __init__(self):
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

    @abstractmethod
    def _verify_dtype(self) -> bool:
        """
        Verifies the data type of the statistics.

        Returns:
            (bool): True if the data type verification passes, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        error_msg: str = (
            f"Method _verify_dtype is not implemented for {self.__class__.__name__}."
        )
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)

    def eval(self, data: dict[str, pd.Series]) -> int | float:
        """
        Evaluates the statistics and returns the result.
            safe_round is used to round 6 digits the result if it is a float.

        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (int | float): The result of the statistics evaluation.
        """
        self._logger.debug(f"Evaluating statistics with {self.__class__.__name__}")

        if not self._verify_dtype(data):
            error_msg: str = (
                f"Data type verification failed for {self.__class__.__name__}."
            )
            self._logger.error(error_msg)
            raise TypeError(error_msg)

        result: int | float = self._eval(data=data)
        self._logger.debug(f"Statistics result: {result}")
        return safe_round(result) if isinstance(result, float) else result

    @abstractmethod
    def _eval(self, data: pd.DataFrame) -> int | float:
        """
        Performs the evaluation of the statistics.

        Args:
            data (pd.DataFrame): The data to be evaluated.

        Returns:
            (int | float): The result of the statistics evaluation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        error_msg: str = (
            f"Method _eval is not implemented for {self.__class__.__name__}."
        )
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)


class StatsMean(BaseStats):
    """
    A class of column-wise statistic for the mean.
        Inherits from BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the data type is numeric/datetime64, False otherwise.
        """
        return is_numeric_dtype(data.get("col")) or is_datetime64_dtype(data.get("col"))

    def _eval(self, data: dict[str, pd.Series]) -> float:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (float): The mean value of the column.
        """
        return data.get("col").mean()


class StatsStd(BaseStats):
    """
    A class of column-wise statistic for the standard deviation.
        Inherits from BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the data type is numeric/datetime64, False otherwise.
        """
        return is_numeric_dtype(data.get("col")) or is_datetime64_dtype(data.get("col"))

    def _eval(self, data: dict[str, pd.Series]) -> float:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (float): The standard deviation of the column.
        """
        return data.get("col").std()


class StatsMedian(BaseStats):
    """
    A class of column-wise statistic for the median.
        Inherits from BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the data type is numeric/datetime64, False otherwise.
        """
        return is_numeric_dtype(data.get("col")) or is_datetime64_dtype(data.get("col"))

    def _eval(self, data: dict[str, pd.Series]) -> int | float:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (int | float): The median of the column.
        """
        return data.get("col").median()


class StatsMin(BaseStats):
    """
    A class of column-wise statistic for the min.
        Inherits from BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the data type is numeric/datetime64, False otherwise.
        """
        return is_numeric_dtype(data.get("col")) or is_datetime64_dtype(data.get("col"))

    def _eval(self, data: dict[str, pd.Series]) -> int | float:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (int | float): The min of the column.
        """
        return data.get("col").min()


class StatsMax(BaseStats):
    """
    A class of column-wise statistic for the max.
        Inherits from BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the data type is numeric/datetime64, False otherwise.
        """
        return is_numeric_dtype(data.get("col")) or is_datetime64_dtype(data.get("col"))

    def _eval(self, data: dict[str, pd.Series]) -> int | float:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (int | float): The max of the column.
        """
        return data.get("col").max()


class StatsNUnique(BaseStats):
    """
    A class of column-wise statistic for the number of unique values.
        Inherits from the BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True for all data types - nunique can be calculated for any type.
        """
        # nunique 可以計算任何資料類型的唯一值數量
        # 不再限制資料類型
        return True

    def _eval(self, data: dict[str, pd.Series]) -> int:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (int): The number of unique values in the column.
        """
        return data.get("col").nunique(dropna=True)


class StatsJSDivergence(BaseStats):
    """
    A class of pair-wise statistic for the Jensen–Shannon divergence.
        Inherits from the BaseStats.
    """

    def _verify_dtype(self, data: dict[str, pd.Series]) -> bool:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (bool): True if the both data types are compatible for JS divergence calculation.
                This includes bool/string/category/object types, as well as numeric types
                that are treated as categorical (e.g., discrete values).
        """
        from pandas.api.types import is_categorical_dtype

        col_ori = data.get("col_ori")
        col_syn = data.get("col_syn")

        # 如果任一欄位不存在，返回 False
        if col_ori is None or col_syn is None:
            return False

        # JS divergence 可以計算任何離散型資料
        # 包括：bool、string、categorical、object 或作為類別使用的數值型態
        return (
            (is_bool_dtype(col_ori) and is_bool_dtype(col_syn))
            or (is_string_dtype(col_ori) and is_string_dtype(col_syn))
            or (is_categorical_dtype(col_ori) and is_categorical_dtype(col_syn))
            or (is_object_dtype(col_ori) and is_object_dtype(col_syn))
            # 允許數值型態（當作類別變數處理）
            or (is_numeric_dtype(col_ori) and is_numeric_dtype(col_syn))
        )

    def _eval(self, data: dict[str, pd.Series]) -> int:
        """
        Args:
            data (dict[str, pd.Series]): The data to be evaluated.

        Returns:
            (float): The Jensen-Shannon divergence of column pair.
        """
        from scipy.spatial.distance import jensenshannon

        value_cnts_ori = data.get("col_ori").value_counts(normalize=True)
        value_cnts_syn = data.get("col_syn").value_counts(normalize=True)

        all_categories = set(value_cnts_ori.index) | set(value_cnts_syn.index)

        p = np.array([value_cnts_ori.get(cat, 0) for cat in all_categories])
        q = np.array([value_cnts_syn.get(cat, 0) for cat in all_categories])

        return jensenshannon(p, q) ** 2
