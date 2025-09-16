---
title: "align"
weight: 4
---

根據詮釋資料定義對齊資料結構。

## 語法

```python
Metadater.align(metadata: Metadata, data: dict[str, pd.DataFrame], strategy: dict = None) -> dict[str, pd.DataFrame]
```

## 參數

- **metadata** (`Metadata`)
  - 詮釋資料定義
  - 作為對齊的目標結構

- **data** (`dict[str, pd.DataFrame]`)
  - 待對齊的資料
  - key 為表格名稱，value 為 DataFrame

- **strategy** (`dict`, 選填)
  - 對齊策略設定
  - 控制如何處理缺失或額外的欄位

## 返回值

- **dict[str, pd.DataFrame]**
  - 對齊後的資料
  - 結構符合詮釋資料定義

## 範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備詮釋資料
metadata = Metadater.from_data(original_data)

# 準備不一致的資料
messy_data = {
    'users': pd.DataFrame({
        'id': ['1', '2', '3'],  # 型別錯誤
        'email': ['a@test.com', 'b@test.com', 'c@test.com'],
        'extra_col': [1, 2, 3]  # 額外欄位
    })
}

# 對齊資料
aligned_data = Metadater.align(metadata, messy_data)

# aligned_data 的結構現在符合 metadata 定義
```

## 對齊策略

```python
strategy = {
    'add_missing_columns': True,    # 新增缺失欄位
    'remove_extra_columns': False,  # 移除額外欄位
    'reorder_columns': True,        # 重新排序欄位
    'add_missing_tables': False     # 新增缺失表格
}
```

## 對齊操作

- **型別轉換**：自動轉換相容的資料型別
- **欄位處理**：新增缺失欄位、移除額外欄位
- **欄位排序**：依照詮釋資料定義重新排序
- **預設值填充**：為缺失欄位填入預設值

## 注意事項

- 對齊不會修改原始資料
- 回傳新的資料副本
- 型別轉換失敗時會保留原始資料