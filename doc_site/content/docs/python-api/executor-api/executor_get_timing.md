---
title: "get_timing()"
weight: 313
---

Get execution time report, displaying time spent by each module and step.

## Syntax

```python
executor.get_timing()
```

## Parameters

This method takes no parameters.

## Return Value

- **Type**: `pd.DataFrame`
- **Description**: DataFrame containing execution time information for all modules and steps

### DataFrame Columns

| Column | Type | Description |
|--------|------|-------------|
| `record_id` | `str` | Unique record identifier |
| `module_name` | `str` | Module name (e.g., Loader, Synthesizer) |
| `experiment_name` | `str` | Experiment name |
| `step_name` | `str` | Execution step name |
| `start_time` | `datetime` | Step start time |
| `end_time` | `datetime` | Step end time |
| `duration_seconds` | `float` | Execution duration in seconds |

## Description

The `get_timing()` method retrieves detailed timing information for all executed modules and steps. This information helps:

- Identify performance bottlenecks
- Compare execution efficiency of different methods
- Optimize workflow configuration
- Plan resource allocation

### Timing Information Levels

Timing information is collected at multiple levels:

1. **Module Level**: Total time for each module (Loader, Synthesizer, etc.)
2. **Experiment Level**: Time for each experiment configuration
3. **Step Level**: Time for individual execution steps

## Basic Example

### Example 1: View Timing Report

```python
from petsard import Executor

config = {
    'Loader': {
        'load_data': {'filepath': 'data.csv'}
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'GaussianCopula'
        }
    }
}

executor = Executor(config=config)
executor.run()

# Get timing report
timing = executor.get_timing()
print(timing)

# Output example:
#   record_id  module_name  experiment_name    step_name           start_time  ...
# 0  rec_001    Loader       load_data         load_data    2024-01-01 10:00:00  ...
# 1  rec_002    Synthesizer  generate          fit          2024-01-01 10:00:05  ...
# 2  rec_003    Synthesizer  generate          sample       2024-01-01 10:01:20  ...
```

### Example 2: Analyze Module Performance

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

timing = executor.get_timing()

# Calculate total time by module
module_times = timing.groupby('module_name')['duration_seconds'].sum()
print("\nTime by Module:")
print(module_times.sort_values(ascending=False))

# Output:
# module_name
# Synthesizer    75.3
# Evaluator      12.5
# Loader          2.1
# Preprocessor    1.8
```

### Example 3: Compare Experiment Performance

```python
from petsard import Executor

config = {
    'Loader': {
        'load': {'filepath': 'data.csv'}
    },
    'Synthesizer': {
        'gaussian': {'method': 'sdv', 'model': 'GaussianCopula'},
        'ctgan': {'method': 'sdv', 'model': 'CTGAN'},
        'tvae': {'method': 'sdv', 'model': 'TVAE'}
    }
}

executor = Executor(config=config)
executor.run()

timing = executor.get_timing()

# Compare different synthesis methods
synth_timing = timing[timing['module_name'] == 'Synthesizer']
exp_times = synth_timing.groupby('experiment_name')['duration_seconds'].sum()

print("\nSynthesis Method Comparison:")
print(exp_times.sort_values(ascending=False))

# Output:
# experiment_name
# ctgan       125.7
# tvae         98.3
# gaussian     45.2
```

## Advanced Usage

### Example 4: Detailed Step Analysis

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

timing = executor.get_timing()

# Analyze each step
for module in timing['module_name'].unique():
    module_data = timing[timing['module_name'] == module]
    
    print(f"\n{module} Steps:")
    print("-" * 60)
    
    for _, row in module_data.iterrows():
        print(f"  {row['step_name']}: {row['duration_seconds']:.2f}s")
        print(f"    Start: {row['start_time']}")
        print(f"    End: {row['end_time']}")
```

### Example 5: Performance Visualization

```python
from petsard import Executor
import matplotlib.pyplot as plt

executor = Executor(config='config.yaml')
executor.run()

timing = executor.get_timing()

# Create bar chart
module_times = timing.groupby('module_name')['duration_seconds'].sum()

plt.figure(figsize=(10, 6))
module_times.plot(kind='bar')
plt.title('Execution Time by Module')
plt.xlabel('Module')
plt.ylabel('Time (seconds)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('timing_report.png')
print("Timing chart saved")
```

### Example 6: Performance Comparison Across Runs

```python
from petsard import Executor
import pandas as pd
from datetime import datetime

# Run multiple times and compare
results = []

for run_id in range(3):
    executor = Executor(config='config.yaml', verbose=False)
    executor.run()
    
    timing = executor.get_timing()
    timing['run_id'] = run_id
    results.append(timing)

# Combine results
all_timing = pd.concat(results, ignore_index=True)

# Compare runs
comparison = all_timing.groupby(['run_id', 'module_name'])['duration_seconds'].sum().unstack()
print("\nPerformance Across Runs:")
print(comparison)
print("\nAverage Time by Module:")
print(comparison.mean())
```

### Example 7: Identify Bottlenecks

