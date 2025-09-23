---
title: "Loader YAML"
weight: 110
---

Loader 模組的 YAML 設定檔案格式。

## 主要參數

- **filepath** (`string`, 條件必要¹)
  - 資料檔案路徑
  - 支援本地檔案或 benchmark 資料集

- **method** (`string`, 條件必要¹)
  - 載入方法，目前僅支援 `'default'`
  - 載入預設資料集 (adult-income)

- **schema** (`string | dict`, 選用)
  - 資料結構定義
  - 可為外部檔案路徑或內嵌定義

¹ 注意：`filepath` 和 `method` 二選一，不可同時使用

## 支援的檔案格式

| 格式 | 副檔名 | 說明 | 特殊參數 |
|------|--------|------|----------|
| **CSV** | `.csv`, `.tsv` | 逗號/製表符分隔檔案 | `sep`, `encoding`, `header_names` |
| **Excel** | `.xlsx`, `.xls` | Excel 試算表 | `sheet_name`, `header` |
| **Parquet** | `.parquet` | 列式儲存格式 | `engine`, `columns` |
| **Benchmark** | `benchmark://` | 內建基準資料集 | `cache_dir`, `force_download` |
| **Default** | - | 使用 `method='default'` | - |

## 參數詳細說明

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `filepath` | `string` | 資料檔案路徑² | `data/users.csv` |
| `method` | `string` | 載入方法³ | `default` |

² 支援格式：
- 本地檔案：`data/file.csv`、`../input/data.xlsx`
- Benchmark：`benchmark://adult-income`、`benchmark://german-credit`

³ 目前僅支援 `'default'`，載入 adult-income 資料集

### 選用參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `schema` | `string\|dict` | 資料結構定義 | `schemas/user.yaml` |
| `header_names` | `list` | 無標題列的欄位名稱 | `[id, name, age]` |

### CSV 特定參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `sep` | `string` | `,` | 分隔符號 |
| `encoding` | `string` | `utf-8` | 檔案編碼 |
| `skiprows` | `int` | `0` | 跳過的列數 |
| `nrows` | `int` | `None` | 讀取列數 |
| `usecols` | `list` | `None` | 使用的欄位 |
| `parse_dates` | `list` | `False` | 解析為日期的欄位 |

### 已棄用參數

| 參數 | 替代方案 | 移除版本 |
|------|----------|----------|
| `column_types` | 使用 `schema` | v2.0.0 |
| `na_values` | 使用 `schema` | v2.0.0 |

## 可用的 Benchmark 資料集

目前 PETsARD 提供 **Adult Income Dataset** 作為基準資料集：

| 資料集名稱 | 筆數 | 欄位數 | 任務類型 | 特性 |
|------------|------|--------|----------|------|
| `adult-income` | 48,842 | 15 | 分類 | 混合數值與類別型特徵，包含敏感資訊（收入） |

來源：美國人口普查局 (U.S. Census Bureau)

## 使用範例

### 基本載入

```yaml
Loader:
  load_csv:
    filepath: data/users.csv
```

### 使用 Benchmark 資料集

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
```

### 使用外部 Schema

```yaml
Loader:
  load_with_schema:
    filepath: data/customers.csv
    schema: schemas/customer_schema.yaml
```

### CSV 進階設定

```yaml
Loader:
  load_csv_advanced:
    filepath: data/sales.csv
    sep: ";"                    # 分號分隔
    encoding: "latin-1"         # 不同編碼
    skiprows: 2                 # 跳過前兩列
    nrows: 10000               # 只讀取 10,000 筆
    usecols: [id, product, price]  # 選擇特定欄位
    parse_dates: [order_date, ship_date]  # 解析日期
```

### 無標題列 CSV

```yaml
Loader:
  load_no_header:
    filepath: data/no_header.csv
    header_names: [id, name, age, salary, department]
```

### 內嵌 Schema 定義

```yaml
Loader:
  load_with_inline_schema:
    filepath: data/employees.csv
    schema:
      schema_id: employee_data
      optimize_dtypes: true
      fields:
        id:
          type: int
          nullable: false
        salary:
          type: float
          precision: 2
        department:
          type: str
          category: true
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
    
  # 載入基準資料集
  load_benchmark:
    filepath: benchmark://adult-income
```

### 完整範例

```yaml
Loader:
  customer_data_loader:
    filepath: data/customers.csv
    header_names: [id, name, age, income, registration_date, city, vip_status]
    sep: ","
    encoding: "utf-8"
    parse_dates: [registration_date]
    schema:
      schema_id: customer_data
      name: 客戶資料
      compute_stats: true
      optimize_dtypes: true
      fields:
        id:
          type: int
          nullable: false
          unique: true
        name:
          type: str
          nullable: false
        age:
          type: int
          min: 0
          max: 120
        income:
          type: float
          precision: 2
          min: 0
        registration_date:
          type: datetime
          format: "%Y-%m-%d"
        city:
          type: str
          category: true
        vip_status:
          type: bool
          nullable: false
```

## 效能優化建議

### 大型檔案處理

```yaml
Loader:
  load_large_file:
    filepath: data/large_dataset.csv
    nrows: 100000              # 限制讀取筆數
    usecols: [id, feature1, feature2, target]  # 只讀取需要的欄位
    schema:
      optimize_dtypes: true     # 優化資料類型以節省記憶體
```

### Benchmark 快取設定

```yaml
Loader:
  cached_benchmark:
    filepath: benchmark://adult-income
    cache_dir: ~/.petsard/data  # 指定快取目錄
    force_download: false        # 使用快取（如果存在）
```

## 執行說明

- 實驗名稱（第二層）可自由命名，建議使用描述性名稱
- 可定義多個實驗，系統會依序執行
- 每個實驗的結果會傳遞給下一個模組使用
- 大型檔案建議使用 `nrows` 或 `usecols` 參數以節省記憶體
- Benchmark 資料集首次使用時會自動下載並快取

## 注意事項

- `filepath` 和 `method` 參數互斥，不可同時使用
- 檔案路徑支援相對路徑和絕對路徑
- Schema 配置優先順序：參數指定 > YAML 檔案 > 自動推論
- CSV 檔案若無標題列，必須提供 `header_names` 參數
- 使用 `parse_dates` 參數可自動解析日期時間欄位