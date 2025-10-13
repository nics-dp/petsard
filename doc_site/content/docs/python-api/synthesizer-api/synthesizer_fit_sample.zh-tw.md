---
title: "fit_sample()"
weight: 4
---

依序執行訓練和生成。

## 語法

```python
def fit_sample(data: pd.DataFrame) -> pd.DataFrame
```

## 參數

- **data** : pd.DataFrame, required
    - 用於訓練的資料集
    - 必須是 pandas DataFrame
    - 不能為 None

## 返回值

- **pd.DataFrame**
    - 生成的合成資料
    - 具有與原始訓練資料相同的欄位

## 說明

`fit_sample()` 方法結合了 `fit()` 和 `sample()` 的功能，在單一呼叫中完成模型訓練和合成資料生成。這是最常用的方法，特別適合標準的合成資料生成工作流程。

此方法執行以下操作：
1. 使用提供的資料訓練模型（相當於呼叫 `fit()`）
2. 從訓練好的模型生成合成資料（相當於呼叫 `sample()`）
3. 返回生成的合成資料

## 範例

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# 載入資料
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# 一步完成訓練和生成
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthetic_data = synthesizer.fit_sample(data=df)

# 存取合成資料
print(f"生成了 {len(synthetic_data)} 列合成資料")

# 如需儲存到檔案
synthetic_data.to_csv('synthetic_output.csv', index=False)
```

## 注意事項

- 必須先呼叫 `create()` 才能使用 `fit_sample()`
- 此方法會覆寫任何先前的訓練狀態
- 每次呼叫都會重新訓練模型，即使資料相同
- 如需多次生成不同數量的合成資料，建議分別使用 `fit()` 和 `sample()`
- 訓練時間取決於資料大小和選擇的合成方法
- 適合一次性的訓練和生成需求
- 生成的資料列數在 `create()` 或從訓練資料決定