---
title: "get_inferred_schema()"
weight: 315
---

Get inferred Schema based on Loader, Preprocessor, and Postprocessor configuration.

## Syntax

```python
executor.get_inferred_schema()
```

## Parameters

This method takes no parameters.

## Return Value

- **Type**: `dict`
- **Description**: Dictionary containing inferred Schema for each experiment combination

### Return Structure

```python
{
    'experiment_key': Schema,
    ...
}
```

Where `experiment_key` follows the format: `'ModuleName[experiment]_ModuleName[experiment]_...'`

## Description

The `get_inferred_schema()` method analyzes the configuration of Loader, Preprocessor, and Postprocessor to infer the final Schema that will be passed to Synthesizer. This is particularly useful for:

- Understanding data transformations before execution
- Validating preprocessing configurations
- Debugging Schema-related issues
- Planning data synthesis strategies

### Schema Inference Process

1. **Load Original Schema**: Get Schema from Loader configuration
2. **Apply Preprocessing**: Infer Schema changes from Preprocessor configuration
3. **Apply Postprocessing**: Consider Postprocessor transformations (if applicable)
4. **Generate Final Schema**: Produce Schema that Synthesizer will receive

### When to Use

- **Before Execution**: Preview Schema without running full workflow
- **Configuration Validation**: Verify transformations produce expected Schema
- **Debugging**: Troubleshoot Schema mismatches
- **Documentation**: Generate Schema documentation for data pipelines

## Basic Example

### Example 1: Simple Schema Inference

```python
from petsard import Executor

config = {
    'Loader': {
        'load_data': {
            'filepath': 'data.csv'
        }
    },
    'Preprocessor': {
        'preprocess': {
            'scaling': {
                'age': 'minmax',
                'income': 'standard'
            },
            'encoding': {
                'education': 'onehot'
            }
        }
    },
    'Synthesizer': {
        'generate': {
            'method': 'sdv'
        }
    }
}

executor = Executor(config=config)

# Get inferred Schema before execution
inferred_schemas = executor.get_inferred_schema()

for exp_key, schema in inferred_schemas.items():
    print(f"\nExperiment: {exp_key}")
    print(f"Schema columns: {len(schema.columns)}")
    for col in schema.columns:
        print(f"  - {col.name}: {col.dtype}")
```

### Example 2: Compare Original and Inferred Schema

```python
from petsard import Executor

executor = Executor(config='config.yaml')

# Get inferred Schema
inferred_schemas = executor.get_inferred_schema()

# Execute to get actual Schema
executor.run()
results = executor.get_result()

# Compare
for exp_key in inferred_schemas.keys():
    inferred = inferred_schemas[exp_key]
    actual = results[exp_key]['schema']
    
    print(f"\nExperiment: {exp_key}")
    print(f"Inferred columns: {len(inferred.columns)}")
    print(f"Actual columns: {len(actual.columns)}")
    
    # Should match
    assert len(inferred.columns) == len(actual.columns)
    print("✓ Schema matches")
```

### Example 3: Validate Preprocessing Configuration

```python
from petsard import Executor

config = {
    'Loader': {
        'load': {'filepath': 'data.csv'}
    },
    'Preprocessor': {
        'preprocess': {
            'scaling': {
                'age': 'minmax',
                'salary': 'standard'
            },
            'encoding': {
                'gender': 'label',
                'city': 'onehot'
            }
        }
    },
    'Synthesizer': {
        'generate': {'method': 'sdv'}
    }
}

executor = Executor(config=config)
inferred_schemas = executor.get_inferred_schema()

# Validate transformations
for exp_key, schema in inferred_schemas.items():
    print(f"\n{exp_key}")
    
    # Check if scaled columns are numeric
    for col in schema.columns:
        if 'age' in col.name or 'salary' in col.name:
            assert col.dtype in ['int', 'float'], \
                f"Scaled column {col.name} should be numeric"
            print(f"✓ {col.name} is numeric (scaled)")
        
        # Check if onehot encoded columns exist
        if col.name.startswith('city_'):
            assert col.dtype in ['int', 'bool'], \
                f"Onehot column {col.name} should be binary"
            print(f"✓ {col.name} is binary (onehot)")
```

## Advanced Usage

### Example 4: Multi-Experiment Schema Analysis

