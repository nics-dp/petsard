---
title: "Status 狀態追蹤"
weight: 52
---

Status 負責追蹤整個工作流程的執行狀態，提供完整的執行歷史、結果儲存和詮釋資料（Schema）管理。

## 概述

Status 是 Executor 內部使用的狀態管理系統，**不需要在 YAML 中配置**。它會自動：

- 記錄每個模組的執行結果
- 追蹤詮釋資料（Schema）的變化
- 建立執行快照以供恢復
- 收集執行時間資訊

## 自動狀態追蹤

當 Executor 執行時，Status 會自動記錄：

### 1. 執行結果

每個模組執行後，結果會自動儲存到 Status 中：

```python
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# 透過 Executor 取得結果
results = exec.get_result()
print(results)
```

### 2. 詮釋資料追蹤

Status 會追蹤資料的 Schema 在各模組間的變化：

```yaml
# config.yaml
Loader:
  load_data:
    filepath: data.csv

Preprocessor:
  preprocess:
    method: default

Synthesizer:
  generate:
    method: sdv
```

執行過程中，Status 會記錄：
- Loader 載入後的原始 Schema
- Preprocessor 處理後的 Schema 變化
- Synthesizer 可用的 Schema 資訊

### 3. 執行快照

每個模組執行前後都會建立快照，包含：
- 執行時間戳
- 模組名稱和實驗名稱
- 詮釋資料狀態（執行前/執行後）
- 執行上下文資訊

### 4. 時間記錄

自動收集每個模組和步驟的執行時間：

```python
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# 取得時間報告
timing = exec.get_timing()
print(timing)
```

## 透過 Executor 取得狀態

Status 的所有資訊都可以透過 Executor 的方法取得：

### 取得執行結果

```python
# 取得所有結果
results = exec.get_result()

# 結果格式
# {
#   'Loader[load_data]_Synthesizer[generate]': {
#     'data': DataFrame,
#     'schema': Schema
#   }
# }
```

### 取得執行時間

```python
# 取得時間資訊
timing_df = exec.get_timing()

# DataFrame 欄位：
# - record_id: 記錄 ID
# - module_name: 模組名稱
# - experiment_name: 實驗名稱
# - step_name: 執行步驟
# - start_time: 開始時間
# - end_time: 結束時間
# - duration_seconds: 執行時間（秒）
```

### 檢查執行狀態

```python
# 檢查是否執行完成
if exec.is_execution_completed():
    print("執行完成")
    results = exec.get_result()
else:
    print("執行中或尚未執行")
```

## 多實驗結果管理

當配置包含多個實驗時，Status 會管理所有組合的結果：

### 配置範例

```yaml
Loader:
  load_v1:
    filepath: data_v1.csv
  load_v2:
    filepath: data_v2.csv

Synthesizer:
  method_a:
    method: sdv
    model: GaussianCopula
  method_b:
    method: sdv
    model: CTGAN

Reporter:
  save_all:
    method: save_data
    source: Synthesizer
```

### 結果組織

```python
results = exec.get_result()

# 結果包含所有實驗組合：
# {
#   'Loader[load_v1]_Synthesizer[method_a]_Reporter[save_all]': {...},
#   'Loader[load_v1]_Synthesizer[method_b]_Reporter[save_all]': {...},
#   'Loader[load_v2]_Synthesizer[method_a]_Reporter[save_all]': {...},
#   'Loader[load_v2]_Synthesizer[method_b]_Reporter[save_all]': {...}
# }
```

## Schema 推論和追蹤

Status 提供 Schema 推論功能，特別是在使用 Preprocessor 時：

### 自動 Schema 推論

```yaml
Loader:
  load_data:
    filepath: data.csv

Preprocessor:
  preprocess:
    scaling:
      age: minmax
      income: standard
    encoding:
      education: onehot

Synthesizer:
  generate:
    method: sdv
```

執行流程：
1. Loader 載入資料後，Status 記錄原始 Schema
2. Executor 根據 Preprocessor 配置推論處理後的 Schema
3. Synthesizer 使用推論的 Schema 進行合成
4. 整個過程的 Schema 變化都被追蹤記錄

## 執行快照

Status 在執行過程中會建立多個快照：

### 快照內容

每個快照包含：
- **快照 ID**：唯一識別碼
- **模組資訊**：模組名稱和實驗名稱
- **時間戳**：建立時間
- **詮釋資料**：執行前後的 Schema 狀態
- **執行上下文**：相關的配置和參數

### 快照用途

- **除錯**：檢查執行過程中的狀態變化
- **稽核**：追蹤資料處理的完整歷史
- **恢復**：在需要時恢復到特定狀態

## 變更追蹤

Status 會記錄詮釋資料的所有變更：

### 追蹤內容

- **變更類型**：建立、更新、刪除
- **變更目標**：Schema 或 Field 層級
- **變更前後**：狀態對比
- **變更時間**：發生時間戳
- **模組上下文**：哪個模組造成的變更

### 變更範例

```
Loader → Preprocessor：
- age: numerical → numerical (minmax scaled)
- education: categorical → categorical (onehot encoded)
- income: numerical → numerical (standard scaled)
```

## 狀態摘要

取得執行狀態的完整摘要：

```python
# 透過 Python API 直接存取（進階用法）
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# 取得狀態摘要
summary = exec.status.get_status_summary()

# 摘要包含：
# - sequence: 模組執行序列
# - active_modules: 已執行的模組
# - metadata_modules: 具有詮釋資料的模組
# - total_snapshots: 總快照數
# - total_changes: 總變更記錄數
# - last_snapshot: 最新快照 ID
# - last_change: 最新變更 ID
```

## 注意事項

- **自動管理**：Status 完全由 Executor 自動管理，不需要在 YAML 中配置
- **結果獲取**：使用 `exec.get_result()` 和 `exec.get_timing()` 取得狀態資訊
- **記憶體使用**：長時間執行的工作流程會累積較多快照，Status 會自動管理記憶體
- **快照數量**：每個模組執行會產生一個快照，大量實驗組合會產生相應數量的快照
- **進階功能**：完整的 Status API 請參考 Python API 文檔