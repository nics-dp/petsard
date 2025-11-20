"""測試 ConstantProcessor 功能"""

import pandas as pd
import pytest

from petsard.metadater import SchemaMetadater
from petsard.processor import ConstantProcessor, Processor


class TestConstantDetection:
    """測試 constant column 檢測功能"""

    def test_detect_constant_column(self):
        """測試檢測所有值都相同的欄位"""
        # 創建測試資料：有一個 constant 欄位
        data = pd.DataFrame(
            {
                "normal_col": [1, 2, 3, 4, 5],
                "constant_col": [100, 100, 100, 100, 100],
                "another_normal": ["a", "b", "c", "d", "e"],
            }
        )

        # 使用 Metadater 生成 schema（會自動檢測 constant）
        schema = SchemaMetadater.from_data(data, enable_stats=True)

        # 驗證 constant_col 被正確標記
        assert schema.attributes["constant_col"].is_constant is True
        assert schema.attributes["normal_col"].is_constant is False
        assert schema.attributes["another_normal"].is_constant is False

    def test_detect_constant_with_na(self):
        """測試含有 NA 值的 constant 欄位"""
        data = pd.DataFrame(
            {
                "constant_with_na": [100, 100, None, 100, 100],
                "not_constant": [1, 2, None, 3, 4],
            }
        )

        schema = SchemaMetadater.from_data(data, enable_stats=True)

        # 有 NA 但非 NA 值都相同，應該被標記為 constant
        assert schema.attributes["constant_with_na"].is_constant is True
        assert schema.attributes["not_constant"].is_constant is False

    def test_detect_all_na_not_constant(self):
        """測試全部是 NA 的欄位不應被視為 constant"""
        data = pd.DataFrame(
            {
                "all_na": [None, None, None, None],
                "constant": [1, 1, 1, 1],
            }
        )

        schema = SchemaMetadater.from_data(data, enable_stats=True)

        # 全部 NA 不應被視為 constant
        assert schema.attributes["all_na"].is_constant is False
        assert schema.attributes["constant"].is_constant is True


class TestConstantProcessor:
    """測試 ConstantProcessor 類別"""

    def test_constant_processor_fit_transform(self):
        """測試 ConstantProcessor 的 fit 和 transform"""
        # 創建測試資料
        data = pd.DataFrame(
            {
                "normal": [1, 2, 3, 4, 5],
                "constant": [999, 999, 999, 999, 999],
                "text": ["a", "b", "c", "d", "e"],
            }
        )

        # 生成 metadata
        schema = SchemaMetadater.from_data(data, enable_stats=True)

        # 創建並 fit ConstantProcessor
        processor = ConstantProcessor()
        processor.fit(data, schema)

        # 驗證檢測到 constant column
        assert "constant" in processor.constant_columns
        assert processor.constant_columns["constant"] == 999

        # Transform：應該移除 constant column
        transformed = processor.transform(data)
        assert "constant" not in transformed.columns
        assert "normal" in transformed.columns
        assert "text" in transformed.columns
        assert len(transformed.columns) == 2  # 只剩 2 個欄位

    def test_constant_processor_inverse_transform(self):
        """測試 ConstantProcessor 的 inverse_transform"""
        # 創建測試資料
        original_data = pd.DataFrame(
            {
                "normal": [1, 2, 3, 4, 5],
                "constant": [777, 777, 777, 777, 777],
            }
        )

        # 生成 metadata
        schema = SchemaMetadater.from_data(original_data, enable_stats=True)

        # Fit 和 transform
        processor = ConstantProcessor()
        processor.fit(original_data, schema)
        transformed = processor.transform(original_data)

        # Inverse transform：應該還原 constant column
        restored = processor.inverse_transform(transformed)
        assert "constant" in restored.columns
        assert "normal" in restored.columns
        assert all(restored["constant"] == 777)
        assert list(restored["normal"]) == [1, 2, 3, 4, 5]

    def test_no_constant_columns(self):
        """測試沒有 constant columns 的情況"""
        data = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": ["a", "b", "c", "d", "e"],
            }
        )

        schema = SchemaMetadater.from_data(data, enable_stats=True)

        processor = ConstantProcessor()
        processor.fit(data, schema)

        # 沒有 constant columns
        assert len(processor.constant_columns) == 0

        # Transform 應該返回原始資料的副本
        transformed = processor.transform(data)
        pd.testing.assert_frame_equal(transformed, data)


class TestProcessorIntegration:
    """測試 ConstantProcessor 與 Processor 的集成"""

    def test_processor_with_constant_columns(self):
        """測試 Processor 正確處理 constant columns"""
        # 創建包含 constant column 的測試資料
        data = pd.DataFrame(
            {
                "normal_num": [1.0, 2.0, 3.0, 4.0, 5.0],
                "constant_num": [100.0, 100.0, 100.0, 100.0, 100.0],
                "normal_cat": ["a", "b", "c", "d", "e"],
                "constant_cat": ["X", "X", "X", "X", "X"],
            }
        )

        # 生成 metadata
        schema = SchemaMetadater.from_data(data, enable_stats=True)

        # 創建 Processor
        processor = Processor(metadata=schema)

        # Fit（應該會自動處理 constant columns）
        processor.fit(data)

        # 驗證 ConstantProcessor 檢測到 constant columns
        assert len(processor._constant_processor.constant_columns) == 2
        assert "constant_num" in processor._constant_processor.constant_columns
        assert "constant_cat" in processor._constant_processor.constant_columns

        # Transform
        transformed = processor.transform(data)

        # Constant columns 應該在 transform 過程中被移除
        assert "constant_num" not in transformed.columns
        assert "constant_cat" not in transformed.columns
        assert "normal_num" in transformed.columns
        assert "normal_cat" in transformed.columns

        # Inverse transform（模擬合成資料）
        synthetic = pd.DataFrame(
            {
                "normal_num": [1.5, 2.5, 3.5],
                "normal_cat": [0.1, 0.5, 0.9],  # 編碼後的值
            }
        )

        # Inverse transform 應該還原 constant columns
        restored = processor.inverse_transform(synthetic)
        assert "constant_num" in restored.columns
        assert "constant_cat" in restored.columns
        assert all(restored["constant_num"] == 100.0)
        assert all(restored["constant_cat"] == "X")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
