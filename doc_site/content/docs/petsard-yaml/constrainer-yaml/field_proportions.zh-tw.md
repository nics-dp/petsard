---
title: "欄位比例"
weight: 4
---

在約束過濾過程中維護原始資料的分布比例。

## 功能說明

理想情況下，合成器應該自動保持各欄位的比例分布。然而，根據不同的合成原理（如 CTGAN、TVAE 等），合成資料可能無法完全保持原始分布比例。此功能提供了一個**有效的後處理機制**，透過約束過濾來**保證一定程度的比例維持**，確保合成資料在經過各種約束條件篩選後，仍能維持與原始資料相近的分布特性。

**使用場景**：
- 合成資料的某些欄位分布偏離原始資料
- 需要確保特定欄位的缺失值比例與原始一致
- 多個約束條件可能導致某些類別過度被篩除

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_proportions.ipynb)

```yaml
field_proportions:
  - fields: 'education'      # 目標欄位：education
    mode: 'all'              # 模式：維護所有值（包括 NA）的分布比例
    tolerance: 0.1           # 容忍度：允許 10% 偏差

  - fields: 'workclass'      # 目標欄位：workclass
    mode: 'missing'          # 模式：僅維護缺失值（NA）的比例
    tolerance: 0.03          # 容忍度：允許 3% 偏差
```

## 語法格式

### 單一欄位

```yaml
- fields: 'field_name'
  mode: 'all' | 'missing'
  tolerance: 0.1  # 可選，預設 0.1
```

---

### 多欄位組合

```yaml
-
  fields:
    - field_name1
    - field_name2
  mode: 'all'
  tolerance: 0.15
```

## 參數說明

### mode

- **`'all'`**：維護所有值（包括 NA）的分布比例
- **`'missing'`**：僅維護缺失值（NA）的比例

### tolerance

- 允許與原始比例的偏差範圍（0.0-1.0）
- 預設值：`0.1`（10%）
- 例：原始 30%，tolerance 0.1 → 允許 27%-33%

## 注意事項

- 透過迭代移除過量資料來維護分布
- 高基數欄位（值太多）維護效果有限
- 多個規則可能產生衝突，建議使用較寬鬆的 tolerance
- 空值（NA）在 'all' 模式下也會被維護
