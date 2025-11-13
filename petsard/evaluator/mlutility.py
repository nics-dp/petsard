import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    fbeta_score,
    matthews_corrcoef,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from petsard.config_base import BaseConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.utils import safe_round


class TaskType(Enum):
    """Machine learning task types"""

    CLASSIFICATION = auto()
    REGRESSION = auto()
    CLUSTERING = auto()

    @classmethod
    def from_string(cls, value: str) -> "TaskType":
        """Convert string to task type"""
        mapping = {
            "classification": cls.CLASSIFICATION,
            "clustering": cls.CLUSTERING,
            "regression": cls.REGRESSION,
            # Aliases
            "class": cls.CLASSIFICATION,
            "cluster": cls.CLUSTERING,
            "reg": cls.REGRESSION,
        }

        value_lower = value.lower()
        if value_lower not in mapping:
            raise ValueError(f"Unsupported task type: {value}")
        return mapping[value_lower]


class MetricRegistry:
    """Metric registry - complete sklearn.metrics implementation"""

    # Default metrics
    DEFAULT_METRICS = {
        TaskType.CLASSIFICATION: [
            "f1_score",
            "roc_auc",
            "accuracy",
            "precision",
            "recall",
            "specificity",
            "mcc",
            "pr_auc",
            "tp",
            "tn",
            "fp",
            "fn",
        ],
        TaskType.REGRESSION: ["r2_score", "rmse"],  # Simplified default metrics
        TaskType.CLUSTERING: ["silhouette_score"],
    }

    @staticmethod
    def compute_confusion_matrix_metrics(y_true, y_pred):
        """Compute complete confusion matrix related metrics"""

        cm = confusion_matrix(y_true, y_pred)

        # Handle binary or multi-class classification
        if cm.shape == (2, 2):
            # Binary classification
            tn, fp, fn, tp = cm.ravel()
        else:
            # Multi-class classification: compute micro-average
            tp = np.diag(cm).sum()
            fp = cm.sum(axis=0) - np.diag(cm)
            fn = cm.sum(axis=1) - np.diag(cm)
            fp = fp.sum()
            fn = fn.sum()
            tn = cm.sum() - tp - fp - fn

        # Compute all derived metrics
        metrics = {
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tpr": tp / (tp + fn) if (tp + fn) > 0 else 0,  # Sensitivity, Recall
            "tnr": tn / (tn + fp) if (tn + fp) > 0 else 0,  # Specificity
            "ppv": tp / (tp + fp) if (tp + fp) > 0 else 0,  # Precision
            "npv": tn / (tn + fn) if (tn + fn) > 0 else 0,
            "fpr": fp / (fp + tn) if (fp + tn) > 0 else 0,
            "fnr": fn / (fn + tp) if (fn + tp) > 0 else 0,
            "fdr": fp / (fp + tp) if (fp + tp) > 0 else 0,
            "for": fn / (fn + tn) if (fn + tn) > 0 else 0,  # False Omission Rate
            "accuracy": (tp + tn) / (tp + tn + fp + fn)
            if (tp + tn + fp + fn) > 0
            else 0,
            "prevalence": (tp + fn) / (tp + tn + fp + fn)
            if (tp + tn + fp + fn) > 0
            else 0,
            "dor": (tp * tn) / (fp * fn)
            if (fp * fn) > 0
            else float("inf"),  # Diagnostic Odds Ratio
        }

        # Compute other statistical metrics
        metrics["sensitivity"] = metrics["tpr"]  # Synonym
        metrics["specificity"] = metrics["tnr"]  # Synonym
        metrics["precision"] = metrics["ppv"]  # Synonym
        metrics["recall"] = metrics["tpr"]  # Synonym
        metrics["informedness"] = metrics["tpr"] + metrics["tnr"] - 1  # Youden's J
        metrics["markedness"] = metrics["ppv"] + metrics["npv"] - 1

        return metrics

    # Built-in metric functions - complete sklearn.metrics
    BUILTIN_METRICS = {
        # Basic classification metrics
        "accuracy": accuracy_score,
        "f1_score": lambda y_true, y_pred: f1_score(
            y_true,
            y_pred,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
        ),
        "f2_score": lambda y_true, y_pred: fbeta_score(
            y_true,
            y_pred,
            beta=2,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
        ),
        "f0.5_score": lambda y_true, y_pred: fbeta_score(
            y_true,
            y_pred,
            beta=0.5,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
        ),
        "precision": lambda y_true, y_pred: precision_score(
            y_true,
            y_pred,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
            zero_division=0,
        ),
        "recall": lambda y_true, y_pred: recall_score(
            y_true,
            y_pred,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
            zero_division=0,
        ),
        "mcc": matthews_corrcoef,
        # Metrics requiring probabilities (special handling)
        "roc_auc": None,
        "pr_auc": None,
        # Confusion Matrix derived metrics (special handling)
        "tp": None,
        "tn": None,
        "fp": None,
        "fn": None,
        "tpr": None,
        "tnr": None,
        "ppv": None,
        "npv": None,
        "fpr": None,
        "fnr": None,
        "fdr": None,
        "for": None,
        "specificity": None,
        "sensitivity": None,
        "informedness": None,
        "markedness": None,
        "prevalence": None,
        "dor": None,
        # Regression metrics
        "r2_score": r2_score,
        "mse": mean_squared_error,
        "mae": mean_absolute_error,
        "rmse": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
        "mape": lambda y_true, y_pred: np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        if np.all(y_true != 0)
        else np.inf,
        # Clustering metrics
        "silhouette_score": silhouette_score,
    }

    # Metric task compatibility
    METRIC_TASK_COMPATIBILITY = {
        # Classification metrics
        "accuracy": [TaskType.CLASSIFICATION],
        "f1_score": [TaskType.CLASSIFICATION],
        "f2_score": [TaskType.CLASSIFICATION],
        "f0.5_score": [TaskType.CLASSIFICATION],
        "precision": [TaskType.CLASSIFICATION],
        "recall": [TaskType.CLASSIFICATION],
        "mcc": [TaskType.CLASSIFICATION],
        "roc_auc": [TaskType.CLASSIFICATION],
        "pr_auc": [TaskType.CLASSIFICATION],
        "tp": [TaskType.CLASSIFICATION],
        "tn": [TaskType.CLASSIFICATION],
        "fp": [TaskType.CLASSIFICATION],
        "fn": [TaskType.CLASSIFICATION],
        "tpr": [TaskType.CLASSIFICATION],
        "tnr": [TaskType.CLASSIFICATION],
        "ppv": [TaskType.CLASSIFICATION],
        "npv": [TaskType.CLASSIFICATION],
        "fpr": [TaskType.CLASSIFICATION],
        "fnr": [TaskType.CLASSIFICATION],
        "fdr": [TaskType.CLASSIFICATION],
        "for": [TaskType.CLASSIFICATION],
        "specificity": [TaskType.CLASSIFICATION],
        "sensitivity": [TaskType.CLASSIFICATION],
        "informedness": [TaskType.CLASSIFICATION],
        "markedness": [TaskType.CLASSIFICATION],
        "prevalence": [TaskType.CLASSIFICATION],
        "dor": [TaskType.CLASSIFICATION],
        # Regression metrics
        "r2_score": [TaskType.REGRESSION],
        "mse": [TaskType.REGRESSION],
        "mae": [TaskType.REGRESSION],
        "rmse": [TaskType.REGRESSION],
        "mape": [TaskType.REGRESSION],
        # Clustering metrics
        "silhouette_score": [TaskType.CLUSTERING],
    }

    def __init__(self):
        """Initialize metric registry"""
        self.custom_metrics = {}

    def register_metric(
        self, name: str, func: Callable, task_types: list[TaskType]
    ) -> None:
        """
        Register custom metric

        Args:
            name: Metric name
            func: Metric calculation function
            task_types: Applicable task types
        """
        self.custom_metrics[name] = func
        if name not in self.METRIC_TASK_COMPATIBILITY:
            self.METRIC_TASK_COMPATIBILITY[name] = task_types

    def get_metric(self, name: str) -> Callable:
        """
        Get metric function

        Args:
            name: Metric name

        Returns:
            Metric calculation function
        """
        if name in self.custom_metrics:
            return self.custom_metrics[name]
        if name in self.BUILTIN_METRICS:
            return self.BUILTIN_METRICS[name]
        raise ValueError(f"Unknown metric: {name}")

    def is_compatible(self, metric_name: str, task_type: TaskType) -> bool:
        """
        Check if metric is compatible with task type

        Args:
            metric_name: Metric name
            task_type: Task type

        Returns:
            Whether compatible
        """
        if metric_name in self.custom_metrics:
            # Custom metrics are compatible with all tasks by default
            return True

        if metric_name not in self.METRIC_TASK_COMPATIBILITY:
            return False

        return task_type in self.METRIC_TASK_COMPATIBILITY[metric_name]

    def get_default_metrics(self, task_type: TaskType) -> list[str]:
        """Get default metrics for task type"""
        return self.DEFAULT_METRICS.get(task_type, [])


