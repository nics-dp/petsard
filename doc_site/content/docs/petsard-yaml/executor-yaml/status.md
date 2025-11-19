---
title: "Status Tracking"
weight: 52
---

Status is responsible for tracking the execution status of the entire workflow, providing complete execution history, result storage, and Schema metadata management.

## Overview

Status is a state management system used internally by Executor and **does not require configuration in YAML**. It automatically:

- Records execution results of each module
- Tracks changes in metadata (Schema)
- Creates execution snapshots for recovery
- Collects execution time information

## Automatic Status Tracking

When Executor runs, Status automatically records:

### 1. Execution Results

After each module executes, results are automatically saved to Status:

```python
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# Get results through Executor
results = exec.get_result()
print(results)
```

### 2. Metadata Tracking

Status tracks Schema changes of data across modules:

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

During execution, Status records:
- Original Schema after Loader loading
- Schema changes after Preprocessor processing
- Schema information available to Synthesizer

### 3. Execution Snapshots

Snapshots are created before and after each module execution, containing:
- Execution timestamp
- Module name and experiment name
- Metadata state (before/after execution)
- Execution context information

### 4. Time Recording

Automatically collects execution time for each module and step:

```python
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# Get time report
timing = exec.get_timing()
print(timing)
```

## Accessing Status Through Executor

All Status information can be accessed through Executor methods:

### Get Execution Results

```python
# Get all results
results = exec.get_result()

# Result format
# {
#   'Loader[load_data]_Synthesizer[generate]': {
#     'data': DataFrame,
#     'schema': Schema
#   }
# }
```

### Get Execution Time

```python
# Get time information
timing_df = exec.get_timing()

# DataFrame columns:
# - record_id: Record ID
# - module_name: Module name
# - experiment_name: Experiment name
# - step_name: Execution step
# - start_time: Start time
# - end_time: End time
# - duration_seconds: Execution time (seconds)
```

### Check Execution Status

```python
# Check if execution completed
if exec.is_execution_completed():
    print("Execution completed")
    results = exec.get_result()
else:
    print("Execution in progress or not started")
```

## Multi-Experiment Result Management

When configuration contains multiple experiments, Status manages results for all combinations:

### Configuration Example

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

### Result Organization

```python
results = exec.get_result()

# Results contain all experiment combinations:
# {
#   'Loader[load_v1]_Synthesizer[method_a]_Reporter[save_all]': {...},
#   'Loader[load_v1]_Synthesizer[method_b]_Reporter[save_all]': {...},
#   'Loader[load_v2]_Synthesizer[method_a]_Reporter[save_all]': {...},
#   'Loader[load_v2]_Synthesizer[method_b]_Reporter[save_all]': {...}
# }
```

## Schema Inference and Tracking

Status provides Schema inference functionality, especially when using Preprocessor:

### Automatic Schema Inference

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

Execution flow:
1. After Loader loads data, Status records original Schema
2. Executor infers processed Schema based on Preprocessor configuration
3. Synthesizer uses inferred Schema for synthesis
4. All Schema changes throughout the process are tracked and recorded

## Execution Snapshots

Status creates multiple snapshots during execution:

### Snapshot Contents

Each snapshot contains:
- **Snapshot ID**: Unique identifier
- **Module Information**: Module name and experiment name
- **Timestamp**: Creation time
- **Metadata**: Schema state before and after execution
- **Execution Context**: Related configuration and parameters

### Snapshot Purposes

- **Debugging**: Check state changes during execution
- **Auditing**: Track complete history of data processing
- **Recovery**: Restore to specific state when needed

## Change Tracking

Status records all metadata changes:

### Tracking Contents

- **Change Type**: Create, update, delete
- **Change Target**: Schema or Field level
- **Before and After**: State comparison
- **Change Time**: Occurrence timestamp
- **Module Context**: Which module caused the change

### Change Example

```
Loader → Preprocessor:
- age: numerical → numerical (minmax scaled)
- education: categorical → categorical (onehot encoded)
- income: numerical → numerical (standard scaled)
```

## Status Summary

Get complete summary of execution status:

```python
# Direct access through Python API (advanced usage)
from petsard import Executor

exec = Executor(config='config.yaml')
exec.run()

# Get status summary
summary = exec.status.get_status_summary()

# Summary includes:
# - sequence: Module execution sequence
# - active_modules: Executed modules
# - metadata_modules: Modules with metadata
# - total_snapshots: Total snapshot count
# - total_changes: Total change record count
# - last_snapshot: Latest snapshot ID
# - last_change: Latest change ID
```

## Notes

- **Automatic Management**: Status is fully managed automatically by Executor; no YAML configuration needed
- **Result Access**: Use `exec.get_result()` and `exec.get_timing()` to get status information
- **Memory Usage**: Long-running workflows accumulate more snapshots; Status automatically manages memory
- **Snapshot Count**: Each module execution generates one snapshot; large experiment combinations produce corresponding number of snapshots
- **Advanced Features**: For complete Status API, refer to Python API documentation