```python
from petsard import Executor

config = {
    'Loader': {
        'data_v1': {'filepath': 'data_v1.csv'},
        'data_v2': {'filepath': 'data_v2.csv'}
    },
    'Preprocessor': {
        'light': {
            'scaling': {'age': 'minmax'}
        },
        'heavy': {
            'scaling': {'age': 'minmax', 'income': 'standard'},
            'encoding': {'education': 'onehot'}
        }
    },
    'Synthesizer': {
        'generate': {'method': 'sdv'}
    }
}

executor = Executor(config=config)
inferred_schemas = executor.get_inferred_schema()

# Analyze each combination
print(f"Total combinations: {len(inferred_schemas)}")

for exp_key, schema in inferred_schemas.items():
    print(f"\n{exp_key}")
    print(f"  Columns: {len(schema.columns)}")
    
    # Categorize columns
    numeric_cols = [col for col in schema.columns if col.dtype in ['int', 'float']]
    categorical_cols = [col for col in schema.columns if col.dtype in ['str', 'object']]
    
    print(f"  Numeric: {len(numeric_cols)}")
    print(f"  Categorical: {len(categorical_cols)}")
```

### Example 5: Export Schema Documentation

```python
from petsard import Executor
import json
from pathlib import Path

executor = Executor(config='config.yaml')
inferred_schemas = executor.get_inferred_schema()

# Create documentation directory
doc_dir = Path('schema_docs')
doc_dir.mkdir(exist_ok=True)

# Export each schema
for exp_key, schema in inferred_schemas.items():
    # Create filename from experiment key
    filename = exp_key.replace('[', '_').replace(']', '').replace('_', '-')
    
    # Prepare schema documentation
    schema_doc = {
        'experiment': exp_key,
        'columns': []
    }
    
    for col in schema.columns:
        col_info = {
            'name': col.name,
            'dtype': col.dtype,
            'metadata': col.metadata if hasattr(col, 'metadata') else {}
        }
        schema_doc['columns'].append(col_info)
    
    # Save to JSON
    output_path = doc_dir / f'{filename}_schema.json'
    with open(output_path, 'w') as f:
        json.dump(schema_doc, f, indent=2)
    
    print(f"✓ Exported: {filename}_schema.json")
```

### Example 6: Schema-Based Configuration Validation

```python
from petsard import Executor

def validate_preprocessing_config(config):
    """Validate preprocessing configuration against Schema"""
    executor = Executor(config=config)
    
    try:
        inferred_schemas = executor.get_inferred_schema()
        
        # Check if all experiments have valid Schema
        if len(inferred_schemas) == 0:
            return False, "No schemas inferred"
        
        for exp_key, schema in inferred_schemas.items():
            # Validate schema has columns
            if len(schema.columns) == 0:
                return False, f"Empty schema for {exp_key}"
            
            # Validate data types
            for col in schema.columns:
                if col.dtype not in ['int', 'float', 'str', 'object', 'bool', 'datetime']:
                    return False, f"Invalid dtype {col.dtype} for {col.name}"
        
        return True, "Validation passed"
        
    except Exception as e:
        return False, str(e)

# Use validation
config = {
    'Loader': {'load': {'filepath': 'data.csv'}},
    'Preprocessor': {'preprocess': {'scaling': {'age': 'minmax'}}},
    'Synthesizer': {'generate': {'method': 'sdv'}}
}

valid, message = validate_preprocessing_config(config)
print(f"Valid: {valid}, Message: {message}")
```

### Example 7: Compare Different Preprocessing Strategies

```python
from petsard import Executor

# Define multiple preprocessing strategies
strategies = {
    'minimal': {
        'scaling': {'age': 'minmax'}
    },
    'standard': {
        'scaling': {'age': 'minmax', 'income': 'standard'},
        'encoding': {'education': 'label'}
    },
    'comprehensive': {
        'scaling': {'age': 'minmax', 'income': 'standard', 'score': 'robust'},
        'encoding': {'education': 'onehot', 'city': 'onehot'}
    }
}

# Compare schemas for each strategy
for strategy_name, preprocessing_config in strategies.items():
    config = {
        'Loader': {'load': {'filepath': 'data.csv'}},
        'Preprocessor': {'preprocess': preprocessing_config},
        'Synthesizer': {'generate': {'method': 'sdv'}}
    }
    
    executor = Executor(config=config)
    inferred_schemas = executor.get_inferred_schema()
    
    for exp_key, schema in inferred_schemas.items():
        print(f"\nStrategy: {strategy_name}")
        print(f"  Total columns: {len(schema.columns)}")
        print(f"  Column names: {[col.name for col in schema.columns]}")
```

