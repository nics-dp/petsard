---
title: "run()"
weight: 311
---

Execute the entire workflow and generate all experiment combinations.

## Syntax

```python
executor.run()
```

## Parameters

This method takes no parameters.

## Return Value

- **Type**: `None`
- **Description**: No return value; results stored internally in Status object

## Description

The `run()` method is the core execution method of Executor. It:

1. Parses module dependencies and determines execution sequence
2. Loads and initializes required modules
3. Generates all experiment combinations
4. Executes each combination sequentially
5. Records execution status and results
6. Collects execution time information

### Execution Flow

```
Initialization → Load Modules → Generate Combinations → Execute Workflow → Store Results
```

### Module Execution Sequence

Executor automatically determines the optimal execution sequence based on module dependencies:

1. **Loader**: Always executed first, loading raw data
2. **Preprocessor**: Executed after Loader (if configured), preprocessing data
3. **Synthesizer**: Uses preprocessed data to generate synthetic data
4. **Postprocessor**: Postprocesses synthetic data (if configured)
5. **Evaluator**: Evaluates synthesis quality (if configured)
6. **Reporter**: Saves results (if configured)

### Experiment Combination Generation

When configuration contains multiple experiments, Executor automatically generates all combinations:

```yaml
Loader:
  exp1: {...}
  exp2: {...}

Synthesizer:
  method_a: {...}
  method_b: {...}
```

Generates 4 combinations:
- `Loader[exp1]` → `Synthesizer[method_a]`
- `Loader[exp1]` → `Synthesizer[method_b]`
- `Loader[exp2]` → `Synthesizer[method_a]`
- `Loader[exp2]` → `Synthesizer[method_b]`

## Basic Example

### Example 1: Simple Workflow

```python
from petsard import Executor

# Create configuration
config = {
    'Loader': {
        'load_data': {
            'filepath': 'data.csv'
        }
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'GaussianCopula',
            'num_samples': 1000
        }
    }
}

# Create and execute
executor = Executor(config=config)
executor.run()

# Check completion status
if executor.is_execution_completed():
    print("Execution completed successfully")
    results = executor.get_result()
```

### Example 2: Multi-Module Workflow

```python
from petsard import Executor

config = {
    'Loader': {
        'load': {'filepath': 'original_data.csv'}
    },
    'Preprocessor': {
        'clean': {
            'missing_values': 'drop',
            'outliers': 'clip'
        }
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'CTGAN'
        }
    },
    'Evaluator': {
        'assess': {
            'metrics': ['statistical_similarity', 'privacy_metrics']
        }
    },
    'Reporter': {
        'save': {
            'output_path': 'synthetic_data.csv'
        }
    }
}

executor = Executor(config=config, verbose=True)
executor.run()

# Get execution time report
timing = executor.get_timing()
print(timing)
```

### Example 3: Multiple Experiments

```python
from petsard import Executor

# Configuration with multiple experiments
config = {
    'Loader': {
        'dataset_v1': {'filepath': 'data_v1.csv'},
        'dataset_v2': {'filepath': 'data_v2.csv'}
    },
    'Synthesizer': {
        'gaussian': {'method': 'sdv', 'model': 'GaussianCopula'},
        'ctgan': {'method': 'sdv', 'model': 'CTGAN'},
        'tvae': {'method': 'sdv', 'model': 'TVAE'}
    },
    'Evaluator': {
        'evaluate': {'metrics': ['quality_report']}
    }
}

# Execute all combinations (2 × 3 = 6 experiments)
executor = Executor(config=config)
executor.run()

# Get all results
results = executor.get_result()
print(f"Completed {len(results)} experiments")

# Analyze results
for exp_name, result in results.items():
    print(f"\n{exp_name}:")
    print(f"  Rows: {len(result['data'])}")
    print(f"  Columns: {len(result['data'].columns)}")
```

## Advanced Usage

### Example 4: Error Handling

