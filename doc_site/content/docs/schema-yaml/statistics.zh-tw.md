---
title: "統計資訊"
weight: 6
---

設定 `enable_stats: true` 時，系統會自動計算並記錄欄位的統計資訊，用於資料品質分析、合成資料驗證和欄位特徵理解。大型資料集（超過 100 萬列）計算會較耗時，建議謹慎使用。

## 啟用方式

### 全域設定

```yaml
id: my_schema
enable_stats: true  # 全域啟用
attributes:
  age:
    type: int
```

### 個別欄位設定

```yaml
attributes:
  age:
    type: int
    enable_stats: true   # 啟用
  notes:
    type: str
    enable_stats: false  # 停用
```

## 統計項目

### 通用統計（所有欄位）

| 項目 | 說明 |
|------|------|
| `row_count` | 總列數 |
| `na_count` | 空值數量 |
| `na_percentage` | 空值百分比 |
| `detected_type` | 偵測到的資料型別 |
| `actual_dtype` | pandas dtype |

### 數值統計

僅在 `type` 為 `int` 或 `float` 且 `category: false` 時計算：

| 項目 | 說明 |
|------|------|
| `mean` | 平均值 |
| `std` | 標準差 |
| `min` | 最小值 |
| `max` | 最大值 |
| `median` | 中位數 |
| `q1` | 第一四分位數 |
| `q3` | 第三四分位數 |

### 類別統計

僅在 `category: true` 時計算：

| 項目 | 說明 |
|------|------|
| `unique_count` | 唯一值數量 |
| `mode` | 眾數 |
| `mode_frequency` | 眾數出現次數 |
| `category_distribution` | 類別分佈（最多 20 個） |

## 統計資訊結構

```yaml
attributes:
  age:
    type: int
    enable_stats: true
    stats:
      row_count: 1000
      na_count: 50
      na_percentage: 0.05
      mean: 35.5
      std: 12.3
      min: 18
      max: 85
      median: 34.0
      q1: 27.0
      q3: 43.0