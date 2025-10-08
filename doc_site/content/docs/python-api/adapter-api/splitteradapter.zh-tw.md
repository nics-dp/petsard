---
title: "SplitterAdapter"
weight: 363
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
  - 支援所有 Splitter 初始化參數
  - 鍵值：`num_samples`、`train_split_ratio`、`random_state`、`max_overlap_ratio`、`max_attempts`

**內部處理：**
1. **配置驗證**：驗證所有分割參數
2. **Splitter 初始化**：建立內部 Splitter 實例

### `run(input: dict)`

執行資料分割操作。

**參數：**
- `input`：dict，必要
  - 輸入參數字典
  - 必須包含：
    - `data`：pd.DataFrame - 要分割的資料集
    - `metadata`：Schema - 資料詮釋資料
    - `exist_train_indices`：list[set]（選擇性）- 要避免重疊的現有訓練索引

**執行流程：**
1. **輸入驗證**：驗證必要的輸入參數
2. **資料分割**：
   - 執行拔靴法抽樣
   - 控制樣本間的重疊
   - 產生訓練/驗證分割
3. **詮釋資料更新**：為每個分割更新詮釋資料

**回傳：**

無直接回傳值。結果儲存在內部屬性中：
- 使用 `get_result()` 取得分割結果

### `get_result()`

取得分割結果。

**回傳：**
- `tuple[dict, dict, list[set]]`：
  - 分割資料字典
  - 詮釋資料字典
  - 訓練索引列表

### `set_input(data, metadata, exist_train_indices=None)`

設定分割器的輸入資料。

**參數：**
- `data`：pd.DataFrame - 要分割的資料集
- `metadata`：Schema - 資料詮釋資料
- `exist_train_indices`：list[set]（選擇性）- 現有訓練索引

## 使用範例

### 基本分割

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

### 重疊控制

```python
# 設定具備重疊控制的分割器
adapter = SplitterAdapter({
    "num_samples": 5,
    "train_split_ratio": 0.7,
    "max_overlap_ratio": 0.1,  # 最大 10% 重疊
    "max_attempts": 50
})

# 設定含現有索引的輸入
adapter.set_input(
    data=df,
    metadata=schema,
    exist_train_indices=existing_indices
)

# 執行
adapter.run({
    "data": df,
    "metadata": schema,
    "exist_train_indices": existing_indices
})
```

### 錯誤處理

```python
try:
    adapter = SplitterAdapter(config)
    adapter.run(input_dict)
except ConfigError as e:
    print(f"配置錯誤：{e}")
except Exception as e:
    print(f"分割失敗：{e}")
```

## 工作流程

1. **配置**：使用分割參數初始化
2. **輸入設定**：提供資料、詮釋資料和選擇性的現有索引
3. **分割執行**：執行具備重疊控制的拔靴法抽樣
4. **結果取得**：取得分割資料、詮釋資料和索引

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
  - module: synthesizer
    config:
      method: "ctgan"
```

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 樣本編號從 1 開始，而非 0
- `max_overlap_ratio=0.0` 確保樣本完全無重疊
- 如果重疊約束過於嚴格，拔靴法抽樣可能失敗
- 詮釋資料會自動更新分割資訊
- 結果會快取直到下次 run() 呼叫