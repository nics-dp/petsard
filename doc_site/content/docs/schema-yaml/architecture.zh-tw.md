---
title: "Schema 架構說明"
weight: 201
---

Schema 定義資料的結構與型別，由 Metadater 模組處理。採用三層架構對應實際資料。

## 三層架構

| 設定層級 | 對應資料 | 說明 |
|---------|---------|------|
| **Metadata** | Datasets | 管理多個表格的資料集 |
| **Schema** | Table | 定義單一表格結構 |
| **Attribute** | Field | 描述單一欄位屬性 |

## Metadata 層級

Metadata 是最上層的結構，用於管理包含多個表格的資料集。

### 結構定義

```python
class Metadata:
    id: str                      # 資料集識別碼
    name: str                    # 資料集名稱（選填）
    description: str             # 資料集描述（選填）
    schemas: dict[str, Schema]   # 表格結構字典 {table_name: Schema}
```

### 使用情境

- **單表格場景**：大多數情況下，一個資料集只包含一個表格
- **多表格場景**：當資料集包含多個相關表格時（如關聯式資料庫）
- **資料集管理**：提供資料集層級的識別和描述資訊

### 範例

```yaml
# 單表格資料集
id: user_dataset
name: 使用者資料集
schemas:
  users:              # 單一表格
    id: users
    fields: {...}
```

```yaml
# 多表格資料集
id: ecommerce_dataset
name: 電商資料集
schemas:
  users:              # 第一個表格
    id: users
    fields: {...}
  orders:             # 第二個表格
    id: orders
    fields: {...}
  products:           # 第三個表格
    id: products
    fields: {...}
```

## Schema 層級

Schema 是中間層，定義單一表格的結構。

### 結構定義

```python
class Schema:
    id: str                          # 表格識別碼
    name: str                        # 表格名稱（選填）
    description: str                 # 表格描述（選填）
    attributes: dict[str, Attribute] # 欄位屬性字典 {field_name: Attribute}
    stats: dict                      # 表格統計資料（選填，自動產生）
```

### 使用情境

- **表格定義**：描述單一表格的完整結構
- **欄位管理**：包含該表格所有欄位的定義
- **結構驗證**：確保資料符合預期的表格結構

### 在 YAML 中的表示

```yaml
# 完整的 Schema 定義
id: users                  # 表格識別碼
name: 使用者表             # 表格顯示名稱
description: 系統使用者資料 # 表格說明

fields:                    # 欄位定義（Attributes）
  user_id:
    type: int64
    nullable: false
  
  username:
    type: object
    nullable: false
  
  email:
    type: object
    nullable: true
    logical_type: email

stats:                     # 表格統計（自動產生）
  row_count: 1000
  column_count: 3
```

## Attribute 層級

Attribute 是最底層，描述單一欄位的屬性。

### 結構定義

```python
class Attribute:
    name: str           # 欄位名稱
    type: str           # 資料型別
    nullable: bool      # 是否允許空值
    logical_type: str   # 邏輯型別（選填）
    description: str    # 欄位描述（選填）
    na_values: list     # 自訂空值表示（選填）
    stats: dict         # 欄位統計資料（選填，自動產生）
```

### 使用情境

- **欄位定義**：描述單一欄位的所有屬性
- **型別約束**：定義欄位的資料型別和空值處理
- **語意標記**：透過 logical_type 提供額外的語意資訊

### 在 YAML 中的表示

```yaml
# 單一欄位的完整定義
user_id:                    # 欄位名稱（key）
  type: int64               # 資料型別
  nullable: false           # 不允許空值
  description: 使用者唯一識別碼

email:
  type: object              # 字串型別
  nullable: true            # 允許空值
  logical_type: email       # 標記為電子郵件
  description: 電子郵件地址

age:
  type: int64
  nullable: true
  description: 年齡
  stats:                    # 欄位統計（自動產生）
    count: 950              # 非空值數量
    null_count: 50          # 空值數量
    min: 18                 # 最小值
    max: 95                 # 最大值
    mean: 35.5              # 平均值
```

## 架構層級關係

```
Metadata (資料集)
├── Schema (表格 1)
│   ├── Attribute (欄位 1)
│   ├── Attribute (欄位 2)
│   └── Attribute (欄位 3)
├── Schema (表格 2)
│   ├── Attribute (欄位 1)
│   └── Attribute (欄位 2)
└── Schema (表格 3)
    └── Attribute (...)
```

## 實際資料對應

### 對應關係

| Schema 層級 | 實際資料 | Python 型別 | 範例 |
|------------|---------|------------|------|
| Metadata | Dataset | dict[str, DataFrame] | `{'users': df1, 'orders': df2}` |
| Schema | Table | pd.DataFrame | `pd.DataFrame(...)` |
| Attribute | Field | pd.Series | `df['user_id']` |


## Metadater 模組的角色

Metadater 模組負責處理這三層架構，提供以下功能：

- **建立 Metadata**：從資料自動推斷或從配置檔建立結構定義
- **結構驗證**：比較實際資料與預期結構的差異
- **資料對齊**：根據 metadata 調整資料結構

## 使用建議

- **單表格場景**：大多數情況下只需定義一個表格的欄位結構
- **多表格場景**：當資料集包含多個相關表格時，在 `schemas` 下定義各表格
- **最小定義**：只定義關鍵欄位（如主鍵），其餘欄位由系統自動推斷