---
title: "SplitterAdapter"
weight: 392
---

SplitterAdapter 處理訓練/驗證集的資料分割，具備重疊控制功能。

## 主要功能

- 統一的資料分割介面
- 具備重疊控制的拔靴法抽樣
- 支援多重樣本產生
- 回傳分割資料、詮釋資料和訓練索引
- 與管線系統整合

## 方法參考

### `__init__(config: dict)`

初始化 SplitterAdapter 實例，設定分割配置。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 鍵值：`num_samples`、`train_split_ratio`、`random_state`、`max_overlap_ratio`、`max_attempts`

### `run(input: dict)`

執行資料分割操作。

**參數：**
- `input`：dict，必要
  - 必須包含：
    - `data`：pd.DataFrame - 要分割的資料集
    - `metadata`：Schema - 資料詮釋資料
    - `exist_train_indices`：list[set]（選擇性）- 要避免重疊的現有訓練索引

**回傳：**
無直接回傳值。使用 `get_result()` 取得分割結果。

### `get_result()`

取得分割結果。

**回傳：**
- `tuple[dict, dict, list[set]]`：分割資料、詮釋資料和訓練索引

### `set_input(data, metadata, exist_train_indices=None)`

設定分割器的輸入資料。

**參數：**
- `data`：pd.DataFrame - 要分割的資料集
- `metadata`：Schema - 資料詮釋資料
- `exist_train_indices`：list[set]（選擇性）- 現有訓練索引

## 使用範例

```python
from petsard.adapter import SplitterAdapter

# 設定分割器
adapter = SplitterAdapter({
    "num_samples": 3,
    "train_split_ratio": 0.8,
    "random_state": 42
})

# 設定輸入
adapter.set_input(data=df, metadata=schema)

# 執行分割
adapter.run({
    "data": df,
    "metadata": schema
})

# 取得結果
split_data, metadata_dict, train_indices = adapter.get_result()
```

## 與管線整合

```yaml
# YAML 管線配置
pipeline:
  - module: loader
    config:
      filepath: "data.csv"
  - module: splitter
    config:
      num_samples: 5
      train_split_ratio: 0.8
      max_overlap_ratio: 0.0
```

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 樣本編號從 1 開始，而非 0
- 結果會快取直到下次 run() 呼叫