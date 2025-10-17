---
title: "Config API (WIP)"
weight: 32
---

Config is the configuration management module of PETsARD, responsible for parsing YAML configuration files or dictionaries, validating configuration content, and providing a configuration query interface.

## Class Architecture

{{< include file="config-class-diagram.mmd" >}}

## Design Philosophy

Config follows the principle of separation of concerns:

### 1. Configuration Parsing
- Support YAML file loading
- Support dictionary format configuration
- Automatic format detection and parsing

### 2. Configuration Validation
- Validate configuration structure
- Check required fields
- Verify parameter validity

### 3. Configuration Query
- Provide module configuration access
- Support experiment name queries
- Facilitate configuration traversal

## Basic Usage

### Import Module

```python
from petsard import Config
```

### Create Config Instance

```python
# From YAML file
config = Config(config='path/to/config.yaml')

# From dictionary
config_dict = {
    'Loader': {
        'load_data': {
            'filepath': 'data.csv'
        }
    }
}
config = Config(config=config_dict)
```

### Query Configuration

```python
# Get module configuration
loader_config = config.get_module_config('Loader')

# Get experiment names
experiments = config.get_experiment_names('Loader')

# Validate configuration
is_valid = config.validate()
```

## Constructor (`__init__`)

Creates a Config instance and parses configuration.

### Syntax

```python
Config(config)
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `config` | `str` or `dict` | Yes | - | YAML file path or configuration dictionary |

### Return Value

Returns a Config instance with parsed configuration.

### Usage Examples

**Example 1: Load from YAML file**

```python
from petsard import Config

# Load configuration
config = Config(config='workflow.yaml')
print("Configuration loaded successfully")
```

**Example 2: Use configuration dictionary**

```python
from petsard import Config

# Define configuration
config_dict = {
    'Loader': {
        'load_csv': {
            'filepath': 'data.csv',
            'delimiter': ','
        }
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'GaussianCopula'
        }
    }
}

# Create Config
config = Config(config=config_dict)
```

**Example 3: Error Handling**

```python
from petsard import Config

try:
    config = Config(config='config.yaml')
    print("Configuration valid")
except FileNotFoundError:
    print("Configuration file not found")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

### Notes

- **Path Support**: Supports both absolute and relative paths
- **Format Detection**: Automatically detects YAML or dictionary format
- **Immediate Parsing**: Configuration parsed during initialization
- **Validation**: Basic validation performed automatically
- **Immutability**: Configuration cannot be modified after creation

## Configuration Structure

### Standard Configuration Format

```yaml
ModuleName:
  experiment_name:
    parameter1: value1
    parameter2: value2
    ...
```

### Multi-Module Configuration

```yaml
Loader:
  load_data:
    filepath: data.csv

Preprocessor:
  preprocess:
    scaling:
      age: minmax
      income: standard

Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula

Evaluator:
  assess:
    metrics:
      - statistical_similarity
      - privacy_metrics
```

### Multiple Experiments

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

## Configuration Query Methods

### Get Module Configuration

```python
config = Config(config='config.yaml')

# Get entire module configuration
loader_config = config.get_module_config('Loader')

# Returns:
# {
#   'experiment_1': {'filepath': 'data1.csv'},
#   'experiment_2': {'filepath': 'data2.csv'}
# }
```

### Get Experiment Names

```python
config = Config(config='config.yaml')

# Get all experiment names for a module
experiments = config.get_experiment_names('Loader')

# Returns: ['experiment_1', 'experiment_2']
```

### Validate Configuration

```python
config = Config(config='config.yaml')

# Validate configuration
is_valid = config.validate()

if is_valid:
    print("Configuration is valid")
else:
    print("Configuration has errors")
```

## Configuration Validation

### Validation Rules

Config validates the following:

1. **Structure Validation**
   - Correct YAML/dictionary format
   - Valid module names
   - Proper nesting structure

2. **Required Fields**
   - Each module has at least one experiment
   - Each experiment has required parameters

3. **Parameter Validation**
   - Parameter types are correct
   - Values are within valid ranges
   - Required parameters are present

### Validation Examples

**Example 1: Valid Configuration**

```python
from petsard import Config

config_dict = {
    'Loader': {
        'load_data': {
            'filepath': 'data.csv'
        }
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv',
            'model': 'GaussianCopula'
        }
    }
}

config = Config(config=config_dict)
print(f"Valid: {config.validate()}")  # True
```

**Example 2: Invalid Configuration**

```python
from petsard import Config

# Missing required parameters
config_dict = {
    'Loader': {
        'load_data': {}  # Missing 'filepath'
    }
}

try:
    config = Config(config=config_dict)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Configuration Access Patterns

### Pattern 1: Iterate Over Modules

```python
config = Config(config='config.yaml')

