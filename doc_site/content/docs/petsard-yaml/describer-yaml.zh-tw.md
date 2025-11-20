---
title: "Describer YAML"
type: docs
weight: 680
prev: docs/petsard-yaml/constraints-yaml
next: docs/petsard-yaml/evaluator-yaml
---

Describer 模組的 YAML 設定檔案格式。提供資料集的統計描述與比較功能。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/describer-yaml/describer.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

### 單一資料集描述 (describe 模式)

```yaml
---
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Describer:
  describer-describe:
    method: default    # 自動判斷為 describe（因為只有一個 source）
    source: Synthesizer
...
```

### 資料集比較 (compare 模式)

```yaml
---
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Describer:
  describer-compare:
    method: default         # 自動判斷為 compare（因為有兩個 source）
    source:
      base: Splitter.train  # 使用 Splitter 的 train 輸出作為基準
      target: Synthesizer   # 比較 Synthesizer 的輸出
...
```

### 自訂比較方法

```yaml
---
Loader:
  load_original:
    filepath: benchmark://adult-income_ori
    schema: benchmark://adult-income_schema
Synthesizer:
  generate_synthetic:
    method: custom_data
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Describer:
  custom_comparison:
    method: compare           # 明確指定 compare 方法
    source:
      base: Loader
      target: Synthesizer
    stats_method:             # 自訂統計方法
      - mean
      - std
      - nunique
      - jsdivergence
    compare_method: diff      # 使用差值而非百分比變化
    aggregated_method: mean
    summary_method: mean
...
```

## 主要參數

- **method** (`string`, 選用)
  - 評估方法
  - `default`：根據 source 數量自動決定（1個→describe，2個→compare）
  - `describe`：單一資料集統計描述
  - `compare`：資料集比較（整合 Stats 功能）
  - 預設值：`default`

- **source** (`string | dict`, 必要)
  - 指定資料來源
  - 單一來源：適用於 describe 方法
  - 兩個來源：適用於 compare 方法（必須使用字典格式）
  - 可用值：`Loader`, `Splitter`, `Preprocessor`, `Synthesizer`, `Postprocessor`, `Constrainer`

## 支援的方法

| 方法 | 說明 | 資料需求 | 輸出內容 |
|------|------|----------|----------|
| **default** | 自動判斷模式 | 根據 source 數量決定 | 根據判斷結果 |
| **describe** | 單一資料集統計描述 | 一個資料來源 | global、columnwise、pairwise |
| **compare** | 資料集比較分析 | 兩個資料來源 | global（含 Score）、columnwise |

## 參數詳細說明

### 通用參數

| 參數 | 類型 | 必要/選用 | 預設值 | 說明 | 範例 |
|------|------|-----------|--------|------|------|
| `method` | `string` | 選用 | `default` | 評估方法 | `describe`, `compare` |
| `source` | `string\|dict` | **必要** | 無 | 資料來源模組 | 見下方說明 |

### Source 參數格式

#### 1. 單一來源（describe 方法）
```yaml
source: Loader
```

#### 2. 字典格式（compare 方法 - 必須使用）
```yaml
source:
  base: Splitter.train    # 明確指定基準資料
  target: Synthesizer     # 明確指定比較目標
```

註：向後相容支援 `ori`/`syn` 鍵名，但建議使用 `base`/`target`。

### Compare 方法專用參數

| 參數 | 類型 | 預設值 | 說明 | 可選值 |
|------|------|--------|------|--------|
| `stats_method` | `list` | 全部方法 | 統計方法列表 | `mean`, `std`, `median`, `min`, `max`, `nunique`, `jsdivergence` |
| `compare_method` | `string` | `pct_change` | 比較方法 | `pct_change`, `diff` |
| `aggregated_method` | `string` | `mean` | 聚合方法 | `mean` |
| `summary_method` | `string` | `mean` | 總結方法 | `mean` |

### 統計方法說明

| 方法 | 適用資料類型 | 說明 | 執行粒度 |
|------|-------------|------|----------|
| `mean` | 數值型 | 平均值 | columnwise |
| `std` | 數值型 | 標準差 | columnwise |
| `median` | 數值型 | 中位數 | columnwise |
| `min` | 數值型 | 最小值 | columnwise |
| `max` | 數值型 | 最大值 | columnwise |
| `nunique` | 分類型 | 唯一值數量 | columnwise |
| `jsdivergence` | 分類型 | JS 散度 | percolumn |

### 比較方法說明

| 方法 | 計算公式 | 適用場景 |
|------|----------|----------|
| `pct_change` | `(target - base) / abs(base)` | 檢視相對變化幅度 |
| `diff` | `target - base` | 檢視絕對變化量 |

## 執行說明

- source 參數為必要參數，必須明確指定資料來源
- method 參數可省略，預設為 `default`（自動判斷）
- 統計方法會根據資料類型自動篩選適用的計算

## 注意事項

- **source 為必要參數**：必須明確指定要分析的資料來源
- **compare 模式必須使用字典格式**：需明確指定 `base` 和 `target` 鍵
- **向後相容性**：仍支援 `ori`/`syn` 參數名稱，但建議使用 `base`/`target`
- compare 方法整合了原 Stats 評估器功能
- 不適用的統計方法會返回 NaN
- 建議數值資料使用 `mean`, `std`, `median`, `min`, `max`
- 建議分類資料使用 `nunique`, `jsdivergence`

## 相關說明

- **資料來源**：可使用任何產生資料的模組作為來源，如 Loader、Splitter、Synthesizer 等
- **Module.key 格式**：當模組有多個輸出時，使用點號語法精確指定，如 `Splitter.train`
- **統計方法**：根據資料類型自動判斷適用的統計方法