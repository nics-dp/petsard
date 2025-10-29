---
title: "Executor API (WIP)"
weight: 31
---

Executor is the core orchestration module of the PETsARD framework. It parses YAML configuration, executes each module in workflow sequence, manages execution state, and provides result access interface.

## Class Architecture

{{< mermaid-file="executor-class-diagram.mmd" >}}

## Design Philosophy

Executor follows three core design principles:

### 1. Single Responsibility
Executor only handles workflow orchestration, delegating specific functions to dedicated modules:
- **Config**: Configuration parsing and validation
- **Status**: State management and result storage
- **Modules**: Actual data processing tasks

### 2. Clear Interface
All interactions through Executor's public methods:
- Construction phase: `__init__()`
- Execution phase: `run()`
- Result retrieval: `get_result()`, `get_timing()`, `is_execution_completed()`
- Schema inference: `get_inferred_schema()`

### 3. Automated Management
Users only need to provide configuration; Executor handles:
- Module loading and initialization
- Execution sequence management
- State tracking and snapshot creation
- Result collection and organization

## Basic Usage

### Import Module

```python
from petsard import Executor
```

### Create Executor Instance

```python
# From YAML file
executor = Executor(config='path/to/config.yaml')

# From YAML string
config_yaml = """
Loader:
  load_data:
    filepath: data.csv
Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula
"""
executor = Executor(config=config_yaml)
```

### Execute Workflow

```python
# Execute all experiments
executor.run()

# Check execution status
if executor.is_execution_completed():
    print("Execution completed")
```

### Get Results

```python
# Get all results
results = executor.get_result()

# Get execution time report
timing_df = executor.get_timing()
```

## Constructor (`__init__`)

Creates an Executor instance and initializes configuration.

### Syntax

```python
Executor(config, verbose=True)
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `config` | `str` | Yes | - | Configuration input: YAML file path or YAML string |
| `verbose` | `bool` | No | `True` | Whether to display execution progress information |

### Return Value

Returns an Executor instance with initialized Config and Status.

### Usage Examples

**Example 1: Load from YAML file**

```python
from petsard import Executor

# Create Executor from file
exec = Executor(config='workflow_config.yaml')
print("Configuration loaded successfully")
```

**Example 2: Use YAML string**

```python
from petsard import Executor

# Define configuration as YAML string
config_yaml = """
Loader:
  load_csv:
    filepath: data/input.csv

Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula
    num_samples: 1000
"""

# Create Executor from YAML string
exec = Executor(config=config_yaml)
exec.run()
```

**Example 3: Dynamic YAML string generation**

```python
from petsard import Executor

# Generate YAML string dynamically
def create_config_yaml(filepath, model_name):
    return f"""
Loader:
  load_data:
    filepath: {filepath}

Synthesizer:
  generate:
    method: sdv
    model: {model_name}
"""

# Use dynamic configuration
config = create_config_yaml('data/input.csv', 'CTGAN')
exec = Executor(config=config)
exec.run()
```

**Example 3: Disable progress information**

```python
from petsard import Executor

# Create silent Executor
exec = Executor(
    config='config.yaml',
    verbose=False
)
exec.run()
```

### Notes

- **Input Type Detection**: Executor automatically detects whether `config` is a file path or YAML string:
  - If the string is a valid file path → loads from file
  - Otherwise → parses as YAML string
- **Configuration Validation**: Config automatically validates configuration content during initialization
- **Module Check**: Ensures all referenced modules exist in the system
- **Path Handling**: File path supports absolute and relative paths; relative paths resolve from current working directory
- **Error Reporting**: Provides detailed error messages for configuration errors and YAML parsing errors
- **Memory Management**: Large configurations may consume more memory; consider splitting into multiple smaller workflows

## Method Documentation

Executor provides the following public methods:

### [run()](executor_run)
Execute the entire workflow and generate all experiment combinations.

### [get_result()](executor_get_result)
Get execution results, including DataFrames and Schema for all experiments.

### [get_timing()](executor_get_timing)
Get execution time report, displaying time spent by each module and step.

### [is_execution_completed()](executor_is_execution_completed)
Check if workflow execution is complete.

### [get_inferred_schema()](executor_get_inferred_schema)
Get inferred Schema based on Loader, Preprocessor, and Postprocessor configuration.

## Internal Components

### Config
Responsible for configuration parsing and validation:
- Parse YAML or dictionary configuration
- Validate configuration structure and parameters
- Provide configuration query interface

See: [Config API](../../config-api)

### Status
Responsible for state management and result storage:
- Record execution status of each module
- Track metadata (Schema) changes
- Create execution snapshots
- Collect execution time information

See: [Status API](../../status-api)

## Workflow Execution Mechanism

### 1. Initialization Phase

```python
executor = Executor(config='config.yaml')
```

Actions performed during this phase:
- Load and parse configuration file
- Initialize Config object
- Validate configuration content
- Initialize Status object
- Prepare module loading environment

### 2. Execution Phase

```python
executor.run()
```

Actions performed during this phase:
- Parse module dependencies
- Determine execution sequence
- Load and initialize modules
- Create execution snapshots
- Execute module methods
- Record execution results
- Collect time information

### 3. Result Retrieval Phase

```python
results = executor.get_result()
timing = executor.get_timing()
```

Actions performed during this phase:
- Organize execution results
- Format result structure
- Generate time report
- Provide result access interface

## Multiple Experiment Management

Executor automatically handles combinations of multiple experiments:

### Configuration Example

```yaml
Loader:
  experiment_1:
    filepath: data1.csv
  experiment_2:
    filepath: data2.csv

