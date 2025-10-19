#!/usr/bin/env python3
"""
測試 DescriberCompare 重構版本
- 驗證 DescriberCompare 重用 DescriberDescribe 的功能
- 測試 JS Divergence 計算
- 測試比較邏輯（diff/pct_change）
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# 將 petsard 加入 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from petsard.evaluator.describer_compare import DescriberCompare
from petsard.evaluator.describer_describe import DescriberDescribe
from petsard.evaluator.stats_base import StatsJSDivergence
from petsard.executor import Executor


class TestDescriberCompare:
    """測試 DescriberCompare 類別"""

    def test_js_divergence_type_validation(self):
        """測試 JS Divergence 的資料類型驗證"""
        js_div = StatsJSDivergence()

        # 測試數值型資料（應該通過）
        data_numeric = {
            "col_ori": pd.Series([1, 2, 3, 4, 5]),
            "col_syn": pd.Series([1, 2, 3, 4, 5]),
        }

        # 不應該拋出錯誤
        result = js_div.eval(data_numeric)
        assert isinstance(result, (int, float))

        # 測試類別型資料（應該通過）
        data_categorical = {
            "col_ori": pd.Series(["A", "B", "C", "A", "B"]),
            "col_syn": pd.Series(["A", "B", "C", "A", "C"]),
        }

        result = js_div.eval(data_categorical)
        assert isinstance(result, (int, float))

    def test_describer_compare_initialization(self):
        """測試 DescriberCompare 的初始化"""
        config = {
            "eval_method": "compare",
            "stats_method": ["mean", "std", "nunique", "jsdivergence"],
            "compare_method": "pct_change",
            "aggregated_method": "mean",
            "summary_method": "mean",
        }

        comparer = DescriberCompare(config)

        # 驗證 DescriberDescribe 實例被創建
        assert hasattr(comparer, "ori_describer")
        assert hasattr(comparer, "syn_describer")
        assert isinstance(comparer.ori_describer, DescriberDescribe)
        assert isinstance(comparer.syn_describer, DescriberDescribe)

        # 驗證 jsdivergence 被過濾掉（不在 describe_method 中）
        describe_methods = comparer.ori_describer.desc_config.describe_method
        assert "jsdivergence" not in describe_methods
        assert "mean" in describe_methods
        assert "std" in describe_methods
        assert "nunique" in describe_methods

    def test_na_value_handling(self):
        """測試 NA 值處理"""
        config = {
            "eval_method": "compare",
            "stats_method": ["mean", "std"],
            "compare_method": "pct_change",
        }

        comparer = DescriberCompare(config)

        # 創建包含 NA 值的測試資料
        ori_df = pd.DataFrame({"mean": [1.0, 2.0, pd.NA], "std": [0.5, pd.NA, 1.5]})

        syn_df = pd.DataFrame({"mean": [1.1, 2.2, pd.NA], "std": [0.6, pd.NA, 1.4]})

        # 執行比較（不應該拋出錯誤）
        result = comparer._apply_comparison(ori_df, syn_df, "pct_change")

        assert "mean_base" in result.columns
        assert "mean_target" in result.columns
        assert "mean_pct_change" in result.columns

        # 驗證 NA 值被正確處理
        assert pd.isna(result.loc[2, "mean_pct_change"])
        assert pd.isna(result.loc[1, "std_pct_change"])

    @pytest.mark.integration
    def test_full_yaml_execution(self):
        """完整的 YAML 執行測試"""
        yaml_path = "demo/petsard-yaml/describer-yaml/describer copy.yaml"
        yaml_file = Path(yaml_path)

        if not yaml_file.exists():
            pytest.skip(f"YAML file not found: {yaml_path}")

        try:
            # 創建執行器
            exec_now = Executor(str(yaml_path))

            # 執行
            exec_now.run()

            # 取得結果
            result = exec_now.get_result()

            # 驗證結果結構
            assert result is not None

            # 檢查是否有 Describer 結果
            describer_keys = [k for k in result.keys() if "Describer" in k]
            assert len(describer_keys) > 0

            # 檢查 columnwise 和 global 結果
            for key in describer_keys:
                if isinstance(result[key], dict):
                    # 應該包含 columnwise 結果
                    if "columnwise" in result[key]:
                        columnwise = result[key]["columnwise"]
                        assert isinstance(columnwise, pd.DataFrame)

                        # 檢查是否有比較欄位
                        compare_cols = [
                            c
                            for c in columnwise.columns
                            if "_pct_change" in c or "_diff" in c
                        ]
                        assert len(compare_cols) > 0, "應該有比較結果欄位"

                        # 檢查是否有 JS Divergence
                        if "jsdivergence" in columnwise.columns:
                            assert columnwise["jsdivergence"].notna().any(), (
                                "應該有 JS Divergence 值"
                            )

                    # 應該包含 global 結果
                    if "global" in result[key]:
                        global_result = result[key]["global"]
                        assert isinstance(global_result, pd.DataFrame)
                        assert "Score" in global_result.columns

        except Exception as e:
            pytest.fail(f"YAML 執行失敗: {e}")


class TestDescriberRefactoring:
    """測試重構的架構改進"""

    def test_code_reuse(self):
        """驗證 DescriberCompare 重用 DescriberDescribe 的功能"""
        config = {
            "eval_method": "compare",
            "stats_method": ["mean", "std", "median", "min", "max"],
            "compare_method": "pct_change",
        }

        comparer = DescriberCompare(config)

        # 創建測試資料
        test_data = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": [10, 20, 30, 40, 50],
                "col3": ["A", "B", "C", "A", "B"],
            }
        )

        # 使用內部的 DescriberDescribe 實例
        ori_result = comparer.ori_describer.eval({"data": test_data})

        # 驗證結果結構
        assert "columnwise" in ori_result
        assert isinstance(ori_result["columnwise"], pd.DataFrame)

        # 驗證統計方法被正確執行
        columnwise = ori_result["columnwise"]
        expected_methods = ["mean", "std", "median", "min", "max"]
        for method in expected_methods:
            assert method in columnwise.columns, f"應該包含 {method} 統計"

    def test_separation_of_concerns(self):
        """測試關注點分離 - 統計計算與比較邏輯分離"""
        config = {
            "eval_method": "compare",
            "stats_method": ["mean"],
            "compare_method": "diff",
        }

        comparer = DescriberCompare(config)

        # DescriberDescribe 負責統計計算
        assert hasattr(comparer.ori_describer, "_eval")
        assert hasattr(comparer.syn_describer, "_eval")

        # DescriberCompare 負責比較邏輯
        assert hasattr(comparer, "_apply_comparison")
        assert hasattr(comparer, "_calculate_jsdivergence")

        # 比較方法映射
        assert "diff" in comparer.COMPARE_METHOD_MAP
        assert "pct_change" in comparer.COMPARE_METHOD_MAP


if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v"])
