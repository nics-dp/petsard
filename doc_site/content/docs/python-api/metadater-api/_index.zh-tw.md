---
title: "Metadater API（更新中）"
weight: 320
---

資料結構描述管理器，提供資料集的詮釋資料（Metadata）定義、比較與對齊功能。

## 類別架構

{{< mermaid-file file="content/docs/python-api/metadater-api/metadater-class-diagram.zh-tw.mmd" >}}

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

若需直接使用 Metadater 類別方法：

```python
from petsard.metadater import Metadater
import pandas as pd

# 從資料自動推斷結構
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# 從字典建立詮釋資料
config = {'tables': {...}}
metadata = Metadater.from_dict(config)

# 比較資料差異
diff = Metadater.diff(metadata, new_data)

# 對齊資料結構
aligned = Metadater.align(metadata, new_data)
```

## 類別方法說明

Metadater 提供靜態類別方法（`@classmethod` 或 `@staticmethod`），不需要實例化即可使用：

### 建立詮釋資料

- `from_data()`：從資料自動推斷並建立 Metadata
- `from_dict()`：從配置字典建立 Metadata

### 比較與對齊

- `diff()`：比較 Metadata 與實際資料的差異
- `align()`：根據 Metadata 對齊資料結構

## 資料結構

### Metadata
最上層，管理整個資料集：
- `id`: 資料集識別碼
- `name`: 資料集名稱（選填）
- `description`: 資料集描述（選填）
- `schemas`: 表格結構字典 `{table_name: Schema}`

### Schema
中間層，描述單一表格：
- `id`: 表格識別碼
- `name`: 表格名稱（選填）
- `description`: 表格描述（選填）
- `attributes`: 欄位屬性字典 `{field_name: Attribute}`

### Attribute
最底層，定義單一欄位：
- `name`: 欄位名稱
- `type`: 資料型別（`int`, `float`, `str`, `bool`, `datetime` 等）
- `nullable`: 是否允許空值（`True`/`False`）
- `logical_type`: 邏輯型別（選填，如 `email`, `phone`, `url` 等）
- `na_values`: 自訂空值表示（選填）
- `is_constant`: 標記所有值都相同的欄位（自動偵測，請勿手動設定）

## 使用情境

### 1. 資料載入時的 Schema 管理

Loader 內部使用 Metadater 處理 schema：

```python
# Loader 內部流程（簡化）
schema = Metadater.from_dict(schema_config)  # 從 YAML 載入
data = pd.read_csv(filepath)                  # 讀取資料
aligned_data = Metadater.align(schema, data)  # 對齊資料結構
```

### 2. 資料結構驗證

比較期望結構與實際資料：

```python
# 定義期望的 schema
expected_schema = Metadater.from_dict(config)

# 比較實際資料
diff = Metadater.diff(expected_schema, {'users': actual_data})

if diff:
    print("發現結構差異：", diff)
```

### 3. 多資料集結構統一

確保多個資料集具有相同結構：

```python
# 定義標準結構
standard_schema = Metadater.from_data({'users': reference_data})

# 對齊其他資料集
aligned_data1 = Metadater.align(standard_schema, {'users': data1})
aligned_data2 = Metadater.align(standard_schema, {'users': data2})
```

## 注意事項

- **內部使用為主**：Metadater 主要供 PETsARD 內部模組使用，一般使用者透過 Loader 的 `schema` 參數即可
- **類別方法設計**：所有方法都是類別方法，不需要實例化 Metadater
- **自動推斷**：`from_data()` 會自動推斷欄位類型和是否可為空值
- **對齊行為**：`align()` 會根據 schema 調整欄位順序、補充缺失欄位、轉換資料類型
- **差異檢測**：`diff()` 檢測欄位名稱、類型、空值處理等差異
- **YAML 配置**：詳細的 Schema YAML 配置請參閱 [Schema YAML 文檔](../../schema-yaml/)
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容