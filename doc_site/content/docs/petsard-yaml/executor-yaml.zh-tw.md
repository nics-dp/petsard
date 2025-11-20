---
title: "Executor YAML"
type: docs
weight: 610
prev: docs/petsard-yaml
next: docs/petsard-yaml/loader-yaml
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

## Executor 參數

Executor 支援在 YAML 檔案中設定執行相關的配置選項：

```yaml
Executor:
  log_output_type: "both"
  log_level: "INFO"
  log_dir: "./logs"
  log_filename: "PETsARD_{timestamp}.log"
```

### 參數說明

- **log_output_type** (`string`, 選填)：日誌輸出位置 - `"stdout"`, `"file"`, 或 `"both"`（預設：`"file"`）
- **log_level** (`string`, 選填)：日誌等級 - `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, 或 `"CRITICAL"`（預設：`"INFO"`）
- **log_dir** (`string`, 選填)：日誌檔案儲存目錄（預設：`"."`）
- **log_filename** (`string`, 選填)：日誌檔案名稱模板，支援 `{timestamp}` 佔位符（預設：`"PETsARD_{timestamp}.log"`）

## 執行流程

Executor 會按照以下順序執行各模組：

1. **Loader** → 2. **Preprocessor**（選填）→ 3. **Splitter**（選填）→ 4. **Synthesizer** → 5. **Postprocessor**（選填）→ 6. **Constrainer**（選填）→ 7. **Evaluator**（選填）→ 8. **Reporter**（選填）

## 內部機制

### Config

{{< callout type="info" >}}
Config 由 Executor 自動管理。設定各模組的 YAML 配置，即是在設定 Config。
{{< /callout >}}

**核心功能**：
- 自動安排模組執行順序
- 驗證實驗命名（不可使用 `_[xxx]` 模式）
- 當 `num_samples > 1` 時自動展開 Splitter
- 為多實驗配置產生笛卡爾積

### Status

{{< callout type="info" >}}
Status 由 Executor 自動管理。不需要 YAML 配置 - 所有追蹤都是自動進行的。
{{< /callout >}}

**自動追蹤**：
- 每個模組的執行結果
- 各模組間的 Schema 詮釋資料變化
- 每個模組執行前後的快照
- 每個模組和步驟的執行時間

**存取方法**：
- `exec.get_result()` - 取得執行結果
- `exec.get_timing()` - 取得執行時間
- `exec.is_execution_completed()` - 檢查執行狀態

## 注意事項

- `Executor` 區段可以放在 YAML 檔案的任何位置
- 所有 Executor 參數都是選填的
- 模組執行順序由系統自動決定
- Config 和 Status 是內部機制，完全由 Executor 管理