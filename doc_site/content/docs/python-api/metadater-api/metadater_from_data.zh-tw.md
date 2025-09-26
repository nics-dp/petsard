---
title: "from_data"
weight: 321
---

從資料自動推斷並建立詮釋資料結構。

## 語法

```python
Metadater.from_data(
    data: dict[str, pd.DataFrame],
    enable_stats: bool = False
) -> Metadata
```

## 參數

- **data** (`dict[str, pd.DataFrame]`)
  - 資料表字典
  
- **enable_stats** (`bool`, 選填)
  - 是否計算統計資料
  - 預設值：`False`

## 返回值

- **Metadata**
  - 自動推斷的詮釋資料物件

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
    })
}

# 自動推斷結構
metadata = Metadater.from_data(data)
```

## 注意事項

- 會自動偵測每個欄位是否可為空值
- 表格名稱會作為 schema id
- 詳細的推斷規則請參考 YAML 配置文件中的 Schema 章節