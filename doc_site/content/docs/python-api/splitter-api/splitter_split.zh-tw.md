---
title: "split()"
weight: 352
---

將資料分割為訓練集和驗證集，具備增強的重疊控制功能。

## 語法

```python
def split(
    data: pd.DataFrame = None,
    metadata: SchemaMetadata = None,
    exist_train_indices: list[set] = None
) -> tuple[dict, dict, list[set]]
```

## 參數

- **data** : pd.DataFrame, required
    - 要分割的資料集
    - 必須是 pandas DataFrame
    - 不能為 None

- **metadata** : SchemaMetadata, optional
    - 資料集的詮釋資料
    - 包含資料的結構描述資訊
    - 會更新分割資訊
    - 預設值：`None`

- **exist_train_indices** : list[set], optional
    - 要避免重疊的現有訓練索引集合列表
    - 每個集合包含來自先前分割的訓練索引
    - 用於確保新分割不會與現有分割重疊
    - 預設值：`None`

## 返回值

- **tuple[dict, dict, list[set]]**
    - 包含三個元素的元組：
        - `split_data` (`dict`)：格式為 `{sample_num: {'train': df, 'validation': df}}` 的字典
        - `metadata_dict` (`dict`)：格式為 `{sample_num: {'train': metadata, 'validation': metadata}}` 的字典
        - `train_indices` (`list[set]`)：每個樣本的訓練索引集合列表

## 說明

`split()` 方法使用函數式程式設計模式執行資料分割，具備增強的重疊控制功能。它根據初始化時提供的設定產生多個訓練/驗證分割。

此方法執行以下操作：
1. 驗證輸入資料
2. 根據重疊控制設定產生訓練索引
3. 建立訓練和驗證 DataFrames
4. 如果提供，更新詮釋資料
5. 以不可變資料結構回傳結果

## 基本範例

```python
from petsard import Splitter
import pandas as pd

# 建立範例資料
df = pd.DataFrame({
    'feature1': range(100),
    'feature2': range(100, 200),
    'target': [0, 1] * 50
})

# 基本分割
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# 存取結果
for i in range(1, 4):
    train_df = split_data[i]['train']
    val_df = split_data[i]['validation']
    print(f"樣本 {i}: 訓練集={len(train_df)}, 驗證集={len(val_df)}")
```

## 進階範例

### 含詮釋資料的分割

```python
from petsard import Splitter, SchemaMetadata

# 建立詮釋資料
metadata = SchemaMetadata.from_data(df)

# 含詮釋資料的分割
splitter = Splitter(num_samples=3, train_split_ratio=0.75)
split_data, metadata_dict, train_indices = splitter.split(
    data=df,
    metadata=metadata
)

# 存取分割的詮釋資料
train_meta = metadata_dict[1]['train']
val_meta = metadata_dict[1]['validation']
```

## 注意事項

- 此方法遵循函數式程式設計原則回傳不可變資料結構
- 樣本編號從 1 開始，而非 0
- 當 `max_overlap_ratio` 設為 0.0 時，樣本將完全無重疊
- 如果方法無法在 `max_attempts` 內產生有效樣本，將引發例外
- 詮釋資料是選擇性的，但建議使用以維護資料血緣
- 回傳的 DataFrames 是副本，而非原始資料的參考