---
title: "遺失值處理"
type: docs
weight: 641
prev: docs/petsard-yaml/preprocessor-yaml
next: docs/petsard-yaml/preprocessor-yaml/outlier-handling
---

處理資料中的遺失值（NA/NaN）。

## 背景

由於大部分的合成演算法都是基於機率模型，我們的研究發現，大多數演算法無法直接支援遺失值（`None`、`np.nan`、`pd.NA`）。即使某些演算法聲稱可以處理遺失值，也很難確認其各自的實作是否適當。

因此，**PETsARD 建議主動處理任何包含遺失值的欄位**：
- 數值欄位：預設使用平均值填補
- 類別/文字/日期欄位：預設使用直接刪除策略

## 使用範例

點擊下方按鈕在 Colab 中執行完整範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_missing-handling.ipynb)

### 範例 1：欄位特定遺失值方法

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  missing-field-specific:
    sequence:
      - missing
    config:
      missing:
        workclass: 'missing_drop'     # 刪除有遺失值的資料列
        education: 'missing_drop'     # 刪除有遺失值的資料列
        occupation: None              # 跳過此欄位的遺失值處理
        age: 'missing_mean'           # 使用平均值填補

        # 注意：
        # - 設定為 None 的欄位：不會進行遺失值處理，保留原始的遺失值
        # - 未列出的欄位：會使用預設方法處理
        #   * 數值欄位（如 fnlwgt、capital-gain）：使用 missing_mean
        #   * 類別欄位：使用 missing_drop

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

### 範例 2：使用自訂值填補

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  missing-custom-value:
    sequence:
      - missing
    config:
      missing:
        age:
          method: 'missing_simple'
          value: -1.0                 # 使用 -1.0 填補 age 的遺失值
        hours-per-week:
          method: 'missing_simple'
          value: 0.0                  # 使用 0.0 填補 hours-per-week 的遺失值

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

## 可用處理器

| 處理器 | 描述 | 適用資料類型 | 參數 |
|--------|------|-------------|------|
| `missing_mean` | 使用平均值填補 | 數值 | 無 |
| `missing_median` | 使用中位數填補 | 數值 | 無 |
| `missing_mode` | 使用眾數填補 | 類別、數值 | 無 |
| `missing_simple` | 使用指定值填補 | 數值 | `value`（預設：0.0） |
| `missing_drop` | 刪除有遺失值的資料列 | 所有類型 | 無 |

## 參數說明

### missing_simple

- **value** (`float`, 選填)
  - 用於填補遺失值的自訂值
  - 預設值：`0.0`
  - 範例：`value: -1.0`

## 處理邏輯

### 1. 統計值填補（平均值/中位數/眾數）

- **訓練階段（fit）**：計算並儲存統計值（平均值/中位數/眾數）
- **轉換階段（transform）**：使用儲存的統計值填補 NA
- **逆轉換階段（inverse_transform）**：根據原始資料的遺失比例隨機插入 NA

### 2. 自訂值填補（Simple）

- **訓練階段（fit）**：記錄填補值
- **轉換階段（transform）**：使用指定值填補 NA
- **逆轉換階段（inverse_transform）**：根據原始資料的遺失比例隨機插入 NA

### 3. 刪除（Drop）

- **訓練階段（fit）**：不需要訓練
- **轉換階段（transform）**：刪除包含 NA 的資料列
- **逆轉換階段（inverse_transform）**：根據原始資料的遺失比例隨機插入 NA

## 預設行為

不同資料類型的預設遺失值處理：

| 資料類型 | 預設處理器 | 描述 |
|---------|-----------|------|
| 數值 | `missing_mean` | 使用平均值填補 |
| 類別 | `missing_drop` | 刪除有遺失值的資料列 |
| 日期時間 | `missing_drop` | 刪除有遺失值的資料列 |

## Schema 變化

schema 中的 `nullable` 屬性反映了實際遺失值的存在狀況：

- **Loader 階段**
  - 自動從資料偵測：`nullable = data.isnull().any()`
  - 若欄位有遺失值 → `nullable: true`
  - 若欄位無遺失值 → `nullable: false`

- **Preprocessor 階段（有執行遺失值處理）**
  - 原本 `nullable: true` 的欄位 → 處理後 → `nullable: false`
  - 原本 `nullable: false` 的欄位 → 維持 `nullable: false`

**Schema 演進範例**：

```yaml
# Loader 輸出（資料有遺失值）
workclass:
  type: string
  nullable: true          # 原始資料有遺失值

age:
  type: int64
  nullable: false         # 原始資料無遺失值

# Preprocessor 輸出（經過 missing_drop 處理）
workclass:
  type: string
  nullable: false         # 遺失值已移除

age:
  type: int64
  nullable: false         # 不變（原本就沒有遺失值）
```

## 注意事項

- **處理順序**：遺失值處理通常是第一步
- **眾數填補**：如果有多個眾數，將隨機選擇一個
- **刪除影響**：使用 `missing_drop` 可能會大幅減少資料量
- **還原機制**：在後處理期間，會根據原始比例隨機插入 NA，但位置不會完全相同
- **統計值儲存**：訓練期間計算的統計值會用於所有後續的轉換
- **NA 識別**：自動識別 pandas NA 值（`np.nan`、`None`、`pd.NA`）
- **Schema 對齊**：各階段（Loader、Preprocessor、Synthesizer、Postprocessor、Constrainer）都會根據其輸出 schema 對齊資料
