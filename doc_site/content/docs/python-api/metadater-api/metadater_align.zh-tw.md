---
title: "align"
weight: 324
---

根據詮釋資料定義對齊資料結構。

## 語法

```python
Metadater.align(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]
```

## 參數

- **metadata** (`Metadata`)
  - 詮釋資料定義
  
- **data** (`dict[str, pd.DataFrame]`)
  - 待對齊資料

## 返回值

- **dict[str, pd.DataFrame]**
  - 對齊後的資料

## 範例

```python
from petsard.metadater import Metadater

# 對齊資料結構
aligned_data = Metadater.align(metadata, raw_data)

# 對齊後的資料會符合 metadata 定義的結構
```

## 注意事項

- 會自動處理欄位順序、類型轉換、缺失欄位等
- 詳細的對齊規則請參考 YAML 配置文件中的 Schema 章節