Synthesizer:
  method_a:
    method: sdv
    model: GaussianCopula
  method_b:
    method: sdv
    model: CTGAN
```

### Execution Flow

1. **Generate Combinations**: Executor automatically generates 4 experiment combinations:
   - `Loader[experiment_1]` + `Synthesizer[method_a]`
   - `Loader[experiment_1]` + `Synthesizer[method_b]`
   - `Loader[experiment_2]` + `Synthesizer[method_a]`
   - `Loader[experiment_2]` + `Synthesizer[method_b]`

2. **Sequential Execution**: Execute each combination in order, ensuring result independence

3. **Result Organization**: Organize results by combination, facilitating comparison

### Result Retrieval

```python
results = executor.get_result()

# Result structure
# {
#   'Loader[experiment_1]_Synthesizer[method_a]': {
#     'data': DataFrame,
#     'schema': Schema
#   },
#   'Loader[experiment_1]_Synthesizer[method_b]': {...},
#   'Loader[experiment_2]_Synthesizer[method_a]': {...},
#   'Loader[experiment_2]_Synthesizer[method_b]': {...}
# }
```

## Error Handling

Executor provides comprehensive error handling mechanisms:

### Configuration Errors

```python
try:
    executor = Executor(config='invalid_config.yaml')
except Exception as e:
    print(f"Configuration error: {e}")
```

Common configuration errors:
- File not found
- Invalid YAML format
- Missing required fields
- Invalid parameter values

### Execution Errors

```python
executor = Executor(config='config.yaml')
try:
    executor.run()
except Exception as e:
    print(f"Execution error: {e}")
    # Check which module failed
    print(f"Execution status: {executor.is_execution_completed()}")
```

Common execution errors:
- Module loading failure
- Data processing errors
- Insufficient memory
- File I/O errors

## Performance Optimization

### Memory Management

```python
# For large datasets, process in batches
executor = Executor(config='config.yaml')
executor.run()

# Get results and clear memory immediately
results = executor.get_result()
del executor  # Release memory
```

### Parallel Execution

For independent experiments, consider parallel execution:

```python
from concurrent.futures import ProcessPoolExecutor

def run_experiment(config_file):
    executor = Executor(config=config_file)
    executor.run()
    return executor.get_result()

# Execute multiple experiments in parallel
with ProcessPoolExecutor() as executor:
    configs = ['config1.yaml', 'config2.yaml', 'config3.yaml']
    results = executor.map(run_experiment, configs)
```

## Best Practices

### 1. Configuration Management

```python
# Use version control for configuration files
config_v1 = 'configs/workflow_v1.yaml'
config_v2 = 'configs/workflow_v2.yaml'

# Add descriptive information to configuration
config = {
    'metadata': {
        'version': '1.0',
        'author': 'Data Team',
        'description': 'Production synthesis workflow'
    },
    'Loader': {...}
}
```

### 2. Result Validation

```python
executor = Executor(config='config.yaml')
executor.run()

# Check execution status
if not executor.is_execution_completed():
    raise RuntimeError("Execution incomplete")

