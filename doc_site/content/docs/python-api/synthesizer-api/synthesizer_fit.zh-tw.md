---
title: "fit()"
weight: 363
---

訓練合成模型。

## 語法

```python
def fit(data: pd.DataFrame)
```

## 參數

- **data** : pd.DataFrame, required
    - 用於訓練的資料集
    - 必須是 pandas DataFrame
    - 不能為 None

## 返回值

無。更新合成器的內部狀態。

## 說明

`fit()` 方法用於訓練合成模型。此方法會使用提供的資料集來學習資料的統計特性和模式，以便後續生成合成資料。

此方法執行以下操作：
1. 驗證輸入資料的有效性
2. 將資料傳遞給底層合成器實作
3. 執行模型訓練過程
4. 儲存訓練後的模型狀態

訓練過程的具體細節取決於所選的合成方法：
- **GaussianCopula**：學習邊際分布和相關結構
- **CTGAN/CopulaGAN**：訓練生成對抗網路
- **TVAE**：訓練變分自編碼器
- **自訂方法**：執行自訂的訓練邏輯

## 範例

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# 準備訓練資料
df = pd.read_csv('training_data.csv')
metadata = Metadater.from_data(df)

# 初始化並訓練合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# 訓練完成後可以生成合成資料
synthetic_data = synthesizer.sample()
```

## 注意事項

- 必須在呼叫 `fit()` 之前先呼叫 `create()`
- 訓練時間取決於資料大小、複雜度和選擇的合成方法
- 深度學習方法（CTGAN、TVAE）通常需要較長的訓練時間
- 訓練過程可能消耗大量記憶體，特別是對於大型資料集
- 某些合成器（如 CTGAN）可能需要 GPU 加速以提升效能
- 訓練完成後，模型狀態會儲存在合成器內部
- 可以多次呼叫 `sample()` 而無需重新訓練
- 如需重新訓練，請再次呼叫 `fit()` 方法