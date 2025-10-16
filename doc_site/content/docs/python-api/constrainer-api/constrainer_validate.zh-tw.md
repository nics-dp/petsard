---
title: "validate()"
weight: 353
---

驗證資料是否符合約束條件，不修改資料。

## 語法

```python
def validate(
    data: pd.DataFrame,
    return_details: bool = True,
    max_examples_per_rule: int = 6
) -> dict
```

## 參數

- `data`: 要驗證的資料框
- `return_details`: 是否返回詳細違規記錄（預設 True）
- `max_examples_per_rule`: 每條規則的違規範例數上限（預設 6）

## 返回值

驗證結果字典：

```python
{
    'total_rows': 100,           # 總列數
    'passed_rows': 85,           # 通過列數
    'failed_rows': 15,           # 失敗列數
    'pass_rate': 0.85,           # 通過率
    'is_fully_compliant': False, # 是否完全符合
    'constraint_violations': {   # 違規統計
        'field_constraints': {
            'Rule 1: age >= 18': {
                'failed_count': 10,
                'fail_rate': 0.1,
                'violation_examples': [0, 5, 12]
            }
        }
    },
    'violation_details': DataFrame  # 違規資料（可選）
}
```

## 與其他方法的差異

| 方法 | 修改資料 | 返回內容 |
|------|---------|---------|
| validate() | ❌ | 驗證報告 |
| apply() | ✅ | 過濾後的資料 |
| resample_until_satisfy() | ✅ | 重新生成的資料 |

## 基本範例

```python
from petsard import Constrainer
import pandas as pd

# 準備資料
df = pd.DataFrame({
    'age': [25, 15, 45, 70, 35],
    'performance': [5, 3, 4, 2, 5]
})

# 驗證
constrainer = Constrainer(config)
result = constrainer.validate(df)

print(f"通過率: {result['pass_rate']:.2%}")
print(f"完全符合: {result['is_fully_compliant']}")
```

## 查看違規詳情

```python
result = constrainer.validate(df, return_details=True)

# 檢視違規統計
for constraint_type, violations in result['constraint_violations'].items():
    print(f"\n{constraint_type}:")
    for rule_name, stats in violations.items():
        print(f"  {rule_name}: {stats['failed_count']} 次違規")

# 檢視違規資料
if not result['is_fully_compliant']:
    print(result['violation_details'])
```

## 批次驗證

```python
# 驗證多批資料
batches = {'batch_1': df1, 'batch_2': df2, 'batch_3': df3}

for name, data in batches.items():
    result = constrainer.validate(data, return_details=False)
    print(f"{name}: {result['pass_rate']:.1%}")
```

## 驗證合成資料

```python
# 生成合成資料
synthetic = synthesizer.sample(num_rows=1000)

# 驗證品質
result = constrainer.validate(synthetic)

if result['pass_rate'] < 0.95:
    # 品質不佳，重新生成
    better_data = constrainer.resample_until_satisfy(
        data=pd.DataFrame(),
        target_rows=1000,
        synthesizer=synthesizer
    )
```

## 注意事項

- 不會修改輸入資料
- 適用於資料品質檢查和監控
- `return_details=False` 可節省記憶體
- 違規標記欄位以 `__violated_` 開頭
- 驗證結果會儲存在 `constrainer.validation_result`