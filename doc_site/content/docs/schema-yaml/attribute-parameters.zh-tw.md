---
title: "欄位屬性參數"
type: docs
weight: 720
prev: docs/schema-yaml/architecture
next: docs/schema-yaml/data-types
---

欄位屬性（Attribute）的參數參考手冊。

## 參數列表

### 必填參數

| 參數 | 類型 | 說明 |
|------|------|------|
| `name` | `string` | 欄位名稱（作為 key 時自動設定） |

### 基本屬性

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `type` | `string` | `null` | 資料型別：`int`, `float`, `str`, `date`, `datetime` |
| `description` | `string` | `null` | 欄位說明文字 |
| `logical_type` | `string` | `null` | 邏輯型別標註（如 `email`, `phone`） |

### 型別屬性（type_attr）

`type_attr` 是一個字典，包含型別相關的設定：

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `type_attr.nullable` | `boolean` | `true` | 是否允許空值 |
| `type_attr.category` | `boolean` | `false` | 是否為類別資料 |
| `type_attr.precision` | `integer` | `null` | 數值精度（小數位數） |
| `type_attr.format` | `string` | `null` | 日期時間格式字串（如 `"%Y-%m-%d"`） |
| `type_attr.width` | `integer` | `null` | 字串寬度（用於前導零） |

{{< callout type="info" >}}
**簡化寫法**：`type_attr` 中的參數可直接寫在屬性層級。例如 `nullable: false` 等同於 `type_attr.nullable: false`。
{{< /callout >}}

### 資料處理

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `na_values` | `list/string` | `null` | 自訂缺失值標記（如 `"?"`, `["?", "N/A"]`） |
| `default_value` | `any` | `null` | 預設填充值 |
| `cast_errors` | `string` | `"coerce"` | 型別轉換錯誤處理：`"raise"`, `"coerce"`, `"ignore"` |
| `null_strategy` | `string` | `"keep"` | 空值處理策略：`"keep"`, `"drop"`, `"fill"` |

### 資料驗證

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `constraints` | `dict` | `null` | 欄位約束條件（`min`, `max`, `pattern`） |

### 效能與統計

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `enable_optimize_type` | `boolean` | `true` | 啟用型別優化（選擇最小資料型別） |
| `enable_stats` | `boolean` | `true` | 計算欄位統計資訊 |

## 系統自動生成

這些參數由系統自動設定，**請勿手動設定**：

| 參數 | 類型 | 說明 |
|------|------|------|
| `stats` | `FieldStats` | 欄位統計資訊（`enable_stats=True` 時） |
| `is_constant` | `boolean` | 標記所有值相同的欄位 |
| `created_at` | `datetime` | 建立時間 |
| `updated_at` | `datetime` | 更新時間 |

## 常用範例

### 整數欄位

```yaml
age:
  type: int
  nullable: false
  description: "年齡"
```

### 類別欄位

```yaml
gender:
  type: str
  category: true
  description: "性別"
```

### 浮點數（指定精度）

```yaml
price:
  type: float
  precision: 2
  description: "價格（兩位小數）"
```

### 日期欄位

```yaml
birth_date:
  type: date
  format: "%Y-%m-%d"
  description: "出生日期"
```

### 自訂缺失值

```yaml
workclass:
  type: str
  category: true
  na_values: "?"
  description: "就業類型"
```

## 重要提醒

- **型別簡化**：使用 `int`, `float`, `str`, `date`, `datetime`（自動轉換舊版型別名稱）
- **類別標記**：正確設定 `category: true` 影響資料處理和合成策略
- **自動推斷**：未指定的參數會從資料自動推斷
- **效能考量**：大型資料集可停用 `enable_stats` 以提升速度