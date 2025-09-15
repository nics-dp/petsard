---
title: "from_data"
weight: 1
---

從資料自動推斷並建立詮釋資料結構。

## 語法

```python
Metadater.from_data(data: dict[str, pd.DataFrame]) -> Metadata
```

## 參數

- **data** (`dict[str, pd.DataFrame]`)
  - 資料表字典
  - key 為表格名稱，value 為 pandas DataFrame

## 返回值

- **Metadata**
  - 自動推斷的詮釋資料物件
  - 包含所有表格的結構定義

## 範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備資料
data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    }),
    'orders': pd.DataFrame({
        'order_id': [101, 102],
        'user_id': [1, 2],
        'amount': [99.99, 149.99]
    })
}

# 自動推斷結構
metadata = Metadater.from_data(data)

# metadata 現在包含：
# - 兩個 schema：'users' 和 'orders'
# - 每個 schema 的所有欄位定義
# - 自動推斷的資料型別
```

## 自動推斷規則

- **整數**：推斷為 `int64`
- **浮點數**：推斷為 `float64`
- **字串**：推斷為 `object`
- **布林**：推斷為 `bool`
- **日期時間**：推斷為 `datetime64`
- **類別**：保持為 `category`

## 注意事項

- 會自動偵測每個欄位是否可為空值
- 表格名稱會作為 schema id
- 欄位名稱保持原樣