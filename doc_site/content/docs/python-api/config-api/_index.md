---
title: "Config API"
weight: 32
---

Config is PETsARD's internal configuration management class, responsible for parsing configuration dictionaries and building module execution sequences.

{{< callout type="info" >}}
**Internal Use Only**: Config is primarily used internally by Executor. Users should interact with PETsARD through [`Executor`](../executor-api/) instead of using Config directly.
{{< /callout >}}

## Class Architecture

{{< mermaid-file="config-class-diagram.mmd" >}}

## Basic Usage

```python
from petsard.config import Config

# Create Config from dictionary
config_dict = {
    "Loader": {
        "load_data": {
            "filepath": "data.csv"
        }
    },
    "Synthesizer": {
        "generate": {
            "method": "sdv",
            "model": "GaussianCopula"
        }
    }
}

config = Config(config_dict)

# Config is typically used internally by Executor
from petsard import Executor
exec = Executor('config.yaml')  # Executor creates Config internally
```

## Constructor

### Syntax

```python
Config(config: dict)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `dict` | Yes | Configuration dictionary containing all module configurations |

### Return Value

Returns a Config instance with parsed configuration.

## Configuration Structure

Config expects a dictionary with the following structure:

```python
{
    "ModuleName": {
        "experiment_name": {
            "parameter1": "value1",
            "parameter2": "value2"
        }
    }
}
```

### Example

```python
config_dict = {
    "Loader": {
        "load_data": {"filepath": "data.csv"}
    },
    "Synthesizer": {
        "method_a": {"method": "sdv", "model": "GaussianCopula"},
        "method_b": {"method": "sdv", "model": "CTGAN"}
    }
}
```

## Core Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `config` | `queue.Queue` | Queue of instantiated Adapters |
| `module_flow` | `queue.Queue` | Queue of module names |
| `expt_flow` | `queue.Queue` | Queue of experiment names |
| `sequence` | `list` | Module execution order |
| `yaml` | `dict` | Processed configuration dictionary |

## Automatic Processing

### 1. Module Ordering

Config automatically arranges modules in the correct order:

```
Loader → Preprocessor → Splitter → Synthesizer → 
Postprocessor → Constrainer → Evaluator → Reporter
```

### 2. Splitter Expansion

When Splitter configuration includes `num_samples > 1`, Config automatically expands it:

```python
# Input
"Splitter": {
    "split_data": {
        "train_split_ratio": 0.8,
        "num_samples": 3
    }
}

# Automatically expanded to
"Splitter": {
    "split_data_[3-1]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-2]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-3]": {"train_split_ratio": 0.8, "num_samples": 1}
}
```

### 3. Cartesian Product Generation

Multiple experiments generate all combinations:

```python
config_dict = {
    "Loader": {
        "load_v1": {...},
        "load_v2": {...}
    },
    "Synthesizer": {
        "method_a": {...},
        "method_b": {...}
    }
}

# Generates 4 execution paths:
# load_v1 → method_a
# load_v1 → method_b
# load_v2 → method_a
# load_v2 → method_b
```

## Configuration Validation

Config validates experiment names to ensure they don't use reserved patterns:

```python
# ✓ Valid experiment names
"experiment_name"
"load_data"
"method_v2"

# ✗ Invalid experiment names (reserved pattern)
"experiment_[1]"    # Raises ConfigError
"load_data_[test]"  # Raises ConfigError
```

## Integration with Executor

Config is typically used through Executor:

```python
from petsard import Executor

# Executor internally:
# 1. Loads YAML file
# 2. Creates Config instance
# 3. Uses Config to build execution queue
exec = Executor('config.yaml')
exec.run()
```

## Notes

- **Internal Use**: Config is primarily for internal use by Executor
- **Recommended Practice**: Use YAML configuration files with Executor rather than Config directly
- **Naming Restrictions**: Experiment names cannot use `_[xxx]` pattern (reserved for system use)
- **Automatic Processing**: Splitter multi-sample configurations are automatically expanded
- **Execution Order**: Module order is automatically determined by Config
- **Memory Usage**: Large experiment combinations may consume significant memory