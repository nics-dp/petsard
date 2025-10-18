"""
Test PyTorch Gaussian Copula Synthesizer
測試 PyTorch Gaussian Copula 合成器

Note: This synthesizer assumes preprocessed data (all numeric)
注意：此合成器假設數據已預處理（全為數值型）
"""

import unittest

import numpy as np
import pandas as pd
import torch

from petsard.synthesizer import Synthesizer
from petsard.synthesizer.petsard_gaussian_copula import PetsardGaussianCopulaSynthesizer


class TestPetsardGaussianCopulaSynthesizer(unittest.TestCase):
    """Test PyTorch Gaussian Copula Synthesizer functionality 測試 PyTorch Gaussian Copula 合成器的功能"""

    def setUp(self):
        """Set up test environment 設置測試環境"""
        # Set random seeds for reproducibility 設置隨機種子以確保可重複性
        np.random.seed(42)
        torch.manual_seed(42)

        # Create test data with ALL NUMERIC types (preprocessed)
        # 創建全為數值型的測試數據（已預處理）
        self.test_data = pd.DataFrame(
            {
                "numerical_col": np.random.normal(100, 15, 100),
                "encoded_categorical": np.random.choice(
                    [0, 1, 2], 100
                ),  # Encoded A, B, C
                "integer_col": np.random.randint(1, 10, 100),
                "float_col": np.random.uniform(0, 1, 100),
                "binary_col": np.random.choice([0, 1], 100),
            }
        )

        # Add some missing values to test handling 添加一些缺失值來測試處理能力
        self.test_data.loc[::10, "numerical_col"] = np.nan

    def test_direct_initialization(self):
        """Test direct synthesizer initialization 測試直接初始化合成器"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        self.assertIsNotNone(synthesizer)
        self.assertEqual(synthesizer.config["sample_num_rows"], 50)

    def test_fit_and_sample(self):
        """Test fit and sample functionality 測試擬合和採樣功能"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Fit data 擬合數據
        synthesizer.fit(self.test_data)

        # Generate synthetic data 生成合成數據
        synthetic_data = synthesizer.sample()

        # Verify results 驗證結果
        self.assertIsInstance(synthetic_data, pd.DataFrame)
        self.assertEqual(len(synthetic_data), 50)
        self.assertEqual(set(synthetic_data.columns), set(self.test_data.columns))

    def test_dtype_preservation(self):
        """Test that original dtypes are preserved 測試原始數據類型是否保留"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(self.test_data)
        synthetic_data = synthesizer.sample()

        # Check that integer columns remain integers 檢查整數列是否仍為整數
        self.assertTrue(pd.api.types.is_integer_dtype(synthetic_data["integer_col"]))
        self.assertTrue(pd.api.types.is_integer_dtype(synthetic_data["binary_col"]))
        self.assertTrue(
            pd.api.types.is_integer_dtype(synthetic_data["encoded_categorical"])
        )

    def test_string_rejection(self):
        """Test that string/object columns are rejected 測試字串/物件列會被拒絕"""
        # Create data with string column 創建帶有字串列的數據
        bad_data = self.test_data.copy()
        bad_data["string_col"] = ["A", "B", "C"] * 33 + ["A"]

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 10}
        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Should raise ValueError 應該引發 ValueError
        with self.assertRaises(ValueError) as context:
            synthesizer.fit(bad_data)

        self.assertIn("non-numeric", str(context.exception))

    def test_correlation_preservation(self):
        """Test correlation preservation 測試相關性保留"""
        # Create data with known correlations 創建具有已知相關性的數據
        corr_data = pd.DataFrame(
            {
                "x": np.random.normal(0, 1, 200),
            }
        )
        corr_data["y"] = corr_data["x"] * 0.8 + np.random.normal(0, 0.5, 200)
        corr_data["z"] = -corr_data["x"] * 0.6 + np.random.normal(0, 0.5, 200)

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 200}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(corr_data)
        synthetic_data = synthesizer.sample()

        # Calculate correlations of original and synthetic data 計算原始和合成數據的相關性
        orig_corr = corr_data.corr()
        synth_corr = synthetic_data.corr()

        # Verify correlations are roughly preserved (allow some error) 驗證相關性大致保留（允許一定誤差）
        for col1 in orig_corr.columns:
            for col2 in orig_corr.columns:
                diff = abs(orig_corr.loc[col1, col2] - synth_corr.loc[col1, col2])
                self.assertLess(
                    diff,
                    0.3,
                    f"Correlation difference too large 相關性差異太大: {col1}-{col2}",
                )

    def test_null_handling(self):
        """Test missing value handling 測試缺失值處理"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 100}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(self.test_data)

        # Check if null rate is recorded 檢查是否記錄了缺失率
        null_rate = synthesizer.marginals["numerical_col"]["null_rate"]
        self.assertGreater(null_rate, 0)

        # Generate data and check missing values 生成數據並檢查缺失值
        synthetic_data = synthesizer.sample()
        synth_null_rate = synthetic_data["numerical_col"].isna().mean()

        # Null rates should be similar 缺失率應該相似
        self.assertAlmostEqual(null_rate, synth_null_rate, delta=0.1)

    def test_via_synthesizer_class(self):
        """Test usage via Synthesizer class 測試通過 Synthesizer 類使用"""
        # Use main Synthesizer class 使用主 Synthesizer 類
        synthesizer = Synthesizer(method="petsard-gaussian-copula", sample_num_rows=50)

        # Create and fit 創建並擬合
        synthesizer.create()
        synthesizer.fit(self.test_data)

        # Generate synthetic data 生成合成數據
        synthetic_data = synthesizer.sample()

        # Verify results 驗證結果
        self.assertIsInstance(synthetic_data, pd.DataFrame)
        self.assertEqual(len(synthetic_data), 50)
        self.assertEqual(set(synthetic_data.columns), set(self.test_data.columns))

    def test_get_correlation_matrix(self):
        """Test getting correlation matrix 測試獲取相關矩陣"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 10}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Should return None before fitting 擬合前應該返回 None
        self.assertIsNone(synthesizer.get_correlation_matrix())

        # Should return correlation matrix after fitting 擬合後應該返回相關矩陣
        synthesizer.fit(self.test_data)
        corr_matrix = synthesizer.get_correlation_matrix()

        self.assertIsInstance(corr_matrix, pd.DataFrame)
        self.assertEqual(corr_matrix.shape[0], corr_matrix.shape[1])
        self.assertEqual(list(corr_matrix.columns), synthesizer.column_names)

        # Diagonal should be 1 對角線應該為 1
        for i in range(len(corr_matrix)):
            self.assertAlmostEqual(corr_matrix.iloc[i, i], 1.0, delta=0.01)

    def test_get_marginal_info(self):
        """Test getting marginal distribution info 測試獲取邊際分佈信息"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 10}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(self.test_data)

        # Get marginal info for numerical column 獲取數值列的邊際信息
        num_info = synthesizer.get_marginal_info("numerical_col")
        self.assertIn("null_rate", num_info)
        self.assertIn("n_samples", num_info)
        self.assertIn("n_quantiles", num_info)
        self.assertIn("min", num_info)
        self.assertIn("max", num_info)
        self.assertIn("original_dtype", num_info)

        # Get marginal info for encoded categorical (now treated as numeric)
        # 獲取已編碼類別的邊際信息（現在視為數值）
        cat_info = synthesizer.get_marginal_info("encoded_categorical")
        self.assertIn("n_samples", cat_info)
        self.assertIn("n_quantiles", cat_info)

        # Non-existent column should return None 不存在的列應該返回 None
        self.assertIsNone(synthesizer.get_marginal_info("non_existent_col"))

    def test_device_selection(self):
        """Test device selection (CPU/GPU) 測試設備選擇（CPU/GPU）"""
        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 10}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Device should be None before fitting 擬合前設備應該為 None
        self.assertIsNone(synthesizer.device)

        # Fit with test data to trigger device selection 使用測試數據擬合以觸發設備選擇
        synthesizer.fit(self.test_data)

        # Should auto-select available device after fitting 擬合後應該自動選擇可用設備
        # For small datasets (< gpu_threshold), should use CPU 對於小數據集（< gpu_threshold），應該使用 CPU
        self.assertEqual(synthesizer.device.type, "cpu")

    def test_encoded_categorical_handling(self):
        """Test handling of encoded categorical variables 測試已編碼類別變數的處理"""
        # Create data with encoded categoricals 創建帶有已編碼類別的數據
        encoded_data = pd.DataFrame(
            {
                "id": range(100),
                "encoded_category": np.random.choice(
                    [0, 1, 2, 3, 4], 100
                ),  # 5 categories
                "value": np.random.normal(0, 1, 100),
            }
        )

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(encoded_data)
        synthetic_data = synthesizer.sample()

        # Verify generated data 驗證生成的數據
        self.assertEqual(len(synthetic_data), 50)
        self.assertIn("encoded_category", synthetic_data.columns)

        # Generated categories should be integers 生成的類別應該是整數
        self.assertTrue(
            pd.api.types.is_integer_dtype(synthetic_data["encoded_category"])
        )

    def test_regularization(self):
        """Test correlation matrix regularization 測試相關矩陣正規化"""
        # Create data that might cause numerical issues 創建可能導致數值問題的數據
        problematic_data = pd.DataFrame(
            {
                "col1": np.ones(100),  # Constant column 常數列
                "col2": np.random.normal(0, 1, 100),
                "col3": np.random.normal(0, 1, 100),
            }
        )
        problematic_data["col4"] = problematic_data[
            "col2"
        ]  # Perfectly correlated 完全相關

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Should handle this case without crashing 應該能夠處理這種情況而不崩潰
        try:
            synthesizer.fit(problematic_data)
            synthetic_data = synthesizer.sample()
            self.assertEqual(len(synthetic_data), 50)
        except Exception as e:
            self.fail(f"Could not handle problematic data 無法處理問題數據: {e}")

    def test_empty_data(self):
        """Test empty data handling 測試空數據處理"""
        empty_data = pd.DataFrame()

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 10}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)

        # Should handle empty data gracefully 應該能夠優雅地處理空數據
        with self.assertRaises(Exception):
            synthesizer.fit(empty_data)

    def test_single_column(self):
        """Test single column data 測試單列數據"""
        single_col_data = pd.DataFrame({"only_col": np.random.normal(0, 1, 100)})

        config = {"syn_method": "petsard-gaussian-copula", "sample_num_rows": 50}

        synthesizer = PetsardGaussianCopulaSynthesizer(config)
        synthesizer.fit(single_col_data)
        synthetic_data = synthesizer.sample()

        # Verify results 驗證結果
        self.assertEqual(len(synthetic_data), 50)
        self.assertEqual(list(synthetic_data.columns), ["only_col"])

        # Distributions should be similar 分佈應該相似
        orig_mean = single_col_data["only_col"].mean()
        orig_std = single_col_data["only_col"].std()
        synth_mean = synthetic_data["only_col"].mean()
        synth_std = synthetic_data["only_col"].std()

        self.assertAlmostEqual(orig_mean, synth_mean, delta=0.5)
        self.assertAlmostEqual(orig_std, synth_std, delta=0.5)


if __name__ == "__main__":
    unittest.main()
