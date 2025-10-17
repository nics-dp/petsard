---
title: "fit()"
weight: 332
---

訓練處理器，學習資料的統計特性。

## 語法

```python
def fit(
    data: pd.DataFrame,
    sequence: list = None
) -> None
```

## 參數

- **data** : pd.DataFrame, required
    - 用於訓練的資料集
    - 必要參數
    - 處理器會從此資料學習統計特性

- **sequence** : list, optional
    - 自訂處理序列
    - 預設值：`['missing', 'outlier', 'encoder', 'scaler']`
    - 可用值：`'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`

## 返回值

無（方法會修改實例狀態）

## 說明

[`fit()`](processor_fit.zh-tw.md:1) 方法用於訓練處理器。此方法會：

1. 分析資料的統計特性（平均值、標準差、類別等）
2. 建立各個處理器的轉換規則
3. 準備好後續的 [`transform()`](processor_transform.zh-tw.md:1) 操作

此方法必須在 [`transform()`](processor_transform.zh-tw.md:1) 之前呼叫。

## 基本範例

```python
from petsard import Loader, Processor

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 建立並訓練處理器
processor = Processor(metadata=schema)
processor.fit(data)

# 轉換資料
processed_data = processor.transform(data)
```

## 自訂處理序列

```python
from petsard import Processor

# 只使用缺失值處理和編碼
processor = Processor(metadata=schema)
processor.fit(data, sequence=['missing', 'encoder'])

# 使用完整序列
processor = Processor(metadata=schema)
processor.fit(
    data,
    sequence=['missing', 'outlier', 'encoder', 'scaler']
)
```

## 使用離散化

```python
from petsard import Processor

# 使用離散化（不能與 encoder 同時使用）
processor = Processor(metadata=schema)
processor.fit(
    data,
    sequence=['missing', 'outlier', 'discretizing']
)
```

## 訓練流程

```
開始
  ↓
驗證序列有效性
  ↓
為每個步驟創建協調器（Mediator）
  ↓
按序列順序訓練各處理器：
  - missing: 學習填補值（平均值、中位數等）
  - outlier: 學習離群值閾值
  - encoder: 學習類別映射
  - scaler: 學習縮放參數（均值、標準差等）
  ↓
設置訓練完成標記
  ↓
結束
```

## 注意事項

- 必須在 [`transform()`](processor_transform.zh-tw.md:1) 之前呼叫此方法
- 訓練資料應該與後續要轉換的資料具有相同的結構
- `discretizing` 和 `encoder` 不能同時使用
- `discretizing` 必須是序列中的最後一步
- 序列最多支援 4 個處理步驟
- 某些處理器（如 `outlier_isolationforest`）會進行全域轉換
- 訓練後的統計資訊會保存在處理器實例中
- 重新呼叫 [`fit()`](processor_fit.zh-tw.md:1) 會覆蓋之前的訓練結果