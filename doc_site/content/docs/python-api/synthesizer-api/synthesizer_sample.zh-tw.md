---
title: "sample()"
weight: 3
---

生成合成資料。

## 語法

```python
def sample() -> pd.DataFrame
```

## 參數

無

## 返回值

- **pd.DataFrame**
    - 生成的合成資料
    - 具有與原始訓練資料相同的欄位

## 說明

`sample()` 方法用於從已訓練的模型生成合成資料。必須在呼叫 `fit()` 完成訓練後才能使用此方法。

此方法執行以下操作：
1. 檢查模型是否已訓練
2. 生成合成資料列（數量由設定決定）
3. 返回生成的合成資料作為 DataFrame

## 範例

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# 載入並準備資料
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# 初始化、建立並訓練合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# 生成合成資料
synthetic_data = synthesizer.sample()
print(f"生成了 {len(synthetic_data)} 列合成資料")

# 如需儲存到檔案
synthetic_data.to_csv('synthetic_data.csv', index=False)
```

## 注意事項

- 必須先完成 `fit()` 訓練才能呼叫 `sample()`
- 生成的資料列數在 `create()` 或 `fit()` 時根據 metadata 或訓練資料決定
- 大量資料生成可能需要較長時間和記憶體
- 某些合成器可能有生成數量的限制
- 若要指定生成的資料列數，請在初始化 Synthesizer 時設定 `sample_num_rows` 參數