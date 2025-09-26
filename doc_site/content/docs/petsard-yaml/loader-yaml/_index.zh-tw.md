---
title: "Loader YAML"
weight: 110
---

Loader 模組的 YAML 設定檔案格式。

## 主要參數

- **filepath** (`string`, 必要)
  - 資料檔案路徑
  - 支援本地檔案路徑

- **schema** (`string | dict`, 選用)
  - 資料結構定義
  - 可為外部 YAML 檔案路徑（string）或內嵌的完整 Schema YAML（dict）

- **header_names** (`list`, 選用)
  - 無標題列的欄位名稱

## 支援的檔案格式

| 格式 | 副檔名 | 說明 | 額外需求 |
|------|--------|------|----------|
| **CSV** | `.csv`, `.tsv` | 逗號/製表符分隔檔案 | - |
| **Excel** | `.xlsx`, `.xls` | Excel 試算表 | 需安裝 `openpyxl` |
| **OpenDocument** | `.ods`, `.odf`, `.odt` | OpenDocument 格式 | 需安裝 `openpyxl` |

\* 使用 Excel 和 OpenDocument 格式需要安裝 `openpyxl` 套件，請參閱安裝說明。

## 參數詳細說明

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `filepath` | `string` | 資料檔案路徑 | `data/users.csv` |

### 選用參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `schema` | `string\|dict` | 資料結構定義 | `schemas/user.yaml` 或內嵌 dict |
| `header_names` | `list` | 無標題列的欄位名稱 | 見下方範例 |

### 已棄用參數

| 參數 | 替代方案 | 移除版本 |
|------|----------|----------|
| `column_types` | 使用 `schema` | v2.0.0 |
| `na_values` | 使用 `schema` | v2.0.0 |

## 使用範例

### 基本載入

```yaml
Loader:
  load_csv:
    filepath: data/users.csv
```

### 使用外部 Schema

```yaml
Loader:
  load_with_schema:
    filepath: data/customers.csv
    schema: schemas/customer_schema.yaml
```

### 無標題列 CSV

```yaml
Loader:
  load_no_header:
    filepath: data/no_header.csv
    header_names:
      - id
      - name
      - age
      - salary
      - department
```

### 內嵌 Schema 定義

```yaml
Loader:
  load_with_inline_schema:
    filepath: data/employees.csv
    schema:
      # 完整的 Schema YAML 結構
      # 詳細設定請參閱 Schema YAML 文檔
      id: employee_schema
      name: Employee Data Schema
      # ... 其他 Schema 設定
```

### 多個載入實驗

```yaml
Loader:
  # 載入訓練資料
  load_train:
    filepath: data/train.csv
    schema: schemas/data_schema.yaml
    
  # 載入測試資料
  load_test:
    filepath: data/test.csv
    schema: schemas/data_schema.yaml
    
  # 載入驗證資料
  load_validation:
    filepath: data/validation.csv
    schema: schemas/data_schema.yaml
```

### 使用 Schema 的完整範例

```yaml
Loader:
  customer_data_loader:
    filepath: data/customers.csv
    header_names:
      - id
      - name
      - age
      - income
      - registration_date
      - city
      - vip_status
    # 使用外部 Schema 檔案
    schema: schemas/customer_schema.yaml
    
  # 或使用內嵌 Schema
  employee_data_loader:
    filepath: data/employees.csv
    schema:
      # 這裡放置完整的 Schema YAML 結構
      # 具體 Schema 設定方式請參閱 Schema YAML 文檔
```

## Schema 配置說明

Schema 參數接受兩種格式：

1. **字串（string）**：外部 Schema YAML 檔案的路徑
   - 範例：`schema: schemas/data_schema.yaml`

2. **字典（dict）**：內嵌的完整 Schema YAML 結構
   - 直接在 Loader 配置中定義完整的 Schema

Schema 的具體設定方式、可用參數和屬性定義等詳細資訊，請參閱 Schema YAML 文檔。

## 執行說明

- 實驗名稱（第二層）可自由命名，建議使用描述性名稱
- 可定義多個實驗，系統會依序執行
- 每個實驗的結果會傳遞給下一個模組使用

## 注意事項

- 檔案路徑支援相對路徑和絕對路徑
- Schema 配置優先順序：參數指定 > 自動推論
- CSV 檔案若無標題列，必須提供 `header_names` 參數
- `column_types` 和 `na_values` 參數已棄用，請改用 `schema`
- Excel 和 OpenDocument 格式需要安裝 `openpyxl` 套件
- Schema 的詳細設定請參閱 Schema YAML 文檔