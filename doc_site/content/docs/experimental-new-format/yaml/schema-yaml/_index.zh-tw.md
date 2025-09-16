---
title: "Schema YAML"
weight: 220
---

資料結構定義的 YAML 設定格式。

## 概述

Schema 定義資料的結構與型別，由 Metadater 模組處理。採用三層架構對應實際資料：

| 設定層級 | 對應資料 | 說明 |
|---------|---------|------|
| **Metadata** | Datasets | 管理多個表格的資料集 |
| **Schema** | Table | 定義單一表格結構 |
| **Attribute** | Field | 描述單一欄位屬性 |

## 使用方式

Schema 在 Loader 中使用，有兩種定義方式：

### 1. 外部檔案引用

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml  # 引用外部檔案
```

### 2. 內嵌定義

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema:                   # 內嵌 schema 定義
      id: user_data
      fields:                 # 欄位定義
        user_id:              # 欄位名稱
          type: int64
          nullable: false
        username:
          type: object
          nullable: true
```

## Schema 結構

```yaml
id: <schema_id>           # 必填：結構識別碼
fields:                   # 必填：欄位屬性定義
  <field_name>:           # 欄位名稱作為 key
    type: <data_type>     # 必填：資料型別
    nullable: <boolean>   # 選填：是否允許空值（預設 true）
    logical_type: <type>  # 選填：邏輯型別提示
    stats: <dict>         # 選填：統計資料（自動產生）
stats: <dict>             # 選填：表格統計資料（自動產生）
```

## 支援的資料型別

### 基本型別
- `int64`：64 位元整數
- `float64`：64 位元浮點數
- `object`：字串或物件
- `bool`：布林值
- `datetime64`：日期時間
- `category`：類別型

### 邏輯型別（logical_type）
用於提供額外的語義資訊：
- `email`：電子郵件地址
- `url`：網址
- `ip_address`：IP 位址
- `phone`：電話號碼
- `postal_code`：郵遞區號
- `category`：分類資料

## 基本範例

### 簡單結構（外部檔案）

```yaml
# schemas/simple_schema.yaml
id: simple_data
fields:
  user_id:
    type: int64
    nullable: false
  username:
    type: object
  age:
    type: int64
    nullable: true
```

### 完整結構（內嵌）

```yaml
Loader:
  load_transaction:
    filepath: data/transactions.csv
    schema:
      id: transaction_data
      fields:
        transaction_id:
          type: int64
          nullable: false
          
        customer_email:
          type: object
          logical_type: email
          
        amount:
          type: float64
          nullable: false
          
        transaction_date:
          type: datetime64
          
        product_category:
          type: category
          
        status:
          type: category
          nullable: true
```

## 自動推斷

如果不提供 schema，系統會自動從資料推斷結構：

```yaml
Loader:
  auto_infer:
    filepath: data/auto.csv
    # 不指定 schema，自動推斷
```

## 資料型別對應

| Pandas dtype | Schema type |
|-------------|-------------|
| int8, int16, int32, int64 | int64 |
| uint8, uint16, uint32, uint64 | int64 |
| float16, float32, float64 | float64 |
| object, string | object |
| bool | bool |
| datetime64 | datetime64 |
| category | category |

## 注意事項

1. **欄位順序**：Schema 中的欄位順序不影響資料載入
2. **缺失欄位**：資料中缺少的欄位會填入預設值（nullable=true）
3. **額外欄位**：資料中的額外欄位會被保留
4. **型別轉換**：系統會嘗試自動轉換相容的型別

## 進階用法

### 多表格結構

當處理多個表格時，可以在不同的 Loader 中重複使用相同的 schema：

```yaml
Loader:
  train_data:
    filepath: data/train.csv
    schema: schemas/common_schema.yaml
    
  test_data:
    filepath: data/test.csv
    schema: schemas/common_schema.yaml
    
  validation_data:
    filepath: data/validation.csv
    schema: schemas/common_schema.yaml
```

### 部分定義

可以只定義關鍵欄位，其餘由系統推斷：

```yaml
schema:
  id: partial_schema
  fields:
    # 只定義重要欄位
    primary_key:
      type: int64
      nullable: false
    # 其他欄位會自動推斷
```

## 統計資料（Stats）

當使用 `Metadater.from_data()` 建立 Schema 時，如果設定 `enable_stats=True`，系統會自動計算並儲存統計資料。

### 欄位統計（Attribute.stats）

每個欄位會包含以下統計資訊：

```yaml
fields:
  age:
    type: int64
    nullable: true
    stats:                    # 自動產生的統計資料
      count: 1000            # 非空值數量
      null_count: 50         # 空值數量
      unique_count: 65       # 唯一值數量
      min: 18                # 最小值（數值型）
      max: 95                # 最大值（數值型）
      mean: 35.5             # 平均值（數值型）
      median: 34.0           # 中位數（數值型）
      std: 12.3              # 標準差（數值型）
      q1: 26.0               # 第一四分位數
      q3: 44.0               # 第三四分位數
      most_common:           # 最常見的值（類別型）
        - ["adult", 450]
        - ["senior", 300]
```

### 表格統計（Schema.stats）

Schema 層級的統計資訊：

```yaml
id: user_table
stats:                       # 自動產生的表格統計
  row_count: 1000           # 總列數
  column_count: 12          # 總欄數
  memory_usage: 98304       # 記憶體使用量（bytes）
  null_columns:             # 含空值的欄位列表
    - age
    - address
  numeric_columns:          # 數值型欄位列表
    - age
    - salary
  categorical_columns:      # 類別型欄位列表
    - gender
    - department
```

### 程式化存取統計資料

```python
from petsard.metadater import Metadater

# 從資料建立並計算統計
metadata = Metadater.from_data(
    data=df,
    enable_stats=True  # 啟用統計計算
)

# 存取統計資料
schema = metadata.schemas["table_name"]
print(f"總列數：{schema.stats.row_count}")

# 欄位統計
age_attr = schema.fields["age"]
print(f"平均年齡：{age_attr.stats.mean}")
print(f"空值數量：{age_attr.stats.null_count}")
```

### 注意事項

1. **效能考量**：計算統計資料會增加處理時間，特別是大型資料集
2. **隱私保護**：統計資料可能包含敏感資訊（如最小值、最大值），使用時需注意
3. **更新時機**：統計資料在建立時計算，不會自動更新
4. **儲存格式**：統計資料會儲存在 YAML 中，可用於稽核和分析

## 相關文檔

- [Metadater API](/docs/experimental-new-format/python-api/metadater-api)：程式化操作 Schema
- [Loader API](/docs/experimental-new-format/python-api/loader-api)：資料載入器配置