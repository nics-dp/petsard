---
title: "欄位約束"
weight: 2
---

設定單一欄位的值域限制，使用字串表達式定義約束條件。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_constraints.ipynb)

```yaml
field_constraints:
  - "age >= 18 & age <= 65"  # 年齡範圍：18-65 歲
  - "hours-per-week >= 20 & hours-per-week <= 60"  # 工時範圍：每週 20-60 小時
  - "income == '>50K' | income == '<=50K'"  # 收入只能是 '>50K' 或 '<=50K'
```

## 語法格式

### 比較運算子

```yaml
- "field_name > value"   # 大於（數值）
- "field_name >= value"  # 大於等於（數值）
- "field_name == value"  # 等於（數值、文字）
- "field_name != value"  # 不等於（數值、文字）
- "field_name < value"   # 小於（數值）
- "field_name <= value"  # 小於等於（數值）
```

---

### 邏輯運算子

```yaml
- "field_name > value1 & field_name < value2"        # AND
- "field_name == 'value1' | field_name == 'value2'"  # OR
- "(condition1 & condition2) | condition3"           # 括號優先級
```

---

### 空值檢查

```yaml
- "field_name IS pd.NA"      # 欄位為空值
- "field_name IS NOT pd.NA"  # 欄位不為空值
```

---

### 日期比較

```yaml
- "date_field >= DATE('2020-01-01')"  # 日期大於等於 2020-01-01
```

---

### 運算子優先級

| 優先級 | 運算子 | 說明 |
|--------|--------|------|
| 1（最高）| `()` | 括號 |
| 2 | `>`, `>=`, `==`, `!=`, `<`, `<=`, `IS`, `IS NOT` | 比較運算子 |
| 3 | `&` | 邏輯 AND |
| 4（最低）| `\|` | 邏輯 OR |

**說明**：比較運算子優先於邏輯運算子（AND、OR）。這意味著 `age >= 20 & age <= 60` 會被正確解析為 `(age >= 20) & (age <= 60)`。

**建議**：使用括號明確指定優先級，避免歧義。

## 注意事項

- 每個約束必須用引號包圍成字串
- 字串值必須加單引號：`"field == 'value'"`
- 空值檢查使用 `IS` 或 `IS NOT`，不用 `==` 或 `!=`
- 不支援跨欄位運算（如 `field1 + field2 > 100`）
