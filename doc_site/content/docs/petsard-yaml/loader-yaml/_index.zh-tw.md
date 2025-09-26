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
  - 可為外部檔案路徑或內嵌定義

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
| `schema` | `string\|dict` | 資料結構定義 | `schemas/user.yaml` |
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
      id: employee_schema
      name: Employee Data Schema
      attributes:
        id:
          type: int64
          enable_null: false
        name:
          type: string
        salary:
          type: float64
          precision: 2
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

### 完整範例

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
    schema:
      id: customer_schema
      name: Customer Data Schema
      description: Schema for customer data
      attributes:
        id:
          type: int64
          enable_null: false
        name:
          type: string
          enable_null: false
        age:
          type: int64
          min: 0
          max: 120
        income:
          type: float64
          precision: 2
          min: 0
        registration_date:
          type: datetime64
        city:
          type: category
          logical_type: category
        vip_status:
          type: boolean
          enable_null: false
```

## Schema 配置

Schema 定義了資料的結構與類型，可透過三種方式提供：

1. **外部 YAML 檔案**：提供檔案路徑
2. **內嵌定義**：直接在 YAML 中定義
3. **自動推論**：不提供時由系統自動推論

詳細 Schema 配置請參閱 Metadater YAML 文檔。

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