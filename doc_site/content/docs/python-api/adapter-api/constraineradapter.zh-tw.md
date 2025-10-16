---
title: "ConstrainerAdapter"
weight: 4
---

ConstrainerAdapter 處理合成資料的約束條件套用，整合 Constrainer 與執行框架。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/constraineradapter-usage-diagram.zh-tw.mmd" >}}

> **圖例：**
> - 淺紫色框：ConstrainerAdapter 主類別
> - 藍色框：核心約束模組
> - 紫色框：各類約束處理器
> - `..>`：依賴關係
> - `-->`：管理關係

## 主要功能

- 統一的約束處理介面
- 自動轉換 YAML 配置格式
- 支援兩種約束模式：
  - 簡單約束：直接過濾資料
  - 重採樣約束：重複生成直到滿足條件
- 整合 Synthesizer 與 Postprocessor
- 自動處理欄位組合規則格式

## 方法參考

### `__init__(config: dict)`

初始化 ConstrainerAdapter 實例。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - **配置方式（二選一）：**
    1. **使用 YAML 檔案（推薦）：**
       - `constraints_yaml`：str - YAML 檔案路徑，包含所有約束配置
    2. **使用個別參數：**
       - `nan_groups`：空值處理規則
       - `field_constraints`：欄位約束條件
       - `field_combinations`：欄位組合規則
       - `field_proportions`：欄位比例維護規則
  - 重採樣參數（可選，與兩種配置方式兼容）：
    - `target_rows`：目標列數
    - `sampling_ratio`：採樣比例（預設 10.0）
    - `max_trials`：最大嘗試次數（預設 300）
    - `verbose_step`：進度顯示頻率（預設 10）

**注意：** `constraints_yaml` 與個別約束參數（nan_groups, field_constraints 等）不能同時使用，否則會引發 [`ConfigError`](../../exceptions)。

### `run(input: dict)`

執行約束處理。

**參數：**
- `input`：dict，必要
  - 輸入參數字典
  - 必要欄位：
    - `data`：pd.DataFrame - 要約束的資料
  - 可選欄位：
    - `synthesizer`：Synthesizer - 用於重採樣
    - `postprocessor`：Postprocessor - 用於資料還原

**回傳：**
無直接回傳值。使用 `get_result()` 取得結果。

### `get_result()`

取得約束處理後的資料。

**回傳：**
- `pd.DataFrame`：符合約束條件的資料

## 使用範例

### 方式 1：使用 YAML 檔案（推薦）

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# 使用 YAML 檔案配置
config = {
    'constraints_yaml': 'config/constraints.yaml',
    # 可選：重採樣參數
    'target_rows': 1000,
    'sampling_ratio': 10.0
}

adapter = ConstrainerAdapter(config)

# 準備輸入
input_data = {
    'data': df
}

# 執行約束
adapter.run(input_data)

# 取得結果
constrained_data = adapter.get_result()
```

**constraints.yaml 範例：**
```yaml
nan_groups:
  workclass: delete
  
field_constraints:
  - "age >= 18 & age <= 65"
  - "hours_per_week >= 1 & hours_per_week <= 99"

field_combinations:
  -
    - education: workclass
    - Doctorate: [Prof-specialty, Exec-managerial]
```

### 方式 2：使用個別參數

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# 直接在程式碼中指定約束配置
config = {
    'nan_groups': {
        'workclass': 'delete'
    },
    'field_constraints': [
        "age >= 18 & age <= 65"
    ]
}

adapter = ConstrainerAdapter(config)

# 準備輸入
input_data = {
    'data': df
}

# 執行約束
adapter.run(input_data)

# 取得結果
constrained_data = adapter.get_result()
```

### 使用重採樣

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# 包含重採樣參數的配置
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",
        "salary >= 60000"
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [80000, 90000, 100000]}
        )
    ],
    # 重採樣參數
    'target_rows': 1000,
    'sampling_ratio': 20.0,
    'max_trials': 100,
    'verbose_step': 10
}

