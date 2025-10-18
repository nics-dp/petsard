---
title: "apply()"
weight: 352
---

套用已設定的約束條件到輸入資料。

## 語法

```python
def apply(
    df: pd.DataFrame,
    target_rows: int = None
) -> pd.DataFrame
```

## 參數

- **df** : pd.DataFrame, required
    - 要套用約束的輸入資料框
    - 必要參數
    
- **target_rows** : int, optional
    - 目標列數
    - 由 `\1` 內部使用
    - 用於欄位比例約束的目標行數設定
    - 預設值：`None`

## 返回值

- **pd.DataFrame**
    - 套用所有約束條件後的資料框
    - 可能比輸入資料框的列數少（因約束過濾）

## 說明

`\1` 方法按以下順序依序套用所有已設定的約束條件：

1. **NaN Groups** (`nan_groups`)：處理空值相關規則
2. **Field Constraints** (`field_constraints`)：檢查欄位值域約束
3. **Field Combinations** (`field_combinations`)：驗證欄位組合規則
4. **Field Proportions** (`field_proportions`)：維護欄位比例分布

每個階段都會過濾不符合條件的資料列，最終返回同時滿足所有約束的資料。

### 約束套用流程

```
輸入資料 (N 列)
    ↓
NaN Groups 處理 (刪除/清除/複製)
    ↓
Field Constraints 過濾 (值域檢查)
    ↓
Field Combinations 過濾 (組合規則)
    ↓
Field Proportions 過濾 (比例維護)
    ↓
輸出資料 (≤N 列)
```

## 基本範例

### 簡單約束套用

```python
from petsard import Constrainer
import pandas as pd

# 準備資料
df = pd.DataFrame({
    'age': [25, 15, 45, 70, 35],
    'performance': [5, 3, 4, 2, 5],
    'education': ['PhD', 'Bachelor', 'Master', 'Bachelor', 'PhD']
})

# 設定約束
config = {
    'field_constraints': [
        "age >= 18 & age <= 65",
        "performance >= 4"
    ]
}

# 套用約束
constrainer = Constrainer(config)
result = constrainer.apply(df)

print(f"原始列數: {len(df)}")
print(f"約束後列數: {len(result)}")
# 原始列數: 5
# 約束後列數: 2 (只有年齡 25 和 35 的資料滿足條件)
```

### 多重約束套用

```python
from petsard import Constrainer
import pandas as pd

# 準備資料
df = pd.DataFrame({
    'name': ['Alice', None, 'Charlie', 'David'],
    'age': [25, 30, 45, 55],
    'salary': [50000, 60000, 80000, 90000],
    'education': ['Bachelor', 'Master', 'PhD', 'Master']
})

# 設定多重約束
config = {
    'nan_groups': {
        'name': 'delete'  # 刪除 name 為空的資料列
    },
    'field_constraints': [
        "age >= 20 & age <= 50"  # 年齡限制
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {
                'PhD': [70000, 80000, 90000],  # PhD 薪資範圍
                'Master': [50000, 60000, 70000]  # Master 薪資範圍
            }
        )
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)

print("套用約束後的資料：")
print(result)
# 只會保留同時滿足以下條件的資料：
# 1. name 不為空
# 2. age 在 20-50 之間
# 3. education-salary 組合符合規則
```

## 進階範例

### 與欄位比例約束配合

```python
from petsard import Constrainer
import pandas as pd

# 準備資料（類別不平衡）
df = pd.DataFrame({
    'category': ['A'] * 80 + ['B'] * 15 + ['C'] * 5,
    'value': range(100)
})

print("原始分布：")
print(df['category'].value_counts())
# A    80
# B    15
# C     5

# 設定欄位比例約束
config = {
    'field_proportions': [
        {
            'fields': 'category',
            'mode': 'all',
            'tolerance': 0.1  # 容許 10% 偏差
        }
    ]
}

constrainer = Constrainer(config)
# 注意：通常由 resample_until_satisfy 自動設定 target_rows
# 這裡手動設定為示範
result = constrainer.apply(df, target_rows=50)

print("\n約束後分布：")
print(result['category'].value_counts())
# 會維護原始比例 (80:15:5)，但總數約為 50 列
```

### 複雜條件組合

```python
from petsard import Constrainer
import pandas as pd

# 準備員工資料
df = pd.DataFrame({
    'workclass': ['Private', None, 'Government', 'Private', 'Self-emp'],
    'occupation': ['Manager', 'Sales', None, 'Tech', 'Manager'],
    'age': [35, 28, 45, 22, 50],
    'hours_per_week': [40, 35, 50, 65, 38],
    'income': ['>50K', '<=50K', '>50K', '<=50K', '>50K'],
    'education': ['Master', 'Bachelor', 'PhD', 'Bachelor', 'Master']
})

config = {
    'nan_groups': {
        'workclass': 'delete',  # 刪除 workclass 為空的列
        'occupation': {
            'erase': ['income']  # occupation 為空時，清除 income
        }
    },
    'field_constraints': [
        "age >= 18 & age <= 65",
        "hours_per_week >= 20 & hours_per_week <= 60",
        "(education == 'PhD' & income == '>50K') | education != 'PhD'"
    ],
    'field_combinations': [
        (
            {'education': 'income'},
            {
                'PhD': ['>50K'],  # PhD 必須高收入
                'Master': ['>50K', '<=50K']  # Master 可高可低
            }
        )
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)

print(f"原始資料: {len(df)} 列")
print(f"約束後資料: {len(result)} 列")
print("\n約束後的資料：")
print(result)
```

## 注意事項

- **資料副本**：方法會複製輸入資料框，不會修改原始資料
- **順序重要**：約束按固定順序套用，順序不可調整
- **資料減少**：約束通常會過濾資料，返回的資料列數可能大幅減少
- **AND 邏輯**：所有約束以 AND 組合，資料必須全部滿足才會保留
- **target_rows**：一般使用者不需手動設定此參數，由 `\1` 內部使用
- **空結果**：如果約束條件過於嚴格，可能返回空的資料框
- **效能考量**：大型資料集上的複雜約束可能需要較長執行時間
- **欄位比例**：只有設定了 field_proportions 且提供 target_rows 時才會進行比例維護
- **驗證建議**：建議在套用前先用小樣本測試約束條件的合理性

## 相關方法

- `\1`：初始化約束設定
- `\1`：重複採樣直到滿足約束
- `\1`：註冊自訂約束類型