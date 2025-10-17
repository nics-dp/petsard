---
title: "get_config()"
weight: 335
---

Retrieve the processor's configuration settings.

## Syntax

```python
def get_config(
    col: list = None
) -> dict
```

## Parameters

- **col** : list, optional
    - List of column names to retrieve configuration for
    - Default: `None` (returns configuration for all columns)

## Returns

- **dict**
    - Processor configuration dictionary
    - Structure: `{processor_type: {field_name: processor_instance}}`

## Description

The [`get_config()`](processor_get_config.md:1) method is used to view the processor's current configuration. It can be used to:

1. View processing methods for all columns
2. Check configuration for specific columns
3. Verify configuration meets expectations

## Basic Example

```python
from petsard import Loader, Processor

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Create processor
processor = Processor(metadata=schema)

# Get configuration for all columns
config = processor.get_config()

# View configuration
for proc_type, fields in config.items():
    print(f"\n{proc_type}:")
    for field, proc_obj in fields.items():
        if proc_obj is not None:
            print(f"  {field}: {type(proc_obj).__name__}")
```

## Get Configuration for Specific Columns

```python
from petsard import Processor

processor = Processor(metadata=schema)

# Get configuration only for specific columns
config = processor.get_config(col=['age', 'income', 'gender'])

print("Configuration for age, income, gender:")
for proc_type, fields in config.items():
    print(f"\n{proc_type}:")
    for field, proc_obj in fields.items():
        if proc_obj is not None:
            print(f"  {field}: {type(proc_obj).__name__}")
```

## Return Structure Example

```python
{
    'missing': {
        'age': <MissingMean instance>,
        'income': <MissingMean instance>,
        'gender': <MissingDrop instance>
    },
    'outlier': {
        'age': <OutlierIQR instance>,
        'income': <OutlierIQR instance>,
        'gender': None
    },
    'encoder': {
        'age': None,
        'income': None,
        'gender': <EncoderUniform instance>
    },
    'scaler': {
        'age': <ScalerStandard instance>,
        'income': <ScalerStandard instance>,
        'gender': None
    }
}
```

## Use Cases

### 1. Validate Configuration

```python
processor = Processor(metadata=schema, config=custom_config)
config = processor.get_config()

# Verify specific column uses correct processor
assert type(config['encoder']['gender']).__name__ == 'EncoderOneHot'
print("Configuration validation passed!")
```

### 2. Check Default Configuration

```python
# Use default configuration
processor = Processor(metadata=schema)
config = processor.get_config()

# View default processing for numerical fields
numerical_fields = ['age', 'income', 'hours_per_week']
for field in numerical_fields:
    print(f"{field}:")
    for proc_type in ['missing', 'outlier', 'scaler']:
        proc = config[proc_type][field]
        if proc:
            print(f"  {proc_type}: {type(proc).__name__}")
```

### 3. Compare Configuration Differences

```python
# Create two processors with different configurations
processor1 = Processor(metadata=schema)
processor2 = Processor(metadata=schema, config=custom_config)

config1 = processor1.get_config(col=['age'])
config2 = processor2.get_config(col=['age'])

print("Processor 1 configuration:")
for proc_type, fields in config1.items():
    if fields['age']:
        print(f"  {proc_type}: {type(fields['age']).__name__}")

print("\nProcessor 2 configuration:")
for proc_type, fields in config2.items():
    if fields['age']:
        print(f"  {proc_type}: {type(fields['age']).__name__}")
```

## Notes

- Returned configuration contains processor instances, not string names
- `None` values indicate that processor type is not applied to that column
- Can be called at any time, does not require calling [`fit()`](processor_fit.md:1) first
- Configuration updates after calling [`update_config()`](processor_update_config.md:1)
- Non-existent column names will be ignored in returned configuration
- Global transformation processors (e.g., `outlier_isolationforest`) apply to all columns