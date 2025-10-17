---
title: "ReporterAdapter"
weight: 7
---

ReporterAdapter 處理結果輸出與報告產生，包裝 Reporter 模組以提供統一的管線介面。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/reporteradapter-usage-diagram.zh-tw.mmd" >}}

> **圖例：**
> - 淺紫色框：ReporterAdapter 主類別
> - 藍色框：Reporter 工廠類別
> - 綠色框：具體報告器實作
> - 淺粉色框：配置類別
> - `-->`：擁有關係
> - `..>`：依賴關係

## 主要功能

- 統一的報告產生介面
- 支援多種報告方法（資料儲存、評估報告、時間資訊）
- 自動處理檔名生成與命名策略
- 整合管線狀態以自動收集報告資料
- 支援多粒度報告產生

## 方法參考

### `__init__(config: dict)`

初始化 ReporterAdapter 實例。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 必須包含 `method` 鍵
  - 根據方法需要不同的額外參數：
    - **save_data**：需要 `source` 參數
    - **save_report**：需要 `granularity` 參數
    - **save_timing**：可選 `time_unit` 和 `module` 參數
    - **save_validation**：無額外必要參數
  - 可選參數：
    - `output`：輸出檔案名稱前綴（預設：'petsard'）
    - `naming_strategy`：命名策略（'traditional' 或 'compact'）

### `run(input: dict)`

執行報告產生操作。

**參數：**
- `input`：dict，必要
  - 從管線狀態收集的資料
  - 通常由 `set_input()` 方法自動設定
  - 包含要報告的實驗結果

**回傳：**
無直接回傳值。報告檔案會直接儲存到磁碟。

### `set_input(status)`

從管線狀態自動收集要報告的資料。

**參數：**
- `status`：Status 物件
  - 管線執行狀態
  - 包含所有模組的執行結果

**回傳：**
- `dict`：準備用於報告的資料字典

### `get_result()`

取得報告產生的結果資料。

**回傳：**
- `dict | pd.DataFrame | None`：處理後的報告資料
  - save_data：DataFrame 字典
  - save_report：粒度結果字典
  - save_timing：時間資訊 DataFrame
  - save_validation：驗證結果字典

## 使用範例

### 儲存合成資料

```python
from petsard.adapter import ReporterAdapter

# 儲存合成資料
adapter = ReporterAdapter({
    "method": "save_data",
    "source": "Synthesizer",
    "output": "my_experiment"
})

# 從狀態設定輸入
input_data = adapter.set_input(status)

# 執行報告產生
adapter.run(input_data)
# 輸出：my_experiment_Synthesizer[exp1].csv
```

### 產生評估報告（單一粒度）

```python
from petsard.adapter import ReporterAdapter

# 產生全域評估報告
adapter = ReporterAdapter({
    "method": "save_report",
    "granularity": "global",
    "output": "evaluation_results"
})

# 執行
input_data = adapter.set_input(status)
adapter.run(input_data)
# 輸出：evaluation_results[Report]_eval1_[global].csv
```

### 產生評估報告（多重粒度）

```python
from petsard.adapter import ReporterAdapter

# 產生多粒度評估報告
adapter = ReporterAdapter({
    "method": "save_report",
    "granularity": ["global", "columnwise", "details"],
    "naming_strategy": "compact"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# 輸出：
# - petsard_eval1_global.csv
# - petsard_eval1_columnwise.csv
# - petsard_eval1_details.csv
```

### 儲存時間資訊

```python
from petsard.adapter import ReporterAdapter

# 儲存特定模組的時間資訊
adapter = ReporterAdapter({
    "method": "save_timing",
    "time_unit": "minutes",
    "module": ["Loader", "Synthesizer"],
    "output": "timing_analysis"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# 輸出：timing_analysis_timing_report.csv
```

### 使用簡化命名策略

```python
from petsard.adapter import ReporterAdapter

# 使用簡化命名
adapter = ReporterAdapter({
    "method": "save_data",
    "source": ["Synthesizer"],
    "naming_strategy": "compact",
    "output": "results"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# 輸出：results_Synthesizer_exp1.csv（更簡潔的檔名）
```

## 配置參數詳細說明

### 通用參數

| 參數 | 類型 | 必要 | 預設值 | 說明 |
|------|------|------|--------|------|
| `method` | `string` | 是 | - | 報告方法：'save_data'、'save_report'、'save_timing'、'save_validation' |
| `output` | `string` | 否 | `'petsard'` | 輸出檔案名稱前綴 |
| `naming_strategy` | `string` | 否 | `'traditional'` | 命名策略：'traditional' 或 'compact' |

### save_data 方法專用

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `source` | `string\|list` | 是 | 目標模組名稱（如 'Synthesizer'） |

### save_report 方法專用

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `granularity` | `string\|list` | 是 | 報告粒度：'global'、'columnwise'、'pairwise'、'details'、'tree' |
| `eval` | `string\|list` | 否 | 過濾特定評估實驗 |

### save_timing 方法專用

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `time_unit` | `string` | 否 | 時間單位：'seconds'、'minutes'、'hours'、'days' |
| `module` | `string\|list` | 否 | 過濾特定模組 |

## 工作流程

1. **初始化**：創建 ReporterAdapter 並設定配置
2. **收集資料**：`set_input()` 從管線狀態收集相關資料
3. **處理資料**：Reporter 內部處理並格式化資料
4. **產生報告**：將資料寫入 CSV 檔案
5. **回傳結果**：透過 `get_result()` 提供處理後的資料

## 命名策略

### Traditional 策略（預設）

保持向後相容，使用詳細的命名格式：
- `petsard_Synthesizer[exp1].csv`
- `petsard[Report]_eval1_[global].csv`

### Compact 策略

使用簡化命名，更易讀：
- `petsard_Synthesizer_exp1.csv`
- `petsard_eval1_global.csv`

## 與管線整合

ReporterAdapter 通常作為管線的最後階段，收集並輸出結果：

```python
from petsard.config import Config
from petsard.executor import Executor

config_dict = {
    "Loader": {
        "load_data": {"filepath": "data.csv"}
    },
    "Synthesizer": {
        "synth": {"method": "default"}
    },
    "Evaluator": {
        "eval": {"method": "default"}
    },
    "Reporter": {
        # 儲存合成資料
        "save_synthetic": {
            "method": "save_data",
            "source": "Synthesizer"
        },
        # 產生評估報告
        "save_evaluation": {
            "method": "save_report",
            "granularity": ["global", "columnwise"]
        },
        # 儲存時間資訊
        "save_timing": {
            "method": "save_timing",
            "time_unit": "minutes"
        }
    }
}

config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 報告檔案儲存在當前工作目錄
- 同名檔案會被覆寫
- 多粒度報告會產生多個檔案
- `set_input()` 會自動從管線狀態收集資料
- CSV 檔案使用 UTF-8 編碼

## 相關文件

- Reporter Python API：Reporter 模組詳細說明
- Reporter YAML：YAML 配置說明
- Adapter 概覽：所有 Adapter 的概覽