# Access raw configuration
raw_config = config.raw_config

for module_name, module_config in raw_config.items():
    print(f"\nModule: {module_name}")
    for exp_name, exp_config in module_config.items():
        print(f"  Experiment: {exp_name}")
        print(f"    Config: {exp_config}")
```

### Pattern 2: Check Module Existence

```python
config = Config(config='config.yaml')

modules = ['Loader', 'Preprocessor', 'Synthesizer', 'Evaluator']

for module in modules:
    if module in config.raw_config:
        experiments = config.get_experiment_names(module)
        print(f"{module}: {len(experiments)} experiments")
    else:
        print(f"{module}: Not configured")
```

### Pattern 3: Extract Specific Configuration

```python
config = Config(config='config.yaml')

# Get specific experiment configuration
loader_config = config.get_module_config('Loader')
if 'load_data' in loader_config:
    load_config = loader_config['load_data']
    filepath = load_config.get('filepath')
    print(f"Data file: {filepath}")
```

## Integration with Executor

Config is primarily used internally by Executor:

```python
from petsard import Executor

# Executor creates and uses Config internally
executor = Executor(config='config.yaml')

# Access Config through Executor
config = executor.config

# Query configuration
loader_config = config.get_module_config('Loader')
```

## Advanced Usage

### Dynamic Configuration

```python
from petsard import Config

def create_config(data_path, method, model):
    """Dynamically create configuration"""
    return Config(config={
        'Loader': {
            'load': {'filepath': data_path}
        },
        'Synthesizer': {
            'generate': {
                'method': method,
                'model': model
            }
        }
    })

# Use dynamic configuration
config = create_config('data.csv', 'sdv', 'GaussianCopula')
```

### Configuration Merging

```python
from petsard import Config

# Base configuration
base_config = {
    'Loader': {
        'load': {'filepath': 'data.csv'}
    }
}

# Additional configuration
synth_config = {
    'Synthesizer': {
        'generate': {'method': 'sdv', 'model': 'GaussianCopula'}
    }
}

# Merge configurations
merged = {**base_config, **synth_config}
config = Config(config=merged)
```

### Configuration Templates

```python
from petsard import Config

# Define templates
TEMPLATES = {
    'basic': {
        'Loader': {'load': {'filepath': 'data.csv'}},
        'Synthesizer': {'generate': {'method': 'sdv'}}
    },
    'advanced': {
        'Loader': {'load': {'filepath': 'data.csv'}},
        'Preprocessor': {'preprocess': {'scaling': {'age': 'minmax'}}},
        'Synthesizer': {'generate': {'method': 'sdv'}},
        'Evaluator': {'assess': {'metrics': ['quality_report']}}
    }
}

# Use template
config = Config(config=TEMPLATES['advanced'])
```

## Error Handling

### Common Errors

**1. File Not Found**

```python
from petsard import Config

try:
    config = Config(config='nonexistent.yaml')
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

**2. Invalid YAML**

```python
from petsard import Config

try:
    config = Config(config='invalid.yaml')
except ValueError as e:
    print(f"Invalid YAML: {e}")
```

**3. Invalid Structure**

```python
from petsard import Config

try:
    config = Config(config={'invalid': 'structure'})
except ValueError as e:
    print(f"Invalid configuration structure: {e}")
```

## Best Practices

### 1. Use YAML Files for Complex Configurations

```yaml
# config.yaml - easier to read and maintain
Loader:
  load_data:
    filepath: data.csv
    delimiter: ","
    encoding: utf-8

Preprocessor:
  preprocess:
    scaling:
      age: minmax
      income: standard
    encoding:
      education: onehot
```

### 2. Validate Before Use

```python
from petsard import Config

config = Config(config='config.yaml')

# Validate before proceeding
if not config.validate():
    raise ValueError("Invalid configuration")

# Proceed with valid configuration
loader_config = config.get_module_config('Loader')
```

### 3. Use Descriptive Experiment Names

```yaml
# Good: Descriptive names
Loader:
  load_training_data:
    filepath: train.csv
  load_validation_data:
    filepath: valid.csv

# Avoid: Generic names
Loader:
  exp1:
    filepath: train.csv
  exp2:
    filepath: valid.csv
```

## Notes

- **Immutability**: Configuration cannot be modified after creation
- **Thread Safety**: Config instances are thread-safe for reading
- **Memory Usage**: Entire configuration stored in memory
- **File Watching**: Does not automatically reload configuration file changes
- **Validation Timing**: Basic validation performed during initialization
- **Error Messages**: Provides detailed error messages for invalid configurations

## See Also

- [Executor API](../executor-api)
- [Status API](../status-api)
- [YAML Configuration Guide](../../petsard-yaml)