---
title: "Executor YAML (WIP)"
weight: 50
---

YAML configuration file format for the Executor module, responsible for coordinating the entire PETsARD workflow execution.

## Basic Usage

```python
from petsard import Executor

# Using YAML configuration file
exec = Executor(config='config.yaml')
exec.run()

# Get results
results = exec.get_result()
timing = exec.get_timing()
```

## Main Parameters

Executor supports execution-related configuration options in the YAML file:

```yaml
Executor:
  log_output_type: "both"    # Log output location
  log_level: "INFO"          # Log level
  log_dir: "./logs"          # Log file directory
  log_filename: "PETsARD_{timestamp}.log"  # Log filename template
```

### Parameter Descriptions

- **log_output_type** (`string`, optional)
  - Log output location
  - Options:
    - `"stdout"`: Output to terminal
    - `"file"`: Output to file (default)
    - `"both"`: Output to both terminal and file
  - Default: `"file"`

- **log_level** (`string`, optional)
  - Log level
  - Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`
  - Default: `"INFO"`

- **log_dir** (`string`, optional)
  - Log file storage directory
  - Default: `"."`(current directory)

- **log_filename** (`string`, optional)
  - Log filename template
  - Supports `{timestamp}` placeholder, automatically replaced with execution time
  - Default: `"PETsARD_{timestamp}.log"`

## Complete Configuration Example

```yaml
# Executor settings (optional)
Executor:
  log_output_type: "both"
  log_level: "DEBUG"
  log_dir: "./logs"
  log_filename: "experiment_{timestamp}.log"

# Data loading
Loader:
  load_data:
    filepath: benchmark://adult-income

# Data splitting
Splitter:
  split_data:
    train_split_ratio: 0.8
    num_samples: 3

# Data synthesis
Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula

# Data evaluation
Evaluator:
  evaluate:
    method: sdmetrics-qualityreport

# Results reporting
Reporter:
  save_results:
    method: save_data
    source: Synthesizer
```

## Execution Flow

Executor executes modules in the following order:

1. **Loader** - Data loading
2. **Preprocessor** (optional) - Data preprocessing
3. **Splitter** (optional) - Data splitting
4. **Synthesizer** - Data synthesis
5. **Postprocessor** (optional) - Data postprocessing
6. **Constrainer** (optional) - Constraint application
7. **Evaluator** (optional) - Data evaluation
8. **Reporter** (optional) - Results reporting

## Notes

- **Executor Section Position**: The `Executor` section can be placed anywhere in the YAML file without affecting functionality
- **Optional Parameters**: All Executor parameters are optional; defaults are used if not specified
- **Log Files**: Using `file` or `both` mode automatically creates log directories
- **Timestamp Format**: `{timestamp}` is replaced with `YYYY-MM-DD_HH-MM-SS` format
- **Module Order**: Executor automatically executes modules in the correct order; manual specification is unnecessary