---
title: "Status API"
type: docs
weight: 1030
---

Status 是 PETsARD 的內部狀態管理模組，負責追蹤工作流程執行、儲存結果、管理詮釋資料（Schema），並建立執行快照。

{{< callout type="info" >}}
**僅供內部使用**：Status 主要由 Executor 內部使用。使用者應透過 [`Executor`](../executor-api/) 方法存取 Status 功能。
{{< /callout >}}

## 類別架構

{{< mermaid-file file="content/docs/python-api/status-api/status-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 淺紫框：資料類別與輔助類別
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 基本使用

```python
from petsard import Executor

# Status 由 Executor 內部建立和管理
exec = Executor('config.yaml')
exec.run()

# 透過 Executor 方法存取 Status 功能
results = exec.get_result()        # Status.get_result()
timing = exec.get_timing()         # Status.get_timing_report_data()

# 進階：直接存取 Status
summary = exec.status.get_status_summary()
snapshots = exec.status.get_snapshots()
```

## 建構函式

### 語法

```python
Status(config: Config, max_snapshots: int = 1000, max_changes: int = 5000, max_timings: int = 10000)
```

### 參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|------|------|--------|--------|------|
| `config` | `Config` | 必要 | - | 包含模組序列和執行配置的 Config 物件 |
| `max_snapshots` | `int` | 選填 | `1000` | 保留的最大快照數量 |
| `max_changes` | `int` | 選填 | `5000` | 最大變更記錄數量 |
| `max_timings` | `int` | 選填 | `10000` | 最大時間記錄數量 |

### 返回值

返回已初始化狀態管理的 Status 實例。

## 核心功能

### 1. 執行結果追蹤

Status 會記錄每個模組的執行結果：

```python
# 由 Executor 自動呼叫
# status.put(module, experiment, adapter)

# 透過 Executor 取得結果
results = exec.get_result()
```

### 2. 詮釋資料管理

追蹤資料 Schema 在各模組間的變化：

```python
# 取得特定模組的 Schema
loader_schema = exec.status.get_metadata('Loader')
print(f"欄位數：{len(loader_schema.attributes)}")
```

### 3. 執行快照

在每個模組執行前後建立快照：

```python
# 取得所有快照
snapshots = exec.status.get_snapshots()

for snapshot in snapshots:
    print(f"{snapshot.module_name}[{snapshot.experiment_name}]")
    print(f"  時間：{snapshot.timestamp}")
```

### 4. 時間記錄

收集執行時間資訊：

```python
# 取得時間報告
timing_df = exec.get_timing()
print(timing_df)
```

## 主要方法

### 狀態管理方法

| 方法 | 說明 |
|------|------|
| `put(module, experiment, adapter)` | 記錄模組執行狀態 |
| `get_result(module)` | 取得模組執行結果 |
| `get_metadata(module)` | 取得模組 Schema |
| `get_full_expt(module)` | 取得實驗配置字典 |

### 快照與追蹤方法

| 方法 | 說明 |
|------|------|
| `get_snapshots(module)` | 取得執行快照 |
| `get_snapshot_by_id(snapshot_id)` | 透過 ID 取得特定快照 |
| `get_change_history(module)` | 取得變更歷史 |
| `get_metadata_evolution(module)` | 追蹤 Schema 演進 |

### 報告方法

| 方法 | 說明 |
|------|------|
| `get_timing_report_data()` | 取得時間報告為 DataFrame |
| `get_status_summary()` | 取得狀態摘要 |

## 資料類別

### ExecutionSnapshot

執行快照的不可變記錄：

```python
@dataclass(frozen=True)
class ExecutionSnapshot:
    snapshot_id: str
    module_name: str
    experiment_name: str
    timestamp: datetime
    metadata_before: Schema | None = None
    metadata_after: Schema | None = None
    context: dict[str, Any] = field(default_factory=dict)
```

### TimingRecord

時間資訊的不可變記錄：

```python
@dataclass(frozen=True)
class TimingRecord:
    record_id: str
    module_name: str
    experiment_name: str
    step_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    context: dict[str, Any] = field(default_factory=dict)
```

## 與 Executor 整合

Status 主要透過 Executor 使用：

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 透過 Executor 存取 Status 功能
results = exec.get_result()          # → status.get_result()
timing = exec.get_timing()           # → status.get_timing_report_data()

# 進階：直接存取 Status
summary = exec.status.get_status_summary()
snapshots = exec.status.get_snapshots()
```

## Schema 推論

Status 支援 Schema 推論功能：

```python
from petsard import Executor

exec = Executor('config.yaml')  # 包含 Preprocessor
exec.run()

# 取得推論的 Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    print(f"推論的 Schema：{inferred_schema.id}")
```

## 狀態摘要

取得完整的執行狀態摘要：

```python
summary = exec.status.get_status_summary()

print(f"模組序列：{summary['sequence']}")
print(f"活躍模組：{summary['active_modules']}")
print(f"總快照數：{summary['total_snapshots']}")
print(f"總變更數：{summary['total_changes']}")
```

## 注意事項

- **內部使用**：Status 主要由 Executor 內部使用
- **建議作法**：透過 Executor 的方法存取 Status 功能
- **自動追蹤**：執行過程中自動記錄快照和變更
- **記憶體管理**：長時間執行會累積較多快照
- **不可變性**：快照和變更記錄是不可變的
- **進階功能**：直接存取 Status 需要了解內部機制