---
title: "Executor YAML"
type: docs
weight: 610
prev: docs/petsard-yaml
next: docs/petsard-yaml/loader-yaml
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

## Executor Parameters

Executor supports execution-related configuration options in the YAML file:

```yaml
Executor:
  log_output_type: "both"
  log_level: "INFO"
  log_dir: "./logs"
  log_filename: "PETsARD_{timestamp}.log"
```

### Parameter Descriptions

- **log_output_type** (`string`, optional): Log output location - `"stdout"`, `"file"`, or `"both"` (default: `"file"`)
- **log_level** (`string`, optional): Log level - `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, or `"CRITICAL"` (default: `"INFO"`)
- **log_dir** (`string`, optional): Log file storage directory (default: `"."`)
- **log_filename** (`string`, optional): Log filename template supporting `{timestamp}` placeholder (default: `"PETsARD_{timestamp}.log"`)

## Execution Flow

Executor executes modules in the following order:

1. **Loader** → 2. **Preprocessor** (optional) → 3. **Splitter** (optional) → 4. **Synthesizer** → 5. **Postprocessor** (optional) → 6. **Constrainer** (optional) → 7. **Evaluator** (optional) → 8. **Reporter** (optional)

## Internal Mechanisms

### Config

{{< callout type="info" >}}
Config is automatically managed by Executor. Configuring YAML for each module is configuring Config.
{{< /callout >}}

**Key Features**:
- Automatically arranges module execution order
- Validates experiment naming (cannot use `_[xxx]` pattern)
- Auto-expands Splitter when `num_samples > 1`
- Generates cartesian product for multi-experiment configurations

### Status

{{< callout type="info" >}}
Status is automatically managed by Executor. No YAML configuration needed - all tracking is automatic.
{{< /callout >}}

**Automatic Tracking**:
- Execution results for each module
- Schema metadata changes across modules
- Execution snapshots before/after each module
- Execution time for each module and step

**Access Methods**:
- `exec.get_result()` - Get execution results
- `exec.get_timing()` - Get execution time
- `exec.is_execution_completed()` - Check execution status

## Notes

- The `Executor` section can be placed anywhere in the YAML file
- All Executor parameters are optional
- Module execution order is automatically determined
- Config and Status are internal mechanisms, fully managed by Executor