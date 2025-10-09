---
title: "sample()"
weight: 364
---

生成合成資料。

## 語法

```python
def sample(
    sample_num_rows: int = None,
    reset_sampling: bool = False,
    output_file_path: str = None
)
```

## 參數

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

`sample()` 方法用於從已訓練的模型生成合成資料。必須在呼叫 `fit()` 完成訓練後才能使用此方法。

此方法執行以下操作：
1. 檢查模型是否已訓練
2. 根據參數生成指定數量的合成資料
3. 套用精度四捨五入（如果在 schema 中定義）
4. 將結果儲存到 `data_syn` 屬性
5. 可選地將資料儲存到檔案

## 基本範例

```python
from petsard import Synthesizer

# 初始化、建立並訓練合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# 生成與原始資料相同列數的合成資料
synthesizer.sample()
synthetic_data = synthesizer.data_syn

# 生成指定列數
synthesizer.sample(sample_num_rows=1000)
print(f"生成了 {len(synthesizer.data_syn)} 列合成資料")
```

## 進階範例

### 生成並儲存到檔案

```python
from petsard import Synthesizer

# 訓練合成器
synthesizer = Synthesizer(method='sdv-single_table-gaussiancopula')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# 生成並儲存到檔案
synthesizer.sample(
    sample_num_rows=5000,
    output_file_path='synthetic_data.csv'
)

print(f"合成資料已儲存到 synthetic_data.csv")
```

### 多次採樣

```python
# 第一次採樣
synthesizer.sample(sample_num_rows=1000)
first_batch = synthesizer.data_syn.copy()

# 第二次採樣（結果會不同）
synthesizer.sample(sample_num_rows=1000)
second_batch = synthesizer.data_syn.copy()

# 使用重置獲得可重現的結果
synthesizer.sample(sample_num_rows=1000, reset_sampling=True)
third_batch = synthesizer.data_syn.copy()

synthesizer.sample(sample_num_rows=1000, reset_sampling=True)
fourth_batch = synthesizer.data_syn.copy()

# third_batch 和 fourth_batch 應該相同
```

### 批次生成大量資料

```python
# 對於大量資料，可以分批生成
batch_size = 10000
total_rows = 100000
all_synthetic = []

for i in range(0, total_rows, batch_size):
    synthesizer.sample(sample_num_rows=batch_size)
    all_synthetic.append(synthesizer.data_syn)
    print(f"已生成 {i + batch_size} / {total_rows} 列")

# 合併所有批次
import pandas as pd
final_synthetic = pd.concat(all_synthetic, ignore_index=True)
```

## 注意事項

- 必須先完成 `fit()` 訓練才能呼叫 `sample()`
- 生成的資料會覆蓋 `data_syn` 屬性中的先前結果
- 大量資料生成可能需要較長時間和記憶體
- `reset_sampling` 參數對某些合成器可能無效
- 輸出檔案會覆蓋已存在的同名檔案
- 精度四捨五入會自動根據 schema 設定套用
- 某些合成器可能有生成數量的限制