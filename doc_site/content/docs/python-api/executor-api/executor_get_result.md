---
title: "get_result()"
weight: 312
---

Get execution results, including DataFrames and Schema for all experiments.

## Syntax

```python
executor.get_result()
```

## Parameters

This method takes no parameters.

## Return Value

- **Type**: `dict`
- **Description**: Dictionary containing all experiment results

### Result Structure

```python
{
    'experiment_key': {
        'data': pd.DataFrame,      # Result DataFrame
        'schema': Schema           # Schema object
    },
    ...
}
```

### Experiment Key Format

Experiment keys are composed of module names and experiment names:

```
'ModuleName[experiment_name]_ModuleName[experiment_name]_...'
```

Example:
```
'Loader[load_data]_Synthesizer[generate]_Evaluator[assess]'
```

## Description

The `get_result()` method retrieves all results stored in the Status object after workflow execution. Each result includes:

- **data**: Result DataFrame containing the actual data
- **schema**: Schema object describing data structure and metadata

### Result Contents

| Field | Type | Description |
|-------|------|-------------|
| `data` | `pd.DataFrame` | Result data; may be original, synthetic, or processed data |
| `schema` | `Schema` | Schema object containing column information, data types, and metadata |

### When to Call

- **Before `run()`**: Will raise error; no results available
- **After `run()`**: Returns all experiment results
- **Multiple Calls**: Can be called multiple times; returns same results

## Basic Example

### Example 1: Single Experiment

```python
from petsard import Executor

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

executor = Executor(config=config)
executor.run()

# Get results
results = executor.get_result()

# Access result data
for exp_key, exp_result in results.items():
    print(f"Experiment: {exp_key}")
    print(f"  Data shape: {exp_result['data'].shape}")
    print(f"  Columns: {list(exp_result['data'].columns)}")
    print(f"  Schema: {exp_result['schema']}")
```

### Example 2: Multiple Experiments

```python
from petsard import Executor

config = {
    'Loader': {
        'dataset_a': {'filepath': 'data_a.csv'},
        'dataset_b': {'filepath': 'data_b.csv'}
    },
    'Synthesizer': {
        'method_1': {'method': 'sdv', 'model': 'GaussianCopula'},
        'method_2': {'method': 'sdv', 'model': 'CTGAN'}
    }
}

executor = Executor(config=config)
executor.run()

# Get all results (4 combinations)
results = executor.get_result()

print(f"Total experiments: {len(results)}")

# Iterate over all experiments
for exp_key, exp_result in results.items():
    data = exp_result['data']
    schema = exp_result['schema']

    print(f"\n{exp_key}")
    print(f"  Records: {len(data)}")
    print(f"  Columns: {len(data.columns)}")
    print(f"  Memory: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

### Example 3: Result Validation

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

results = executor.get_result()

# Validate results
for exp_key, exp_result in results.items():
    # Check required fields
    assert 'data' in exp_result, f"Missing data: {exp_key}"
    assert 'schema' in exp_result, f"Missing schema: {exp_key}"

    data = exp_result['data']
    schema = exp_result['schema']

    # Validate data
    assert not data.empty, f"Empty data: {exp_key}"
    assert len(data.columns) > 0, f"No columns: {exp_key}"

    # Validate schema
    assert schema is not None, f"Invalid schema: {exp_key}"

    print(f"✓ {exp_key} validation passed")
```

## Advanced Usage

### Example 4: Extract Specific Experiment

```python
from petsard import Executor

config = {
    'Loader': {
        'load_v1': {'filepath': 'data_v1.csv'},
        'load_v2': {'filepath': 'data_v2.csv'}
    },
    'Synthesizer': {
        'gaussian': {'method': 'sdv', 'model': 'GaussianCopula'},
        'ctgan': {'method': 'sdv', 'model': 'CTGAN'}
    }
}

executor = Executor(config=config)
executor.run()

results = executor.get_result()

# Extract specific experiment
target_key = 'Loader[load_v1]_Synthesizer[ctgan]'
if target_key in results:
    target_result = results[target_key]
    data = target_result['data']
    schema = target_result['schema']

    print(f"Target experiment: {target_key}")
    print(f"Data shape: {data.shape}")
else:
    print(f"Experiment not found: {target_key}")

# Or use pattern matching
for exp_key in results.keys():
    if 'ctgan' in exp_key.lower():
        print(f"CTGAN experiment: {exp_key}")
        print(f"  Rows: {len(results[exp_key]['data'])}")
```

### Example 5: Result Comparison

```python
from petsard import Executor
import pandas as pd

config = {
    'Loader': {
        'load': {'filepath': 'data.csv'}
    },
    'Synthesizer': {
        'gaussian': {'method': 'sdv', 'model': 'GaussianCopula'},
        'ctgan': {'method': 'sdv', 'model': 'CTGAN'},
        'tvae': {'method': 'sdv', 'model': 'TVAE'}
    }
}

executor = Executor(config=config)
executor.run()

results = executor.get_result()

# Compare statistics of different methods
comparison = []
for exp_key, exp_result in results.items():
    data = exp_result['data']

    stats = {
        'experiment': exp_key,
        'rows': len(data),
        'columns': len(data.columns),
        'numeric_cols': len(data.select_dtypes(include='number').columns),
        'missing_values': data.isnull().sum().sum(),
        'memory_mb': data.memory_usage(deep=True).sum() / 1024**2
    }
    comparison.append(stats)

comparison_df = pd.DataFrame(comparison)
print("\nMethod Comparison:")
print(comparison_df)
```

