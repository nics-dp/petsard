---
title: "fit_sample()"
weight: 365
---

依序執行訓練和生成。

## 語法

```python
def fit_sample(
    data: pd.DataFrame,
    sample_num_rows: int = None,
    reset_sampling: bool = False,
    output_file_path: str = None
)
```

## 參數

- **data** : pd.DataFrame, required
    - 用於訓練的資料集
    - 必須是 pandas DataFrame
    - 不能為 None

- **sample_num_rows** : int, optional
    - 要生成的資料列數
    - 預設值：`None`（使用原始資料列數）
    - 必須為正整數

- **reset_sampling** : bool, optional
    - 是否重置採樣狀態
    - 預設值：`False`
    - 設為 `True` 可確保可重現的結果

- **output_file_path** : str, optional
    - 輸出檔案路徑
    - 預設值：`None`（不儲存到檔案）
    - 支援 CSV 格式

## 返回值

無。生成的資料儲存於 `data_syn` 屬性。

## 說明

`fit_sample()` 方法結合了 `fit()` 和 `sample()` 的功能，在單一呼叫中完成模型訓練和合成資料生成。這是最常用的方法，特別適合標準的合成資料生成工作流程。

此方法執行以下操作：
1. 使用提供的資料訓練模型（相當於呼叫 `fit()`）
2. 從訓練好的模型生成合成資料（相當於呼叫 `sample()`）
3. 套用精度四捨五入（如果在 schema 中定義）
4. 將結果儲存到 `data_syn` 屬性
5. 可選地將資料儲存到檔案

## 基本範例

```python
from petsard import Synthesizer
import pandas as pd

# 載入資料
df = pd.read_csv('data.csv')

# 一步完成訓練和生成
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df)

# 存取合成資料
synthetic_data = synthesizer.data_syn
print(f"生成了 {len(synthetic_data)} 列合成資料")
```

## 進階範例

### 指定生成數量

```python
from petsard import Synthesizer, Metadater

# 準備資料和 metadata
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# 訓練並生成指定數量的資料
synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(
    data=df,
    sample_num_rows=10000  # 生成 10000 列
)

print(f"原始資料: {len(df)} 列")
print(f"合成資料: {len(synthesizer.data_syn)} 列")
```

### 直接儲存結果

```python
# 訓練、生成並儲存到檔案
synthesizer = Synthesizer(method='sdv-single_table-gaussiancopula')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(
    data=df,
    sample_num_rows=5000,
    output_file_path='synthetic_output.csv'
)

print("合成資料已儲存到 synthetic_output.csv")
```

### 完整工作流程範例

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# 1. 載入資料
df = pd.read_csv('original_data.csv')
print(f"載入資料: {df.shape}")

# 2. 建立 metadata
metadata = Metadater.from_data(df)

# 3. 設定合成器
synthesizer = Synthesizer(
    method='sdv-single_table-ctgan',
    epochs=300,
    batch_size=500
)

# 4. 建立合成器實例
synthesizer.create(metadata=metadata)

# 5. 訓練並生成
synthesizer.fit_sample(
    data=df,
    sample_num_rows=len(df) * 2,  # 生成兩倍資料量
    reset_sampling=True,  # 確保可重現性
    output_file_path='synthetic_double.csv'
)

# 6. 驗證結果
print(f"合成資料: {synthesizer.data_syn.shape}")
print(f"欄位一致性: {set(df.columns) == set(synthesizer.data_syn.columns)}")
```

## 注意事項

- 必須先呼叫 `create()` 才能使用 `fit_sample()`
- 此方法會覆寫任何先前的訓練狀態
- 每次呼叫都會重新訓練模型，即使資料相同
- 如需多次生成不同數量的合成資料，建議分別使用 `fit()` 和 `sample()`
- 訓練時間取決於資料大小和選擇的合成方法
- 生成的資料會覆蓋 `data_syn` 屬性中的先前結果
- 適合一次性的訓練和生成需求
- 不適合需要微調或多次採樣的場景