adapter = ConstrainerAdapter(config)

# 準備輸入（包含 synthesizer）
input_data = {
    'data': initial_data,
    'synthesizer': synthesizer,  # 已訓練的 Synthesizer 實例
    'postprocessor': postprocessor  # 可選
}

# 執行重採樣約束
adapter.run(input_data)

# 取得結果
result = adapter.get_result()
print(f"最終列數: {len(result)}")
```

### 完整工作流程範例

```python
from petsard.adapter import (
    LoaderAdapter,
    PreprocessorAdapter,
    SynthesizerAdapter,
    PostprocessorAdapter,
    ConstrainerAdapter
)

# 1. 載入資料
loader_config = {'filepath': 'data.csv'}
loader = LoaderAdapter(loader_config)
loader.run({})
data = loader.get_result()
schema = loader.get_metadata()

# 2. 前處理
preprocessor_config = {'method': 'default'}
preprocessor = PreprocessorAdapter(preprocessor_config)
preprocessor.run({'data': data, 'metadata': schema})
processed_data = preprocessor.get_result()

# 3. 合成
synthesizer_config = {'method': 'default', 'sample_num_rows': 1000}
synthesizer = SynthesizerAdapter(synthesizer_config)
synthesizer.run({'data': processed_data, 'metadata': schema})
synthetic_data = synthesizer.get_result()

# 4. 後處理
postprocessor_config = {'method': 'default'}
postprocessor = PostprocessorAdapter(postprocessor_config)
postprocessor.run({
    'data': synthetic_data,
    'preprocessor': preprocessor.processor
})
postprocessed_data = postprocessor.get_result()

# 5. 約束處理
constrainer_config = {
    'field_constraints': [
        "age >= 18 & age <= 65"
    ],
    'field_proportions': [
        {'fields': 'category', 'mode': 'all', 'tolerance': 0.1}
    ],
    # 重採樣參數
    'target_rows': 800,
    'sampling_ratio': 15.0
}

constrainer = ConstrainerAdapter(constrainer_config)
constrainer.run({
    'data': postprocessed_data,
    'synthesizer': synthesizer.synthesizer,
    'postprocessor': postprocessor.processor
})

# 取得最終結果
final_data = constrainer.get_result()
print(f"最終資料列數: {len(final_data)}")
```

## 工作流程

### 簡單約束模式

```
輸入資料
  ↓
套用約束條件
  ↓
返回符合條件的資料
```

### 重採樣約束模式

```
輸入資料
  ↓
套用約束條件
  ↓
資料量足夠? ──是──> 返回結果
  ↓ 否
迭代開始
  ↓
使用 Synthesizer 生成新資料
  ↓
使用 Postprocessor 還原資料（如有）
  ↓
套用約束條件
  ↓
累積符合條件的資料
  ↓
達到目標? ──是──> 返回結果
  ↓ 否
未達最大嘗試次數? ──是──> 繼續迭代
  ↓ 否
返回已收集的資料（警告）
```

## 配置轉換

ConstrainerAdapter 會自動轉換 YAML 配置格式：

### field_combinations 轉換

YAML 配置中的列表格式會自動轉換為元組：

```yaml
# YAML 格式
field_combinations:
  -
    - education: income
    - Doctorate: ['>50K']
