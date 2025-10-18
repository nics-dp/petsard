---
title: "Status API (WIP)"
weight: 33
---

Status is the state management module of PETsARD, responsible for tracking workflow execution status, storing results, managing metadata (Schema), and creating execution snapshots.

## Class Architecture

{{< mermaid-file="status-class-diagram.mmd" >}}

## Design Philosophy

Status follows comprehensive state management principles:

### 1. Execution Tracking
- Record execution status of each module
- Track experiment execution sequence
- Maintain execution timeline

### 2. Result Storage
- Store execution results for each experiment
- Manage data and Schema associations
- Provide result query interface

### 3. Metadata Management
- Track Schema changes throughout workflow
- Create metadata snapshots before and after execution
- Record transformation history

### 4. Snapshot System
- Create execution snapshots at key points
- Enable state recovery and auditing
- Support execution history review

## Basic Usage

### Access Through Executor

Status is typically accessed through Executor (not directly instantiated):

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Access Status through Executor
status = executor.status

# Get execution status
is_completed = status.is_completed()
print(f"Execution completed: {is_completed}")
```

### Get Results

```python
# Get results through Executor (recommended)
results = executor.get_result()

# Or access directly through Status (advanced)
results = executor.status.get_result()
```

### Get Timing Information

```python
# Get timing through Executor (recommended)
timing = executor.get_timing()

# Or access directly through Status (advanced)
timing = executor.status.get_timing()
```

## Constructor (`__init__`)

Creates a Status instance and initializes state management.

### Syntax

```python
Status()
```

### Parameters

No parameters required.

### Return Value

Returns a Status instance with initialized state.

### Usage Example

```python
# Note: Typically not instantiated directly
# Status is created internally by Executor

from petsard.core.status import Status

# Direct instantiation (advanced usage)
status = Status()
```

### Notes

- **Internal Use**: Primarily used internally by Executor
- **Automatic Initialization**: Executor automatically creates Status instance
- **No Configuration**: Does not require configuration parameters
- **Empty State**: Starts with empty state (no snapshots or results)

## State Management

### Execution State

Status tracks three main execution states:

1. **Not Started**: Before `run()` is called
2. **In Progress**: During execution (each module)
3. **Completed**: After all modules finish successfully

### State Transitions

```
Not Started → In Progress → Completed
              ↓
            Failed
```

## Result Storage

### Result Structure

Status stores results in the following structure:

```python
{
    'experiment_key': {
        'data': pd.DataFrame,    # Result data
        'schema': Schema         # Schema object
    },
    ...
}
```

### Result Recording

Results are automatically recorded during execution:

```python
# During Executor.run()
# 1. Module executes
# 2. Result generated
# 3. Status records result
# 4. Snapshot created
```

### Result Retrieval

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Get all results
results = executor.status.get_result()

# Access specific experiment
exp_key = list(results.keys())[0]
exp_result = results[exp_key]

data = exp_result['data']
schema = exp_result['schema']

print(f"Data shape: {data.shape}")
print(f"Schema columns: {len(schema.columns)}")
```

## Snapshot System

### Snapshot Creation

Snapshots are created at key execution points:

1. **Before Module Execution**: Initial state snapshot
2. **After Module Execution**: Result state snapshot
3. **At Key Transitions**: State change snapshots

### Snapshot Contents

Each snapshot contains:

```python
{
    'snapshot_id': 'unique_id',
    'timestamp': datetime,
    'module_name': 'module_name',
    'experiment_name': 'experiment_name',
    'metadata': {
        'schema_before': Schema,
        'schema_after': Schema
    },
    'context': {...}
}
```

### Snapshot Access

```python
# Access snapshots (advanced usage)
snapshots = executor.status.snapshots

print(f"Total snapshots: {len(snapshots)}")

for snapshot in snapshots:
    print(f"Snapshot: {snapshot['snapshot_id']}")
    print(f"  Module: {snapshot['module_name']}")
    print(f"  Experiment: {snapshot['experiment_name']}")
    print(f"  Time: {snapshot['timestamp']}")
```

## Change Tracking

### Change Recording

Status tracks all metadata changes:

```python
# Changes are automatically recorded
# 1. Schema field added
# 2. Schema field modified
# 3. Schema field removed
# 4. Data transformation applied
```

### Change Types

| Change Type | Description | Example |
|-------------|-------------|---------|
| `CREATE` | New field added | Adding onehot encoded columns |
| `UPDATE` | Field modified | Scaling numeric values |
| `DELETE` | Field removed | Dropping columns |
| `TRANSFORM` | Data transformation | Type conversion |

### Change Access

```python
# Access change history (advanced usage)
changes = executor.status.changes

print(f"Total changes: {len(changes)}")

for change in changes:
    print(f"Change: {change['change_id']}")
    print(f"  Type: {change['type']}")
    print(f"  Target: {change['target']}")
    print(f"  Time: {change['timestamp']}")
```

## Timing Information

### Time Recording

Status records execution time for:

- Each module
- Each experiment
- Each execution step

### Timing Structure

```python
{
    'record_id': 'unique_id',
    'module_name': 'module_name',
    'experiment_name': 'experiment_name',
    'step_name': 'step_name',
    'start_time': datetime,
    'end_time': datetime,
    'duration_seconds': float
}
```

### Timing Retrieval

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Get timing DataFrame
timing = executor.status.get_timing()

# Analyze timing
total_time = timing['duration_seconds'].sum()
print(f"Total execution time: {total_time:.2f}s")

