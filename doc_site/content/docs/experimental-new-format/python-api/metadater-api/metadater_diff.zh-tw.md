---
title: "diff"
weight: 3
---

比較詮釋資料定義與實際資料的差異。

## 語法

```python
Metadater.diff(metadata: Metadata, data: dict[str, pd.DataFrame]) -> dict
```

## 參數

- **metadata** (`Metadata`)
  - 詮釋資料定義
  - 作為比較的基準

- **data** (`dict[str, pd.DataFrame]`)
  - 實際資料
  - key 為表格名稱，value 為 DataFrame

## 返回值

- **dict**
  - 差異報告，包含：
    - `missing_tables`: 詮釋資料有定義但資料中缺少的表格
    - `extra_tables`: 資料中有但詮釋資料未定義的表格
    - `table_diffs`: 各表格的詳細差異

## 範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備詮釋資料
metadata = Metadater.from_data(original_data)

# 準備新資料
new_data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3, 4],  # 多一筆
        'email': ['a@test.com', 'b@test.com', 'c@test.com', 'd@test.com'],
        'age': [25, 30, 35, 40]  # 多一個欄位
    })
}

# 比較差異
diff_result = Metadater.diff(metadata, new_data)

# 檢視結果
print(f"缺失表格: {diff_result.get('missing_tables', [])}")
print(f"額外表格: {diff_result.get('extra_tables', [])}")
```

## 差異類型

- **表格層級**
  - 缺失表格
  - 額外表格

- **欄位層級**
  - 缺失欄位
  - 額外欄位
  - 型別不符

## 注意事項

- 比較以詮釋資料定義為基準
- 不會修改原始資料
- 回傳的是結構差異，不是資料內容差異