### Example 6: Save Results

```python
from petsard import Executor
import pandas as pd
from pathlib import Path

executor = Executor(config='config.yaml')
executor.run()

results = executor.get_result()

# Create output directory
output_dir = Path('output')
output_dir.mkdir(exist_ok=True)

# Save all results
for exp_key, exp_result in results.items():
    data = exp_result['data']
    schema = exp_result['schema']

    # Clean experiment name for filename
    filename = exp_key.replace('[', '_').replace(']', '').replace('_', '-')

    # Save data
    data_path = output_dir / f"{filename}.csv"
    data.to_csv(data_path, index=False)

    # Save schema info
    schema_path = output_dir / f"{filename}_schema.txt"
    with open(schema_path, 'w') as f:
        f.write(f"Experiment: {exp_key}\n")
        f.write(f"Rows: {len(data)}\n")
        f.write(f"Columns: {len(data.columns)}\n")
        f.write(f"Schema: {schema}\n")

    print(f"✓ Saved: {filename}")
```

### Example 7: Result Statistics

```python
from petsard import Executor
import numpy as np

executor = Executor(config='config.yaml')
executor.run()

results = executor.get_result()

# Calculate statistics for each experiment
for exp_key, exp_result in results.items():
    data = exp_result['data']

    print(f"\n{exp_key}")
    print("=" * 60)

    # Numeric columns
    numeric_data = data.select_dtypes(include=[np.number])
    if not numeric_data.empty:
        print("\nNumeric Statistics:")
        print(numeric_data.describe())

    # Categorical columns
    categorical_data = data.select_dtypes(include=['object', 'category'])
    if not categorical_data.empty:
        print("\nCategorical Statistics:")
        for col in categorical_data.columns:
            print(f"  {col}: {data[col].nunique()} unique values")
            print(f"    Top 3: {data[col].value_counts().head(3).to_dict()}")
```

## Result DataFrame Details

### Data Types

The result DataFrame may contain various data types:

```python
results = executor.get_result()
exp_result = results[list(results.keys())[0]]
data = exp_result['data']

# Check data types
print("Column Types:")
print(data.dtypes)

# Get numeric columns
numeric_cols = data.select_dtypes(include='number').columns
print(f"\nNumeric columns: {list(numeric_cols)}")

# Get categorical columns
categorical_cols = data.select_dtypes(include=['object', 'category']).columns
print(f"Categorical columns: {list(categorical_cols)}")
```

### Data Operations

Result DataFrames support all pandas operations:

```python
results = executor.get_result()
exp_result = results[list(results.keys())[0]]
data = exp_result['data']

# Filtering
filtered_data = data[data['age'] > 30]

# Grouping
grouped_data = data.groupby('category').mean()

# Merging
# merged_data = pd.merge(data, other_data, on='key')

# Sorting
sorted_data = data.sort_values('column_name')
```

## Schema Object Details

### Access Schema Information

```python
results = executor.get_result()
exp_result = results[list(results.keys())[0]]
schema = exp_result['schema']

# Get column information
for column in schema.columns:
    print(f"Column: {column.name}")
    print(f"  Type: {column.dtype}")
    print(f"  Metadata: {column.metadata}")
```

### Schema-DataFrame Consistency

Schema describes DataFrame structure:

```python
results = executor.get_result()
exp_result = results[list(results.keys())[0]]
data = exp_result['data']
schema = exp_result['schema']

# Verify consistency
assert len(schema.columns) == len(data.columns)
assert set(col.name for col in schema.columns) == set(data.columns)

print("Schema and DataFrame are consistent")
```

## Error Handling

### Example 8: Handle Missing Results

```python
from petsard import Executor

try:
    executor = Executor(config='config.yaml')

    # Attempt to get results before running
    results = executor.get_result()  # May raise error

except Exception as e:
    print(f"Error: {e}")
    print("Please run executor.run() first")
```

### Example 9: Validate Execution Before Getting Results

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Check if execution completed
if executor.is_execution_completed():
    results = executor.get_result()
    print(f"Retrieved {len(results)} results")
else:
    print("Execution incomplete; no results available")
```

## Notes

- **Execution Required**: Must call `run()` before `get_result()`, otherwise may raise error
- **Memory Usage**: All results stored in memory; may consume significant memory for large datasets
- **Result Immutability**: Returned dictionary is a reference; modifications affect stored results
- **Schema Validity**: Schema always matches corresponding DataFrame structure
- **Experiment Keys**: Keys are automatically generated; cannot be customized
- **Result Persistence**: Results exist only in Executor instance; not automatically saved
- **Multiple Calls**: Calling multiple times returns same results; no additional computation

## Related Methods

- `run()`: Execute workflow
- `get_timing()`: Get execution time report
- `is_execution_completed()`: Check execution status
- `get_inferred_schema()`: Get inferred Schema