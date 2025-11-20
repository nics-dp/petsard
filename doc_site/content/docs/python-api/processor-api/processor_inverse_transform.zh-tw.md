---
title: "inverse_transform()"
weight: 334
---

執行資料後處理還原轉換，將處理過的資料還原到原始格式。

## 語法

```python
def inverse_transform(
    data: pd.DataFrame
) -> pd.DataFrame
```

## 參數

- **data** : pd.DataFrame, required
    - 待還原的資料集（通常是合成資料）
    - 必要參數
    - 應該是經過相同前處理步驟處理的資料

## 返回值

- **pd.DataFrame**
    - 還原後的資料
    - 已套用所有逆向轉換步驟
    - 資料格式接近原始資料

## 說明

`inverse_transform()` 方法用於執行資料的逆向轉換。此方法會：

1. 按照前處理序列的反向順序執行還原操作
2. 依序套用反縮放、反編碼、恢復缺失值等操作
3. 將資料類型對齊到原始 schema
4. 返回接近原始格式的資料

此方法必須在 `fit()` 和 `transform()` 之後呼叫。

## 基本範例

```python
from petsard import Loader, Processor, Synthesizer

# 1. 載入並前處理資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# 2. 合成資料
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data)
synthetic_data = synthesizer.data_syn

# 3. 後處理還原
restored_data = processor.inverse_transform(synthetic_data)

print(f"原始資料形狀: {data.shape}")
print(f"還原資料形狀: {restored_data.shape}")
```

## 完整工作流程

```python
from petsard import Loader, Processor, Synthesizer
import pandas as pd

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 前處理
processor = Processor(metadata=schema)
processor.fit(data, sequence=['missing', 'outlier', 'encoder', 'scaler'])
processed_data = processor.transform(data)

# 合成
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data, sample_num_rows=len(data))
synthetic_data = synthesizer.data_syn

# 後處理還原
# 還原序列自動為: ['scaler', 'encoder', 'missing']
restored_data = processor.inverse_transform(synthetic_data)

# 比較資料分布
print("原始資料描述統計：")
print(data.describe())
print("\n還原資料描述統計：")
print(restored_data.describe())
```

## 還原流程

```
開始
  ↓
檢查是否已訓練
  ↓
設置缺失值恢復參數
  ↓
反轉前處理序列（移除 outlier）
  ↓
按反序執行還原：
  4. Scaler: 反縮放到原始範圍
     ↓ (協調器調整欄位)
  3. Encoder: 類別變數解碼
     ↓ (協調器調整欄位)
  1. Missing: 依比例插入 NA
     ↓
對齊資料類型到 schema
  ↓
返回還原後的資料
  ↓
結束
```

## 還原步驟說明

### 1. 反縮放（Inverse Scaler）
- 將正規化的數值還原到原始範圍
- 使用前處理時學習的縮放參數
- 例如：反標準化、反最小-最大縮放

### 2. 反編碼（Inverse Encoder）
- 將數值還原為類別標籤
- 獨熱編碼會被還原為單一欄位
- 使用前處理時建立的映射表

### 3. 恢復缺失值（Restore Missing）
- 依照原始資料的缺失比例
- 隨機選擇位置插入 `NA` 值
- 每個欄位獨立計算缺失比例

### 4. 對齊資料類型
- 根據 schema 定義調整資料類型
- 確保類別型、數值型、日期型正確
- 處理特殊的日期時間格式

## 缺失值恢復機制

```python
# 系統會自動計算並恢復缺失值
# 假設原始資料有 10% 的缺失值

# 前處理時記錄：
# - 全域缺失值比例：10%
# - age 欄位缺失值比例：15%
# - income 欄位缺失值比例：5%

# 後處理時恢復：
# 1. 隨機選擇 10% 的資料列
# 2. 在 age 欄位中，這些列的 15% 設為 NA
# 3. 在 income 欄位中，這些列的 5% 設為 NA
```

## 注意事項

- 必須先完成 `fit()` 和 `transform()`
- 輸入資料應該是經過相同前處理的資料
- 離群值處理不會被還原（步驟會被跳過）
- 缺失值的位置是隨機的，與原始資料不完全相同
- 獨熱編碼會減少欄位數量
- 還原後的資料類型會對齊到原始 schema
- 返回的是資料的副本，不會修改輸入資料
- 日期時間資料會被轉換為適當的格式
- 某些合成器產生的浮點數會被四捨五入為整數（如 discretizing 情況）