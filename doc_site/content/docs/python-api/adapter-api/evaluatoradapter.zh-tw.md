---
title: "EvaluatorAdapter"
weight: 6
---

EvaluatorAdapter 處理資料評估，支援原始、合成和控制資料集的比較評估。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/evaluatoradapter-usage-diagram.zh-tw.mmd" >}}

> **圖例：**
> - 淺紫色框：EvaluatorAdapter 主類別
> - 藍色框：核心評估模組
> - 紫色框：資料對齊模組
> - 淺粉色框：配置類別
> - `..>`：依賴關係
> - `-->`：擁有關係

## 主要功能

- 統一的資料評估介面
- 自動資料類型對齊（使用 Schema）
- 支援多資料集評估（ori、syn、control）
- 整合各種評估方法（Privacy、Utility、Diagnostic）
- 固定的資料源命名邏輯

## 方法參考

### `__init__(config: dict)`

初始化 EvaluatorAdapter 實例。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 必須包含 `method` 鍵（評估方法）
  - 支援的評估方法：privacy、utility、diagnostic 等

### `run(input: dict)`

執行資料評估，包括自動資料類型對齊。

**參數：**
- `input`：dict，必要
  - 輸入參數字典
  - 包含 `data` 字典（ori、syn、control 資料）
  - 可選 `schema` 用於資料類型對齊

**回傳：**
無直接回傳值。使用 `get_result()` 取得結果。

### `set_input(status)`

設定評估器的輸入資料。

**參數：**
- `status`：Status，必要
  - 系統狀態物件
  - 自動提取 ori、syn、control 資料

**回傳：**
- `dict`：包含評估所需的資料字典

### `get_result()`

取得評估結果。

**回傳：**
- `dict[str, pd.DataFrame]`：評估結果字典

## 使用範例

```python
from petsard.adapter import EvaluatorAdapter

# 初始化評估器
adapter = EvaluatorAdapter({
    "method": "privacy",
    "privacy_method": ["membership_inference", "attribute_inference"]
})

# 設定輸入資料（通常由 Executor 自動處理）
input_data = {
    "data": {
        "ori": original_df,
        "syn": synthetic_df,
        "control": control_df  # 可選
    },
    "schema": schema  # 可選，用於資料類型對齊
}

# 執行評估
adapter.run(input_data)

# 取得結果
results = adapter.get_result()
```

## 工作流程

1. **資料收集**：從 Status 收集 ori、syn、control 資料
2. **Schema 取得**：優先順序為 Loader > Splitter > Preprocessor
3. **資料類型對齊**（有 Schema 時）
   - 使用 SchemaMetadater.align() 對齊資料類型
   - 確保評估時資料類型一致
4. **評估執行**：呼叫底層 Evaluator 執行評估

## 資料源邏輯

EvaluatorAdapter 使用固定的資料源命名：

- **ori（原始資料）**：
  - 有 Splitter 時：取 Splitter 的 train
  - 無 Splitter 時：取 Loader 的結果
  
- **syn（合成資料）**：
  - 取前一個模組的結果（通常是 Synthesizer 或 Postprocessor）
  
- **control（控制資料）**：
  - 僅在有 Splitter 時存在
  - 取 Splitter 的 validation

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 資料源命名固定，不支援自訂
- 自動處理資料類型對齊，確保評估正確性
- 結果會快取直到下次 run() 呼叫