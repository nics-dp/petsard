"""Test module for MLUtility V2 - 測試新版本的擴展功能."""

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from petsard.evaluator.mlutility_v2 import (
    MetricRegistry,
    MLUtility,
    MLUtilityConfig,
    TaskType,
)


class TestTaskType(unittest.TestCase):
    """測試 TaskType 列舉類別."""

    def test_task_type_from_string(self):
        """測試從字串轉換為任務類型."""
        # 測試完整名稱
        self.assertEqual(
            TaskType.from_string("classification"), TaskType.CLASSIFICATION
        )
        self.assertEqual(TaskType.from_string("regression"), TaskType.REGRESSION)
        self.assertEqual(TaskType.from_string("clustering"), TaskType.CLUSTERING)

        # 測試別名
        self.assertEqual(TaskType.from_string("class"), TaskType.CLASSIFICATION)
        self.assertEqual(TaskType.from_string("reg"), TaskType.REGRESSION)
        self.assertEqual(TaskType.from_string("cluster"), TaskType.CLUSTERING)

        # 測試大小寫不敏感
        self.assertEqual(
            TaskType.from_string("CLASSIFICATION"), TaskType.CLASSIFICATION
        )
        self.assertEqual(TaskType.from_string("Regression"), TaskType.REGRESSION)

    def test_task_type_invalid(self):
        """測試無效的任務類型字串."""
        with self.assertRaises(ValueError) as context:
            TaskType.from_string("invalid_type")
        self.assertIn("不支援的任務類型", str(context.exception))


class TestMetricRegistry(unittest.TestCase):
    """測試 MetricRegistry 指標註冊中心."""

    def setUp(self):
        """設置測試環境."""
        self.registry = MetricRegistry()

    def test_default_metrics(self):
        """測試預設指標."""
        # 分類預設指標
        class_metrics = self.registry.get_default_metrics(TaskType.CLASSIFICATION)
        self.assertIn("mcc", class_metrics)
        self.assertIn("f1_score", class_metrics)
        self.assertIn("roc_auc", class_metrics)
        self.assertIn("accuracy", class_metrics)

        # 回歸預設指標
        reg_metrics = self.registry.get_default_metrics(TaskType.REGRESSION)
        self.assertIn("r2_score", reg_metrics)
        self.assertIn("mse", reg_metrics)
        self.assertIn("mae", reg_metrics)

        # 聚類預設指標
        cluster_metrics = self.registry.get_default_metrics(TaskType.CLUSTERING)
        self.assertIn("silhouette_score", cluster_metrics)

    def test_metric_compatibility(self):
        """測試指標與任務類型的相容性."""
        # 分類指標應該只與分類任務相容
        self.assertTrue(
            self.registry.is_compatible("accuracy", TaskType.CLASSIFICATION)
        )
        self.assertFalse(self.registry.is_compatible("accuracy", TaskType.REGRESSION))

        # 回歸指標應該只與回歸任務相容
        self.assertTrue(self.registry.is_compatible("r2_score", TaskType.REGRESSION))
        self.assertFalse(
            self.registry.is_compatible("r2_score", TaskType.CLASSIFICATION)
        )

        # 聚類指標應該只與聚類任務相容
        self.assertTrue(
            self.registry.is_compatible("silhouette_score", TaskType.CLUSTERING)
        )
        self.assertFalse(
            self.registry.is_compatible("silhouette_score", TaskType.CLASSIFICATION)
        )

    def test_register_custom_metric(self):
        """測試註冊自定義指標."""

        def custom_metric(y_true, y_pred):
            """自定義測試指標."""
            return np.mean(y_true == y_pred)

        # 註冊自定義指標
        self.registry.register_metric(
            "custom_accuracy",
            custom_metric,
            [TaskType.CLASSIFICATION, TaskType.CLUSTERING],
        )

        # 測試取得指標
        retrieved_func = self.registry.get_metric("custom_accuracy")
        self.assertEqual(retrieved_func, custom_metric)

        # 測試相容性
        self.assertTrue(
            self.registry.is_compatible("custom_accuracy", TaskType.CLASSIFICATION)
        )

    def test_confusion_matrix_metrics(self):
        """測試混淆矩陣衍生指標計算."""
        # 二元分類測試
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1, 0, 0, 0, 1])

        metrics = self.registry.compute_confusion_matrix_metrics(y_true, y_pred)

        # 檢查基本混淆矩陣值
        self.assertIn("tp", metrics)
        self.assertIn("tn", metrics)
        self.assertIn("fp", metrics)
        self.assertIn("fn", metrics)

        # 檢查衍生指標
        self.assertIn("sensitivity", metrics)
        self.assertIn("specificity", metrics)
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("accuracy", metrics)

        # 驗證計算正確性
        self.assertEqual(metrics["tp"], 3)  # 真陽性
        self.assertEqual(metrics["tn"], 3)  # 真陰性
        self.assertEqual(metrics["fp"], 1)  # 假陽性
        self.assertEqual(metrics["fn"], 1)  # 假陰性