@dataclass
class MLUtilityConfig(BaseConfig):
    """
    MLUtility evaluator configuration

    Attributes:
        eval_method: Evaluation method name (mlutility)
        experiment_design: Experiment design approach
            - 'dual_model_control': Dual model control group (default) - train ori and syn separately, test on control
            - 'domain_transfer': Domain transfer - train on syn, test on ori
        resampling: Imbalanced data handling method (classification tasks only)
            - None: No handling (default)
            - 'smote-enn': Use SMOTE-ENN to synthesize minority class and clean noisy samples
            - 'smote-tomek': Use SMOTE-Tomek to synthesize minority class and clean boundary samples
        task_type: Task type
        target: Target column (required for classification/regression tasks)
        metrics: Evaluation metrics to compute
        n_clusters: Number of clusters (default 5)
        xgb_params: Additional XGBoost parameters
        random_state: Random seed
    """

    eval_method: str
    experiment_design: str = "dual_model_control"
    resampling: str | None = None
    task_type: TaskType | None = None
    target: str | None = None
    metrics: list[str] | None = None
    n_clusters: int = 3
    xgb_params: dict = field(default_factory=dict)
    random_state: int = 42

    # Internal use
    REQUIRED_INPUT_KEYS: list[str] = field(
        default_factory=lambda: ["ori", "syn", "control"]
    )
    n_rows: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()

        # Parse task type
        if self.task_type is None:
            # Parse from eval_method
            method_suffix = self.eval_method.replace("mlutility-", "")
            try:
                self.task_type = TaskType.from_string(method_suffix)
            except ValueError as e:
                error_msg = (
                    f"Cannot parse task type from eval_method '{self.eval_method}': {e}"
                )
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg) from e
        elif isinstance(self.task_type, str):
            self.task_type = TaskType.from_string(self.task_type)

        # Validate target column
        if self.task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
            if not self.target:
                error_msg = f"Task type {self.task_type.name} requires a target column to be specified"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        elif self.task_type == TaskType.CLUSTERING:
            if self.target:
                self._logger.info(
                    "Clustering task does not require a target column, ignoring"
                )
                self.target = None

        # Validate experiment design
        if self.experiment_design not in ["dual_model_control", "domain_transfer"]:
            error_msg = f"Unsupported experiment design: {self.experiment_design}. Must be 'dual_model_control' or 'domain_transfer'"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Validate resampling method
        if self.resampling is not None and self.resampling != "None":
            if self.resampling not in ["smote-enn", "smote-tomek"]:
                error_msg = f"Unsupported resampling method: {self.resampling}. Supported methods are 'smote-enn' or 'smote-tomek'"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # Resampling is only for classification tasks
            if self.task_type != TaskType.CLASSIFICATION:
                error_msg = f"Resampling method {self.resampling} is only available for classification tasks"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            self._logger.info(
                f"Will use {self.resampling} for imbalanced data handling"
            )
        elif self.resampling == "None":
            # Treat string "None" as None
            self.resampling = None

        # Adjust required input keys
        if self.experiment_design == "domain_transfer":
            # Domain transfer only needs ori and syn
            self.REQUIRED_INPUT_KEYS = ["ori", "syn"]

        # Set default metrics
        metric_registry = MetricRegistry()
        if self.metrics is None:
            self.metrics = metric_registry.get_default_metrics(self.task_type)
            self._logger.info(f"Using default metrics: {self.metrics}")
        else:
            # Validate metric compatibility
            incompatible = []
            for metric in self.metrics:
                if not metric_registry.is_compatible(metric, self.task_type):
                    incompatible.append(metric)

            if incompatible:
                error_msg = f"The following metrics are incompatible with task type {self.task_type.name}: {incompatible}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

    def update_data(self, data: dict[str, pd.DataFrame]) -> None:
        """
        Validate and update data-related configuration

        Args:
            data: Input data dictionary
        """
        # Validate required keys
        if not all(key in data for key in self.REQUIRED_INPUT_KEYS):
            error_msg = f"Missing required data keys: {self.REQUIRED_INPUT_KEYS}"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Validate data is not empty
        for key in self.REQUIRED_INPUT_KEYS:
            df = data[key].dropna()
            if df.empty:
                error_msg = f"{key} data is empty after removing missing values"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        # Validate target column exists
        if self.target:
            for key in self.REQUIRED_INPUT_KEYS:
                if self.target not in data[key].columns:
                    error_msg = (
                        f"Target column '{self.target}' does not exist in {key} data"
                    )
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

        # Record data sizes
        self.n_rows = {key: data[key].shape[0] for key in self.REQUIRED_INPUT_KEYS}
        self._logger.debug(f"Data row counts: {self.n_rows}")


