---
title: "SynthesizerAdapter"
weight: 393
---

SynthesizerAdapter 使用各種生成模型處理合成資料生成，並與管線整合。

## 主要功能

- 統一的合成資料生成介面
- 支援多種合成方法（CTGAN、TVAE、CopulaGAN、GaussianCopula）
- 自動模型訓練和取樣
- 詮釋資料和隱私保護支援
- 與管線系統整合

## 方法參考

### `__init__(config: dict)`

初始化 SynthesizerAdapter 實例，設定合成配置。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 鍵值：`method`、`sample_size`、`epochs`、`batch_size`、`use_metadata`、`random_state`

### `run(input: dict)`

執行合成資料生成操作。

**參數：**
- `input`：dict，必要
  - 必須包含：
    - `data`：pd.DataFrame - 訓練資料
    - `metadata`：Schema - 資料詮釋資料
    - `sample_size`：int（選擇性）- 要生成的合成樣本數

**回傳：**
無直接回傳值。使用 `get_result()` 取得合成資料。

### `get_result()`

取得合成資料生成結果。

**回傳：**
- `tuple[pd.DataFrame, Schema]`：合成資料和更新後的詮釋資料

### `set_input(data, metadata)`

設定合成器的輸入資料。

**參數：**
- `data`：pd.DataFrame - 訓練資料
- `metadata`：Schema - 資料詮釋資料

## 使用範例

```python
from petsard.adapter import SynthesizerAdapter

# 設定合成器
adapter = SynthesizerAdapter({
    "method": "ctgan",
    "sample_size": 1000,
    "epochs": 300,
    "batch_size": 500,
    "random_state": 42
})

# 設定輸入
adapter.set_input(data=df, metadata=schema)

# 執行合成
adapter.run({
    "data": df,
    "metadata": schema
})

# 取得結果
synthetic_data, synthetic_metadata = adapter.get_result()
```

## 與管線整合

```yaml
# YAML 管線配置
pipeline:
  - module: loader
    config:
      filepath: "data.csv"
  - module: synthesizer
    config:
      method: "ctgan"
      sample_size: 1000
      epochs: 300
```

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 結果會快取直到下次 run() 呼叫