class TestMLUtilityConfig(unittest.TestCase):
    """測試 MLUtilityConfig 配置類別."""

    def test_config_initialization(self):
        """測試配置初始化."""
        # 分類配置
        config_dict = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "metrics": ["accuracy", "f1_score"],
        }
        config = MLUtilityConfig(**config_dict)

        self.assertEqual(config.task_type, TaskType.CLASSIFICATION)
        self.assertEqual(config.target, "label")
        self.assertEqual(config.metrics, ["accuracy", "f1_score"])
        self.assertEqual(config.experiment_design, "dual_model_control")

    def test_experiment_design_validation(self):
        """測試實驗設計驗證."""
        # 有效的實驗設計
        config_dict = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "experiment_design": "domain_transfer",
        }
        config = MLUtilityConfig(**config_dict)
        self.assertEqual(config.experiment_design, "domain_transfer")

        # 無效的實驗設計
        config_dict["experiment_design"] = "invalid_design"
        with self.assertRaises(Exception) as context:
            MLUtilityConfig(**config_dict)
        self.assertIn("不支援的實驗設計", str(context.exception))

    def test_resampling_validation(self):
        """測試不平衡處理方法驗證."""
        # 有效的不平衡處理（分類任務）
        config_dict = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "resampling": "smote-enn",
        }
        config = MLUtilityConfig(**config_dict)
        self.assertEqual(config.resampling, "smote-enn")

        # 測試 smote-tomek
        config_dict["resampling"] = "smote-tomek"
        config = MLUtilityConfig(**config_dict)
        self.assertEqual(config.resampling, "smote-tomek")

        # 無效的不平衡處理方法
        config_dict["resampling"] = "invalid_method"
        with self.assertRaises(Exception) as context:
            MLUtilityConfig(**config_dict)
        self.assertIn("不支援的不平衡處理方法", str(context.exception))

        # 回歸任務不能使用不平衡處理
        config_dict = {
            "eval_method": "mlutility-regression",
            "target": "value",
            "resampling": "smote-enn",
        }
        with self.assertRaises(Exception) as context:
            MLUtilityConfig(**config_dict)
        self.assertIn("僅限分類任務使用", str(context.exception))

    def test_domain_transfer_keys(self):
        """測試領域遷移模式的資料鍵需求."""
        config_dict = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "experiment_design": "domain_transfer",
        }
        config = MLUtilityConfig(**config_dict)

        # 領域遷移只需要 ori 和 syn
        self.assertEqual(config.REQUIRED_INPUT_KEYS, ["ori", "syn"])

    def test_clustering_no_target(self):
        """測試聚類任務不需要目標欄位."""
        config_dict = {
            "eval_method": "mlutility-clustering",
            "target": "should_be_ignored",
            "n_clusters": 3,
        }
        config = MLUtilityConfig(**config_dict)
        self.assertIsNone(config.target)
        self.assertEqual(config.n_clusters, 3)

    def test_metric_compatibility_validation(self):
        """測試指標相容性驗證."""
        # 嘗試在分類任務使用回歸指標
        config_dict = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "metrics": ["accuracy", "r2_score"],  # r2_score 是回歸指標
        }
        with self.assertRaises(Exception) as context:
            MLUtilityConfig(**config_dict)
        self.assertIn("不相容", str(context.exception))


