---
title: "離群值處理"
weight: 2
---

識別並處理資料中的離群值（Outliers）。

## 使用範例

點擊下方按鈕在 Colab 中執行完整範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_outlier-handling.ipynb)

### 範例 1：欄位特定離群值方法

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  outlier-field-specific:
    sequence:
      - outlier
    config:
      outlier:
        age: 'outlier_zscore'       # 對 age 欄位使用 Z-Score 方法
        fnlwgt: 'outlier_iqr'       # 對 fnlwgt 欄位使用 IQR 方法
        education-num: None         # 跳過此欄位的離群值處理

        # 注意：
        # - 設定為 None 的欄位：不會進行離群值處理
        # - 未列出的欄位（如 capital-gain、capital-loss、hours-per-week）：
        #   會使用預設方法（outlier_iqr）

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

### 範例 2：全域離群值方法

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: 'benchmark://adult-income'
    schema: 'benchmark://adult-income_schema'

Preprocessor:
  outlier-global-simple:
    sequence:
      - outlier
    config:
      # 簡化語法：將一個全域方法套用到所有數值欄位
      outlier: 'outlier_isolationforest'

      # 可用的全域方法：
      # - 'outlier_isolationforest': Isolation Forest 演算法
      # - 'outlier_lof': Local Outlier Factor 演算法

      # 這等同於：
      # outlier:
      #   age: 'outlier_isolationforest'
      #   fnlwgt: 'outlier_isolationforest'
      #   education-num: 'outlier_isolationforest'
      #   capital-gain: 'outlier_isolationforest'
      #   capital-loss: 'outlier_isolationforest'
      #   hours-per-week: 'outlier_isolationforest'

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

## 可用的處理器

| 處理器 | 說明 | 適用類型 | 全域處理 |
|--------|------|---------|---------|
| `outlier_zscore` | Z-Score 方法（\|z\| > 3） | 數值型 | ❌ |
| `outlier_iqr` | 四分位距方法（1.5 IQR） | 數值型 | ❌ |
| `outlier_isolationforest` | 隔離森林演算法 | 數值型 | ✅ |
| `outlier_lof` | 局部離群因子演算法 | 數值型 | ✅ |

## 處理器詳細說明

### outlier_zscore

使用 Z-Score 統計方法識別離群值。

**判定標準**：
- \|Z-Score\| > 3 視為離群值
- Z-Score = (x - μ) / σ

### outlier_iqr

使用四分位距（Interquartile Range）方法識別離群值。

**判定標準**：
- 低於 Q1 - 1.5 × IQR
- 高於 Q3 + 1.5 × IQR
- IQR = Q3 - Q1

### outlier_isolationforest

使用 sklearn 的 Isolation Forest 演算法。

**特性**：
- 全域轉換（套用到所有數值欄位）
- 適合多維度離群值檢測
- 自動學習離群值模式

### outlier_lof

使用局部離群因子（Local Outlier Factor）演算法。

**特性**：
- 全域轉換（套用到所有數值欄位）
- 基於密度的離群值檢測
- 考慮局部資料分布

## 處理邏輯

### 一般離群值處理（Z-Score、IQR）

- **訓練階段（fit）**：計算統計參數（均值、標準差、四分位數）
- **轉換階段（transform）**：
  1. 識別離群值
  2. 移除包含離群值的列
- **還原階段（inverse_transform）**：⚠️ 無法還原（離群值處理不可逆）

### 全域離群值處理（Isolation Forest、LOF）

- **訓練階段（fit）**：使用所有數值欄位訓練模型
- **轉換階段（transform）**：
  1. 使用模型預測離群值
  2. 移除被標記為離群值的列
- **還原階段（inverse_transform）**：⚠️ 無法還原（離群值處理不可逆）

## 預設行為

不同資料類型的預設離群值處理：

| 資料類型 | 預設處理器 | 說明 |
|---------|-----------|------|
| 數值型 | `outlier_iqr` | 使用四分位距方法 |
| 類別型 | 無 | 不處理離群值 |
| 日期時間型 | `outlier_iqr` | 使用四分位距方法 |

系統會自動：
1. 偵測到全域處理器
2. 將所有數值欄位的處理器替換為該全域處理器
3. 記錄警告訊息

## 注意事項

- **不可逆性**：離群值處理無法在後處理時還原
- **資料減少**：處理離群值會移除部分資料列
- **全域覆蓋**：使用全域處理器時，所有數值欄位的設定都會被覆蓋
- **處理順序**：建議在缺失值處理之後、編碼之前執行
- **類別型資料**：離群值處理不適用於類別型資料
- **影響評估**：移除過多離群值可能影響資料分布和模型效果
- **合成資料**：後處理時合成資料的範圍可能與原始資料略有差異

## 方法選擇建議

| 情況 | 建議方法 | 原因 |
|-----|---------|------|
| 單一欄位異常 | `outlier_zscore` 或 `outlier_iqr` | 簡單有效，易於解釋 |
| 多維度離群值 | `outlier_isolationforest` | 考慮欄位間關聯性 |
| 密度基礎檢測 | `outlier_lof` | 適合非均勻分布資料 |
| 不確定時 | `outlier_iqr` | 穩健且廣泛適用 |