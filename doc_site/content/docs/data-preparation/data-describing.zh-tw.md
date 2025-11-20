---
title: 資料描述統計
type: docs
weight: 310
prev: docs/data-preparation
next: docs/data-preparation/multi-table-relationships
---

適用於**所有資料準備流程的起點**。

使用 Describer 模組產生資料集的統計描述報告，協助您檢視資料的基本統計資訊、識別資料品質問題、了解資料分布特性，並評估資料是否適合進行合成。

> Describer 是資料準備的第一步，強烈建議在進行任何資料整合或約束定義前先執行。

## 使用 Describer 產生統計報告

### 基本用法

```yaml
Loader:
  data:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Describer:
  profile_data:
    method: describe  # 或使用 default（會自動判斷為 describe）
    source: Loader
```

### 參數說明

- **`method`**: 評估方法
  - `describe`：單一資料集統計描述
  - `compare`：資料集比較分析（需要兩個資料來源）
  - `default`：根據 source 數量自動判斷（推薦）
  - 預設值：`default`

- **`source`**: 資料來源模組
  - 單一來源（describe 模式）：直接指定模組名稱，如 `Loader`
  - 兩個來源（compare 模式）：使用字典格式指定 `base` 和 `target`
  - 可用值：`Loader`, `Splitter`, `Preprocessor`, `Synthesizer`, `Postprocessor`, `Constrainer`

## 產生的統計報告

Describer 會產生三個層級的統計報告：

### 1. Global（全域層級）

整體資料集的總體統計：
- 資料筆數（總記錄數）
- 欄位數量
- 記憶體使用量
- 資料型別分布（數值型、類別型、日期時間型）

### 2. Columnwise（欄位層級）

**數值型欄位統計**：
- 平均值（mean）
- 標準差（std）
- 中位數（median）
- 最小值（min）
- 最大值（max）
- 四分位數（Q1, Q3）
- 缺失值比例

**類別型欄位統計**：
- 唯一值數量（nunique）
- 最常出現的值
- 出現頻率
- 缺失值比例

**日期時間欄位統計**：
- 時間範圍（最早、最晚日期）
- 時間間隔分布

### 3. Pairwise（成對層級）

欄位間的相關性分析：
- 數值型欄位間的相關係數矩陣
- 高度相關的欄位對識別
- 類別型欄位間的關聯強度

## 資料品質檢查

使用 Describer 報告進行資料品質評估：

**缺失值檢查**
- 觀察各欄位的缺失值比例
- 高比例缺失值（>30%）可能影響合成品質
- 考慮使用 nan_groups 約束定義處理規則

**離群值檢查**
- 檢視數值欄位的最小值、最大值
- 觀察標準差與四分位數的關係
- 極端值可能需要在前處理階段處理

**類別分布檢查**
- 檢查類別型欄位的唯一值數量
- 評估類別平衡性（是否有主導類別）
- 少數類別（<1%）可能在合成後消失

**資料相關性檢查**
- 識別高度相關的欄位（相關係數 >0.9）
- 考慮是否需要降維或特徵選擇
- 了解欄位間的依賴關係

## 比較原始資料與合成資料

當您需要比較兩個資料集（例如原始資料與合成資料）時：

```yaml
Loader:
  original:
    filepath: 'original_data.csv'
    schema: 'data_schema.yaml'

Synthesizer:
  synthetic:
    method: custom_data
    filepath: 'synthetic_data.csv'
    schema: 'data_schema.yaml'

Describer:
  compare_data:
    method: compare  # 或使用 default（會自動判斷為 compare）
    source:
      base: Loader      # 基準資料（原始資料）
      target: Synthesizer  # 比較目標（合成資料）
```

### 比較報告內容

**Global 層級（含 Score）**：
- 整體相似度分數
- 資料筆數差異
- 欄位統計值的總體比較

**Columnwise 層級**：
- 各欄位統計值的差異或百分比變化
- 分布相似度（JS 散度）
- 缺失值比例變化

### 自訂比較方法

```yaml
Describer:
  custom_comparison:
    method: compare
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
```

**可用的統計方法**：
- 數值型：`mean`, `std`, `median`, `min`, `max`
- 類別型：`nunique`, `jsdivergence`

**比較方法**：
- `pct_change`：百分比變化 `(target - base) / abs(base)`（預設）
- `diff`：絕對差值 `target - base`

## 實務建議

**檢查順序**：
1. 執行 Describer 產生統計報告
2. 檢視 Global 層級了解整體狀況
3. 檢查 Columnwise 層級識別問題欄位
4. 觀察 Pairwise 層級了解欄位關聯

**決策判斷**：
- 若發現多表格資料需求 → 參考[多表格關聯資料](../multi-table-relationships)
- 若發現需要約束條件 → 參考[商業邏輯約束資料](../business-logic-constraints)
- 若資料品質良好 → 直接進行[快速入門](../../getting-started)

**品質標準**：
- 缺失值比例建議 <20%
- 離群值比例建議 <5%
- 類別平衡度建議主導類別 <80%
- 高相關欄位對建議進一步分析

## 注意事項

- Describer 不會修改原始資料，僅產生統計報告
- source 參數為必要參數，必須明確指定資料來源
- compare 模式必須使用字典格式指定 `base` 和 `target`
- 統計方法會根據資料類型自動篩選適用的計算
- 不適用的統計方法會返回 NaN
