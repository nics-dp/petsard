---
title: "Metadater API"
weight: 320
---

資料結構描述管理器，提供資料集的詮釋資料定義與管理功能。

## 類別架構

{{< mermaid-file file="content/docs/experimental-new-format/python-api/metadater-api/metadater-class-diagram.mmd" >}}

> **圖例說明：**
> - 藍色框：主要操作類別
> - 橘色框：操作子類別
> - 淺藍框：資料設定類別
> - `..>`：建立/操作關係
> - `*--`：組合關係
> - `-->`：呼叫關係

## 基本使用

Metadater 主要作為內部元件使用，通常透過 Loader 的 schema 參數間接使用：

```python
# 在 YAML 中定義
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

若需直接使用：

```python
from petsard.metadater import Metadater
import pandas as pd

# 從資料自動推斷結構
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# 比較資料差異
diff = Metadater.diff(metadata, new_data)

# 對齊資料結構
aligned = Metadater.align(metadata, new_data)
```

## 資料結構

### Metadata
最上層，管理整個資料集：
- `id`: 資料集識別碼
- `schemas`: 表格結構字典

### Schema  
中間層，描述單一表格：
- `id`: 表格識別碼
- `attributes`: 欄位屬性字典（內部名稱）

### Attribute
最底層，定義單一欄位：
- `name`: 欄位名稱
- `type`: 資料型別
- `nullable`: 是否允許空值
- `logical_type`: 邏輯型別

## 相關配置

詳細的 Schema 配置選項請參考 YAML 配置文件中的 Schema 章節。