---
title: "Config Configuration"
weight: 51
---

Config is responsible for parsing and managing YAML configuration files, converting declarative configurations into executable module sequences.

## Configuration Structure

YAML configuration files adopt a hierarchical structure, with each module containing one or more experiment configurations:

```yaml
ModuleName:
  experiment_name:
    parameter1: value1
    parameter2: value2
```

## Complete Configuration Example

```yaml
# Data loading
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
  load_custom:
    filepath: ./data/custom.csv

# Data preprocessing
Preprocessor:
  preprocess:
    method: default

# Data splitting
Splitter:
  split_train_test:
    train_split_ratio: 0.8
    num_samples: 3

# Data synthesis
Synthesizer:
  sdv_gaussian:
    method: sdv
    model: GaussianCopula
  sdv_ctgan:
    method: sdv
    model: CTGAN

# Data evaluation
Evaluator:
  evaluate_quality:
    method: sdmetrics-qualityreport
  evaluate_privacy:
    method: anonymeter-singlingout

# Results reporting
Reporter:
  save_synthetic:
    method: save_data
    source: Synthesizer
  generate_report:
    method: save_report
    granularity: global
```

## Module Execution Order

Config automatically arranges module execution in the following order:

1. **Loader** - Data loading
2. **Preprocessor** - Data preprocessing (optional)
3. **Splitter** - Data splitting (optional)
4. **Synthesizer** - Data synthesis
5. **Postprocessor** - Data postprocessing (optional)
6. **Constrainer** - Constraints (optional)
7. **Evaluator** - Data evaluation (optional)
8. **Reporter** - Results reporting (optional)

## Experiment Naming Rules

### Basic Rules

- Experiment names must be unique within the same module
- Can use letters, numbers, underscores, and hyphens
- Cannot end with `_[xxx]` pattern (reserved for system internal use)

### Valid Experiment Names

```yaml
Loader:
  load_data:           # ✓ Valid
    filepath: data.csv
  
  load-benchmark:      # ✓ Valid
    filepath: benchmark://adult-income
  
  load_custom_v2:      # ✓ Valid
    filepath: custom.csv
```

### Invalid Experiment Names

```yaml
Loader:
  load_data_[1]:       # ✗ Invalid: Reserved pattern
    filepath: data.csv
  
  load_[test]:         # ✗ Invalid: Reserved pattern
    filepath: test.csv
```

## Splitter Special Handling

When Splitter configuration includes `num_samples > 1`, Config automatically expands it into multiple experiments:

### Original Configuration

```yaml
Splitter:
  split_data:
    train_split_ratio: 0.8
    num_samples: 3
```

### After Automatic Expansion

```yaml
Splitter:
  split_data_[3-1]:
    train_split_ratio: 0.8
    num_samples: 1
  split_data_[3-2]:
    train_split_ratio: 0.8
    num_samples: 1
  split_data_[3-3]:
    train_split_ratio: 0.8
    num_samples: 1
```

This expansion process is automatic; users only need to specify the `num_samples` parameter in the configuration.

## Multi-Experiment Configuration

### Cartesian Product Execution

When multiple modules contain multiple experiments, Config generates cartesian product execution combinations:

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
```

Execution combinations:
1. `load_v1` → `method_a`
2. `load_v1` → `method_b`
3. `load_v2` → `method_a`
4. `load_v2` → `method_b`

### Result Naming

Results for each execution combination are stored with combination names:

```
Loader[load_v1]_Synthesizer[method_a]
Loader[load_v1]_Synthesizer[method_b]
Loader[load_v2]_Synthesizer[method_a]
Loader[load_v2]_Synthesizer[method_b]
```

## Configuration Validation

Config performs the following validations during initialization:

### 1. Structure Validation
- Check if configuration is a valid dictionary structure
- Verify module names are correct

### 2. Naming Validation
- Check if experiment names use reserved patterns
- Verify experiment names are unique within modules

### 3. Parameter Validation
- Parameter checking performed by each module's Adapter
- Validation occurs during Adapter instance creation

## Error Handling

### ConfigError

When configuration doesn't meet rules, `ConfigError` is raised:

```python
from petsard.exceptions import ConfigError

try:
    config = Config(config_dict)
except ConfigError as e:
    print(f"Configuration error: {e}")
```

Common errors:
- Using reserved experiment naming patterns
- Incorrect configuration structure
- Missing required parameters

## Notes

- **Execution Order**: Config automatically arranges correct module execution order; manual specification unnecessary
- **Experiment Combinations**: Multi-experiment configurations generate cartesian products; note execution time
- **Naming Conventions**: Follow experiment naming rules to avoid using reserved patterns
- **Splitter Expansion**: `num_samples` parameter automatically expands; manual configuration of multiple experiments unnecessary
- **Parameter Validation**: Recommended to test configuration with small-scale data first, then run complete workflow after confirming parameters are correct