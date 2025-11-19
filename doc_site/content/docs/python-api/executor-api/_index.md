---
title: "Executor API"
weight: 31
---

Executor is PETsARD's core orchestration module, responsible for parsing configuration, executing workflow modules in sequence, and providing result access.

## Class Architecture

{{< mermaid-file="executor-class-diagram.mmd" >}}

## Basic Usage

```python
from petsard import Executor

# Load configuration and execute
exec = Executor(config='config.yaml')
exec.run()

# Get results
results = exec.get_result()
timing = exec.get_timing()
```

## Constructor

### Syntax

```python
Executor(config: str)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `str` | Yes | Configuration input: YAML file path or YAML string |

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

## Configuration Options

Executor supports execution-related configuration options in the YAML file:

```yaml
Executor:
  log_output_type: "both"    # Log output location: "stdout", "file", "both"
  log_level: "INFO"          # Log level
  log_dir: "./logs"          # Log file directory
  log_filename: "PETsARD_{timestamp}.log"  # Log file name template

# Other module configurations
Loader:
  load_data:
    filepath: data.csv
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_output_type` | `str` | `"file"` | Log output location: `"stdout"`, `"file"`, `"both"` |
| `log_level` | `str` | `"INFO"` | Log level: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `log_dir` | `str` | `"."` | Log file storage directory |
| `log_filename` | `str` | `"PETsARD_{timestamp}.log"` | Log file name template (supports `{timestamp}` placeholder) |

## Methods

### run()

Execute the workflow based on configuration.

```python
exec = Executor(config='config.yaml')
exec.run()
```

**Note**: In v2.0.0, this method will return execution status (success/failed) instead of None.

### get_result()

Get execution results containing DataFrames and Schemas for all experiments.

```python
results = exec.get_result()

# Result structure
# {
#   'Loader[experiment_1]_Synthesizer[method_a]': {
#     'data': DataFrame,
#     'schema': Schema
#   },
#   ...
# }
```

### get_timing()

Get execution timing report showing time spent by each module and step.

```python
timing_df = exec.get_timing()
print(timing_df)
```

Returns a pandas DataFrame with timing information.

### is_execution_completed()

Check if workflow execution has completed.

```python
if exec.is_execution_completed():
    print("Execution completed")
    results = exec.get_result()
```

**Note**: This method will be deprecated in v2.0.0. Use the return value of `run()` instead.

### get_inferred_schema(module)

Get inferred Schema for specified module.

```python
# Get inferred Preprocessor Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    print(f"Inferred Schema: {inferred_schema.id}")
```

**Parameters**:
- `module` (str): Module name (e.g., 'Preprocessor')

**Returns**: Inferred Schema, or None if not exists

## Workflow Execution

Executor executes modules in the following order:

1. **Loader** - Data loading
2. **Preprocessor** - Data preprocessing (optional)
3. **Splitter** - Data splitting (optional)
4. **Synthesizer** - Data synthesis
5. **Postprocessor** - Data postprocessing (optional)
6. **Constrainer** - Constraint validation (optional)
7. **Evaluator** - Data evaluation (optional)
8. **Reporter** - Result reporting (optional)

## Internal Components

### ExecutorConfig

Configuration dataclass for Executor settings:

```python
@dataclass
class ExecutorConfig:
    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"
```

### Config

Configuration management class responsible for parsing YAML configuration and building execution sequence. See [`Config API`](../config-api/).

### Status

Status tracking class responsible for recording execution history and metadata changes. See [`Status API`](../status-api/).

## Multiple Experiments

Executor automatically handles combinations of multiple experiments:

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

This generates 4 experiment combinations:
- `Loader[experiment_1]_Synthesizer[method_a]`
- `Loader[experiment_1]_Synthesizer[method_b]`
- `Loader[experiment_2]_Synthesizer[method_a]`
- `Loader[experiment_2]_Synthesizer[method_b]`

## Notes

- **Input Type Detection**: Executor automatically detects whether `config` is a file path or YAML string
- **Configuration Validation**: Config automatically validates configuration content during initialization
- **Path Handling**: File paths support absolute and relative paths
- **Error Reporting**: Provides detailed error messages for configuration and YAML parsing errors
- **Logging**: Execution process generates detailed log records
- **Module Order**: Executor automatically executes modules in correct order
- **Single Instance**: Each Executor instance manages one workflow
- **Execution Order**: Must call `run()` before `get_result()` and `get_timing()`