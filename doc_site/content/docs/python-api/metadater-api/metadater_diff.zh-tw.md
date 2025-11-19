---
title: "diff()"
weight: 323
---

比較詮釋資料定義與實際資料的差異。

## 語法

```python
@staticmethod
def diff(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict
```

## 參數

- **metadata** : Metadata, required
  - 詮釋資料定義（期望的結構）
  - 必要參數

- **data** : dict[str, pd.DataFrame], required
  - 實際資料，鍵為表格名稱，值為 DataFrame
  - 必要參數

## 返回值

- **dict**
  - 差異報告字典
  - 如果沒有差異則返回空字典 `{}`
  - 差異報告包含以下可能的鍵：
    - `missing_tables`: metadata 中定義但資料中缺失的表格
    - `extra_tables`: 資料中存在但 metadata 未定義的表格
    - `table_diffs`: 各表格的詳細差異
      - `missing_columns`: 定義但缺失的欄位
      - `extra_columns`: 存在但未定義的欄位
      - `type_mismatches`: 型別不符的欄位
      - `nullable_mismatches`: nullable 屬性不符的欄位

## 說明

`diff()` 方法用於檢測期望的資料結構（metadata）與實際資料之間的差異，適用於：

1. 資料驗證：確保資料符合預期結構
2. 版本控制：追蹤資料結構變更
3. 資料品質檢查：在處理前驗證資料完整性
4. 除錯：識別資料載入或轉換過程中的問題

## 基本範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義期望的 schema
config = {
    'id': 'expected_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 實際資料（有差異）
actual_data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'email': ['alice@ex.com', 'bob@ex.com', 'charlie@ex.com']  # 額外欄位
        # 缺少 'age' 欄位
    })
}

# 比較差異
diff_report = Metadater.diff(metadata, actual_data)

# 檢查結果
if diff_report:
    print("發現資料結構差異：")
    print(diff_report)
else:
    print("資料結構完全符合")
```

## 進階範例

### 詳細差異分析

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義 schema
config = {
    'id': 'user_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True},
                'email': {'name': 'email', 'type': 'str', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 實際資料有多種差異
actual_data = {
    'users': pd.DataFrame({
        'user_id': [1, 2, 3],
        'username': ['alice', 'bob', 'charlie'],
        'age': [25.5, 30.0, 35.0],  # 型別錯誤：應為 int 但為 float
        'phone': ['123-456', '234-567', '345-678']  # 額外欄位
        # 缺少 'email' 欄位
    })
}

# 比較差異
diff_report = Metadater.diff(metadata, actual_data)

# 分析差異報告
if 'table_diffs' in diff_report:
    for table_name, table_diff in diff_report['table_diffs'].items():
        print(f"\n表格: {table_name}")

        if 'missing_columns' in table_diff:
            print(f"  缺失欄位: {table_diff['missing_columns']}")

        if 'extra_columns' in table_diff:
            print(f"  額外欄位: {table_diff['extra_columns']}")

        if 'type_mismatches' in table_diff:
            print(f"  型別不符: {table_diff['type_mismatches']}")
```

### 多表格差異檢測

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義多表格 schema
config = {
    'id': 'ecommerce',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False}
            }
        },
        'orders': {
            'id': 'orders',
            'attributes': {
                'order_id': {'name': 'order_id', 'type': 'int', 'nullable': False},
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'amount': {'name': 'amount', 'type': 'float', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 實際資料（缺少 orders 表）
actual_data = {
    'users': pd.DataFrame({
        'user_id': [1, 2],
        'name': ['Alice', 'Bob']
    }),
    'products': pd.DataFrame({  # 額外的表格
        'product_id': [101, 102],
        'name': ['Product A', 'Product B']
    })
}

# 比較差異
diff_report = Metadater.diff(metadata, actual_data)

# 檢查表格層級的差異
if 'missing_tables' in diff_report:
    print(f"缺失的表格: {diff_report['missing_tables']}")

if 'extra_tables' in diff_report:
    print(f"額外的表格: {diff_report['extra_tables']}")
```

### 資料驗證工作流程

```python
from petsard.metadater import Metadater
import pandas as pd
import sys

# 載入期望的 schema
with open('expected_schema.yaml', 'r') as f:
    import yaml
    config = yaml.safe_load(f)

metadata = Metadater.from_dict(config)

# 載入實際資料
actual_data = {
    'users': pd.read_csv('users.csv'),
    'orders': pd.read_csv('orders.csv')
}

# 驗證資料結構
diff_report = Metadater.diff(metadata, actual_data)

if diff_report:
    print("❌ 資料結構驗證失敗")
    print("\n差異報告：")
    print(diff_report)

    # 記錄到日誌檔
    with open('validation_errors.log', 'a') as log:
        log.write(f"差異報告: {diff_report}\n")

    sys.exit(1)
else:
    print("✅ 資料結構驗證通過")
    # 繼續處理資料...
```

### 型別相容性檢查

```python
from petsard.metadater import Metadater
import pandas as pd
import numpy as np

# 定義嚴格的型別 schema
config = {
    'id': 'strict_schema',
    'schemas': {
        'measurements': {
            'id': 'measurements',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': False},
                'timestamp': {'name': 'timestamp', 'type': 'datetime', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 測試不同的資料型別
test_cases = [
    {
        'name': '正確型別',
        'data': pd.DataFrame({
            'id': [1, 2, 3],
            'value': [1.5, 2.5, 3.5],
            'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
    },
    {
        'name': '型別錯誤',
        'data': pd.DataFrame({
            'id': ['A', 'B', 'C'],  # 應為 int
            'value': [1.5, 2.5, 3.5],
            'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
    }
]

for test_case in test_cases:
    print(f"\n測試案例: {test_case['name']}")
    diff_report = Metadater.diff(metadata, {'measurements': test_case['data']})

    if diff_report:
        print(f"  ❌ 發現差異: {diff_report}")
    else:
        print(f"  ✅ 通過驗證")
```

## 注意事項

- **檢測內容**：
  - 表格存在性：檢查是否有缺失或額外的表格
  - 欄位完整性：檢查欄位是否全部存在
  - 型別一致性：檢查資料型別是否符合定義
  - 空值屬性：檢查 nullable 設定是否一致

- **差異報告結構**：
  - 空字典表示完全相符
  - 非空字典包含詳細的差異資訊
  - 差異報告可用於生成使用者友善的錯誤訊息

- **型別比較**：
  - 型別比較基於 pandas dtype
  - 某些型別轉換可能被視為相容（如 int64 vs int32）
  - 建議使用嚴格的型別定義

- **使用時機**：
  - 資料載入後的驗證
  - 資料轉換前的檢查
  - 持續整合/部署的資料品質檢查
  - 資料契約（Data Contract）驗證

- **效能考量**：
  - 大型資料集的差異檢測可能較耗時
  - 建議對關鍵欄位優先檢查
  - 可考慮抽樣檢查以提升效能

- **與 align() 的關係**：
  - `diff()` 僅報告差異，不修改資料
  - `align()` 會根據 metadata 調整資料結構
  - 建議先用 `diff()` 檢查，再決定是否使用 `align()`

- **錯誤處理**：
  - 如果輸入格式不正確可能引發例外
  - 建議使用 try-except 處理可能的錯誤
  - 差異報告可序列化為 JSON 或 YAML 以便記錄