```python
from petsard import Executor
import numpy as np

executor = Executor(config='config.yaml')
executor.run()

timing = executor.get_timing()

# Calculate statistics
total_time = timing['duration_seconds'].sum()
print(f"Total execution time: {total_time:.2f}s")

# Find bottlenecks (> 20% of total time)
timing['percentage'] = (timing['duration_seconds'] / total_time) * 100

bottlenecks = timing[timing['percentage'] > 20]

if not bottlenecks.empty:
    print("\nBottlenecks (>20% of total time):")
    for _, row in bottlenecks.iterrows():
        print(f"  {row['module_name']}.{row['step_name']}: "
              f"{row['duration_seconds']:.2f}s ({row['percentage']:.1f}%)")
else:
    print("\nNo significant bottlenecks found")

# Show top 5 time-consuming steps
print("\nTop 5 Time-Consuming Steps:")
top_steps = timing.nlargest(5, 'duration_seconds')
for _, row in top_steps.iterrows():
    print(f"  {row['module_name']}.{row['step_name']}: "
          f"{row['duration_seconds']:.2f}s")
```

### Example 8: Export Timing Report

```python
from petsard import Executor
from pathlib import Path
import json

executor = Executor(config='config.yaml')
executor.run()

timing = executor.get_timing()

# Create report directory
report_dir = Path('reports')
report_dir.mkdir(exist_ok=True)

# Export to CSV
timing.to_csv(report_dir / 'timing_report.csv', index=False)

# Export summary to JSON
summary = {
    'total_time': float(timing['duration_seconds'].sum()),
    'module_times': timing.groupby('module_name')['duration_seconds'].sum().to_dict(),
    'experiment_count': len(timing['experiment_name'].unique()),
    'step_count': len(timing)
}

with open(report_dir / 'timing_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Timing reports exported")
```

## Timing Analysis Patterns

### Pattern 1: Module Time Distribution

```python
timing = executor.get_timing()

# Calculate percentage for each module
module_times = timing.groupby('module_name')['duration_seconds'].sum()
total_time = module_times.sum()

print("\nModule Time Distribution:")
for module, time in module_times.items():
    percentage = (time / total_time) * 100
    print(f"  {module:15s}: {time:6.2f}s ({percentage:5.1f}%)")
```

### Pattern 2: Experiment Comparison

```python
timing = executor.get_timing()

# Compare all experiments
exp_times = timing.groupby('experiment_name')['duration_seconds'].sum()
fastest = exp_times.idxmin()
slowest = exp_times.idxmax()

print(f"\nFastest experiment: {fastest} ({exp_times[fastest]:.2f}s)")
print(f"Slowest experiment: {slowest} ({exp_times[slowest]:.2f}s)")
print(f"Time difference: {exp_times[slowest] - exp_times[fastest]:.2f}s")
```

### Pattern 3: Step-Level Analysis

```python
timing = executor.get_timing()

# Analyze steps for specific module
module_name = 'Synthesizer'
module_steps = timing[timing['module_name'] == module_name]

print(f"\n{module_name} Step Breakdown:")
for step_name, group in module_steps.groupby('step_name'):
    avg_time = group['duration_seconds'].mean()
    total_time = group['duration_seconds'].sum()
    count = len(group)
    print(f"  {step_name}:")
    print(f"    Count: {count}")
    print(f"    Total: {total_time:.2f}s")
    print(f"    Average: {avg_time:.2f}s")
```

## Timing DataFrame Operations

### Filter by Module

```python
timing = executor.get_timing()

# Get timing for specific module
loader_timing = timing[timing['module_name'] == 'Loader']
print(loader_timing)
```

### Filter by Time Range

```python
import pandas as pd

timing = executor.get_timing()

# Find long-running steps (> 10 seconds)
long_steps = timing[timing['duration_seconds'] > 10]
print("Long-running steps:")
print(long_steps[['module_name', 'step_name', 'duration_seconds']])
```

### Sort by Duration

```python
timing = executor.get_timing()

# Sort by duration (descending)
sorted_timing = timing.sort_values('duration_seconds', ascending=False)
print("Steps by duration:")
print(sorted_timing[['module_name', 'step_name', 'duration_seconds']].head(10))
```

## Performance Optimization Tips

Based on timing information, you can optimize:

### 1. Data Loading

```python
# If Loader takes long time
timing = executor.get_timing()
loader_time = timing[timing['module_name'] == 'Loader']['duration_seconds'].sum()

if loader_time > 5.0:  # More than 5 seconds
    print("Consider:")
    print("  - Using more efficient file formats (parquet instead of CSV)")
    print("  - Reducing data size")
    print("  - Optimizing data types")
```

### 2. Synthesis Methods

```python
# Compare synthesis method efficiency
synth_timing = timing[timing['module_name'] == 'Synthesizer']
exp_times = synth_timing.groupby('experiment_name')['duration_seconds'].sum()

if exp_times.max() > 100:  # More than 100 seconds
    print("Consider:")
    print("  - Using faster models (GaussianCopula instead of CTGAN)")
    print("  - Reducing epochs")
    print("  - Decreasing batch size")
```

## Notes

- **Execution Required**: Must call `run()` before `get_timing()`, otherwise returns empty DataFrame
- **Time Precision**: Time recorded in seconds with sub-second precision
- **Timezone**: All timestamps in system local timezone
- **Multiple Calls**: Calling multiple times returns same results; no additional computation
- **Memory Usage**: Timing DataFrame typically small; minimal memory impact
- **Empty Result**: Returns empty DataFrame if no execution performed
- **Step Recording**: Not all modules record detailed step timing; depends on implementation

## Related Methods

- [`run()`](executor_run): Execute workflow
- [`get_result()`](executor_get_result): Get execution results
- [`is_execution_completed()`](executor_is_execution_completed): Check execution status

## See Also

- [Executor Class Overview](./_index#basic-usage)
- [Status API](../../status-api)
- [Performance Optimization Guide](../../tutorial/performance-optimization)