```python
from petsard import Executor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    executor = Executor(config='config.yaml')
    executor.run()
    
    # Check execution status
    if not executor.is_execution_completed():
        raise RuntimeError("Execution incomplete")
        
    results = executor.get_result()
    print("Execution successful")
    
except FileNotFoundError as e:
    print(f"Configuration file not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Execution error: {e}")
    # Get partial results (if any)
    if hasattr(executor, 'get_result'):
        partial_results = executor.get_result()
        print(f"Partial results: {len(partial_results)} experiments")
```

### Example 5: Performance Monitoring

```python
from petsard import Executor
import time

start_time = time.time()

executor = Executor(config='config.yaml', verbose=True)
executor.run()

end_time = time.time()
execution_time = end_time - start_time

# Get detailed timing information
timing = executor.get_timing()

print(f"\nTotal execution time: {execution_time:.2f} seconds")
print(f"\nDetailed timing:")
print(timing)

# Analyze module performance
if not timing.empty:
    module_times = timing.groupby('module_name')['duration_seconds'].sum()
    print(f"\nTime by module:")
    print(module_times.sort_values(ascending=False))
```

### Example 6: Batch Processing

```python
from petsard import Executor
import os
from pathlib import Path

# Process multiple data files
data_dir = Path('data/')
results_dir = Path('results/')
results_dir.mkdir(exist_ok=True)

for data_file in data_dir.glob('*.csv'):
    print(f"\nProcessing: {data_file.name}")
    
    config = {
        'Loader': {
            'load': {'filepath': str(data_file)}
        },
        'Synthesizer': {
            'generate': {'method': 'sdv', 'model': 'GaussianCopula'}
        },
        'Reporter': {
            'save': {
                'output_path': str(results_dir / f"synthetic_{data_file.name}")
            }
        }
    }
    
    executor = Executor(config=config, verbose=False)
    executor.run()
    
    if executor.is_execution_completed():
        print(f"  ✓ Completed successfully")
    else:
        print(f"  ✗ Execution failed")
```

## State Changes

After executing `run()`, the following state changes occur:

### 1. Status Object Updated

```python
# Before run()
executor = Executor(config=config)
print(executor.is_execution_completed())  # False

# After run()
executor.run()
print(executor.is_execution_completed())  # True
```

### 2. Results Available

```python
# Before run() - no results
executor = Executor(config=config)
# executor.get_result()  # Would raise error

# After run() - results available
executor.run()
results = executor.get_result()  # Returns results
```

### 3. Timing Information Available

```python
# After run()
executor.run()
timing = executor.get_timing()  # Returns timing DataFrame
```

## Execution Monitoring

### Progress Display

When `verbose=True` (default), execution progress is displayed:

```
Loading module: Loader
Executing: Loader[load_data]
  ✓ Completed in 0.5s

Loading module: Synthesizer  
Executing: Synthesizer[generate]
  ✓ Completed in 15.3s

All experiments completed successfully
```

### Disable Progress Display

```python
executor = Executor(config=config, verbose=False)
executor.run()  # Silent execution
```

## Notes

- **Blocking Execution**: `run()` is a blocking operation; control returns after all experiments complete
- **Single Execution**: Each Executor instance should call `run()` only once; create new instance for re-execution
- **Memory Usage**: All results stored in memory; consider memory limits for large-scale experiments
- **Error Propagation**: If any module fails, execution stops and exception is raised
- **Execution Order**: Cannot modify execution order; determined by module dependencies
- **State Persistence**: Execution state not automatically persisted; use Reporter to save results
- **Resource Cleanup**: Long-running workflows may accumulate memory; consider periodic cleanup

## Related Methods

- [`get_result()`](executor_get_result): Get execution results
- [`get_timing()`](executor_get_timing): Get execution time report
- [`is_execution_completed()`](executor_is_execution_completed): Check execution status
- [`get_inferred_schema()`](executor_get_inferred_schema): Get inferred Schema

## See Also

- [Executor Class Overview](./_index#basic-usage)
- [Config API](../../config-api)
- [Status API](../../status-api)