# Validate results
results = executor.get_result()
for exp_name, result in results.items():
    assert 'data' in result, f"Missing data: {exp_name}"
    assert 'schema' in result, f"Missing schema: {exp_name}"
```

### 3. Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Executor
executor = Executor(config='config.yaml', verbose=True)
executor.run()

# Check execution time
timing = executor.get_timing()
print(timing)
```

## Common Patterns

### Pattern 1: Data Processing Pipeline

```python
# Load → Preprocess → Synthesize → Evaluate
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'Preprocessor': {'clean': {'method': 'default'}},
    'Synthesizer': {'generate': {'method': 'sdv'}},
    'Evaluator': {'assess': {'metrics': ['statistical', 'privacy']}}
}

executor = Executor(config=config)
executor.run()
results = executor.get_result()
```

### Pattern 2: Comparative Experiments

```python
# Compare multiple synthesis methods
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'Synthesizer': {
        'sdv_gc': {'method': 'sdv', 'model': 'GaussianCopula'},
        'sdv_ctgan': {'method': 'sdv', 'model': 'CTGAN'},
        'sdv_tvae': {'method': 'sdv', 'model': 'TVAE'}
    },
    'Evaluator': {'eval': {'metrics': ['quality_report']}}
}

executor = Executor(config=config)
executor.run()

# Compare results of different methods
results = executor.get_result()
for exp_name, result in results.items():
    print(f"{exp_name}: {len(result['data'])} records")
```

### Pattern 3: Batch Processing

```python
# Process multiple datasets
datasets = ['data1.csv', 'data2.csv', 'data3.csv']

for dataset in datasets:
    config = {
        'Loader': {'load': {'filepath': dataset}},
        'Synthesizer': {'generate': {'method': 'sdv'}},
        'Reporter': {'save': {'output_dir': f'output/{dataset}'}}
    }
    
    executor = Executor(config=config, verbose=False)
    executor.run()
    print(f"Completed: {dataset}")
```

## Integration with Other Modules

### With Loader

```python
# Executor automatically calls Loader's load_data method
config = {
    'Loader': {
        'load_csv': {
            'filepath': 'data.csv',
            'delimiter': ','
        }
    }
}

executor = Executor(config=config)
executor.run()

# Get loaded data
results = executor.get_result()
data = results['Loader[load_csv]']['data']
```

### With Synthesizer

```python
# Executor automatically passes data and schema to Synthesizer
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'GaussianCopula',
            'num_samples': 1000
        }
    }
}

executor = Executor(config=config)
executor.run()

# Get synthesized data
results = executor.get_result()
synthetic_data = results['Loader[load]_Synthesizer[generate]']['data']
```

### With Evaluator

```python
# Executor automatically passes original and synthetic data to Evaluator
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'Synthesizer': {'generate': {'method': 'sdv'}},
    'Evaluator': {
        'assess': {
            'metrics': ['statistical_similarity', 'privacy_metrics']
        }
    }
}

executor = Executor(config=config)
executor.run()

# Get evaluation results
results = executor.get_result()
eval_result = results['Loader[load]_Synthesizer[generate]_Evaluator[assess]']
```

## Advanced Features

### Custom Module Integration

```python
# Register custom module (advanced usage)
from petsard import Executor
from my_custom_module import MyCustomModule

# Configure custom module
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'MyCustomModule': {
        'process': {
            'param1': 'value1',
            'param2': 'value2'
        }
    }
}

executor = Executor(config=config)
executor.run()
```

### Dynamic Configuration

```python
# Generate configuration dynamically
def create_config(data_path, synthesis_method):
    return {
        'Loader': {
            'load': {'filepath': data_path}
        },
        'Synthesizer': {
            'generate': {'method': synthesis_method}
        }
    }

# Use dynamic configuration
config = create_config('data.csv', 'sdv')
executor = Executor(config=config)
executor.run()
```

## Notes

- **Single Instance**: Each Executor instance manages one workflow; don't reuse across workflows
- **Execution Order**: Must call `run()` before `get_result()` and `get_timing()`
- **Configuration Immutability**: Cannot modify configuration after Executor creation
- **Thread Safety**: Executor is not thread-safe; use separate instances in multi-threaded environments
- **Resource Management**: Large-scale experiments may consume significant memory and time; plan resources carefully
- **Error Recovery**: Currently does not support resuming from breakpoints; need to re-execute entire workflow upon failure