---
title: "Executor YAML（更新中）"
weight: 50
---

Executor 模組的 YAML 設定檔案格式，負責協調整個 PETsARD 工作流程的執行。

## 基本使用

```python
from petsard import Executor

# 使用 YAML 配置檔
exec = Executor(config='config.yaml')
exec.run()

# 取得結果
results = exec.get_result()
timing = exec.get_timing()
```

## 主要參數

Executor 支援在 YAML 檔案中設定執行相關的配置選項：

```yaml
Executor:
  log_output_type: "both"    # 日誌輸出位置
  log_level: "INFO"          # 日誌等級
  log_dir: "./logs"          # 日誌檔案目錄
  log_filename: "PETsARD_{timestamp}.log"  # 日誌檔案名稱模板
```

### 參數說明

- **log_output_type** (`string`, 選填)
  - 日誌輸出位置
  - 可選值：
    - `"stdout"`：輸出到終端機
    - `"file"`：輸出到檔案（預設）
    - `"both"`：同時輸出到終端機和檔案
  - 預設值：`"file"`

- **log_level** (`string`, 選填)
  - 日誌等級
  - 可選值：`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`
  - 預設值：`"INFO"`

- **log_dir** (`string`, 選填)
  - 日誌檔案儲存目錄
  - 預設值：`"."`（當前目錄）

- **log_filename** (`string`, 選填)
  - 日誌檔案名稱模板
  - 支援 `{timestamp}` 佔位符，會自動替換為執行時間
  - 預設值：`"PETsARD_{timestamp}.log"`

## 完整配置範例

```yaml
# Executor 設定（選填）
Executor:
  log_output_type: "both"
  log_level: "DEBUG"
  log_dir: "./logs"
  log_filename: "experiment_{timestamp}.log"

# 資料載入
Loader:
  load_data:
    filepath: benchmark://adult-income

# 資料分割
Splitter:
  split_data:
    train_split_ratio: 0.8
    num_samples: 3

# 資料合成
Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula

# 資料評測
Evaluator:
  evaluate:
    method: sdmetrics-qualityreport

# 結果報告
Reporter:
  save_results:
    method: save_data
    source: Synthesizer
```

## 執行流程

Executor 會按照以下順序執行各模組：

1. **Loader**：載入資料
2. **Preprocessor**（選填）：資料前處理
3. **Splitter**（選填）：資料分割
4. **Synthesizer**：資料合成
5. **Postprocessor**（選填）：資料後處理
6. **Constrainer**（選填）：約束條件套用
7. **Evaluator**（選填）：資料評測
8. **Reporter**（選填）：結果報告

## 注意事項

- **Executor 區段位置**：`Executor` 區段可以放在 YAML 檔案的任何位置，不影響功能
- **選填參數**：所有 Executor 參數都是選填的，不設定時使用預設值
- **日誌檔案**：使用 `file` 或 `both` 模式時，會自動建立日誌目錄
- **時間戳格式**：`{timestamp}` 會替換為 `YYYY-MM-DD_HH-MM-SS` 格式
- **模組順序**：Executor 會自動按照正確的順序執行各模組，不需要手動指定