```

轉換為：

```python
# Python 格式
field_combinations = [
    (
        {'education': 'income'},
        {'Doctorate': ['>50K']}
    )
]
```

## 約束模式選擇

### 使用簡單約束（apply）的情況

- 資料已足夠多
- 約束條件不太嚴格
- 不需要重複生成資料
- 配置中**未包含** `target_rows`、`synthesizer` 等重採樣參數

```python
config = {
    'field_constraints': ["age >= 18"]
}
# 只會過濾資料，不會重新生成
```

### 使用重採樣約束（resample_until_satisfy）的情況

- 需要特定數量的資料
- 約束條件嚴格，過濾後資料不足
- 配置中**包含**重採樣參數
- 輸入中**包含** `synthesizer`

```python
config = {
    'field_constraints': ["age >= 18"],
    'target_rows': 1000,
    'sampling_ratio': 20.0
}
input_data = {
    'data': df,
    'synthesizer': trained_synthesizer  # 關鍵：提供 synthesizer
}
# 會重複生成直到達到 1000 列
```

## 輸入資料來源

ConstrainerAdapter 會自動從前一個模組取得資料：

| 前置模組 | 資料來源 |
|---------|---------|
| Splitter | `train` 資料 |
| Loader | 完整資料 |
| Preprocessor | 前處理後的資料 |
| Synthesizer | 合成資料 |
| Postprocessor | 後處理後的資料 |

## 注意事項

- **內部 API**：這是內部 API，不建議直接使用
- **建議作法**：使用 YAML 配置檔和 Executor
- **約束順序**：依序套用 nan_groups → field_constraints → field_combinations → field_proportions
- **Synthesizer 要求**：使用重採樣時，synthesizer 必須已透過 `fit()` 訓練
- **記憶體考量**：大 sampling_ratio 會消耗較多記憶體
- **結果快取**：結果會快取直到下次 run() 呼叫
- **自動轉換**：field_combinations 會自動從列表格式轉換為元組格式
- **AND 邏輯**：所有約束條件以 AND 組合

## 錯誤處理

### 配置錯誤

```python
# 錯誤：config 為 None
adapter = ConstrainerAdapter(None)
# 引發 ConfigError

# 錯誤：同時使用 constraints_yaml 和個別參數
config = {
    'constraints_yaml': 'constraints.yaml',
    'nan_groups': {'age': 'delete'}  # 衝突！
}
adapter = ConstrainerAdapter(config)
# 引發 ConfigError: Cannot specify both 'constraints_yaml' and individual constraint parameters

# 錯誤：YAML 檔案不存在
config = {'constraints_yaml': 'non_existent.yaml'}
adapter = ConstrainerAdapter(config)
# 引發 ConfigError: Constraints YAML file not found

# 錯誤：field_combinations 格式錯誤
config = {
    'field_combinations': 'invalid'  # 應為列表
}
# 引發驗證錯誤
```

### 執行錯誤

```python
# 錯誤：使用重採樣但未提供 synthesizer
config = {'target_rows': 1000}
adapter = ConstrainerAdapter(config)
adapter.run({'data': df})  # 缺少 synthesizer
# 無法重採樣，只能使用簡單過濾

# 錯誤：synthesizer 未訓練
adapter.run({
    'data': df,
    'synthesizer': untrained_synthesizer  # 未呼叫 fit()
})
# 引發錯誤
```

## 效能考量

### 約束條件複雜度

- **簡單條件**：`age >= 18`（快速）
- **中等條件**：`age >= 18 & salary > 50000`（中等）
- **複雜條件**：多重巢狀括號、多個組合規則（較慢）

### 重採樣效能

影響重採樣效能的因素：

1. **約束嚴格度**：越嚴格需要越多次迭代
2. **sampling_ratio**：越大每次生成越多資料
3. **target_rows**：目標越大需要越多時間
4. **Synthesizer 速度**：依使用的合成方法而異

### 最佳化建議

```python
# 1. 調整 sampling_ratio
# 約束不嚴格：使用較小值（5-10）
# 約束嚴格：使用較大值（20-50）
config = {
    'sampling_ratio': 20.0  # 根據約束嚴格度調整
}

# 2. 設定合理的 max_trials
config = {
    'max_trials': 100  # 避免無限循環
}

# 3. 使用 verbose_step 監控進度
config = {
    'verbose_step': 10  # 每 10 次顯示進度
}
```