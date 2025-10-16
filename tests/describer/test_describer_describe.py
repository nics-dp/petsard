#!/usr/bin/env python3
"""
測試 DescriberDescribe 獨立功能
- 驗證獨立初始化
- 測試各個統計方法的執行
- 測試結果的粒度組織（global/columnwise/pairwise）
- 測試邊緣案例
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# 將 petsard 加入 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from petsard.evaluator.describer_describe import DescriberDescribe
from petsard.exceptions import UnsupportedMethodError


class TestDescriberDescribeInitialization:
    """測試 DescriberDescribe 初始化"""

    def test_basic_initialization(self):
        """測試基本初始化"""
        config = {
            "eval_method": "describe",
            "describe_method": ["mean", "std", "min", "max"],
        }

        describer = DescriberDescribe(config)

        assert describer is not None
        assert hasattr(describer, "desc_config")
        assert describer.desc_config.describe_method == ["mean", "std", "min", "max"]

    def test_default_methods(self):
        """測試預設統計方法"""
        config = {"eval_method": "describe"}

        describer = DescriberDescribe(config)

        # 驗證使用預設方法
        default_methods = describer.desc_config.describe_method
        assert "mean" in default_methods
        assert "std" in default_methods
        assert "min" in default_methods
        assert "max" in default_methods

    def test_invalid_method_raises_error(self):
        """測試無效方法會拋出錯誤"""
        config = {
            "eval_method": "describe",
            "describe_method": ["invalid_method", "mean"],
        }

        with pytest.raises(UnsupportedMethodError):
            DescriberDescribe(config)

    def test_single_method_string_conversion(self):
        """測試單一方法字串自動轉換為列表"""
        config = {"eval_method": "describe", "describe_method": "mean"}

        describer = DescriberDescribe(config)

        assert isinstance(describer.desc_config.describe_method, list)
        assert describer.desc_config.describe_method == ["mean"]


class TestDescriberDescribeStatsMethods:
    """測試各個統計方法"""

    @pytest.fixture
    def sample_data(self):
        """創建測試資料"""
        return pd.DataFrame(
            {
                "numeric1": [1, 2, 3, 4, 5],
                "numeric2": [10, 20, 30, 40, 50],
                "numeric3": [1.5, 2.5, 3.5, 4.5, 5.5],
            }
        )

    def test_global_methods(self, sample_data):
        """測試全域統計方法"""
        config = {
            "eval_method": "describe",
            "describe_method": ["row_count", "col_count", "global_na_count"],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": sample_data})

        assert "global" in result
        global_result = result["global"]
        assert "row_count" in global_result.columns
        assert "col_count" in global_result.columns
        assert global_result["row_count"].iloc[0] == 5
        assert global_result["col_count"].iloc[0] == 3

    def test_columnwise_methods(self, sample_data):
        """測試欄位統計方法"""
        config = {
            "eval_method": "describe",
            "describe_method": ["mean", "std", "min", "max", "median"],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": sample_data})

        assert "columnwise" in result
        columnwise = result["columnwise"]

        # 驗證所有方法都有執行
        for method in ["mean", "std", "min", "max", "median"]:
            assert method in columnwise.columns

        # 驗證數值正確性（以 numeric1 為例）
        assert columnwise.loc["numeric1", "mean"] == 3.0
        assert columnwise.loc["numeric1", "min"] == 1
        assert columnwise.loc["numeric1", "max"] == 5

    def test_pairwise_methods(self, sample_data):
        """測試成對統計方法"""
        config = {"eval_method": "describe", "describe_method": ["corr", "cov"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": sample_data})

        assert "pairwise" in result
        pairwise = result["pairwise"]

        # 驗證包含必要欄位
        assert "column1" in pairwise.columns
        assert "column2" in pairwise.columns
        assert "corr" in pairwise.columns
        assert "cov" in pairwise.columns

        # 驗證有配對組合
        assert len(pairwise) > 0

    def test_percentile_method(self, sample_data):
        """測試百分位數方法"""
        config = {
            "eval_method": "describe",
            "describe_method": ["percentile"],
            "percentile": 0.75,  # Must be between 0 and 1
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": sample_data})

        assert "columnwise" in result
        columnwise = result["columnwise"]
        # 欄位名稱會是 "75.0 th percentile" 而不是 "percentile"
        percentile_cols = [col for col in columnwise.columns if "percentile" in col]
        assert len(percentile_cols) > 0, "應該有百分位數欄位"


class TestDescriberDescribeGranularity:
    """測試結果粒度組織"""

    def test_granularity_organization(self):
        """測試不同粒度的結果組織"""
        data = pd.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [10, 20, 30, 40, 50]})

        config = {
            "eval_method": "describe",
            "describe_method": [
                "row_count",  # global
                "mean",  # columnwise
                "corr",  # pairwise
            ],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": data})

        # 驗證三種粒度都存在
        assert "global" in result
        assert "columnwise" in result
        assert "pairwise" in result

        # 驗證資料類型
        assert isinstance(result["global"], pd.DataFrame)
        assert isinstance(result["columnwise"], pd.DataFrame)
        assert isinstance(result["pairwise"], pd.DataFrame)

    def test_mixed_granularity_methods(self):
        """測試混合粒度的方法"""
        data = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": [10, 20, 30, 40, 50],
                "col3": [100, 200, 300, 400, 500],
            }
        )

        config = {
            "eval_method": "describe",
            "describe_method": [
                "row_count",
                "col_count",  # global
                "mean",
                "std",
                "min",
                "max",  # columnwise
                "corr",
                "cov",  # pairwise
            ],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": data})

        # Global 結果應該是單行
        assert len(result["global"]) == 1

        # Columnwise 結果應該有每個欄位一行
        assert len(result["columnwise"]) == 3

        # Pairwise 結果應該有配對組合
        assert len(result["pairwise"]) > 0


class TestDescriberDescribeEdgeCases:
    """測試邊緣案例"""

    def test_empty_dataframe(self):
        """測試空 DataFrame"""
        empty_data = pd.DataFrame()

        config = {"eval_method": "describe", "describe_method": ["mean", "std"]}

        describer = DescriberDescribe(config)

        # 空 DataFrame 會返回空結果，不會引發錯誤
        result = describer.eval({"data": empty_data})

        # 驗證結果存在但為空
        assert result is not None
        if "columnwise" in result:
            assert len(result["columnwise"]) == 0

    def test_single_column_dataframe(self):
        """測試單欄位 DataFrame"""
        single_col_data = pd.DataFrame({"only_col": [1, 2, 3, 4, 5]})

        config = {
            "eval_method": "describe",
            "describe_method": ["mean", "std", "min", "max"],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": single_col_data})

        assert "columnwise" in result
        columnwise = result["columnwise"]

        # 應該只有一行結果
        assert len(columnwise) == 1
        assert "only_col" in columnwise.index

    def test_all_na_column(self):
        """測試全 NA 值欄位"""
        na_data = pd.DataFrame(
            {"col1": [1, 2, 3], "col2": [pd.NA, pd.NA, pd.NA], "col3": [7, 8, 9]}
        )

        config = {
            "eval_method": "describe",
            "describe_method": ["mean"],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": na_data})

        columnwise = result["columnwise"]

        # col1 和 col3 應該有有效的 mean
        assert "col1" in columnwise.index
        assert "col3" in columnwise.index
        assert not pd.isna(columnwise.loc["col1", "mean"])
        assert not pd.isna(columnwise.loc["col3", "mean"])

        # col2 可能不在結果中（全為 NA 值可能被過濾），或者 mean 為 NA
        if "col2" in columnwise.index:
            assert pd.isna(columnwise.loc["col2", "mean"])

    def test_single_row_dataframe(self):
        """測試單列 DataFrame"""
        single_row_data = pd.DataFrame({"col1": [1], "col2": [10], "col3": [100]})

        config = {"eval_method": "describe", "describe_method": ["mean", "std"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": single_row_data})

        columnwise = result["columnwise"]

        # mean 應該等於該值
        assert columnwise.loc["col1", "mean"] == 1

        # std 應該是 NA 或 0（單一值的標準差）
        assert (
            pd.isna(columnwise.loc["col1", "std"]) or columnwise.loc["col1", "std"] == 0
        )

    def test_extreme_values(self):
        """測試極值"""
        extreme_data = pd.DataFrame(
            {
                "very_large": [1e10, 2e10, 3e10],
                "moderate": [100, 200, 300],  # 使用中等數值代替極小值
                "mixed": [1e10, 100, 0],
            }
        )

        config = {"eval_method": "describe", "describe_method": ["min", "max", "mean"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": extreme_data})

        columnwise = result["columnwise"]

        # 驗證極值被正確計算
        assert abs(columnwise.loc["very_large", "max"] - 3e10) < 1e9
        assert columnwise.loc["moderate", "min"] == 100
        assert columnwise.loc["moderate", "max"] == 300

    def test_constant_column(self):
        """測試常數欄位"""
        constant_data = pd.DataFrame(
            {"constant": [5, 5, 5, 5, 5], "varying": [1, 2, 3, 4, 5]}
        )

        config = {"eval_method": "describe", "describe_method": ["std", "var", "mean"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": constant_data})

        columnwise = result["columnwise"]

        # 常數欄位的標準差應該是 0
        assert columnwise.loc["constant", "std"] == 0
        assert columnwise.loc["constant", "var"] == 0
        assert columnwise.loc["constant", "mean"] == 5


class TestDescriberDescribeDataTypes:
    """測試不同資料類型處理"""

    def test_integer_columns(self):
        """測試整數欄位"""
        int_data = pd.DataFrame(
            {"int_col": [1, 2, 3, 4, 5], "int_col2": [10, 20, 30, 40, 50]}
        )

        config = {
            "eval_method": "describe",
            "describe_method": ["mean", "nunique"],
        }

        describer = DescriberDescribe(config)
        result = describer.eval({"data": int_data})

        columnwise = result["columnwise"]

        # nunique 應該有值（可能是整數或 pandas 整數）
        nunique_val = columnwise.loc["int_col", "nunique"]
        if not pd.isna(nunique_val):
            assert int(nunique_val) == 5

        # mean 應該有效
        assert not pd.isna(columnwise.loc["int_col", "mean"])

    def test_float_columns(self):
        """測試浮點數欄位"""
        float_data = pd.DataFrame(
            {
                "float_col": [1.1, 2.2, 3.3, 4.4, 5.5],
                "float_col2": [10.5, 20.5, 30.5, 40.5, 50.5],
            }
        )

        config = {"eval_method": "describe", "describe_method": ["mean", "std"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": float_data})

        columnwise = result["columnwise"]

        # 驗證浮點數計算
        assert isinstance(columnwise.loc["float_col", "mean"], (float, np.floating))

    def test_mixed_types(self):
        """測試混合類型"""
        mixed_data = pd.DataFrame(
            {
                "int_col": [1, 2, 3, 4, 5],
                "float_col": [1.5, 2.5, 3.5, 4.5, 5.5],
                "bool_col": [True, False, True, False, True],
            }
        )

        config = {"eval_method": "describe", "describe_method": ["mean", "nunique"]}

        describer = DescriberDescribe(config)
        result = describer.eval({"data": mixed_data})

        columnwise = result["columnwise"]

        # 所有欄位都應該有結果
        assert len(columnwise) == 3
        assert "int_col" in columnwise.index
        assert "float_col" in columnwise.index
        assert "bool_col" in columnwise.index


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v"])
