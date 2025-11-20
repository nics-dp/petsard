---
title: "儲存時間資訊"
type: docs
weight: 705
prev: docs/petsard-yaml/reporter-yaml/save-validation
next: docs/petsard-yaml/reporter-yaml
---

使用 `save_timing` 方法記錄各模組的執行時間，用於效能分析和優化。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-timing.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: default

Synthesizer:
  default:
    method: default

  petsard-gaussian-copula:
    method: petsard-gaussian-copula

Postprocessor:
  default:
    method: default

Reporter:
  save_all_timing:
    method: save_timing  # 必要：固定為 save_timing
    # time_unit: seconds # 選用：時間單位（預設：seconds）
    # module:            # 選用：指定要記錄的模組
    #   - Synthesizer
    #   - Evaluator
    # output: petsard    # 選用：輸出檔案名稱前綴（預設：petsard）
```

## 主要參數

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 固定為 `save_timing` | `save_timing` |

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `time_unit` | `string` | `seconds` | 時間單位：`seconds`、`minutes`、`hours`、`days` | `minutes` |
| `module` | `string` 或 `list` | 全部模組 | 指定要記錄的模組 | `["Synthesizer", "Evaluator"]` |
| `output` | `string` | `petsard` | 輸出檔案名稱前綴 | `timing_analysis` |

#### time_unit 參數詳細說明

`time_unit` 參數用於指定時間顯示單位，支援以下選項：`seconds`（秒）、`minutes`（分鐘）、`hours`（小時）、`days`（天）。

#### module 參數詳細說明

`module` 參數用於過濾要記錄的模組，可指定單一模組或多個模組列表。

## 輸出格式

時間資訊會儲存為 CSV 格式，每筆記錄包含以下欄位：

| 欄位 | 說明 | 範例 |
|------|------|------|
| `record_id` | 記錄唯一識別碼 | `timing_000001_20251017_112722` |
| `module_name` | 模組名稱 | `SynthesizerAdapter` |
| `experiment_name` | 實驗名稱 | `default` |
| `step_name` | 執行步驟 | `run` |
| `start_time` | 開始時間（ISO 8601） | `2025-10-17T11:27:22.182237` |
| `end_time` | 結束時間（ISO 8601） | `2025-10-17T11:27:22.328833` |
| `duration_seconds` | 執行時間（秒） | `0.15` |
| `source` | 資料來源 | `logging` |
| `status` | 執行狀態 | `completed` |

**範例輸出：**
```csv
record_id,module_name,experiment_name,step_name,start_time,end_time,duration_seconds,source,status
timing_000001_20251017_112722,LoaderAdapter,default,run,2025-10-17T11:27:22.182237,2025-10-17T11:27:22.328833,0.15,logging,completed
timing_000004_20251017_112722,SynthesizerAdapter,default,run,2025-10-17T11:27:22.630578,2025-10-17T11:27:24.672193,2.04,logging,completed
timing_000010_20251017_112725,EvaluatorAdapter,default,run,2025-10-17T11:27:25.623084,2025-10-17T11:27:30.833015,5.21,logging,completed
```

## 關鍵欄位說明

- **duration_seconds**：執行時間（秒），使用 `time_unit` 參數可改變顯示單位
- **module_name**：實際執行的適配器名稱（如 `LoaderAdapter`、`SynthesizerAdapter`）
- **start_time / end_time**：精確記錄開始與結束的時間戳記

## 注意事項

- CSV 輸出保留 2 位小數
- 同名檔案會被覆寫
- 系統負載和資料大小會影響執行時間