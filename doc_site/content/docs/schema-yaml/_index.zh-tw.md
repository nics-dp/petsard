---
title: "Schema YAML"
weight: 200
---

資料結構定義的 YAML 設定格式（Schema YAML）。

## 使用範例

### 外部檔案引用

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml  # 引用外部檔案
```

### 內嵌定義

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema:                   # 內嵌 schema 定義
      id: user_data
      attributes:             # 欄位定義（也可寫為 fields）
        user_id:
          type: int64
          enable_null: false
        username:
          type: string
          enable_null: true
```

### 自動推斷

如果不提供 schema，系統會自動從資料推斷結構：

```yaml
Loader:
  auto_infer:
    filepath: data/auto.csv
    # 不指定 schema，自動推斷
```

## 主要結構

```yaml
id: <schema_id>           # 必填：結構識別碼
attributes:               # 必填：欄位屬性定義（也可寫為 fields）
  <attribute_name>:       # 欄位名稱作為 key
    type: <data_type>     # 必填：資料型別
    enable_null: <bool>   # 選填：是否允許空值（預設 true）
    logical_type: <type>  # 選填：邏輯型別提示
```

{{< callout type="info" >}}
`attributes` 也可以寫作 `fields`。
{{< /callout >}}

## Attribute 參數列表

### 必填參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `name` | `string` | 欄位名稱（作為 key 時會自動設定） | `"user_id"`, `"age"` |

### 選填參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `type` | `string` | `null` | 資料型別，未指定時自動推斷 | `"int64"`, `"string"`, `"float64"` |
| `enable_null` | `boolean` | `true` | 是否允許空值 | `true`, `false` |
| `category` | `boolean` | `null` | 是否為分類資料 | `true`, `false` |
| `logical_type` | `string` | `null` | 邏輯型別標註，用於驗證 | `"email"`, `"url"`, `"phone"` |
| `description` | `string` | `null` | 欄位說明文字 | `"使用者唯一識別碼"` |
| `type_attr` | `dict` | `null` | 型別額外屬性（如精度、格式等） | `{"precision": 2}`, `{"format": "%Y-%m-%d"}` |
| `na_values` | `list` | `null` | 自訂缺失值標記 | `["?", "N/A", "unknown"]` |
| `default_value` | `any` | `null` | 預設填充值 | `0`, `"Unknown"`, `false` |
| `constraints` | `dict` | `null` | 欄位約束條件 | `{"min": 0, "max": 100}` |
| `enable_optimize_type` | `boolean` | `true` | 是否啟用型別優化 | `true`, `false` |
| `enable_stats` | `boolean` | `true` | 是否計算統計資訊 | `true`, `false` |
| `cast_errors` | `string` | `"coerce"` | 型別轉換錯誤處理 | `"raise"`, `"coerce"`, `"ignore"` |
| `null_strategy` | `string` | `"keep"` | 空值處理策略 | `"keep"`, `"drop"`, `"fill"` |

### 系統自動生成參數

| 參數 | 類型 | 說明 |
|------|------|------|
| `stats` | `FieldStats` | 欄位統計資訊（使用 `enable_stats=True` 時自動計算） |
| `created_at` | `datetime` | 建立時間（系統自動記錄） |
| `updated_at` | `datetime` | 更新時間（系統自動記錄） |

{{< callout type="info" >}}
**自動推斷機制**：
- 使用 `Metadater.from_data()` 時，`type`、`logical_type`、`enable_null` 等參數會自動從資料推斷
- 手動建立 Schema 時，只有 `name` 是必填的，其他參數都是選填
- 建議明確指定 `type` 以確保資料處理的準確性
{{< /callout >}}

## 進階用法

### 多表格重用

```yaml
Loader:
  train_data:
    filepath: data/train.csv
    schema: schemas/common_schema.yaml
    
  test_data:
    filepath: data/test.csv
    schema: schemas/common_schema.yaml
```

### 部分定義

只定義關鍵欄位，其餘由系統推斷：

```yaml
schema:
  id: partial_schema
  attributes:
    primary_key:
      type: int64
      enable_null: false
    # 其他欄位會自動推斷
```

## 統計資料

使用 `Metadater.from_data()` 時，若設定 `enable_stats=True`，系統會自動計算統計資料。

### 欄位統計範例

```yaml
attributes:
  age:
    type: int64
    enable_null: true
    stats:
      row_count: 1000
      na_count: 50
      unique_count: 65
      mean: 35.5
      median: 34.0
```

### 程式化存取

```python
from petsard.metadater import Metadater
import pandas as pd

# 建立並計算統計
data = {'users': pd.DataFrame({...})}
metadata = Metadater.from_data(
    data=data,
    enable_stats=True
)

# 存取統計
schema = metadata.schemas["users"]
age_attr = schema.attributes["age"]
print(f"平均年齡：{age_attr.stats.mean}")
```

## 相關說明

- **資料型別**：詳見 [資料型別](/docs/schema-yaml/data-types) 說明
- **邏輯型別**：詳見 [邏輯型別](/docs/schema-yaml/logical-types) 說明
- **架構理論**：表詮釋資料 (Schema) 採用三層架構設計，詳見 [表詮釋資料架構](/docs/schema-yaml/architecture) 說明
- **資料對齊**：表詮釋資料可用於對齊和驗證資料，詳見 [Metadater API](/docs/python-api/metadater-api) 文檔
- **Loader 整合**：表詮釋資料在資料載入時的使用方式，詳見 [Loader YAML](/docs/petsard-yaml/loader-yaml) 文檔
- **Reporter 輸出**：可使用 Reporter 的 save_schema 方法輸出各模組的表詮釋資料，詳見 [Reporter - 儲存表詮釋資料](/docs/petsard-yaml/reporter-yaml/save-schema) 說明

## 注意事項

- 欄位順序不影響資料載入
- 資料中缺少的欄位會填入預設值（enable_null=true）
- 資料中的額外欄位會被保留
- 系統會嘗試自動轉換相容的型別
- `attributes` 也可以寫作 `fields`
- 邏輯型別僅用於驗證，不改變儲存格式
- 統計計算會增加處理時間，大型資料集需謹慎使用