---
title: "缺失值處理"
weight: 131
---

處理資料中的缺失值（NA/NaN）。

## 背景說明

由於大部分合成演算法是基於機率模型，經 CAPE 團隊研究發現，多數演算法無法直接支援遺失值（`None`、`np.nan`、`pd.NA`）。即使部分演算法宣稱可以處理遺失值，也很難確認各自的實現方法是否恰當。

因此，**PETsARD 建議對於任何包含遺失值的欄位，都應主動進行處理**：
- 數值型欄位：預設使用平均值插補
- 類別型/文字型/日期型欄位：預設採用直接刪除策略

## 使用範例

請點擊下方按鈕在 Colab 中執行完整範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/getting-started/use-cases/data-preprocessing/handling-missing-values.ipynb)

### 使用預設缺失值處理

```yaml
Preprocessor:
  demo:
    method: 'default'
    # 數值型欄位：使用平均值填補
    # 類別型欄位：刪除含缺失值的列
```

### 自訂特定欄位的缺失值處理

```yaml
Preprocessor:
  custom:
    method: 'default'
    config:
      missing:
        age: 'missing_median'        # 使用中位數填補
        income: 'missing_mean'       # 使用平均值填補
        gender: 'missing_mode'       # 使用眾數填補
        education: 'missing_drop'    # 刪除含缺失值的列
```

### 使用自訂值填補

```yaml
Preprocessor:
  custom_value:
    method: 'default'
    config:
      missing:
        age:
          method: 'missing_simple'
          value: 0.0                # 使用 0 填補缺失值
```

## 可用的處理器

| 處理器 | 說明 | 適用資料類型 | 參數 |
|--------|------|-------------|------|
| `missing_mean` | 使用平均值填補 | 數值型 | 無 |
| `missing_median` | 使用中位數填補 | 數值型 | 無 |
| `missing_mode` | 使用眾數填補 | 類別型、數值型 | 無 |
| `missing_simple` | 使用指定值填補 | 數值型 | `value`（預設：0.0） |
| `missing_drop` | 刪除含缺失值的列 | 所有類型 | 無 |

## 參數說明

### missing_simple

- **value** (`float`, 選用)
  - 用於填補缺失值的自訂值
  - 預設值：`0.0`
  - 範例：`value: -1.0`

## 處理邏輯

### 1. 統計值填補（Mean/Median/Mode）

```
訓練階段（fit）：
  計算並儲存統計值（平均值/中位數/眾數）

轉換階段（transform）：
  使用儲存的統計值填補 NA

還原階段（inverse_transform）：
  依照原始資料的缺失比例，隨機插入 NA
```

### 2. 自訂值填補（Simple）

```
訓練階段（fit）：
  記錄填補值

轉換階段（transform）：
  使用指定值填補 NA

還原階段（inverse_transform）：
  依照原始資料的缺失比例，隨機插入 NA
```

### 3. 刪除（Drop）

```
訓練階段（fit）：
  無需訓練

轉換階段（transform）：
  刪除包含 NA 的列

還原階段（inverse_transform）：
  依照原始資料的缺失比例，隨機插入 NA
```

## 預設行為

不同資料類型的預設缺失值處理：

| 資料類型 | 預設處理器 | 說明 |
|---------|-----------|------|
| 數值型 | `missing_mean` | 使用平均值填補 |
| 類別型 | `missing_drop` | 刪除含缺失值的列 |
| 日期時間型 | `missing_drop` | 刪除含缺失值的列 |

## 完整範例

```yaml
Loader:
  load_data:
    filepath: 'data.csv'
    schema: 'schema.yaml'

Preprocessor:
  handle_missing:
    method: 'default'
    sequence:
      - missing
      - encoder
      - scaler
    config:
      missing:
        # 數值型欄位
        age: 'missing_median'           # 年齡使用中位數
        income: 'missing_mean'          # 收入使用平均值
        hours_per_week:
          method: 'missing_simple'
          value: 40.0                   # 工時預設 40
        
        # 類別型欄位
        gender: 'missing_mode'          # 性別使用眾數
        education: 'missing_drop'       # 教育程度：刪除缺失列
```

## 注意事項

- **處理順序**：缺失值處理通常是第一個步驟
- **眾數填補**：如果有多個眾數，會隨機選擇一個
- **刪除影響**：使用 `missing_drop` 可能大幅減少資料量
- **還原機制**：後處理時會依原始比例隨機插入 NA，位置不會完全相同
- **統計值儲存**：訓練時計算的統計值會用於所有後續的轉換
- **NA 識別**：自動識別 pandas 的 NA 值（`np.nan`、`None`、`pd.NA`）

## 相關文件

- [Processor API - fit()]({{< ref "/docs/python-api/processor-api/processor_fit" >}})
- [Processor API - transform()]({{< ref "/docs/python-api/processor-api/processor_transform" >}})
- [Processor API - inverse_transform()]({{< ref "/docs/python-api/processor-api/processor_inverse_transform" >}})