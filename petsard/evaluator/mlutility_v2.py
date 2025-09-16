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
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    jaccard_score,
    log_loss,
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
    """機器學習任務類型"""

    CLASSIFICATION = auto()
    REGRESSION = auto()
    CLUSTERING = auto()

    @classmethod
    def from_string(cls, value: str) -> "TaskType":
        """從字串轉換為任務類型"""
        mapping = {
            "classification": cls.CLASSIFICATION,
            "clustering": cls.CLUSTERING,
            "regression": cls.REGRESSION,
            # 別名
            "class": cls.CLASSIFICATION,
            "cluster": cls.CLUSTERING,
            "reg": cls.REGRESSION,
        }

        value_lower = value.lower()
        if value_lower not in mapping:
            raise ValueError(f"不支援的任務類型: {value}")
        return mapping[value_lower]


class MetricRegistry:
    """評估指標註冊中心 - 使用 sklearn.metrics 的完整指標"""

    # 預設指標
    DEFAULT_METRICS = {
        TaskType.CLASSIFICATION: [
            "mcc",
            "f1_score",
            "roc_auc",
            "pr_auc",
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "specificity",
            "tp",
            "tn",
            "fp",
            "fn",
        ],
        TaskType.REGRESSION: ["r2_score", "mse", "mae", "rmse"],
        TaskType.CLUSTERING: ["silhouette_score"],
    }

    @staticmethod
    def compute_confusion_matrix_metrics(y_true, y_pred):
        """計算完整的 confusion matrix 相關指標"""

        cm = confusion_matrix(y_true, y_pred)

        # 處理二元或多類別分類
        if cm.shape == (2, 2):
            # 二元分類
            tn, fp, fn, tp = cm.ravel()
        else:
            # 多類別分類：計算微平均
            tp = np.diag(cm).sum()
            fp = cm.sum(axis=0) - np.diag(cm)
            fn = cm.sum(axis=1) - np.diag(cm)
            fp = fp.sum()
            fn = fn.sum()
            tn = cm.sum() - tp - fp - fn

        # 計算所有衍生指標
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

        # 計算其他統計指標
        metrics["sensitivity"] = metrics["tpr"]  # 同義詞
        metrics["specificity"] = metrics["tnr"]  # 同義詞
        metrics["precision"] = metrics["ppv"]  # 同義詞
        metrics["recall"] = metrics["tpr"]  # 同義詞
        metrics["informedness"] = metrics["tpr"] + metrics["tnr"] - 1  # Youden's J
        metrics["markedness"] = metrics["ppv"] + metrics["npv"] - 1

        return metrics

    # 內建指標函數 - 完整的 sklearn.metrics
    BUILTIN_METRICS = {
        # 基本分類指標
        "accuracy": accuracy_score,
        "balanced_accuracy": balanced_accuracy_score,
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
        "cohen_kappa": cohen_kappa_score,
        "jaccard": lambda y_true, y_pred: jaccard_score(
            y_true,
            y_pred,
            average="weighted" if len(np.unique(y_true)) > 2 else "binary",
        ),
        # 需要概率的指標 (特殊處理)
        "roc_auc": None,
        "pr_auc": None,
        "log_loss": None,
        "brier_score": None,
        # Confusion Matrix 衍生指標 (特殊處理)
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
        # 回歸指標
        "r2_score": r2_score,
        "mse": mean_squared_error,
        "mae": mean_absolute_error,
        "rmse": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
        "mape": lambda y_true, y_pred: np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        if np.all(y_true != 0)
        else np.inf,
        # 聚類指標
        "silhouette_score": silhouette_score,
    }

    # 指標適用的任務類型
    METRIC_TASK_COMPATIBILITY = {
        # 分類指標
        "accuracy": [TaskType.CLASSIFICATION],
        "balanced_accuracy": [TaskType.CLASSIFICATION],
        "f1_score": [TaskType.CLASSIFICATION],
        "f2_score": [TaskType.CLASSIFICATION],
        "f0.5_score": [TaskType.CLASSIFICATION],
        "precision": [TaskType.CLASSIFICATION],
        "recall": [TaskType.CLASSIFICATION],
        "mcc": [TaskType.CLASSIFICATION],
        "cohen_kappa": [TaskType.CLASSIFICATION],
        "jaccard": [TaskType.CLASSIFICATION],
        "roc_auc": [TaskType.CLASSIFICATION],
        "pr_auc": [TaskType.CLASSIFICATION],
        "log_loss": [TaskType.CLASSIFICATION],
        "brier_score": [TaskType.CLASSIFICATION],
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
        # 回歸指標
        "r2_score": [TaskType.REGRESSION],
        "mse": [TaskType.REGRESSION],
        "mae": [TaskType.REGRESSION],
        "rmse": [TaskType.REGRESSION],
        "mape": [TaskType.REGRESSION],
        # 聚類指標
        "silhouette_score": [TaskType.CLUSTERING],
    }

    def __init__(self):
        """初始化指標註冊中心"""
        self.custom_metrics = {}

    def register_metric(
        self, name: str, func: Callable, task_types: list[TaskType]
    ) -> None:
        """
        註冊自訂指標

        Args:
            name: 指標名稱
            func: 指標計算函數
            task_types: 適用的任務類型
        """
        self.custom_metrics[name] = func
        if name not in self.METRIC_TASK_COMPATIBILITY:
            self.METRIC_TASK_COMPATIBILITY[name] = task_types

    def get_metric(self, name: str) -> Callable:
        """
        取得指標函數

        Args:
            name: 指標名稱

        Returns:
            指標計算函數
        """
        if name in self.custom_metrics:
            return self.custom_metrics[name]
        if name in self.BUILTIN_METRICS:
            return self.BUILTIN_METRICS[name]
        raise ValueError(f"未知的指標: {name}")

    def is_compatible(self, metric_name: str, task_type: TaskType) -> bool:
        """
        檢查指標是否與任務類型相容

        Args:
            metric_name: 指標名稱
            task_type: 任務類型

        Returns:
            是否相容
        """
        if metric_name in self.custom_metrics:
            # 自訂指標預設相容所有任務
            return True

        if metric_name not in self.METRIC_TASK_COMPATIBILITY:
            return False

        return task_type in self.METRIC_TASK_COMPATIBILITY[metric_name]

    def get_default_metrics(self, task_type: TaskType) -> list[str]:
        """取得任務的預設指標"""
        return self.DEFAULT_METRICS.get(task_type, [])


