---
title: "diff"
weight: 363
---

比較詮釋資料定義與實際資料的差異。

## 語法

```python
Metadater.diff(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict
```

## 參數

- **metadata** (`Metadata`)
  - 詮釋資料定義
  
- **data** (`dict[str, pd.DataFrame]`)
  - 實際資料

## 返回值

- **dict**
  - 差異報告

## 範例

```python
from petsard.metadater import Metadater

# 比較差異
diff_report = Metadater.diff(metadata, new_data)

# 檢查是否有差異
if diff_report:
    print("發現資料結構差異")
```

## 注意事項

- 會檢查欄位名稱、類型、缺失值等差異
- 詳細的差異報告格式請參考 YAML 配置文件中的 Schema 章節