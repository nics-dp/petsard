---
title: "from_data()"
weight: 321
---

從資料自動推斷並建立詮釋資料結構。

## 語法

```python
@classmethod
def from_data(
    cls,
    data: dict[str, pd.DataFrame],
    enable_stats: bool = False,
    **kwargs
) -> Metadata
```

## 參數

- **data** : dict[str, pd.DataFrame], required
  - 資料表字典，鍵為表格名稱，值為 DataFrame
  - 必要參數

- **enable_stats** : bool, optional
  - 是否計算統計資料（如最小值、最大值、平均值等）
  - 預設值：`False`
  - 啟用後會增加處理時間但提供更完整的詮釋資料

- ****kwargs** : optional
  - 額外的 Metadata 參數（如 `id`, `name` 等）

## 返回值

- **Metadata**
  - 自動推斷的詮釋資料物件
  - 包含所有表格的 Schema 定義

## 說明

`from_data()` 方法會自動分析資料內容並建立對應的 Metadata 物件。

推斷過程包括：
1. 偵測每個欄位的資料型別（int, float, str, bool, datetime 等）
2. 判斷欄位是否允許空值（nullable）
3. 識別邏輯型別（如 email、phone 等，若適用）
4. 如啟用 `enable_stats`，計算統計資訊

## 基本範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備單一表格資料
data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'email': ['alice@example.com', 'bob@example.com', None]
    })
}

# 自動推斷結構
metadata = Metadater.from_data(data)

# 檢視結果
print(f"資料集 ID: {metadata.id}")
print(f"表格數量: {len(metadata.schemas)}")

# 存取特定表格的 schema
user_schema = metadata.schemas['users']
print(f"欄位數量: {len(user_schema.attributes)}")

# 檢視欄位屬性
for attr_name, attr in user_schema.attributes.items():
    nullable = attr.type_attr.get('nullable', True) if attr.type_attr else True
    print(f"- {attr_name}: {attr.type}, nullable={nullable}")
```

## 進階範例

### 多表格資料推斷

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備多個表格
data = {
    'users': pd.DataFrame({
        'user_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    }),
    'orders': pd.DataFrame({
        'order_id': [101, 102, 103],
        'user_id': [1, 2, 1],
        'amount': [100.5, 200.0, 150.75],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    })
}

# 推斷多表格結構
metadata = Metadater.from_data(data)

print(f"包含表格: {list(metadata.schemas.keys())}")
print(f"\nUsers 表格欄位:")
for attr_name in metadata.schemas['users'].attributes:
    print(f"  - {attr_name}")

print(f"\nOrders 表格欄位:")
for attr_name in metadata.schemas['orders'].attributes:
    print(f"  - {attr_name}")
```

### 啟用統計資訊

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備數值資料
data = {
    'sales': pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5],
        'price': [10.5, 20.0, 15.5, 30.0, 25.5],
        'quantity': [100, 200, 150, 300, 250]
    })
}

# 啟用統計資訊
metadata = Metadater.from_data(data, enable_stats=True)

# 統計資訊會包含在 schema 中（若實作支援）
sales_schema = metadata.schemas['sales']
print(f"Sales 表格統計資訊已啟用")
```

### 處理含空值的資料

```python
from petsard.metadater import Metadater
import pandas as pd
import numpy as np

# 包含空值的資料
data = {
    'employees': pd.DataFrame({
        'emp_id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'department': ['IT', 'HR', None, 'IT'],  # 有空值
        'salary': [50000, 60000, 55000, np.nan]  # 有空值
    })
}

# 推斷結構
metadata = Metadater.from_data(data)

# 檢查哪些欄位允許空值
emp_schema = metadata.schemas['employees']
for attr_name, attr in emp_schema.attributes.items():
    nullable = attr.type_attr.get('nullable', True) if attr.type_attr else True
    nullable_status = "可為空" if nullable else "不可為空"
    print(f"{attr_name}: {nullable_status}")

# 輸出範例：
# emp_id: 不可為空
# name: 不可為空
# department: 可為空
# salary: 可為空
```

## 注意事項

- **自動推斷規則**：
  - 欄位型別根據實際資料內容推斷
  - 如果欄位包含任何空值（NaN, None），則 `type_attr['nullable'] = True`
  - 表格名稱（字典的鍵）會作為 Schema 的 `id`
  - 可透過 `**kwargs` 覆寫預設的 `id` 和 `name`
  - 會自動偵測常數欄位（所有值都相同），設定 `is_constant = True`

- **資料型別支援**（簡化型別系統）：
  - 數值型：`int`, `float`
  - 文字型：`str`
  - 日期型：`date`
  - 日期時間型：`datetime`

- **效能考量**：
  - 大型資料集推斷可能需要較長時間
  - `enable_stats=True` 會增加處理時間
  - 建議先用小樣本測試

- **使用建議**：
  - 適合快速建立初始 schema
  - 建議檢視推斷結果並依需求調整
  - 對於複雜邏輯型別，可能需要手動定義

- **與 Loader 整合**：
  - Loader 內部使用此方法處理無 schema 的資料載入
  - 一般使用者透過 Loader 的 `schema` 參數即可，無需直接呼叫