---
title: "get_changes()"
weight: 337
---

Compare differences between current configuration and default configuration.

## Syntax

```python
def get_changes() -> pd.DataFrame
```

## Parameters

None

## Returns

- **pd.DataFrame**
    - DataFrame recording configuration differences
    - Columns: `processor` (processor type), `col` (column name), `current` (current config), `default` (default config)

## Description

The [`get_changes()`](processor_get_changes.md:1) method is used to view which configurations have been customized. This method will:

1. Compare current configuration with default configuration
2. List all differences
3. Return results in DataFrame format

This is very useful for debugging and documentation.

## Basic Example

```python
from petsard import Loader, Processor

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Create processor and update configuration
processor = Processor(metadata=schema)
processor.update_config({
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    },
    'scaler': {
        'age': 'scaler_minmax'
    }
})

# View which configurations were modified
changes = processor.get_changes()
print(changes)
```

## Output Example

```
  processor      col           current         default
0   missing      age    MissingMedian     MissingMean
1   encoder   gender   EncoderOneHot  EncoderUniform
2    scaler      age    ScalerMinMax  ScalerStandard
```

## Check Changes for Specific Processor Type

```python
processor = Processor(metadata=schema, config=custom_config)
changes = processor.get_changes()

# View only encoder changes
encoder_changes = changes[changes['processor'] == 'encoder']
print("Encoder changes:")
print(encoder_changes)

# View changes for specific column
age_changes = changes[changes['col'] == 'age']
print("\nChanges for age column:")
print(age_changes)
```

## Count Number of Changes

```python
changes = processor.get_changes()

print(f"Total {len(changes)} configurations modified")
print(f"Modified processor types: {changes['processor'].unique()}")
print(f"Affected columns: {changes['col'].unique()}")
```

## Export Change Records

```python
changes = processor.get_changes()

# Save as CSV
changes.to_csv('processor_config_changes.csv', index=False)

# Or save as Markdown table
print(changes.to_markdown(index=False))
```

## Use Cases

### 1. Validate Custom Configuration

```python
# Ensure important columns use custom configuration
processor = Processor(metadata=schema, config=custom_config)
changes = processor.get_changes()

# Check if age uses median imputation
age_missing = changes[
    (changes['col'] == 'age') & 
    (changes['processor'] == 'missing')
]
assert 'Median' in age_missing['current'].values[0]
print("Age column configuration validation passed!")
```

### 2. Documentation

```python
# Record configuration used in experiment
processor = Processor(metadata=schema, config=experiment_config)
changes = processor.get_changes()

print("Experiment configuration record:")
print(f"Date: {datetime.now()}")
print(f"Number of modifications: {len(changes)}")
print("\nDetailed changes:")
print(changes.to_string(index=False))
```

### 3. Compare Different Configurations

```python
# Create two processors with different configurations
processor1 = Processor(metadata=schema, config=config1)
processor2 = Processor(metadata=schema, config=config2)

changes1 = processor1.get_changes()
changes2 = processor2.get_changes()

print("Configuration 1 changes:")
print(changes1)
print("\nConfiguration 2 changes:")
print(changes2)
```

### 4. Detect Unexpected Configuration Changes

```python
processor = Processor(metadata=schema)

# Perform some operations...
processor.update_config(some_config)

# Check for unexpected changes
changes = processor.get_changes()
unexpected_cols = ['critical_field1', 'critical_field2']

unexpected_changes = changes[changes['col'].isin(unexpected_cols)]
if not unexpected_changes.empty:
    print("Warning: Critical column configurations were modified!")
    print(unexpected_changes)
```

## Output Format

DataFrame contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `processor` | Processor type | `'missing'`, `'encoder'`, `'scaler'` |
| `col` | Column name | `'age'`, `'gender'`, `'income'` |
| `current` | Currently used processor | `'MissingMedian'`, `'EncoderOneHot'` |
| `default` | Default processor | `'MissingMean'`, `'EncoderUniform'` |

## Notes

- Only displays items different from default configuration
- Returns empty DataFrame if there are no changes
- Can be called at any time, does not require calling [`fit()`](processor_fit.md:1) first
- Both current and default configurations show class names (not instances)
- If a column's processor is set to `None`, it may also appear in the change list
- Global transformation processors (e.g., `outlier_isolationforest`) affect display for all columns