from dataclasses import dataclass, field
from enum import Enum, auto

from petsard.evaluator.describer_compare import DescriberCompare
from petsard.evaluator.describer_describe import DescriberDescribe
from petsard.evaluator.evaluator import Evaluator, EvaluatorConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import UnsupportedMethodError


class DescriberMethodMap(Enum):
    """
    Mapping of Describer methods.
    """

    DEFAULT: int = auto()
    DESCRIBE: int = auto()


@dataclass
class DescriberConfig(EvaluatorConfig):
    """
    Configuration for the describer.
        Inherits from EvaluatorConfig.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_EVALUATING_METHOD (str): The default method for evaluating the data.
        DEFAULT_DESCRIBING_METHOD (str): The default method for describing the data.
        method (str): The method to be used for evaluating the data.
        method_code (int): The code of the evaluator method.
        eval_method (str): The name of the evaluator method.
            The difference between 'method' and 'eval_method' is that 'method' is the user input,
            while 'eval_method' is the actual method used for evaluating the data
        custom_params (dict): Any additional parameters to be stored in custom_params.
        mode (str): The operation mode - 'describe' for single dataset or 'compare' for comparison

        # Stats-specific parameters (for compare mode)
        stats_method (list[str]): The statistics methods to use in compare mode
        compare_method (str): The comparison method ('diff' or 'pct_change')
        aggregated_method (str): The aggregation method for global results
        summary_method (str): The summary method for final score

    """

    DEFAULT_DESCRIBING_METHOD: str = "describe"
    mode: str = "describe"  # 'describe' or 'compare'

    # Stats-specific parameters with defaults
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

        # Validate Stats parameters if in compare mode
        if self.mode == "compare":
            self._validate_stats_params()

    def _validate_stats_params(self) -> None:
        """Validate Stats-specific parameters for compare mode."""
        AVAILABLE_STATS_METHODS = [
            "mean",
            "std",
            "median",
            "min",
            "max",
            "nunique",
            "jsdivergence",
        ]
        AVAILABLE_COMPARE_METHODS = ["diff", "pct_change"]
        AVAILABLE_AGGREGATED_METHODS = ["mean"]
        AVAILABLE_SUMMARY_METHODS = ["mean"]

        # Validate stats methods
        invalid_methods = [
            method
            for method in self.stats_method
            if method not in AVAILABLE_STATS_METHODS
        ]
        if invalid_methods:
            error_msg = (
                f"Invalid stats method: {invalid_methods}. "
                f"Available methods are: {AVAILABLE_STATS_METHODS}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Validate compare method
        if self.compare_method not in AVAILABLE_COMPARE_METHODS:
            error_msg = f"Invalid compare method: {self.compare_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Validate aggregated method
        if self.aggregated_method not in AVAILABLE_AGGREGATED_METHODS:
            error_msg = f"Invalid aggregated method: {self.aggregated_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Validate summary method
        if self.summary_method not in AVAILABLE_SUMMARY_METHODS:
            error_msg = f"Invalid summary method: {self.summary_method}."
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

    def _init_eval_method(self) -> None:
        """
        Initialize the eval_method attribute based on the method_code.
            Overridden EvaluatorConfig's _init_eval_method().
        """
        error_msg: str = None

        # Map method to code using DescriberMethodMap
        method_lower = self.method.lower()
        if method_lower in ["default", "describe"]:
            if method_lower == "default":
                self.method_code = DescriberMethodMap.DEFAULT
            else:
                self.method_code = DescriberMethodMap.DESCRIBE

            self._logger.debug(
                f"Mapped evaluating method '{self.method}' to code {self.method_code}"
            )
        else:
            error_msg = f"Unsupported describer method: {self.method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Set the default
        self.eval_method: str = (
            self.DEFAULT_DESCRIBING_METHOD
            if self.method_code == DescriberMethodMap.DEFAULT
            else self.method
        )
        self._logger.info(
            f"DescriberConfig initialized with method: {self.method}, eval_method: {self.eval_method}"
        )


class Describer(Evaluator):
    """
    The Describer class is responsible generate statistical summaries
    and insights from datasets. Can operate in two modes:
    - describe: Statistical summaries of single dataset (original functionality)
    - compare: Comparison between datasets (integrating Stats functionality)
    """

    DESCRIBER_MAP: dict[int, BaseEvaluator] = {
        DescriberMethodMap.DEFAULT: DescriberDescribe,
        DescriberMethodMap.DESCRIBE: DescriberDescribe,
    }

    def __init__(self, method: str, mode: str = "describe", **kwargs):
        """
        Args:
            method (str): The method to be used for evaluating the data.
            mode (str): The operation mode - 'describe' for single dataset or 'compare' for comparison
            **kwargs: Any additional parameters to be stored in custom_params.
                For compare mode, supports:
                - stats_method (list[str]): Statistics methods to compute
                - compare_method (str): Comparison method ('diff' or 'pct_change')
                - aggregated_method (str): Aggregation method for global results
                - summary_method (str): Summary method for final score

        Attr:
            _logger (logging.Logger): The logger object.
            config (DescriberConfig): The configuration parameters for the describer.
            _impl (BaseEvaluator): The evaluator object.
            mode (str): The operation mode
        """
        self.mode = mode
        kwargs["mode"] = mode  # Pass mode to config
        super().__init__(method, **kwargs)

    def _configure_implementation(self, method: str, **kwargs) -> None:
        """
        Configure the describer's implementation based on the specified method.
            Overridden Evaluator's _configure_implementation().

        Args:
            method (str): The method to be used for describe the data.
            **kwargs: Any additional parameters to be stored in custom_params.
        """
        # Extract mode and Stats-specific parameters
        mode = kwargs.pop("mode", "describe")

        # Extract Stats-specific parameters if present
        stats_params = {}
        if mode == "compare":
            # Extract Stats-specific parameters
            for param in [
                "stats_method",
                "compare_method",
                "aggregated_method",
                "summary_method",
            ]:
                if param in kwargs:
                    stats_params[param] = kwargs.pop(param)

        # Initialize the DescriberConfig object with mode and Stats parameters
        config_params = {"method": method, "mode": mode, **stats_params}
        self.config: DescriberConfig = DescriberConfig(**config_params)
        self._logger.debug(
            f"DescriberConfig successfully initialized with mode: {mode}"
        )

        # Add remaining custom parameters to the config
        if kwargs:
            self._logger.debug(
                f"Additional keyword arguments provided: {list(kwargs.keys())}"
            )
            self.config.update({"custom_params": kwargs})
            self._logger.debug("Config successfully updated with custom parameters")
        else:
            self._logger.debug("No additional parameters provided")

    def _create_evaluator_class(self) -> BaseEvaluator:
        """
        Create a Evaluator object with the configuration parameters.
            Overridden Evaluator's _create_evaluator_class().

        Returns:
            BaseEvaluator: The evaluator object.
        """
        # Use appropriate implementation based on mode
        if self.config.mode == "compare":
            # Use DescriberCompare for comparison mode
            return DescriberCompare
        else:
            # Use DescriberDescribe for single dataset mode
            return self.DESCRIBER_MAP[self.config.method_code]

    def create(self) -> None:
        """
        Create the evaluator implementation with proper configuration.
        Overrides the parent create() to handle Stats configuration.
        """
        if self.config.mode == "compare":
            # For compare mode, prepare configuration for DescriberCompare
            compare_config = {
                "eval_method": "compare",  # Updated for DescriberCompare
                "stats_method": self.config.stats_method,
                "compare_method": self.config.compare_method,
                "aggregated_method": self.config.aggregated_method,
                "summary_method": self.config.summary_method,
            }

            # Add any custom parameters
            if hasattr(self.config, "custom_params") and self.config.custom_params:
                compare_config.update(self.config.custom_params)

            # Create DescriberCompare instance with proper configuration
            evaluator_class = self._create_evaluator_class()
            self._impl = evaluator_class(config=compare_config)
            self._logger.debug(
                f"DescriberCompare evaluator created with config: {compare_config}"
            )
        else:
            # Use parent's create method for describe mode
            super().create()

    def eval(self, data: dict) -> dict:
        """
        Evaluate the data based on the configured mode.

        簡化版：資料驗證已在 DescriberAdapter 處理，這裡只執行評估

        Args:
            data (dict): Input data dictionary
                - For describe mode: {'data': DataFrame}
                - For compare mode: {'ori': DataFrame, 'syn': DataFrame}

        Returns:
            dict: Evaluation results
                - For describe mode: Statistical summaries
                - For compare mode: Comparison statistics with scores
        """
        # 簡單的驗證，確保資料格式正確
        if self.config.mode == "compare":
            # 支援新的 base/target 和舊的 ori/syn（向後相容）
            has_new_format = "base" in data and "target" in data
            has_old_format = "ori" in data and "syn" in data

            if not has_new_format and not has_old_format:
                error_msg = f"Compare mode requires 'base' and 'target' keys (or 'ori' and 'syn' for backward compatibility), got: {list(data.keys())}"
                self._logger.error(error_msg)
                raise ValueError(error_msg)

            # 如果使用舊格式，映射到新格式（這個轉換已在 DescriberCompare._eval 中處理）
            if has_old_format and not has_new_format:
                self._logger.debug(
                    "Using backward compatibility: ori/syn format detected"
                )
        else:  # describe mode
            if "data" not in data:
                error_msg = (
                    f"Describe mode requires 'data' key, got: {list(data.keys())}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)

        return super().eval(data)
