import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from petsard.config_base import BaseConfig
from petsard.evaluator.describer_describe import DescriberDescribe
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.evaluator.stats_base import StatsJSDivergence
from petsard.exceptions import UnsupportedMethodError
from petsard.utils import safe_round


@dataclass
class CompareConfig(BaseConfig):
    """
    Configuration for the Compare Evaluator.

    Attributes:
        eval_method (str): The evaluation method.
        eval_method_code (int): The evaluation method code.
        AVAILABLE_STATS_METHODS (list[str]): The available statistics methods.
        AVAILABLE_COMPARE_METHODS (list[str]): The available compare methods.
        AVAILABLE_AGGREGATED_METHODS (list[str]): The available aggregated methods.
        AVAILABLE_SUMMARY_METHODS (list[str]): The available summary methods.
        REQUIRED_INPUT_KEYS (list[str]): The required input keys.
        stats_method (list[str]): The statistics methods to use.
        compare_method (str): The compare method.
        aggregated_method (str): The aggregated method.
        summary_method (str): The summary method.
    """

    eval_method: str
    eval_method_code: int | None = None
    AVAILABLE_STATS_METHODS: list[str] = field(
        default_factory=lambda: [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "nunique",
            "jsdivergence",
        ]
    )
    AVAILABLE_COMPARE_METHODS: list[str] = field(
        default_factory=lambda: ["diff", "pct_change"]
    )
    AVAILABLE_AGGREGATED_METHODS: list[str] = field(default_factory=lambda: ["mean"])
    AVAILABLE_SUMMARY_METHODS: list[str] = field(default_factory=lambda: ["mean"])
    REQUIRED_INPUT_KEYS: list[str] = field(default_factory=lambda: ["base", "target"])
    stats_method: list[str] = field(
        default_factory=lambda: [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "nunique",
            "jsdivergence",
        ]
    )
    compare_method: str = "pct_change"
    aggregated_method: str = "mean"
    summary_method: str = "mean"

    def __post_init__(self):
        super().__post_init__()
        error_msg: str | None = None

        invalid_methods: list[str] = [
            method
            for method in self.stats_method
            if method not in self.AVAILABLE_STATS_METHODS
        ]
        if invalid_methods:
            error_msg = (
                f"Invalid stats method: {invalid_methods}. "
                f"Available methods are: {self.AVAILABLE_STATS_METHODS}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.compare_method not in self.AVAILABLE_COMPARE_METHODS:
            error_msg = f"Invalid compare method: {self.compare_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.aggregated_method not in self.AVAILABLE_AGGREGATED_METHODS:
            error_msg = f"Invalid aggregated method: {self.aggregated_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        if self.summary_method not in self.AVAILABLE_SUMMARY_METHODS:
            error_msg = f"Invalid summary method: {self.summary_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)


class DescriberCompare(BaseEvaluator):
    """
    Evaluator for Describer Compare method - handles dataset comparison.
    This class reuses DescriberDescribe for basic statistics and adds comparison logic.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["base", "target"]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration assign by Evaluator.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self._logger.debug(f"Verifying CompareConfig with parameters: {self.config}")
        self.compare_config = CompareConfig(**self.config)
        self._logger.debug("CompareConfig successfully initialized")

        # 準備 DescriberDescribe 的設定
        # 過濾掉 jsdivergence，因為它需要特殊處理
        describe_methods = [
            m for m in self.compare_config.stats_method if m != "jsdivergence"
        ]

        # 從原始 config 中複製必要的參數並添加 eval_method
        describe_config = {
            "eval_method": "describe",  # 必需的參數
            "describe_method": describe_methods,
        }

        # 如果原始 config 中有其他需要的參數，也複製過去
        if "percentile" in self.config:
            describe_config["percentile"] = self.config["percentile"]

        # 創建兩個 DescriberDescribe 實例來處理 ori 和 syn
        self.ori_describer = DescriberDescribe(config=describe_config.copy())
        self.syn_describer = DescriberDescribe(config=describe_config.copy())

        self.metadata = None  # Store metadata for later use

    COMPARE_METHOD_MAP: dict[str, dict[str, callable]] = {
        "diff": {
            "func": lambda syn, ori: syn - ori,
            "handle_zero": lambda syn, ori: syn - ori,
        },
        "pct_change": {
            "func": lambda syn, ori: (syn - ori) / abs(ori),
            "handle_zero": lambda syn, ori: np.nan,
        },
    }
    AGGREGATED_METHOD_MAP: dict[str, callable] = {
        "mean": lambda df: {k: safe_round(v) for k, v in df.mean().to_dict().items()}
    }
    SUMMARY_METHOD_MAP: dict[str, callable] = {
        "mean": lambda values: safe_round(np.mean(list(values)))
    }

    def _calculate_jsdivergence(
        self, base_data: pd.DataFrame, target_data: pd.DataFrame
    ) -> dict[str, float]:
        """
        計算 JS Divergence（需要同時處理兩個數據集）

        Args:
            base_data: Base dataset
            target_data: Target dataset

        Returns:
            Dictionary with JS divergence values for each column
        """
        result = {}
        common_cols = set(base_data.columns) & set(target_data.columns)

        for col in common_cols:
            try:
                js_div = StatsJSDivergence()
                value = js_div.eval(
                    {
                        "col_ori": base_data[
                            col
                        ],  # StatsJSDivergence 內部仍使用 ori/syn
                        "col_syn": target_data[col],
                    }
                )
                result[col] = value
            except (TypeError, ValueError) as e:
                self._logger.debug(
                    f"Cannot calculate JS divergence for column '{col}': {e}"
                )
                result[col] = np.nan

        return result

    def _apply_comparison(
        self, base_df: pd.DataFrame, target_df: pd.DataFrame, compare_method: str
    ) -> pd.DataFrame:
        """
        Apply comparison method between base and target statistics

        Args:
            base_df: Base statistics DataFrame
            target_df: Target statistics DataFrame
            compare_method: The comparison method to use
        """
        self._logger.debug(
            f"Applying comparison method '{compare_method}' to DataFrames"
        )

        method_info = self.COMPARE_METHOD_MAP.get(compare_method)
        if not method_info:
            error_msg = f"Unsupported comparison method: {compare_method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Ensure both DataFrames have the same index and columns
        # 確保兩個 DataFrame 有相同的索引和欄位
        common_cols = list(set(base_df.columns) & set(target_df.columns))
        common_index = list(set(base_df.index) & set(target_df.index))

        base_df = base_df.loc[common_index, common_cols]
        target_df = target_df.loc[common_index, common_cols]

        # Create result DataFrame containing base and target values
        # 建立結果 DataFrame，包含基準值和目標值
        result = pd.DataFrame(index=common_index)

        for col in common_cols:
            # Add base and target values
            # 添加基準值和目標值
            result[f"{col}_base"] = base_df[col]
            result[f"{col}_target"] = target_df[col]

            # Calculate comparison values
            # 計算比較值
            func = method_info["func"]
            handle_zero = method_info["handle_zero"]

            # Handle NA values - fill with NaN for numerical operations
            # To avoid FutureWarning, use pandas' future behavior
            # 處理 NA 值 - 先填充為 NaN 以便進行數值運算
            # 為了避免 FutureWarning，使用 pandas 的未來行為
            with pd.option_context("future.no_silent_downcasting", True):
                base_col_filled = base_df[col].fillna(np.nan).infer_objects(copy=False)
                target_col_filled = (
                    target_df[col].fillna(np.nan).infer_objects(copy=False)
                )

            comparison_values = func(target_col_filled, base_col_filled)

            # Apply safe_round element-wise if it's a Series, handling NA values
            if isinstance(comparison_values, pd.Series):
                # Use fillna to handle NA values before applying safe_round
                # Then replace NaN back to pd.NA for consistency
                rounded_values = comparison_values.apply(
                    lambda x: safe_round(x) if pd.notna(x) else np.nan
                )
            else:
                rounded_values = (
                    safe_round(comparison_values)
                    if pd.notna(comparison_values)
                    else np.nan
                )

            # Handle zero values and NA values
            # Only check for zero on non-NA base values
            # 處理零值和 NA 值
            # 只對非 NA 的基準值檢查是否為零
            is_zero = pd.Series(
                [float(v) == 0.0 if pd.notna(v) else False for v in base_df[col]],
                index=base_df[col].index,
            )

            result[f"{col}_{compare_method}"] = np.where(
                is_zero,
                handle_zero(target_col_filled, base_col_filled),
                rounded_values,
            )

        self._logger.debug(f"Comparison method '{compare_method}' applied successfully")
        return result

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the comparison by reusing DescriberDescribe

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated with 'ori' and 'syn' keys.

        Return:
            (dict[str, pd.DataFrame]): The evaluation result
        """
        self._logger.info(
            f"Starting comparison evaluation with {len(self.compare_config.stats_method)} methods"
        )

        # 使用 DescriberDescribe 分別描述 base 和 target
        # 支援向後相容：如果輸入是 ori/syn，映射到 base/target
        if "ori" in data and "base" not in data:
            data["base"] = data["ori"]
        if "syn" in data and "target" not in data:
            data["target"] = data["syn"]

        self._logger.debug("Describing base data")
        base_description = self.ori_describer.eval({"data": data["base"]})

        self._logger.debug("Describing target data")
        target_description = self.syn_describer.eval({"data": data["target"]})

        # 初始化結果字典
        compare_result: dict[str, pd.DataFrame] = {}

        # 處理 columnwise 統計的比較
        if "columnwise" in base_description and "columnwise" in target_description:
            base_columnwise = base_description["columnwise"]
            target_columnwise = target_description["columnwise"]

            # 應用比較方法
            compare_result["columnwise"] = self._apply_comparison(
                base_columnwise, target_columnwise, self.compare_config.compare_method
            )

            # 如果需要計算 JS Divergence，添加到結果中
            if "jsdivergence" in self.compare_config.stats_method:
                js_div_results = self._calculate_jsdivergence(
                    data["base"], data["target"]
                )
                for col, value in js_div_results.items():
                    if col in compare_result["columnwise"].index:
                        compare_result["columnwise"].loc[col, "jsdivergence"] = value

        # 處理 global 統計的比較（如果有）
        if "global" in base_description and "global" in target_description:
            base_global = base_description["global"]
            target_global = target_description["global"]

            # 合併 global 結果
            global_result = pd.DataFrame()
            for col in base_global.columns:
                if col in target_global.columns:
                    global_result[f"{col}_base"] = base_global[col]
                    global_result[f"{col}_target"] = target_global[col]

            if not global_result.empty:
                compare_result["global_stats"] = global_result

        # 計算聚合的全局分數
        if "columnwise" in compare_result:
            compare_cols = [
                col
                for col in compare_result["columnwise"].columns
                if col.endswith(f"_{self.compare_config.compare_method}")
            ]

            # 添加 jsdivergence 到比較欄位（如果存在）
            if "jsdivergence" in compare_result["columnwise"].columns:
                compare_cols.append("jsdivergence")

            if compare_cols:
                # 應用聚合方法
                global_result = self.AGGREGATED_METHOD_MAP[
                    self.compare_config.aggregated_method
                ](compare_result["columnwise"][compare_cols])

                # 應用總結方法計算最終分數
                score = self.SUMMARY_METHOD_MAP[self.compare_config.summary_method](
                    global_result.values()
                )

                global_result = {"Score": score, **global_result}
                compare_result["global"] = pd.DataFrame.from_dict(
                    global_result, orient="index"
                ).T

        self._logger.info("Comparison evaluation completed")
        return compare_result
