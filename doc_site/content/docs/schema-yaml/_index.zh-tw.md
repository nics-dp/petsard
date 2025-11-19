---
title: "Schema YAML"
weight: 200
---

資料結構定義的 YAML 設定格式（Schema YAML）。

{{< callout type="info" >}}
**使用方式**：Schema YAML 在 PETsARD 中透過 Loader 使用。關於如何在 Loader 中引用和使用 Schema，請參閱 Loader YAML 文檔。本章節專注於說明如何設定 Schema 的結構和參數。
{{< /callout >}}

## 基本結構

一個完整的 Schema YAML 檔案包含以下部分：

```yaml
# Schema 識別資訊
id: <schema_id>              # 必填：Schema 識別碼
name: <schema_name>          # 選填：Schema 名稱
description: <description>   # 選填：Schema 描述

# 欄位定義
attributes:                  # 或使用 fields
  <field_name>:             # 欄位名稱
    type: <data_type>       # 資料型別
    description: <text>     # 欄位說明
    # ... 其他參數
```

## 範例：Adult Income Dataset

以下是 Adult Income（人口普查）資料集的 Schema 定義範例：

```yaml
# Schema 識別資訊
id: adult-income
name: "Adult Income Dataset"
description: "1994 Census database for income prediction (>50K or <=50K)"

# 欄位定義
attributes:
  age:
    type: integer
    description: "Age of the individual"

  workclass:
    type: string
    category: true
    description: "Employment type"
    na_values: "?"

  fnlwgt:
    type: integer
    description: "Final weight (number of people the census believes the entry represents)"

  education:
    type: string
    category: true
    description: "Highest level of education"
    na_values: "?"

  educational-num:
    type: integer
    description: "Number of education years"

  marital-status:
    type: string
    category: true
    description: "Marital status"

  occupation:
    type: string
    category: true
    description: "Occupation"
    na_values: "?"

  relationship:
    type: string
    category: true
    description: "Relationship to household"

  race:
    type: string
    category: true
    description: "Race"

  gender:
    type: string
    category: true
    description: "Biological sex"

  capital-gain:
  type: integer
  description: "Capital gains"

  capital-loss:
  type: integer
  description: "Capital losses"

  hours-per-week:
    type: integer
    description: "Hours worked per week"

  native-country:
    type: string
    category: true
    description: "Country of origin"

  income:
    type: string
    category: true
    description: "Income class (target variable)"
```

### 範例解說

這個 Schema 定義展示了幾個重要的配置概念：

#### 1. Schema 層級資訊

```yaml
id: adult-income
name: "Adult Income Dataset"
description: "1994 Census database for income prediction (>50K or <=50K)"
```

- **`id`**：必填，用於識別這個 Schema
- **`name`**：選填，提供易讀的名稱
- **`description`**：選填，說明這個資料集的用途

#### 2. 數值型欄位

```yaml
age:
  type: integer
  description: "Age of the individual"

hours-per-week:
  type: integer
  description: "Hours worked per week"
```

- 使用 `type: integer` 定義整數欄位
- `description` 說明欄位的業務意義

#### 3. 類別型欄位

```yaml
workclass:
  type: string
  category: true
  description: "Employment type"
  na_values: "?"

gender:
  type: string
  category: true
  description: "Biological sex"
```

- **`category: true`**：標記為類別資料，系統會據此選擇適當的處理方法
- **`na_values`**：定義自訂的缺失值標記（如 `"?"` 在此資料集中代表缺失值）

#### 4. 特殊情況：數值但視為類別

在某些情況下，數值型欄位可能更適合視為類別資料處理：

```yaml
# 範例：評分等級（雖是數值但選項有限）
rating:
  type: integer
  category: true
  description: "評分等級 (1-5)"

# 範例：郵遞區號（雖是數值但代表區域分類）
zip_code:
  type: integer
  category: true
  description: "郵遞區號"
```

設定 `category: true` 會影響：
- **Preprocessor**：選擇類別資料的處理方法（如 Label Encoding）
- **Synthesizer**：使用適合類別資料的合成策略
- **統計資訊**：計算類別分佈而非數值統計

{{< callout type="info" >}}
是否將數值欄位視為類別，需根據資料特性和業務需求判斷。一般來說，當數值欄位的唯一值數量有限且各值之間沒有明確的數學關係時，可考慮設為類別。
{{< /callout >}}

## 型別系統

PETsARD 使用簡化的型別系統：

| 型別 | 說明 | 範例 |
|------|------|------|
| `int` / `integer` | 整數 | `25`, `-10`, `1000` |
| `float` | 浮點數 | `3.14`, `-0.5`, `1000.00` |
| `str` / `string` | 字串 | `"text"`, `"A"`, `"123"` |
| `date` | 日期 | `2024-01-01` |
| `datetime` | 日期時間 | `2024-01-01 10:30:00` |

{{< callout type="info" >}}
**型別別名**：
- `integer` 和 `int` 可互換使用
- `string` 和 `str` 可互換使用
- 系統內部統一使用簡化型別（`int`, `float`, `str`, `date`, `datetime`）
{{< /callout >}}

## 進階主題

### 欄位屬性參數

常用參數包括：
- `type`：資料型別
- `type_attr`：型別屬性（nullable, category, precision 等）
- `description`：欄位說明
- `logical_type`：邏輯型別（email, phone 等）
- `na_values`：自訂缺失值標記
- `constraints`：欄位約束條件

### 統計資訊

設定 `enable_stats: true` 可啟用統計資訊計算。

## 注意事項

- **欄位名稱**：`attributes` 和 `fields` 都可以使用，系統會自動識別
- **自動推斷**：如果不提供 Schema，系統會自動從資料推斷結構
- **型別轉換**：系統會嘗試自動轉換相容的型別
- **缺失值處理**：可透過 `na_values` 定義自訂的缺失值標記
- **類別資料**：設定 `category: true` 會影響資料處理和合成策略