class MLUtility(BaseEvaluator):
    """
    Simplified machine learning utility evaluator

    Uses XGBoost for classification and regression, K-means for clustering
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn", "control"]
    AVAILABLE_SCORES_GRANULARITY: list[str] = ["global", "details"]

    def __init__(self, config: dict):
        """
        Initialize evaluator

        Args:
            config: Configuration dictionary
        """
        super().__init__(config=config)
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

        self._logger.debug(f"Initializing MLUtilityConfig: {self.config}")
        self.mlutility_config = MLUtilityConfig(**self.config)
        self._logger.debug("MLUtilityConfig initialization successful")

        self.metric_registry = MetricRegistry()
        self._impl = None
        self._schema = None  # Store schema to determine column types

    def _preprocess_data(
        self, data: dict[str, pd.DataFrame], schema=None
    ) -> tuple[dict[str, dict], str]:
        """
        Data preprocessing

        Simplified preprocessing flow:
        1. Remove missing values
        2. Encode categorical variables (using OneHotEncoder)
        3. Standardize numerical features
        4. Handle imbalanced data (classification tasks only, apply SMOTE-ENN or SMOTE-Tomek on training data)

        Important: To avoid data leakage, only use ori and syn data to train encoders and scalers.
        - OneHotEncoder set handle_unknown='ignore' to handle unseen categories
        - control data uses trained transformers for transformation

        Args:
            data: Raw data
            schema: Data schema, used to determine column types

        Returns:
            (Preprocessed data, status code)
        """
        processed_data = {}

        # Copy data
        data_copy = {key: data[key].copy() for key in self.REQUIRED_INPUT_KEYS}

        # Remove missing values
        for key in self.REQUIRED_INPUT_KEYS:
            data_copy[key] = data_copy[key].dropna()
            if data_copy[key].empty:
                return None, "empty_after_dropna"

        # Separate features and target
        if self.mlutility_config.target:
            # Classification/regression task
            target_col = self.mlutility_config.target

            # Extract target column first (after dropna)
            y_data = {
                key: data_copy[key][target_col].copy()
                for key in self.REQUIRED_INPUT_KEYS
            }

            # Check if target is constant
            for key in self.REQUIRED_INPUT_KEYS:
                if data_copy[key][target_col].nunique() == 1:
                    return None, "constant_target"

            # Prepare features (exclude target column)
            feature_cols = [
                col for col in data_copy["ori"].columns if col != target_col
            ]

            # Separate feature data
            X_data = {
                key: data_copy[key][feature_cols].copy()
                for key in self.REQUIRED_INPUT_KEYS
            }

            # Separate numerical and categorical features
            # Conservative check: if any dataset contains non-numeric content, treat as categorical
            numerical_cols = []
            categorical_cols = []

            for col in feature_cols:
                is_categorical = False

                # Check all datasets
                for key in self.REQUIRED_INPUT_KEYS:
                    if col not in data_copy[key].columns:
                        continue

                    # Check dtype first
                    dtype = data_copy[key][col].dtype
                    if dtype == "object" or dtype.name == "category":
                        is_categorical = True
                        break

                    # For non-object types, try converting to numeric to confirm
                    try:
                        # Try converting to numeric, if it fails it's categorical
                        pd.to_numeric(data_copy[key][col], errors="raise")
                    except (ValueError, TypeError):
                        # Cannot convert to numeric, treat as categorical column
                        is_categorical = True
                        break

                if is_categorical:
                    categorical_cols.append(col)
                else:
                    numerical_cols.append(col)

            self._logger.debug(f"Categorical columns: {categorical_cols}")
            self._logger.debug(f"Numerical columns: {numerical_cols}")

            # Process categorical features (using OneHotEncoder)
            encoded_features = {}
            if categorical_cols:
                encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

                # Only use ori and syn data to train encoder to avoid data leakage
                # handle_unknown='ignore' will encode unseen categories in control as all-zero vectors
                train_cat_data = pd.concat(
                    [
                        data_copy["ori"][categorical_cols],
                        data_copy["syn"][categorical_cols],
                    ]
                )
                encoder.fit(train_cat_data)

                # Encode categorical features for each dataset
                for key in self.REQUIRED_INPUT_KEYS:
                    encoded = encoder.transform(data_copy[key][categorical_cols])
                    # Create encoded column names
                    encoded_cols = []
                    for i, col in enumerate(categorical_cols):
                        for cat in encoder.categories_[i]:
                            encoded_cols.append(f"{col}_{cat}")

                    # Store encoded features
                    encoded_features[key] = pd.DataFrame(
                        encoded, columns=encoded_cols, index=data_copy[key].index
                    )

            # Merge numerical features and encoded categorical features
            for key in self.REQUIRED_INPUT_KEYS:
                if categorical_cols:
                    # Merge numerical and encoded categorical features
                    X_features = pd.concat(
                        [
                            data_copy[key][numerical_cols].reset_index(drop=True),
                            encoded_features[key].reset_index(drop=True),
                        ],
                        axis=1,
                    )
                else:
                    # Only numerical features
                    X_features = X_data[key][numerical_cols]

                X_data[key] = X_features

            # Standardize features
            # Only use ori and syn data to compute mean and std to avoid data leakage
            scaler_X = StandardScaler()
            X_train = pd.concat([X_data["ori"], X_data["syn"]])
            scaler_X.fit(X_train)

            # Process target variable
            if self.mlutility_config.task_type == TaskType.CLASSIFICATION:
                # Check if target column is already numeric
                first_target = y_data["ori"]

                if pd.api.types.is_numeric_dtype(first_target):
                    # Target is already numeric, use directly
                    self._logger.info(
                        f"Target column '{target_col}' is already numeric, no encoding needed"
                    )

                    for key in self.REQUIRED_INPUT_KEYS:
                        X_scaled = scaler_X.transform(X_data[key])
                        y_encoded = y_data[key].values
                else:
                    # Target is categorical, needs encoding
                    self._logger.info(
                        f"Target column '{target_col}' is categorical, using LabelEncoder"
                    )

                    # Use only ori and syn data to build label encoding to avoid data leakage
                    label_encoder = LabelEncoder()
                    y_train = pd.concat([y_data["ori"], y_data["syn"]])
                    label_encoder.fit(y_train)

                    for key in self.REQUIRED_INPUT_KEYS:
                        X_scaled = scaler_X.transform(X_data[key])
                        y_encoded = label_encoder.transform(y_data[key])

                        # Apply imbalanced data handling to training data
                        if self.mlutility_config.resampling and key in ["ori", "syn"]:
                            # Only resample training data (ori and syn), not test data (control)
                            try:
                                # Conditionally import imbalanced-learn package
                                if self.mlutility_config.resampling == "smote-enn":
                                    try:
                                        from imblearn.combine import SMOTEENN
                                    except ImportError as import_err:
                                        raise ImportError(
                                            "imbalanced-learn package is required for SMOTE-ENN resampling.\n"
                                            "Please install: pip install imbalanced-learn"
                                        ) from import_err

                                    self._logger.info(
                                        f"Applying SMOTE-ENN resampling to {key} data"
                                    )
                                    resampler = SMOTEENN(
                                        random_state=self.mlutility_config.random_state
                                    )
                                else:  # smote-tomek
                                    try:
                                        from imblearn.combine import SMOTETomek
                                    except ImportError as import_err:
                                        raise ImportError(
                                            "imbalanced-learn package is required for SMOTE-Tomek resampling.\n"
                                            "Please install: pip install imbalanced-learn"
                                        ) from import_err

                                    self._logger.info(
                                        f"Applying SMOTE-Tomek resampling to {key} data"
                                    )
                                    resampler = SMOTETomek(
                                        random_state=self.mlutility_config.random_state
                                    )

                                X_resampled, y_resampled = resampler.fit_resample(
                                    X_scaled, y_encoded
                                )
                                self._logger.info(
                                    f"{key} data resampled: {len(y_encoded)} → {len(y_resampled)} samples"
                                )

                                processed_data[key] = {
                                    "X": X_resampled,
                                    "y": y_resampled,
                                }
                            except ImportError:
                                # Re-raise ImportError
                                raise
                            except Exception as e:
                                self._logger.warning(
                                    f"{self.mlutility_config.resampling.upper()} processing failed: {e}, using original data"
                                )
                                processed_data[key] = {
                                    "X": X_scaled,
                                    "y": y_encoded,
                                }
                        else:
                            # control data or no resampling enabled
                            processed_data[key] = {
                                "X": X_scaled,
                                "y": y_encoded,
                            }
            else:
                # Regression task, standardize target
                # Only use ori and syn data to compute target mean and std
                scaler_y = StandardScaler()
                y_train = pd.concat([y_data["ori"], y_data["syn"]]).values.reshape(
                    -1, 1
                )
                scaler_y.fit(y_train)

                for key in self.REQUIRED_INPUT_KEYS:
                    processed_data[key] = {
                        "X": scaler_X.transform(X_data[key]),
                        "y": scaler_y.transform(
                            y_data[key].values.reshape(-1, 1)
                        ).ravel(),
                    }
        else:
            # Clustering task
            # Separate numerical and categorical features
            feature_cols = list(data_copy["ori"].columns)
            numerical_cols = []
            categorical_cols = []

            for col in feature_cols:
                is_categorical = False

                # Check all datasets
                for key in self.REQUIRED_INPUT_KEYS:
                    if col not in data_copy[key].columns:
                        continue

                    # Check dtype first
                    dtype = data_copy[key][col].dtype
                    if dtype == "object" or dtype.name == "category":
                        is_categorical = True
                        break

                    # For non-object types, try converting to numeric to confirm
                    try:
                        pd.to_numeric(data_copy[key][col], errors="raise")
                    except (ValueError, TypeError):
                        is_categorical = True
                        break

                if is_categorical:
                    categorical_cols.append(col)
                else:
                    numerical_cols.append(col)

            self._logger.debug(f"Categorical columns: {categorical_cols}")
            self._logger.debug(f"Numerical columns: {numerical_cols}")

            # Process categorical features
            encoded_features = {}
            if categorical_cols:
                encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

                # Only use ori and syn data to train encoder
                train_cat_data = pd.concat(
                    [
                        data_copy["ori"][categorical_cols],
                        data_copy["syn"][categorical_cols],
                    ]
                )
                encoder.fit(train_cat_data)

                # Encode categorical features for each dataset
                for key in self.REQUIRED_INPUT_KEYS:
                    encoded = encoder.transform(data_copy[key][categorical_cols])
                    # Create encoded column names
                    encoded_cols = []
                    for i, col in enumerate(categorical_cols):
                        for cat in encoder.categories_[i]:
                            encoded_cols.append(f"{col}_{cat}")

                    # Store encoded features
                    encoded_features[key] = pd.DataFrame(
                        encoded, columns=encoded_cols, index=data_copy[key].index
                    )

            # Merge numerical features and encoded categorical features
            X_data = {}
            for key in self.REQUIRED_INPUT_KEYS:
                if categorical_cols:
                    # Merge numerical and encoded categorical features
                    X_features = pd.concat(
                        [
                            data_copy[key][numerical_cols].reset_index(drop=True),
                            encoded_features[key].reset_index(drop=True),
                        ],
                        axis=1,
                    )
                else:
                    # Only numerical features
                    X_features = data_copy[key][numerical_cols]

                X_data[key] = X_features

            # Standardize features
            # Only use ori and syn data to compute mean and std
            scaler = StandardScaler()
            X_train = pd.concat([X_data["ori"], X_data["syn"]])
            scaler.fit(X_train)

            for key in self.REQUIRED_INPUT_KEYS:
                processed_data[key] = {"X": scaler.transform(X_data[key])}

        return processed_data, "success"

    def _evaluate_classification(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict[str, float]:
        """
        Classification task evaluation

        Uses XGBoost classifier, supports complete sklearn.metrics
        """
        # Train model
        model = XGBClassifier(
            random_state=self.mlutility_config.random_state,
            **self.mlutility_config.xgb_params,
        )
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Compute metrics requiring probabilities
        try:
            y_proba = model.predict_proba(X_test)
            has_proba = True
        except Exception:
            has_proba = False

        # Compute confusion matrix derived metrics
        cm_metrics = self.metric_registry.compute_confusion_matrix_metrics(
            y_test, y_pred
        )

        # Compute metrics
        results = {}
        for metric_name in self.mlutility_config.metrics:
            # Check if it's a confusion matrix derived metric
            if metric_name in cm_metrics:
                results[metric_name] = cm_metrics[metric_name]
                continue

            # Check if probabilities are needed
            if metric_name in ["roc_auc", "pr_auc"]:
                if not has_proba:
                    results[metric_name] = np.nan
                    continue

                # Compute metrics requiring probabilities
                if metric_name == "roc_auc":
                    # Handle binary and multi-class classification
                    if len(np.unique(y_test)) == 2:
                        # Binary classification
                        results[metric_name] = roc_auc_score(y_test, y_proba[:, 1])
                    else:
                        # Multi-class classification
                        try:
                            results[metric_name] = roc_auc_score(
                                y_test, y_proba, multi_class="ovr", average="weighted"
                            )
                        except ValueError:
                            results[metric_name] = np.nan

                elif metric_name == "pr_auc":
                    # Precision-Recall AUC
                    if len(np.unique(y_test)) == 2:
                        precision, recall, _ = precision_recall_curve(
                            y_test, y_proba[:, 1]
                        )
                        results[metric_name] = auc(recall, precision)
                    else:
                        # Multi-class: compute average
                        pr_aucs = []
                        for i in range(y_proba.shape[1]):
                            y_true_binary = (y_test == i).astype(int)
                            precision, recall, _ = precision_recall_curve(
                                y_true_binary, y_proba[:, i]
                            )
                            pr_aucs.append(auc(recall, precision))
                        results[metric_name] = np.mean(pr_aucs)
            else:
                # General metrics
                metric_func = self.metric_registry.get_metric(metric_name)
                if metric_func is not None:
                    try:
                        results[metric_name] = metric_func(y_test, y_pred)
                    except Exception as e:
                        self._logger.warning(
                            f"Failed to compute metric {metric_name}: {e}"
                        )
                        results[metric_name] = np.nan
                else:
                    results[metric_name] = np.nan

        return results

    def _evaluate_regression(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict[str, float]:
        """
        Regression task evaluation

        Uses XGBoost regressor
        """
        # Train model
        model = XGBRegressor(
            random_state=self.mlutility_config.random_state,
            **self.mlutility_config.xgb_params,
        )
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Compute metrics
        results = {}
        for metric_name in self.mlutility_config.metrics:
            metric_func = self.metric_registry.get_metric(metric_name)
            results[metric_name] = metric_func(y_test, y_pred)

        return results

    def _evaluate_clustering(
        self, X_train: np.ndarray, X_test: np.ndarray
    ) -> dict[str, float]:
        """
        Clustering task evaluation

        Uses K-means
        """
        # Train model
        model = KMeans(
            n_clusters=self.mlutility_config.n_clusters,
            random_state=self.mlutility_config.random_state,
            n_init="auto",
        )
        model.fit(X_train)

        # Predict
        labels = model.predict(X_test)

        # Compute metrics
        results = {}
        for metric_name in self.mlutility_config.metrics:
            if metric_name == "silhouette_score":
                # Silhouette score needs special handling
                try:
                    score = silhouette_score(X_test, labels)
                except ValueError:
                    # Only one cluster or too few samples
                    score = -1.0
                results[metric_name] = score
            else:
                metric_func = self.metric_registry.get_metric(metric_name)
                results[metric_name] = metric_func(X_test, labels)

        return results

    def _get_global_scores(self, results: dict[str, dict[str, float]]) -> pd.DataFrame:
        """
        Compute global scores

        Args:
            results: Evaluation results for each dataset

        Returns:
            Global scores DataFrame
        """
        # Compute statistics for each metric
        global_scores = []

        if self.mlutility_config.experiment_design == "domain_transfer":
            # Domain transfer mode: only show syn_to_ori value
            for metric_name in self.mlutility_config.metrics:
                syn_to_ori_score = results.get("syn_to_ori", {}).get(
                    metric_name, np.nan
                )

                global_scores.append(
                    {
                        "metric": metric_name,
                        "syn_to_ori": safe_round(syn_to_ori_score),
                    }
                )
        else:
            # Dual model control mode: horizontal display of ori/syn/diff
            for metric_name in self.mlutility_config.metrics:
                ori_score = results.get("ori", {}).get(metric_name, np.nan)
                syn_score = results.get("syn", {}).get(metric_name, np.nan)

                global_scores.append(
                    {
                        "metric": metric_name,
                        "ori": safe_round(ori_score),
                        "syn": safe_round(syn_score),
                        "diff": safe_round(syn_score - ori_score),
                    }
                )

        return pd.DataFrame(global_scores)

    def _eval(self, data: dict[str, pd.DataFrame], schema=None) -> dict:
        """
        Execute evaluation

        Args:
            data: Input data
            schema: Data schema (optional)

        Returns:
            Evaluation results
        """
        # Adjust data requirements based on experiment design
        if self.mlutility_config.experiment_design == "domain_transfer":
            # Domain transfer mode: only needs ori and syn
            if "ori" not in data or "syn" not in data:
                raise ConfigError("Domain transfer mode requires 'ori' and 'syn' data")
            # Create virtual control for preprocessing compatibility
            if "control" not in data:
                data["control"] = data["ori"].copy()
                self._logger.info("Domain transfer mode: using ori as test set")
        else:
            # Dual model control mode: requires all three datasets
            if not all(key in data for key in ["ori", "syn", "control"]):
                raise ConfigError(
                    "Dual model control mode requires 'ori', 'syn', 'control' data"
                )

        # Update configuration
        self.mlutility_config.update_data(data)

        # Store schema
        if schema is not None:
            self._schema = schema

        # Preprocess with schema
        processed_data, status = self._preprocess_data(data, schema=self._schema)

        if status != "success":
            self._logger.warning(f"Preprocessing failed: {status}")
            # Return NaN results
            nan_results = {
                key: dict.fromkeys(self.mlutility_config.metrics, np.nan)
                for key in ["ori", "syn"]
            }
            return {
                "global": self._get_global_scores(nan_results),
                "details": nan_results,
            }

        # Select evaluation method based on task type
        task_type = self.mlutility_config.task_type

        if task_type == TaskType.CLASSIFICATION:
            evaluate_func = self._evaluate_classification
        elif task_type == TaskType.REGRESSION:
            evaluate_func = self._evaluate_regression
        else:  # CLUSTERING
            evaluate_func = self._evaluate_clustering

        # Execute different evaluation flows based on experiment design
        results = {}

        if self.mlutility_config.experiment_design == "domain_transfer":
            # Domain transfer: train on syn, test on ori
            self._logger.info("Using domain transfer experiment design")

            if task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
                # Supervised learning
                syn_to_ori = evaluate_func(
                    X_train=processed_data["syn"]["X"],
                    y_train=processed_data["syn"]["y"],
                    X_test=processed_data["ori"]["X"],
                    y_test=processed_data["ori"]["y"],
                )
                # For compatibility, record results in both ori and syn
                results["syn_to_ori"] = syn_to_ori
                results["ori"] = dict.fromkeys(self.mlutility_config.metrics, np.nan)
                results["syn"] = syn_to_ori
            else:
                # Unsupervised learning (clustering)
                syn_to_ori = evaluate_func(
                    X_train=processed_data["syn"]["X"],
                    X_test=processed_data["ori"]["X"],
                )
                results["syn_to_ori"] = syn_to_ori
                results["ori"] = dict.fromkeys(self.mlutility_config.metrics, np.nan)
                results["syn"] = syn_to_ori

        else:  # dual_model_control
            # Dual model control: train ori and syn separately, test on control
            self._logger.info("Using dual model control experiment design")

            for data_type in ["ori", "syn"]:
                if task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
                    # Supervised learning
                    results[data_type] = evaluate_func(
                        X_train=processed_data[data_type]["X"],
                        y_train=processed_data[data_type]["y"],
                        X_test=processed_data["control"]["X"],
                        y_test=processed_data["control"]["y"],
                    )
                else:
                    # Unsupervised learning
                    results[data_type] = evaluate_func(
                        X_train=processed_data[data_type]["X"],
                        X_test=processed_data["control"]["X"],
                    )

        # Organize results
        return {"global": self._get_global_scores(results), "details": results}