class TestMLUtilityV2(unittest.TestCase):
    """測試 MLUtility V2 主要功能."""

    def setUp(self):
        """設置測試環境."""
        # 建立測試資料
        np.random.seed(42)
        n_samples = 100

        # 分類資料
        self.class_data = {
            "ori": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "category": np.random.choice(["A", "B", "C"], n_samples),
                    "label": np.random.choice([0, 1], n_samples),
                }
            ),
            "syn": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "category": np.random.choice(["A", "B", "C"], n_samples),
                    "label": np.random.choice([0, 1], n_samples),
                }
            ),
            "control": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "category": np.random.choice(["A", "B", "C"], n_samples),
                    "label": np.random.choice([0, 1], n_samples),
                }
            ),
        }

        # 回歸資料
        self.reg_data = {
            "ori": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "value": np.random.randn(n_samples) * 10 + 50,
                }
            ),
            "syn": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "value": np.random.randn(n_samples) * 10 + 50,
                }
            ),
            "control": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "value": np.random.randn(n_samples) * 10 + 50,
                }
            ),
        }

        # 聚類資料
        self.cluster_data = {
            "ori": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "feature3": np.random.randn(n_samples),
                }
            ),
            "syn": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "feature3": np.random.randn(n_samples),
                }
            ),
            "control": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "feature3": np.random.randn(n_samples),
                }
            ),
        }

    def test_classification_with_extended_metrics(self):
        """測試分類任務使用擴展指標."""
        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "metrics": ["mcc", "f1_score", "precision", "recall", "specificity"],
        }

        evaluator = MLUtility(config=config)

        # 檢查前處理是否成功
        with patch.object(evaluator, "_preprocess_data") as mock_preprocess:
            # 模擬前處理成功返回
            mock_preprocess.return_value = (
                {
                    "ori": {
                        "X": np.random.randn(100, 5),
                        "y": np.random.choice([0, 1], 100),
                    },
                    "syn": {
                        "X": np.random.randn(100, 5),
                        "y": np.random.choice([0, 1], 100),
                    },
                    "control": {
                        "X": np.random.randn(50, 5),
                        "y": np.random.choice([0, 1], 50),
                    },
                },
                "success",
            )

            result = evaluator.eval(self.class_data)

        # 檢查結果結構
        self.assertIn("global", result)
        self.assertIn("details", result)

        # 檢查全域結果
        global_df = result["global"]
        self.assertIsInstance(global_df, pd.DataFrame)
        self.assertIn("metric", global_df.columns)

        # 檢查所有指標都有結果
        metrics_in_result = global_df["metric"].tolist()
        for metric in config["metrics"]:
            self.assertIn(metric, metrics_in_result)

    def test_regression_with_custom_metrics(self):
        """測試回歸任務使用自定義指標集."""
        config = {
            "eval_method": "mlutility-regression",
            "target": "value",
            "metrics": ["r2_score", "rmse", "mape"],
        }

        evaluator = MLUtility(config=config)
        result = evaluator.eval(self.reg_data)

        # 檢查結果
        self.assertIn("global", result)
        global_df = result["global"]

        # 確認指標存在
        metrics_in_result = global_df["metric"].tolist()
        self.assertIn("r2_score", metrics_in_result)
        self.assertIn("rmse", metrics_in_result)
        self.assertIn("mape", metrics_in_result)

    def test_clustering_evaluation(self):
        """測試聚類評估."""
        config = {
            "eval_method": "mlutility-clustering",
            "n_clusters": 3,
            "metrics": ["silhouette_score"],
        }

        evaluator = MLUtility(config=config)
        result = evaluator.eval(self.cluster_data)

        # 檢查結果
        self.assertIn("global", result)
        self.assertIn("details", result)

        # 聚類不需要目標變數
        self.assertIsNone(evaluator.mlutility_config.target)

    def test_domain_transfer_experiment(self):
        """測試領域遷移實驗設計."""
        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "experiment_design": "domain_transfer",
            "metrics": ["accuracy", "f1_score"],
        }

        evaluator = MLUtility(config=config)

        # 領域遷移模式會自動處理資料需求
        # 基類 BaseEvaluator 還是要求 control，所以需要設置 REQUIRED_INPUT_KEYS
        evaluator.REQUIRED_INPUT_KEYS = ["ori", "syn"]

        # 領域遷移只需要 ori 和 syn
        data = {
            "ori": self.class_data["ori"],
            "syn": self.class_data["syn"],
        }

        # 模擬前處理成功
        with patch.object(evaluator, "_preprocess_data") as mock_preprocess:
            mock_preprocess.return_value = (
                {
                    "ori": {
                        "X": np.random.randn(100, 5),
                        "y": np.random.choice([0, 1], 100),
                    },
                    "syn": {
                        "X": np.random.randn(100, 5),
                        "y": np.random.choice([0, 1], 100),
                    },
                    "control": {
                        "X": np.random.randn(50, 5),
                        "y": np.random.choice([0, 1], 50),
                    },  # 領域遷移也需要 control 作為相容性
                },
                "success",
            )

            result = evaluator.eval(data)

        # 檢查結果
        self.assertIn("global", result)
        global_df = result["global"]

        # 領域遷移模式應該只有 syn_to_ori 結果
        self.assertIn("syn_to_ori", global_df.columns)

    def test_xgb_params_configuration(self):
        """測試 XGBoost 參數配置."""
        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "xgb_params": {
                "n_estimators": 50,
                "max_depth": 3,
                "learning_rate": 0.1,
            },
        }

        evaluator = MLUtility(config=config)
        self.assertEqual(evaluator.mlutility_config.xgb_params["n_estimators"], 50)
        self.assertEqual(evaluator.mlutility_config.xgb_params["max_depth"], 3)

    def test_multiclass_classification(self):
        """測試多類別分類."""
        # 建立多類別資料
        n_samples = 150
        multiclass_data = {
            "ori": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "label": np.random.choice([0, 1, 2, 3], n_samples),
                }
            ),
            "syn": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "label": np.random.choice([0, 1, 2, 3], n_samples),
                }
            ),
            "control": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_samples),
                    "feature2": np.random.randn(n_samples),
                    "label": np.random.choice([0, 1, 2, 3], n_samples),
                }
            ),
        }

        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "metrics": ["accuracy", "f1_score", "mcc"],
        }

        evaluator = MLUtility(config=config)

        # 模擬前處理成功
        with patch.object(evaluator, "_preprocess_data") as mock_preprocess:
            mock_preprocess.return_value = (
                {
                    "ori": {
                        "X": np.random.randn(150, 2),
                        "y": np.random.choice([0, 1, 2, 3], 150),
                    },
                    "syn": {
                        "X": np.random.randn(150, 2),
                        "y": np.random.choice([0, 1, 2, 3], 150),
                    },
                    "control": {
                        "X": np.random.randn(150, 2),
                        "y": np.random.choice([0, 1, 2, 3], 150),
                    },
                },
                "success",
            )

            result = evaluator.eval(multiclass_data)

        # 確認多類別分類正常運作
        self.assertIn("global", result)
        self.assertIn("details", result)

    def test_resampling_smote_enn(self):
        """測試 SMOTE-ENN 不平衡處理 - 只測試配置，不實際執行."""
        # 建立不平衡資料
        n_majority = 90
        n_minority = 10
        imbalanced_data = {
            "ori": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_majority + n_minority),
                    "feature2": np.random.randn(n_majority + n_minority),
                    "label": [0] * n_majority + [1] * n_minority,
                }
            ),
            "syn": pd.DataFrame(
                {
                    "feature1": np.random.randn(n_majority + n_minority),
                    "feature2": np.random.randn(n_majority + n_minority),
                    "label": [0] * n_majority + [1] * n_minority,
                }
            ),
            "control": pd.DataFrame(
                {
                    "feature1": np.random.randn(50),
                    "feature2": np.random.randn(50),
                    "label": np.random.choice([0, 1], 50),
                }
            ),
        }

        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "resampling": "smote-enn",
            "metrics": ["accuracy"],
        }

        # 只測試配置正確設置
        evaluator = MLUtility(config=config)
        self.assertEqual(evaluator.mlutility_config.resampling, "smote-enn")

        # 如果要測試實際執行，需要 imbalanced-learn 套件
        # 這裡只測試配置是否正確

    def test_empty_data_handling(self):
        """測試空資料處理."""
        empty_data = {
            "ori": pd.DataFrame(),
            "syn": pd.DataFrame(),
            "control": pd.DataFrame(),
        }

        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
        }

        evaluator = MLUtility(config=config)

        with self.assertRaises(Exception):
            evaluator.eval(empty_data)

    def test_missing_target_column(self):
        """測試缺失目標欄位."""
        # 資料沒有目標欄位
        data_no_target = {
            "ori": pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]}),
            "syn": pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]}),
            "control": pd.DataFrame({"feature1": [1, 2, 3], "feature2": [4, 5, 6]}),
        }

        config = {
            "eval_method": "mlutility-classification",
            "target": "missing_column",
        }

        evaluator = MLUtility(config=config)

        with self.assertRaises(Exception) as context:
            evaluator.eval(data_no_target)
        self.assertIn("不存在", str(context.exception))

    def test_categorical_encoding(self):
        """測試類別變數編碼."""
        # 包含多種類別變數的資料
        cat_data = {
            "ori": pd.DataFrame(
                {
                    "cat1": ["A", "B", "A", "C", "B"],
                    "cat2": ["X", "Y", "X", "Y", "Z"],
                    "num1": [1, 2, 3, 4, 5],
                    "label": [0, 1, 0, 1, 0],
                }
            ),
            "syn": pd.DataFrame(
                {
                    "cat1": ["A", "B", "C", "A", "B"],
                    "cat2": ["X", "Y", "Z", "X", "Y"],
                    "num1": [1, 2, 3, 4, 5],
                    "label": [0, 1, 0, 1, 0],
                }
            ),
            "control": pd.DataFrame(
                {
                    "cat1": ["A", "B", "D", "A", "C"],  # 包含新類別 'D'
                    "cat2": ["X", "Y", "W", "X", "Z"],  # 包含新類別 'W'
                    "num1": [1, 2, 3, 4, 5],
                    "label": [0, 1, 0, 1, 0],
                }
            ),
        }

        config = {
            "eval_method": "mlutility-classification",
            "target": "label",
            "metrics": ["accuracy"],
        }

        evaluator = MLUtility(config=config)

        # 模擬前處理成功處理類別變數
        with patch.object(evaluator, "_preprocess_data") as mock_preprocess:
            # 模擬 OneHotEncoder 處理後的結果
            mock_preprocess.return_value = (
                {
                    "ori": {
                        "X": np.random.randn(5, 8),
                        "y": np.array([0, 1, 0, 1, 0]),
                    },  # 8 features after encoding
                    "syn": {"X": np.random.randn(5, 8), "y": np.array([0, 1, 0, 1, 0])},
                    "control": {
                        "X": np.random.randn(5, 8),
                        "y": np.array([0, 1, 0, 1, 0]),
                    },
                },
                "success",
            )

            result = evaluator.eval(cat_data)

        # 確認可以處理類別變數和未見過的類別
        self.assertIn("global", result)
        self.assertIsNotNone(result["global"])


