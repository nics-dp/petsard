"""
簡單的 Constrainer validate 方法測試腳本
"""

import sys

import pandas as pd

sys.path.insert(0, ".")

from petsard.constrainer import Constrainer


def test_validate_all_pass():
    """測試所有資料都通過驗證的情況"""
    print("\n=== 測試 1: 所有資料都通過驗證 ===")

    data = pd.DataFrame(
        {
            "age": [25, 30, 35, 40],
            "income": [50000, 60000, 70000, 80000],
        }
    )

    config = {"field_constraints": ["age > 20", "income > 40000"]}
    constrainer = Constrainer(config)
    result = constrainer.validate(data, return_details=True)

    print(f"總資料筆數: {result['total_rows']}")
    print(f"通過筆數: {result['passed_rows']}")
    print(f"未通過筆數: {result['failed_rows']}")
    print(f"通過率: {result['pass_rate']:.2%}")
    print(f"是否完全符合: {result['is_fully_compliant']}")
    print(f"違規記錄數: {len(result['violation_details'])}")

    assert result["total_rows"] == 4
    assert result["passed_rows"] == 4
    assert result["is_fully_compliant"] is True
    print("✓ 測試通過！")


def test_validate_partial_pass():
    """測試部分資料通過驗證的情況"""
    print("\n=== 測試 2: 部分資料通過驗證 ===")

    data = pd.DataFrame(
        {
            "age": [15, 25, 30, 35],  # 第一筆不符合 age > 20
            "income": [50000, 60000, 70000, 80000],
        }
    )

    config = {"field_constraints": ["age > 20", "income > 40000"]}
    constrainer = Constrainer(config)
    result = constrainer.validate(data, return_details=True)

    print(f"總資料筆數: {result['total_rows']}")
    print(f"通過筆數: {result['passed_rows']}")
    print(f"未通過筆數: {result['failed_rows']}")
    print(f"通過率: {result['pass_rate']:.2%}")
    print(f"是否完全符合: {result['is_fully_compliant']}")
    print("\n違規記錄:")
    print(result["violation_details"])

    assert result["total_rows"] == 4
    assert result["passed_rows"] == 3
    assert result["is_fully_compliant"] is False
    print("\n✓ 測試通過！")


def test_validate_multiple_violations():
    """測試多個違規的情況"""
    print("\n=== 測試 3: 多個違規統計 ===")

    data = pd.DataFrame(
        {
            "age": [15, 25, 18, 35],  # 2筆不符合 age > 20
            "income": [30000, 60000, 70000, 80000],  # 1筆不符合 income > 40000
        }
    )

    config = {"field_constraints": ["age > 20", "income > 40000"]}
    constrainer = Constrainer(config)
    result = constrainer.validate(data, return_details=True)

    print(f"總資料筆數: {result['total_rows']}")
    print(f"通過筆數: {result['passed_rows']}")
    print(f"未通過筆數: {result['failed_rows']}")
    print(f"通過率: {result['pass_rate']:.2%}")

    print("\n各條件違規統計:")
    for constraint_type, rules_dict in result["constraint_violations"].items():
        print(f"  {constraint_type}:")
        for rule_name, rule_info in rules_dict.items():
            print(f"    {rule_name}:")
            print(f"      - 違規筆數: {rule_info['failed_count']}")
            print(f"      - 違規率: {rule_info['fail_rate']:.2%}")

    print("\n違規記錄:")
    print(result["violation_details"])

    assert result["total_rows"] == 4
    assert result["passed_rows"] == 2

    # 驗證各條規則的違規數量
    field_constraints = result["constraint_violations"]["field_constraints"]
    assert "Rule 1: age > 20" in field_constraints
    assert field_constraints["Rule 1: age > 20"]["failed_count"] == 2
    assert "Rule 2: income > 40000" in field_constraints
    assert field_constraints["Rule 2: income > 40000"]["failed_count"] == 1

    print("\n✓ 測試通過！")


def test_resample_mode():
    """測試 resample 模式（這個需要 synthesizer，我們只驗證邏輯）"""
    print("\n=== 測試 4: Resample 模式說明 ===")
    print("當有 synthesizer 時，Constrainer 會使用 resample_until_satisfy 方法")
    print("進行反覆抽樣直到符合條件。此模式不使用 validate 方法。")
    print("✓ 邏輯說明完成！")


if __name__ == "__main__":
    print("開始測試 Constrainer.validate() 方法...")

    try:
        test_validate_all_pass()
        test_validate_partial_pass()
        test_validate_multiple_violations()
        test_resample_mode()

        print("\n" + "=" * 50)
        print("所有測試通過！✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n測試失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