@dataclass
class MLUtilityConfig(BaseConfig):
    """
    MLUtility 評估器配置

    Attributes:
        eval_method: 評估方法名稱 (mlutility-classification/regression/clustering)
        experiment_design: 實驗設計方式
            - 'dual_model_control': 雙模型控制組（預設）- ori和syn分別訓練，在control測試
            - 'domain_transfer': 領域遷移 - syn訓練，在ori測試
        resampling: 不平衡資料處理方法（僅限分類任務）
            - None: 不處理（預設）
            - 'smote-enn': 使用 SMOTE-ENN 合成少數類別並清理噪音樣本
            - 'smote-tomek': 使用 SMOTE-Tomek 合成少數類別並清理邊界樣本
        task_type: 任務類型
        target: 目標欄位（分類/回歸任務需要）
        metrics: 要計算的評估指標
        n_clusters: 聚類數量（預設為5）
        xgb_params: XGBoost 額外參數
        random_state: 隨機種子
    """

    eval_method: str
    experiment_design: str = "dual_model_control"
    resampling: str | None = None
    task_type: TaskType | None = None
    target: str | None = None
    metrics: list[str] | None = None
    n_clusters: int = 5
    xgb_params: dict = field(default_factory=dict)
    random_state: int = 42

    # 內部使用
    REQUIRED_INPUT_KEYS: list[str] = field(
        default_factory=lambda: ["ori", "syn", "control"]
    )
    n_rows: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()

        # 解析任務類型
        if self.task_type is None:
            # 從 eval_method 解析
            method_suffix = self.eval_method.replace("mlutility-", "")
            try:
                self.task_type = TaskType.from_string(method_suffix)
            except ValueError as e:
                error_msg = f"無法從 eval_method '{self.eval_method}' 解析任務類型: {e}"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg) from e
        elif isinstance(self.task_type, str):
            self.task_type = TaskType.from_string(self.task_type)

        # 驗證目標欄位
        if self.task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
            if not self.target:
                error_msg = f"任務類型 {self.task_type.name} 需要指定 target 欄位"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        elif self.task_type == TaskType.CLUSTERING:
            if self.target:
                self._logger.info("聚類任務不需要 target 欄位，將忽略")
                self.target = None

        # 驗證實驗設計
        if self.experiment_design not in ["dual_model_control", "domain_transfer"]:
            error_msg = f"不支援的實驗設計: {self.experiment_design}。必須是 'dual_model_control' 或 'domain_transfer'"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 驗證不平衡處理方法
        if self.resampling is not None:
            if self.resampling not in ["smote-enn", "smote-tomek"]:
                error_msg = f"不支援的不平衡處理方法: {self.resampling}。支援 'smote-enn' 或 'smote-tomek'"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # 只有分類任務可以使用不平衡處理
            if self.task_type != TaskType.CLASSIFICATION:
                error_msg = f"不平衡處理方法 {self.resampling} 僅限分類任務使用"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            self._logger.info(f"將使用 {self.resampling} 進行不平衡資料處理")

        # 調整必要輸入鍵
        if self.experiment_design == "domain_transfer":
            # 領域遷移只需要 ori 和 syn
            self.REQUIRED_INPUT_KEYS = ["ori", "syn"]

        # 設定預設指標
        metric_registry = MetricRegistry()
        if self.metrics is None:
            self.metrics = metric_registry.get_default_metrics(self.task_type)
            self._logger.info(f"使用預設指標: {self.metrics}")
        else:
            # 驗證指標是否相容
            incompatible = []
            for metric in self.metrics:
                if not metric_registry.is_compatible(metric, self.task_type):
                    incompatible.append(metric)

            if incompatible:
                error_msg = (
                    f"以下指標與任務類型 {self.task_type.name} 不相容: {incompatible}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

    def update_data(self, data: dict[str, pd.DataFrame]) -> None:
        """
        驗證並更新資料相關配置

        Args:
            data: 輸入資料字典
        """
        # 驗證必要的鍵
        if not all(key in data for key in self.REQUIRED_INPUT_KEYS):
            error_msg = f"缺少必要的資料鍵: {self.REQUIRED_INPUT_KEYS}"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 驗證資料不為空
        for key in self.REQUIRED_INPUT_KEYS:
            df = data[key].dropna()
            if df.empty:
                error_msg = f"{key} 資料在移除缺失值後為空"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        # 驗證目標欄位存在
        if self.target:
            for key in self.REQUIRED_INPUT_KEYS:
                if self.target not in data[key].columns:
                    error_msg = f"目標欄位 '{self.target}' 在 {key} 資料中不存在"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

        # 記錄資料大小
        self.n_rows = {key: data[key].shape[0] for key in self.REQUIRED_INPUT_KEYS}
        self._logger.debug(f"資料列數: {self.n_rows}")


class MLUtility(BaseEvaluator):
    """
    簡化的機器學習效用評估器

    使用 XGBoost 進行分類和回歸，K-means 進行聚類
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn", "control"]
    AVAILABLE_SCORES_GRANULARITY: list[str] = ["global", "details"]

    def __init__(self, config: dict):
        """
        初始化評估器

        Args:
            config: 配置字典
        """
        super().__init__(config=config)
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

        self._logger.debug(f"初始化 MLUtilityConfig: {self.config}")
        self.mlutility_config = MLUtilityConfig(**self.config)
        self._logger.debug("MLUtilityConfig 初始化成功")

        self.metric_registry = MetricRegistry()
        self._impl = None

    def _preprocess_data(
        self, data: dict[str, pd.DataFrame]
    ) -> tuple[dict[str, dict], str]:
        """
        資料前處理

        簡化的前處理流程：
        1. 移除缺失值
        2. 編碼類別變數（使用 OneHotEncoder）
        3. 標準化數值特徵
        4. 不平衡處理（僅分類任務，在訓練資料上應用 SMOTE-ENN 或 SMOTE-Tomek）

        重要：為避免資料洩漏，只使用 ori 和 syn 資料來訓練編碼器和標準化器。
        - OneHotEncoder 設定 handle_unknown='ignore' 來處理未見過的類別
        - control 資料使用訓練好的轉換器進行轉換

        Args:
            data: 原始資料

        Returns:
            (前處理後的資料, 狀態碼)
        """
        processed_data = {}

        # 複製資料
        data_copy = {key: data[key].copy() for key in self.REQUIRED_INPUT_KEYS}
        # 保留原始資料供目標欄位使用
        data_copy_original = {key: data[key].copy() for key in self.REQUIRED_INPUT_KEYS}

        # 移除缺失值
        for key in self.REQUIRED_INPUT_KEYS:
            data_copy[key] = data_copy[key].dropna()
            if data_copy[key].empty:
                return None, "empty_after_dropna"

        # 分離特徵和目標
        if self.mlutility_config.target:
            # 分類/回歸任務
            target_col = self.mlutility_config.target

            # 檢查目標是否為常數
            for key in self.REQUIRED_INPUT_KEYS:
                if data_copy[key][target_col].nunique() == 1:
                    return None, "constant_target"

            # 準備特徵
            feature_cols = [
                col for col in data_copy["ori"].columns if col != target_col
            ]

            # 分離數值和類別特徵
            numerical_cols = []
            categorical_cols = []
            for col in feature_cols:
                if data_copy["ori"][col].dtype == "object":
                    categorical_cols.append(col)
                else:
                    numerical_cols.append(col)

            # 處理類別特徵（使用 OneHotEncoder）
            encoded_features = {}
            if categorical_cols:
                encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")

                # 只使用 ori 和 syn 資料來訓練編碼器，避免資料洩漏
                # handle_unknown='ignore' 會將 control 中未見過的類別編碼為全零向量
                train_cat_data = pd.concat(
                    [
                        data_copy["ori"][categorical_cols],
                        data_copy["syn"][categorical_cols],
                    ]
                )
                encoder.fit(train_cat_data)

                # 編碼各資料集的類別特徵
                for key in self.REQUIRED_INPUT_KEYS:
                    encoded = encoder.transform(data_copy[key][categorical_cols])
                    # 建立編碼後的欄位名稱
                    encoded_cols = []
                    for i, col in enumerate(categorical_cols):
                        for cat in encoder.categories_[i]:
                            encoded_cols.append(f"{col}_{cat}")

                    # 儲存編碼後的特徵
                    encoded_features[key] = pd.DataFrame(
                        encoded, columns=encoded_cols, index=data_copy[key].index
                    )

            # 合併數值特徵和編碼後的類別特徵
            for key in self.REQUIRED_INPUT_KEYS:
                if categorical_cols:
                    # 合併數值和編碼後的類別特徵
                    X_features = pd.concat(
                        [
                            data_copy[key][numerical_cols].reset_index(drop=True),
                            encoded_features[key].reset_index(drop=True),
                        ],
                        axis=1,
                    )
                else:
                    # 只有數值特徵
                    X_features = data_copy[key][numerical_cols]

                data_copy[key] = X_features

            # 標準化特徵
            # 只使用 ori 和 syn 資料來計算均值和標準差，避免資料洩漏
            scaler_X = StandardScaler()
            X_train = pd.concat([data_copy["ori"], data_copy["syn"]])
            scaler_X.fit(X_train)

            # 處理目標變數
            if self.mlutility_config.task_type == TaskType.CLASSIFICATION:
                # 檢查目標欄位是否已經是數值型態
                first_target = data_copy_original["ori"][target_col]

                if pd.api.types.is_numeric_dtype(first_target):
                    # 目標已經是數值，直接使用
                    self._logger.info(
                        f"目標欄位 '{target_col}' 已經是數值型態，不需要編碼"
                    )

                    for key in self.REQUIRED_INPUT_KEYS:
                        X_scaled = scaler_X.transform(data_copy[key])
                        y_encoded = data_copy_original[key][target_col].values
                else:
                    # 目標是類別型態，需要編碼
                    self._logger.info(
                        f"目標欄位 '{target_col}' 是類別型態，使用 LabelEncoder 編碼"
                    )

                    # 只使用 ori 和 syn 資料來建立標籤編碼，避免資料洩漏
                    label_encoder = LabelEncoder()
                    y_train = pd.concat(
                        [
                            data_copy_original["ori"][target_col],
                            data_copy_original["syn"][target_col],
                        ]
                    )
                    label_encoder.fit(y_train)

                    for key in self.REQUIRED_INPUT_KEYS:
                        X_scaled = scaler_X.transform(data_copy[key])
                        y_encoded = label_encoder.transform(
                            data_copy_original[key][target_col]
                        )

                        # 對訓練資料應用不平衡處理
                        if self.mlutility_config.resampling and key in ["ori", "syn"]:
                            # 只對訓練資料（ori 和 syn）進行重採樣，不對測試資料（control）處理
                            try:
                                # 條件導入 imbalanced-learn 套件
                                if self.mlutility_config.resampling == "smote-enn":
                                    try:
                                        from imblearn.combine import SMOTEENN
                                    except ImportError as import_err:
                                        raise ImportError(
                                            "需要安裝 imbalanced-learn 套件才能使用 SMOTE-ENN 不平衡處理。\n"
                                            "請執行: pip install imbalanced-learn"
                                        ) from import_err

                                    self._logger.info(
                                        f"對 {key} 資料應用 SMOTE-ENN 不平衡處理"
                                    )
                                    resampler = SMOTEENN(
                                        random_state=self.mlutility_config.random_state
                                    )
                                else:  # smote-tomek
                                    try:
                                        from imblearn.combine import SMOTETomek
                                    except ImportError as import_err:
                                        raise ImportError(
                                            "需要安裝 imbalanced-learn 套件才能使用 SMOTE-Tomek 不平衡處理。\n"
                                            "請執行: pip install imbalanced-learn"
                                        ) from import_err

                                    self._logger.info(
                                        f"對 {key} 資料應用 SMOTE-Tomek 不平衡處理"
                                    )
                                    resampler = SMOTETomek(
                                        random_state=self.mlutility_config.random_state
                                    )

                                X_resampled, y_resampled = resampler.fit_resample(
                                    X_scaled, y_encoded
                                )
                                self._logger.info(
                                    f"{key} 資料重採樣：{len(y_encoded)} → {len(y_resampled)} 樣本"
                                )

                                processed_data[key] = {
                                    "X": X_resampled,
                                    "y": y_resampled,
                                }
                            except ImportError:
                                # 重新拋出 ImportError
                                raise
                            except Exception as e:
                                self._logger.warning(
                                    f"{self.mlutility_config.resampling.upper()} 處理失敗: {e}，使用原始資料"
                                )
                                processed_data[key] = {
                                    "X": X_scaled,
                                    "y": y_encoded,
                                }
                        else:
                            # control 資料或未啟用不平衡處理
                            processed_data[key] = {
                                "X": X_scaled,
                                "y": y_encoded,
                            }
            else:
                # 回歸任務，標準化目標
                # 只使用 ori 和 syn 資料來計算目標變數的均值和標準差
                scaler_y = StandardScaler()
                y_train = pd.concat(
                    [
                        data_copy_original["ori"][[target_col]],
                        data_copy_original["syn"][[target_col]],
                    ]
                )
                scaler_y.fit(y_train)

                for key in self.REQUIRED_INPUT_KEYS:
                    processed_data[key] = {
                        "X": scaler_X.transform(data_copy[key]),
                        "y": scaler_y.transform(
                            data_copy_original[key][[target_col]]
                        ).ravel(),
                    }
        else:
            # 聚類任務
            # 只使用 ori 和 syn 資料來計算均值和標準差
            scaler = StandardScaler()
            X_train = pd.concat([data_copy["ori"], data_copy["syn"]])
            scaler.fit(X_train)

            for key in self.REQUIRED_INPUT_KEYS:
                processed_data[key] = {"X": scaler.transform(data_copy[key])}

        return processed_data, "success"

    def _evaluate_classification(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict[str, float]:
        """
        分類任務評估

        使用 XGBoost 分類器，支援完整的 sklearn.metrics 指標
        """
        # 訓練模型
        model = XGBClassifier(
            random_state=self.mlutility_config.random_state,
            **self.mlutility_config.xgb_params,
        )
        model.fit(X_train, y_train)

        # 預測
        y_pred = model.predict(X_test)

        # 計算需要概率的指標
        try:
            y_proba = model.predict_proba(X_test)
            has_proba = True
        except Exception:
            has_proba = False

        # 計算 confusion matrix 衍生指標
        cm_metrics = self.metric_registry.compute_confusion_matrix_metrics(
            y_test, y_pred
        )

        # 計算指標
        results = {}
        for metric_name in self.mlutility_config.metrics:
            # 檢查是否為 confusion matrix 衍生指標
            if metric_name in cm_metrics:
                results[metric_name] = cm_metrics[metric_name]
                continue

            # 檢查是否需要概率
            if metric_name in ["roc_auc", "pr_auc", "log_loss", "brier_score"]:
                if not has_proba:
                    results[metric_name] = np.nan
                    continue

                # 計算需要概率的指標
                if metric_name == "roc_auc":
                    # 處理二元和多類別分類
                    if len(np.unique(y_test)) == 2:
                        # 二元分類
                        results[metric_name] = roc_auc_score(y_test, y_proba[:, 1])
                    else:
                        # 多類別分類
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
                        # 多類別：計算平均
                        pr_aucs = []
                        for i in range(y_proba.shape[1]):
                            y_true_binary = (y_test == i).astype(int)
                            precision, recall, _ = precision_recall_curve(
                                y_true_binary, y_proba[:, i]
                            )
                            pr_aucs.append(auc(recall, precision))
                        results[metric_name] = np.mean(pr_aucs)

                elif metric_name == "log_loss":
                    results[metric_name] = log_loss(y_test, y_proba)

                elif metric_name == "brier_score":
                    # Brier score 只適用於二元分類
                    if len(np.unique(y_test)) == 2:
                        results[metric_name] = brier_score_loss(y_test, y_proba[:, 1])
                    else:
                        results[metric_name] = np.nan
            else:
                # 一般指標
                metric_func = self.metric_registry.get_metric(metric_name)
                if metric_func is not None:
                    try:
                        results[metric_name] = metric_func(y_test, y_pred)
                    except Exception as e:
                        self._logger.warning(f"計算指標 {metric_name} 失敗: {e}")
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
        回歸任務評估

        使用 XGBoost 回歸器
        """
        # 訓練模型
        model = XGBRegressor(
            random_state=self.mlutility_config.random_state,
            **self.mlutility_config.xgb_params,
        )
        model.fit(X_train, y_train)

        # 預測
        y_pred = model.predict(X_test)

        # 計算指標
        results = {}
        for metric_name in self.mlutility_config.metrics:
            metric_func = self.metric_registry.get_metric(metric_name)
            results[metric_name] = metric_func(y_test, y_pred)

        return results

    def _evaluate_clustering(
        self, X_train: np.ndarray, X_test: np.ndarray
    ) -> dict[str, float]:
        """
        聚類任務評估

        使用 K-means
        """
        # 訓練模型
        model = KMeans(
            n_clusters=self.mlutility_config.n_clusters,
            random_state=self.mlutility_config.random_state,
            n_init="auto",
        )
        model.fit(X_train)

        # 預測
        labels = model.predict(X_test)

        # 計算指標
        results = {}
        for metric_name in self.mlutility_config.metrics:
            if metric_name == "silhouette_score":
                # Silhouette score 需要特殊處理
                try:
                    score = silhouette_score(X_test, labels)
                except ValueError:
                    # 只有一個群集或樣本太少
                    score = -1.0
                results[metric_name] = score
            else:
                metric_func = self.metric_registry.get_metric(metric_name)
                results[metric_name] = metric_func(X_test, labels)

        return results

    def _get_global_scores(self, results: dict[str, dict[str, float]]) -> pd.DataFrame:
        """
        計算全域評分

        Args:
            results: 各資料集的評估結果

        Returns:
            全域評分 DataFrame
        """
        # 計算每個指標的統計值
        global_scores = []

        if self.mlutility_config.experiment_design == "domain_transfer":
            # 領域遷移模式：只顯示 syn_to_ori 值
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
            # 雙模型控制組模式：水平顯示 ori/syn/diff
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

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict:
        """
        執行評估

        Args:
            data: 輸入資料

        Returns:
            評估結果
        """
        # 根據實驗設計調整資料需求
        if self.mlutility_config.experiment_design == "domain_transfer":
            # 領域遷移模式：只需要 ori 和 syn
            if "ori" not in data or "syn" not in data:
                raise ConfigError("領域遷移模式需要 'ori' 和 'syn' 資料")
            # 為了相容前處理，建立虛擬 control
            if "control" not in data:
                data["control"] = data["ori"].copy()
                self._logger.info("領域遷移模式：使用 ori 作為測試集")
        else:
            # 雙模型控制組模式：需要完整三個資料集
            if not all(key in data for key in ["ori", "syn", "control"]):
                raise ConfigError("雙模型控制組模式需要 'ori', 'syn', 'control' 資料")

        # 更新配置
        self.mlutility_config.update_data(data)

        # 前處理
        processed_data, status = self._preprocess_data(data)

        if status != "success":
            self._logger.warning(f"前處理失敗: {status}")
            # 返回 NaN 結果
            nan_results = {
                key: dict.fromkeys(self.mlutility_config.metrics, np.nan)
                for key in ["ori", "syn"]
            }
            return {
                "global": self._get_global_scores(nan_results),
                "details": nan_results,
            }

        # 根據任務類型選擇評估方法
        task_type = self.mlutility_config.task_type

        if task_type == TaskType.CLASSIFICATION:
            evaluate_func = self._evaluate_classification
        elif task_type == TaskType.REGRESSION:
            evaluate_func = self._evaluate_regression
        else:  # CLUSTERING
            evaluate_func = self._evaluate_clustering

        # 根據實驗設計執行不同的評估流程
        results = {}

        if self.mlutility_config.experiment_design == "domain_transfer":
            # 領域遷移：用 syn 訓練，在 ori 測試
            self._logger.info("使用領域遷移實驗設計")

            if task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
                # 有監督學習
                syn_to_ori = evaluate_func(
                    X_train=processed_data["syn"]["X"],
                    y_train=processed_data["syn"]["y"],
                    X_test=processed_data["ori"]["X"],
                    y_test=processed_data["ori"]["y"],
                )
                # 為了相容性，將結果同時記錄在 ori 和 syn
                results["syn_to_ori"] = syn_to_ori
                results["ori"] = dict.fromkeys(self.mlutility_config.metrics, np.nan)
                results["syn"] = syn_to_ori
            else:
                # 無監督學習（聚類）
                syn_to_ori = evaluate_func(
                    X_train=processed_data["syn"]["X"],
                    X_test=processed_data["ori"]["X"],
                )
                results["syn_to_ori"] = syn_to_ori
                results["ori"] = dict.fromkeys(self.mlutility_config.metrics, np.nan)
                results["syn"] = syn_to_ori

        else:  # dual_model_control
            # 雙模型控制組：ori 和 syn 分別訓練，在 control 測試
            self._logger.info("使用雙模型控制組實驗設計")

            for data_type in ["ori", "syn"]:
                if task_type in [TaskType.CLASSIFICATION, TaskType.REGRESSION]:
                    # 有監督學習
                    results[data_type] = evaluate_func(
                        X_train=processed_data[data_type]["X"],
                        y_train=processed_data[data_type]["y"],
                        X_test=processed_data["control"]["X"],
                        y_test=processed_data["control"]["y"],
                    )
                else:
                    # 無監督學習
                    results[data_type] = evaluate_func(
                        X_train=processed_data[data_type]["X"],
                        X_test=processed_data["control"]["X"],
                    )

        # 整理結果
        return {"global": self._get_global_scores(results), "details": results}
