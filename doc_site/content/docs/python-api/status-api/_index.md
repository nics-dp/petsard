---
title: "Status API"
type: docs
weight: 1030
---

Status is PETsARD's internal state management module, responsible for tracking workflow execution, storing results, managing metadata (Schema), and creating execution snapshots.

{{< callout type="info" >}}
**Internal Use Only**: Status is primarily used internally by Executor. Users should access Status functionality through [`Executor`](../executor-api/) methods.
{{< /callout >}}

## Class Architecture

{{< mermaid-file="status-class-diagram.mmd" >}}

## Basic Usage

```python
from petsard import Executor

# Status is created and managed internally by Executor
exec = Executor('config.yaml')
exec.run()

# Access Status functionality through Executor methods
results = exec.get_result()        # Status.get_result()
timing = exec.get_timing()         # Status.get_timing_report_data()

# Advanced: Direct Status access
summary = exec.status.get_status_summary()
snapshots = exec.status.get_snapshots()
```

## Constructor

### Syntax

```python
Status(config: Config, max_snapshots: int = 1000, max_changes: int = 5000, max_timings: int = 10000)
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `config` | `Config` | Yes | - | Config object containing module sequence and execution configuration |
| `max_snapshots` | `int` | No | `1000` | Maximum number of snapshots to retain |
| `max_changes` | `int` | No | `5000` | Maximum number of change records |
| `max_timings` | `int` | No | `10000` | Maximum number of timing records |

### Return Value

Returns a Status instance with initialized state management.

## Core Functionality

### 1. Execution Result Tracking

Status records execution results for each module:

```python
# Automatically called by Executor
# status.put(module, experiment, adapter)

# Get results through Executor
results = exec.get_result()
```

### 2. Metadata Management

Tracks Schema changes across modules:

```python
# Get Schema for specific module
loader_schema = exec.status.get_metadata('Loader')
print(f"Number of fields: {len(loader_schema.attributes)}")
```

### 3. Execution Snapshots

Creates snapshots before and after each module execution:

```python
# Get all snapshots
snapshots = exec.status.get_snapshots()

for snapshot in snapshots:
    print(f"{snapshot.module_name}[{snapshot.experiment_name}]")
    print(f"  Time: {snapshot.timestamp}")
```

### 4. Timing Records

Collects execution time information:

```python
# Get timing report
timing_df = exec.get_timing()
print(timing_df)
```

## Main Methods

### State Management Methods

| Method | Description |
|--------|-------------|
| `put(module, experiment, adapter)` | Record module execution state |
| `get_result(module)` | Get module execution result |
| `get_metadata(module)` | Get module Schema |
| `get_full_expt(module)` | Get experiment configuration dictionary |

### Snapshot and Tracking Methods

| Method | Description |
|--------|-------------|
| `get_snapshots(module)` | Get execution snapshots |
| `get_snapshot_by_id(snapshot_id)` | Get specific snapshot by ID |
| `get_change_history(module)` | Get change history |
| `get_metadata_evolution(module)` | Track Schema evolution |

### Reporting Methods

| Method | Description |
|--------|-------------|
| `get_timing_report_data()` | Get timing report as DataFrame |
| `get_status_summary()` | Get status summary |

## Data Classes

### ExecutionSnapshot

Immutable record of execution snapshot:

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

Immutable record of timing information:

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

## Integration with Executor

Status is primarily used through Executor:

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# Access Status functionality through Executor
results = exec.get_result()          # → status.get_result()
timing = exec.get_timing()           # → status.get_timing_report_data()

# Advanced: Direct Status access
summary = exec.status.get_status_summary()
snapshots = exec.status.get_snapshots()
```

## Schema Inference

Status supports Schema inference functionality:

```python
from petsard import Executor

exec = Executor('config.yaml')  # Includes Preprocessor
exec.run()

# Get inferred Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    print(f"Inferred Schema: {inferred_schema.id}")
```

## Status Summary

Get complete execution status summary:

```python
summary = exec.status.get_status_summary()

print(f"Module sequence: {summary['sequence']}")
print(f"Active modules: {summary['active_modules']}")
print(f"Total snapshots: {summary['total_snapshots']}")
print(f"Total changes: {summary['total_changes']}")
```

## Notes

- **Internal Use**: Status is primarily used internally by Executor
- **Recommended Practice**: Access Status functionality through Executor methods
- **Automatic Tracking**: Snapshots and changes are automatically recorded during execution
- **Memory Management**: Long-running executions accumulate more snapshots
- **Immutability**: Snapshot and change records are immutable
- **Advanced Features**: Direct Status access requires understanding of internal mechanisms