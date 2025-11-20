---
title: "transform()"
weight: 333
---

執行資料前處理轉換。

## 語法

```python
def transform(
    data: pd.DataFrame
) -> pd.DataFrame
```

## 參數

- **data** : pd.DataFrame, required
    - 待轉換的資料集
    - 必要參數
    - 應與訓練時使用的資料具有相同結構

## 返回值

- **pd.DataFrame**
    - 轉換後的資料
    - 已套用所有前處理步驟

## 說明

`transform()` 方法用於執行實際的資料轉換。此方法會：

1. 按照訓練時設定的序列執行各個處理步驟
2. 依序套用缺失值處理、離群值處理、編碼、縮放等操作
3. 返回轉換後的資料

此方法必須在 `fit()` 之後呼叫。

## 基本範例

```python
from petsard import Loader, Processor

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 訓練處理器
processor = Processor(metadata=schema)
processor.fit(data)

# 轉換資料
processed_data = processor.transform(data)

print(f"原始資料形狀: {data.shape}")
print(f"處理後形狀: {processed_data.shape}")
```

## 轉換不同資料集

```python
from petsard import Processor

# 在訓練集上訓練
processor = Processor(metadata=schema)
processor.fit(train_data)

# 轉換訓練集
train_processed = processor.transform(train_data)

# 使用相同的轉換器轉換測試集
test_processed = processor.transform(test_data)
```

## 檢查轉換結果

```python
import pandas as pd
from petsard import Processor

processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# 比較轉換前後
print("轉換前：")
print(data.describe())
print("\n轉換後：")
print(processed_data.describe())

# 檢查缺失值
print(f"\n轉換前缺失值數量: {data.isna().sum().sum()}")
print(f"轉換後缺失值數量: {processed_data.isna().sum().sum()}")
```

## 轉換流程

```
開始
  ↓
檢查是否已訓練
  ↓
複製輸入資料
  ↓
按序列執行處理：
  1. Missing: 填補缺失值
     ↓
  2. Outlier: 處理離群值
     ↓
  3. Encoder: 編碼類別變數
     ↓ (協調器調整欄位)
  4. Scaler: 正規化數值
     ↓
返回處理後的資料
  ↓
結束
```

## 處理步驟說明

### 1. 缺失值處理（Missing）
- 使用訓練時學習的統計值填補
- 例如：平均值、中位數、眾數

### 2. 離群值處理（Outlier）
- 識別並處理異常值
- 使用訓練時計算的閾值

### 3. 編碼（Encoder）
- 將類別變數轉換為數值
- 可能會增加欄位數量（如獨熱編碼）

### 4. 縮放（Scaler）
- 正規化數值範圍
- 使用訓練時學習的參數（均值、標準差等）

## 注意事項

- 必須先呼叫 `fit()` 訓練處理器
- 轉換的資料必須與訓練資料具有相同的欄位結構
- 某些編碼方式（如 One-Hot）會改變欄位數量
- 轉換後的資料類型可能與原始資料不同
- 返回的是資料的副本，不會修改原始資料
- 可以重複呼叫以轉換多個資料集
- 所有轉換都使用相同的訓練參數
- 離群值處理可能會移除部分資料列