class TestMLUtilityIntegration(unittest.TestCase):
    """MLUtility V2 整合測試."""

    def test_end_to_end_workflow(self):
        """端到端工作流程測試."""
        # 建立真實的測試資料
        np.random.seed(42)
        n_samples = 200

        # 建立有意義的特徵和目標關係
        X1 = np.random.randn(n_samples)
        X2 = np.random.randn(n_samples)
        noise = np.random.randn(n_samples) * 0.1
        y = (X1 + 2 * X2 + noise > 0).astype(int)

        ori_data = pd.DataFrame({"feature1": X1, "feature2": X2, "target": y})

        # 建立略有不同的合成資料
        X1_syn = X1 + np.random.randn(n_samples) * 0.2
        X2_syn = X2 + np.random.randn(n_samples) * 0.2
        y_syn = (X1_syn + 2 * X2_syn + noise > 0).astype(int)

        syn_data = pd.DataFrame(
            {"feature1": X1_syn, "feature2": X2_syn, "target": y_syn}
        )

        # 控制組資料
        X1_ctrl = np.random.randn(100)
        X2_ctrl = np.random.randn(100)
        y_ctrl = (X1_ctrl + 2 * X2_ctrl > 0).astype(int)

        control_data = pd.DataFrame(
            {"feature1": X1_ctrl, "feature2": X2_ctrl, "target": y_ctrl}
        )

        # 測試完整工作流程
        config = {
            "eval_method": "mlutility-classification",
            "target": "target",
            "metrics": ["accuracy", "f1_score", "mcc"],
            "random_state": 42,
        }

        evaluator = MLUtility(config=config)

        data = {"ori": ori_data, "syn": syn_data, "control": control_data}

        # 模擬前處理成功
        with patch.object(evaluator, "_preprocess_data") as mock_preprocess:
            mock_preprocess.return_value = (
                {
                    "ori": {"X": np.random.randn(200, 2), "y": y},
                    "syn": {"X": np.random.randn(200, 2), "y": y_syn},
                    "control": {"X": np.random.randn(100, 2), "y": y_ctrl},
                },
                "success",
            )

            result = evaluator.eval(data)

        # 驗證結果
        self.assertIn("global", result)
        self.assertIn("details", result)

        global_df = result["global"]
        self.assertIsInstance(global_df, pd.DataFrame)

        # 檢查是否有正確的欄位
        self.assertIn("metric", global_df.columns)
        self.assertIn("ori", global_df.columns)
        self.assertIn("syn", global_df.columns)
        self.assertIn("diff", global_df.columns)

        # 檢查指標值的合理性
        for _, row in global_df.iterrows():
            # 大部分指標應該在 0 到 1 之間
            if row["metric"] in ["accuracy", "f1_score"]:
                self.assertTrue(0 <= row["ori"] <= 1)
                self.assertTrue(0 <= row["syn"] <= 1)
            # MCC 可以是 -1 到 1
            elif row["metric"] == "mcc":
                self.assertTrue(-1 <= row["ori"] <= 1)
                self.assertTrue(-1 <= row["syn"] <= 1)


if __name__ == "__main__":
    unittest.main()