# Time by module
module_times = timing.groupby('module_name')['duration_seconds'].sum()
print("\nTime by module:")
print(module_times)
```

## Status Summary

### Get Summary Information

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Get status summary (advanced usage)
summary = executor.status.get_status_summary()

print("Status Summary:")
print(f"  Execution sequence: {summary['sequence']}")
print(f"  Active modules: {summary['active_modules']}")
print(f"  Total snapshots: {summary['total_snapshots']}")
print(f"  Total changes: {summary['total_changes']}")
print(f"  Last snapshot: {summary['last_snapshot']}")
```

### Summary Contents

| Field | Description |
|-------|-------------|
| `sequence` | Module execution order |
| `active_modules` | List of executed modules |
| `metadata_modules` | Modules with metadata |
| `total_snapshots` | Total snapshot count |
| `total_changes` | Total change record count |
| `last_snapshot` | Latest snapshot ID |
| `last_change` | Latest change ID |

## Integration with Executor

### Automatic Status Management

```python
from petsard import Executor

# Executor creates and manages Status
executor = Executor(config='config.yaml')

# Status is initialized
assert executor.status is not None

# Execute workflow
executor.run()

# Status is updated automatically
assert executor.status.is_completed()
```

### Status Lifecycle

```
1. Executor.__init__()
   └─> Status created and initialized

2. Executor.run()
   ├─> Status starts tracking
   ├─> Modules execute
   ├─> Results recorded
   ├─> Snapshots created
   └─> Status marks as completed

3. Executor.get_result()
   └─> Retrieves results from Status

4. Executor.get_timing()
   └─> Retrieves timing from Status
```

## Advanced Usage

### Direct Status Access

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Access Status directly (advanced)
status = executor.status

# Check completion
if status.is_completed():
    print("Execution completed")

# Get result count
results = status.get_result()
print(f"Total results: {len(results)}")

# Get snapshot count
print(f"Total snapshots: {len(status.snapshots)}")

# Get change count
print(f"Total changes: {len(status.changes)}")
```

### Status Inspection

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

status = executor.status

# Inspect execution sequence
print("Execution Sequence:")
for i, snapshot in enumerate(status.snapshots, 1):
    print(f"{i}. {snapshot['module_name']}[{snapshot['experiment_name']}]")
    print(f"   Time: {snapshot['timestamp']}")
```

### Custom Status Analysis

```python
from petsard import Executor
import pandas as pd

executor = Executor(config='config.yaml')
executor.run()

status = executor.status

# Analyze Schema changes
print("Schema Evolution:")
for change in status.changes:
    if change['type'] == 'UPDATE':
        print(f"  {change['target']}: {change['before']} → {change['after']}")

# Timing analysis
timing = status.get_timing()
avg_time_per_module = timing.groupby('module_name')['duration_seconds'].mean()
print("\nAverage time per module:")
print(avg_time_per_module)
```

## State Persistence

### Current Limitations

Status state is not automatically persisted:

- State exists only in memory
- Lost when Executor instance is destroyed
- Not saved to disk automatically

### Manual Persistence

```python
from petsard import Executor
import pickle

executor = Executor(config='config.yaml')
executor.run()

# Save Status state (advanced)
with open('status_state.pkl', 'wb') as f:
    pickle.dump(executor.status, f)

# Load Status state (advanced)
with open('status_state.pkl', 'rb') as f:
    loaded_status = pickle.load(f)
```

## Memory Management

### Memory Considerations

Status stores all execution information in memory:

- All results (DataFrames)
- All snapshots
- All change records
- All timing information

### Memory Optimization

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Get results and clear Status (if needed)
results = executor.get_result()

# Process results
for exp_key, exp_result in results.items():
    data = exp_result['data']
    # Process data...

# Delete executor to free memory
del executor
```

## Error Handling

### Status During Errors

```python
from petsard import Executor

executor = Executor(config='config.yaml')

try:
    executor.run()
except Exception as e:
    print(f"Execution error: {e}")
    
    # Check Status even after error
    if hasattr(executor, 'status'):
        status = executor.status
        
        # Get partial results (if any)
        try:
            partial_results = status.get_result()
            print(f"Partial results: {len(partial_results)}")
        except:
            print("No partial results available")
        
        # Check last snapshot
        if status.snapshots:
            last_snapshot = status.snapshots[-1]
            print(f"Last successful module: {last_snapshot['module_name']}")
```

## Best Practices

### 1. Access Through Executor

```python
# Recommended: Use Executor methods
results = executor.get_result()
timing = executor.get_timing()

# Advanced: Direct Status access only when needed
status = executor.status
snapshots = status.snapshots
```

### 2. Check Completion Before Access

```python
executor = Executor(config='config.yaml')
executor.run()

# Always check completion
if executor.is_execution_completed():
    results = executor.get_result()
else:
    print("Execution incomplete")
```

### 3. Memory Management

```python
# Process results in batches for large workflows
executor = Executor(config='config.yaml')
executor.run()

results = executor.get_result()

# Process and save results
for exp_key, exp_result in results.items():
    data = exp_result['data']
    data.to_csv(f'output/{exp_key}.csv')

# Free memory
del executor
del results
```

## Notes

- **Internal Module**: Primarily used internally by Executor
- **Automatic Management**: Status is automatically managed; no manual intervention needed
- **Memory Storage**: All state stored in memory; not persisted to disk
- **Thread Safety**: Not thread-safe; use separate instances in multi-threaded environments
- **Single Instance**: Each Executor has one Status instance
- **No Modification**: Status state should not be modified directly
- **Read-Only Access**: Access Status for reading only; modifications handled by Executor