## Schema Inference Details

### Scaling Transformations

Scaling operations preserve column names and data types:

```python
# Original: age (int)
# After minmax scaling: age (float)

config = {
    'Preprocessor': {
        'preprocess': {
            'scaling': {
                'age': 'minmax',      # → age (float)
                'income': 'standard'   # → income (float)
            }
        }
    }
}
```

### Encoding Transformations

Encoding operations may create new columns:

```python
# Original: education (str)
# After onehot encoding: education_HS, education_BS, education_MS, ...

config = {
    'Preprocessor': {
        'preprocess': {
            'encoding': {
                'education': 'onehot',  # → multiple binary columns
                'gender': 'label'       # → gender (int)
            }
        }
    }
}
```

### Schema Column Structure

Each column in the inferred Schema contains:

```python
column.name        # Column name
column.dtype       # Data type
column.metadata    # Additional metadata (if available)
```

## Use Cases

### Use Case 1: Pre-Execution Validation

```python
# Validate Schema before expensive execution
executor = Executor(config='config.yaml')
schemas = executor.get_inferred_schema()

# Check if expected columns exist
for exp_key, schema in schemas.items():
    required_cols = ['age', 'income', 'education']
    actual_cols = [col.name for col in schema.columns]
    
    missing = set(required_cols) - set(actual_cols)
    if missing:
        print(f"Warning: Missing columns in {exp_key}: {missing}")
    else:
        print(f"✓ All required columns present in {exp_key}")
```

### Use Case 2: Schema Documentation Generation

```python
# Generate human-readable Schema documentation
executor = Executor(config='config.yaml')
schemas = executor.get_inferred_schema()

for exp_key, schema in schemas.items():
    print(f"\n## {exp_key}")
    print("\n| Column | Type | Description |")
    print("|--------|------|-------------|")
    
    for col in schema.columns:
        print(f"| {col.name} | {col.dtype} | Inferred from preprocessing |")
```

### Use Case 3: Configuration Debugging

```python
# Debug why Synthesizer might fail
executor = Executor(config='config.yaml')
schemas = executor.get_inferred_schema()

for exp_key, schema in schemas.items():
    print(f"\n{exp_key}")
    
    # Check for potential issues
    if len(schema.columns) < 2:
        print("  ⚠️  Warning: Very few columns for synthesis")
    
    numeric_count = sum(1 for col in schema.columns if col.dtype in ['int', 'float'])
    if numeric_count == 0:
        print("  ⚠️  Warning: No numeric columns")
    
    if len(schema.columns) > 100:
        print("  ⚠️  Warning: Many columns may slow synthesis")
```

## Limitations

### Current Limitations

1. **Execution Not Required**: Can infer Schema without running workflow
2. **Configuration-Based**: Inference based solely on configuration, not actual data
3. **No Data Validation**: Does not validate if actual data matches inferred Schema
4. **Preprocessing Only**: Primarily focuses on Loader and Preprocessor transformations

### What This Method Does NOT Do

- Does not load or read actual data files
- Does not perform actual preprocessing transformations
- Does not validate data quality or consistency
- Does not check for missing values or outliers in data

## Notes

- **Pre-Execution**: Can be called before `run()`; does not require execution
- **Configuration-Based**: Inference based on configuration, not actual data
- **Schema Accuracy**: Inferred Schema should match actual Schema after execution
- **No Side Effects**: Does not modify Executor state or configuration
- **Multiple Calls**: Can be called multiple times; returns same result
- **Experiment Combinations**: Returns Schema for all experiment combinations
- **Postprocessor Support**: Limited support for Postprocessor Schema inference

## Related Methods

- [`run()`](executor_run): Execute workflow
- [`get_result()`](executor_get_result): Get execution results (includes actual Schema)
- [`get_timing()`](executor_get_timing): Get execution time report
- [`is_execution_completed()`](executor_is_execution_completed): Check execution status

## See Also

- [Executor Class Overview](./_index#basic-usage)
- [Preprocessor API](../../processor-api/preprocessor-api)
- [Schema API](../../schema-api)
- [Data Constraining Tutorial](../../tutorial/use-cases/data-constraining)