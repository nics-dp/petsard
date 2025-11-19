---
title: "diff()"
weight: 323
---

Compare differences between metadata definition and actual data.

## Syntax

```python
@staticmethod
def diff(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict
```

## Parameters

- **metadata** : Metadata, required
  - Metadata definition (expected structure)
  - Required parameter

- **data** : dict[str, pd.DataFrame], required
  - Actual data with table names as keys and DataFrames as values
  - Required parameter

## Returns

- **dict**
  - Difference report dictionary
  - Returns empty dictionary `{}` if no differences
  - Difference report may contain the following keys:
    - `missing_tables`: Tables defined in metadata but missing in data
    - `extra_tables`: Tables present in data but not defined in metadata
    - `table_diffs`: Detailed differences for each table
      - `missing_columns`: Fields defined but missing
      - `extra_columns`: Fields present but not defined
      - `type_mismatches`: Fields with mismatched types
      - `nullable_mismatches`: Fields with mismatched nullable attributes

## Description

The `diff()` method detects differences between expected data structure (metadata) and actual data, useful for:

1. Data Validation: Ensure data conforms to expected structure
2. Version Control: Track data structure changes
3. Data Quality Checks: Validate data integrity before processing
4. Debugging: Identify issues in data loading or transformation

## Basic Example

```python
from petsard.metadater import Metadater
import pandas as pd

# Define expected schema
config = {
    'id': 'expected_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Actual data (with differences)
actual_data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'email': ['alice@ex.com', 'bob@ex.com', 'charlie@ex.com']  # Extra field
        # Missing 'age' field
    })
}

# Compare differences
diff_report = Metadater.diff(metadata, actual_data)

# Check results
if diff_report:
    print("Data structure differences found:")
    print(diff_report)
else:
    print("Data structure fully conforms")
```

## Advanced Examples

### Detailed Difference Analysis

```python
from petsard.metadater import Metadater
import pandas as pd

# Define schema
config = {
    'id': 'user_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True},
                'email': {'name': 'email', 'type': 'str', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Actual data with multiple types of differences
actual_data = {
    'users': pd.DataFrame({
        'user_id': [1, 2, 3],
        'username': ['alice', 'bob', 'charlie'],
        'age': [25.5, 30.0, 35.0],  # Type error: should be int but is float
        'phone': ['123-456', '234-567', '345-678']  # Extra field
        # Missing 'email' field
    })
}

# Compare differences
diff_report = Metadater.diff(metadata, actual_data)

# Analyze difference report
if 'table_diffs' in diff_report:
    for table_name, table_diff in diff_report['table_diffs'].items():
        print(f"\nTable: {table_name}")

        if 'missing_columns' in table_diff:
            print(f"  Missing fields: {table_diff['missing_columns']}")

        if 'extra_columns' in table_diff:
            print(f"  Extra fields: {table_diff['extra_columns']}")

        if 'type_mismatches' in table_diff:
            print(f"  Type mismatches: {table_diff['type_mismatches']}")
```

### Multi-Table Difference Detection

```python
from petsard.metadater import Metadater
import pandas as pd

# Define multi-table schema
config = {
    'id': 'ecommerce',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False}
            }
        },
        'orders': {
            'id': 'orders',
            'attributes': {
                'order_id': {'name': 'order_id', 'type': 'int', 'nullable': False},
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'amount': {'name': 'amount', 'type': 'float', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Actual data (missing orders table)
actual_data = {
    'users': pd.DataFrame({
        'user_id': [1, 2],
        'name': ['Alice', 'Bob']
    }),
    'products': pd.DataFrame({  # Extra table
        'product_id': [101, 102],
        'name': ['Product A', 'Product B']
    })
}

# Compare differences
diff_report = Metadater.diff(metadata, actual_data)

# Check table-level differences
if 'missing_tables' in diff_report:
    print(f"Missing tables: {diff_report['missing_tables']}")

if 'extra_tables' in diff_report:
    print(f"Extra tables: {diff_report['extra_tables']}")
```

### Data Validation Workflow

```python
from petsard.metadater import Metadater
import pandas as pd
import sys

# Load expected schema
with open('expected_schema.yaml', 'r') as f:
    import yaml
    config = yaml.safe_load(f)

metadata = Metadater.from_dict(config)

# Load actual data
actual_data = {
    'users': pd.read_csv('users.csv'),
    'orders': pd.read_csv('orders.csv')
}

# Validate data structure
diff_report = Metadater.diff(metadata, actual_data)

if diff_report:
    print("❌ Data structure validation failed")
    print("\nDifference Report:")
    print(diff_report)

    # Log to file
    with open('validation_errors.log', 'a') as log:
        log.write(f"Difference Report: {diff_report}\n")

    sys.exit(1)
else:
    print("✅ Data structure validation passed")
    # Continue processing data...
```

### Type Compatibility Check

```python
from petsard.metadater import Metadater
import pandas as pd
import numpy as np

# Define strict type schema
config = {
    'id': 'strict_schema',
    'schemas': {
        'measurements': {
            'id': 'measurements',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': False},
                'timestamp': {'name': 'timestamp', 'type': 'datetime', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Test different data types
test_cases = [
    {
        'name': 'Correct types',
        'data': pd.DataFrame({
            'id': [1, 2, 3],
            'value': [1.5, 2.5, 3.5],
            'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
    },
    {
        'name': 'Type error',
        'data': pd.DataFrame({
            'id': ['A', 'B', 'C'],  # Should be int
            'value': [1.5, 2.5, 3.5],
            'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
    }
]

for test_case in test_cases:
    print(f"\nTest case: {test_case['name']}")
    diff_report = Metadater.diff(metadata, {'measurements': test_case['data']})

    if diff_report:
        print(f"  ❌ Differences found: {diff_report}")
    else:
        print(f"  ✅ Validation passed")
```

## Notes

- **Detection Content**:
  - Table existence: Check for missing or extra tables
  - Field completeness: Check if all fields are present
  - Type consistency: Check if data types match definitions
  - Null attributes: Check if nullable settings are consistent

- **Difference Report Structure**:
  - Empty dictionary indicates complete conformance
  - Non-empty dictionary contains detailed difference information
  - Difference reports can be used to generate user-friendly error messages

- **Type Comparison**:
  - Type comparison based on pandas dtype
  - Some type conversions may be considered compatible (e.g., int64 vs int32)
  - Strict type definitions recommended

- **When to Use**:
  - Validation after data loading
  - Checks before data transformation
  - Data quality checks in CI/CD
  - Data Contract validation

- **Performance Considerations**:
  - Difference detection for large datasets may be time-consuming
  - Recommend prioritizing critical field checks
  - Consider sampling for performance improvement

- **Relationship with align()**:
  - `diff()` only reports differences without modifying data
  - `align()` adjusts data structure according to metadata
  - Recommend using `diff()` to check first, then decide whether to use `align()`

- **Error Handling**:
  - Incorrect input format may raise exceptions
  - Use try-except to handle possible errors
  - Difference reports can be serialized to JSON or YAML for logging