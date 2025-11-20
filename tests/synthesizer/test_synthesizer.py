from unittest.mock import Mock, patch

import pandas as pd
import pytest

from petsard.exceptions import (ConfigError, MissingDependencyError,
                                UncreatedError)
from petsard.synthesizer.synthesizer import Synthesizer, SynthesizerMap


# 測試 Synthesizer 基本功能
class TestSynthesizer:
    # 測試初始化功能 - 使用內建方法
    def test_initialization(self):
        synthesizer = Synthesizer(method="petsard-gaussian_copula")
        assert synthesizer.config.method == "petsard-gaussian_copula"
        assert synthesizer._impl is None

        synthesizer = Synthesizer(
            method="petsard-gaussian_copula", sample_num_rows=500
        )
        assert synthesizer.config.sample_num_rows == 500

    # 測試 SDV 方法需要依賴檢查
    def test_sdv_method_requires_dependency(self):
        with pytest.raises(MissingDependencyError):
            Synthesizer(method="petsard-gaussian_copula")

    # 測試 create 方法 - 使用內建方法
    def test_create_basic(self):
        synthesizer = Synthesizer(method="petsard-gaussian_copula")

        # 在 create 前，_impl 為 None
        assert synthesizer._impl is None

        # 模擬 _determine_sample_configuration 方法，避免依賴實際邏輯
        with patch.object(
            synthesizer,
            "_determine_sample_configuration",
            return_value=("Source data", 100),
        ):
            synthesizer.create()

            # 在 create 後，_impl 已設置
            assert synthesizer._impl is not None

    # 測試在未 create 前呼叫 fit 會引發 UncreatedError
    def test_fit_without_create(self):
        synthesizer = Synthesizer(method="petsard-gaussian_copula")
        with pytest.raises(UncreatedError):
            synthesizer.fit(data=pd.DataFrame())

    # 測試非 CUSTOM_DATA 方法但無資料時引發 ConfigError
    def test_fit_without_data_raises_error(self):
        synthesizer = Synthesizer(method="petsard-gaussian_copula")
        # 手動設置 _impl，避免使用 create
        synthesizer._impl = Mock()
        synthesizer.config.method_code = SynthesizerMap.PETSARD

        with pytest.raises(ConfigError):
            synthesizer.fit(data=None)

    # 測試 sample 在未 create 時返回空 DataFrame
    def test_sample_without_create(self):
        synthesizer = Synthesizer(method="petsard-gaussian_copula")
        result = synthesizer.sample()
        assert isinstance(result, pd.DataFrame)
        assert result.empty
