---
title: "欄位組合"
type: docs
weight: 673
prev: docs/petsard-yaml/constrainer-yaml/field_constraints
next: docs/petsard-yaml/constrainer-yaml/field_proportions
---

定義不同欄位間的值配對關係，採用**正面表列**方式（只影響明確指定的值組合）。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_combinations.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

```yaml
field_combinations:
  -
    - education: income        # 定義欄位映射：education（來源）-> income（目標）
    -
        Doctorate:             # 當 education 為 Doctorate 時
          - '>50K'             # income 只能是 '>50K'
        Masters:               # 當 education 為 Masters 時
          - '>50K'             # income 可以是 '>50K'
          - '<=50K'            # 或 '<=50K'
```

**正面表列效果範例**：

假設規則：
```yaml
field_combinations:
  -
    - education: income
    - Doctorate:
        - '>50K'
```

| education | income | 結果 |
|-----------|--------|------|
| Doctorate | >50K | ✅ 保留（符合規則） |
| Doctorate | <=50K | ❌ 過濾（違反規則） |
| Masters | >50K | ➖ 不受影響（規則不適用） |
| Masters | <=50K | ➖ 不受影響（規則不適用） |
| Bachelor | >50K | ➖ 不受影響（規則不適用） |
| Bachelor | <=50K | ➖ 不受影響（規則不適用） |

**重要**：只影響明確指定的值組合（Doctorate），其他組合一律保留。

## 語法格式

欄位組合約束允許您定義不同欄位之間的值域關係，確保合成資料中的欄位組合符合真實世界的邏輯規範。

### 支援的組合類型

- **單一欄位映射**：基於單一欄位的值進行約束
- **多欄位映射**：同時考慮多個欄位的值進行更複雜的約束

### 正面表列機制說明

根據上述範例（`education` → `income`）：
- **受約束的值**：
  - `education = 'Doctorate'` 時，`income` 只能是 `'>50K'`
  - `education = 'Masters'` 時，`income` 可以是 `'>50K'` 或 `'<=50K'`
- **不受約束的值**：
  - `education = 'Bachelors'`、`'HS-grad'` 等其他值的 `income` 不受任何限制
  - 非 Doctorate 和 Masters 的資料一律保留，無論其 `income` 為何

{{< callout type="info" >}}
**實作限制**：在當前的實作中，欄位組合約束採用正面表列方式，僅支援明確列出的值組合。數值欄位可以進行有效值的枚舉，但尚未支援像欄位約束中使用比較運算子（`>`、`<`、`>=`、`<=`）進行數值的邏輯判斷。
{{< /callout >}}

### 單一欄位映射語法

```yaml
-
  - source_field_name: target_field_name
  -
      source_value1:
        - target_value1
        - target_value2
      source_value2:
        - target_value3
```

---

### 多欄位映射語法

```yaml
-
  -
    - source_field_name1
    - source_field_name2
  : target_field_name
  -
    - source_value1
    - source_value2
  :
    - target_value1
    - target_value2
```

## 注意事項

- 採用**正面表列**：只檢查明確列出的值組合
- 空值（NA）不受規則影響
- 字串值需精確匹配（大小寫敏感）
- 目標值必須用列表格式：`[value]` 或 `[value1, value2]`