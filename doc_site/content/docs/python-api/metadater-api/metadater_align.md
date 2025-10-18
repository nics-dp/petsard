---
title: "align()"
weight: 324
---

Align data structure according to metadata definition.

## Syntax

```python
@staticmethod
def align(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]
```

## Parameters

- **metadata** : Metadata, required
  - Metadata definition (target structure)
  - Required parameter
  - Defines expected data structure, field order, types, etc.
  
- **data** : dict[str, pd.DataFrame], required
  - Data to be aligned with table names as keys and DataFrames as values
  - Required parameter

## Returns

- **dict[str, pd.DataFrame]**
  - Aligned data dictionary
  - Structure, field order, and types conform to metadata definition
  - Missing fields are supplemented with NaN
  - Extra fields are preserved

## Description

The `align()` method adjusts actual data structure according to Metadata definition, ensuring data conforms to expected format. This method performs the following operations:

1. **Field Order Adjustment**: Rearrange fields according to metadata definition order
2. **Supplement Missing Fields**: Add NaN values for fields defined in metadata but missing in data
3. **Preserve Extra Fields**: Fields present in data but not defined in metadata are preserved at the end
4. **Type Conversion**: Attempt to convert fields to metadata-defined types (if possible)
5. **Null Value Handling**: Handle null values according to nullable settings

## Basic Example

```python
from petsard.metadater import Metadater
import pandas as pd

# Define expected structure
config = {
    'id': 'target_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True},
                'email': {'name': 'email', 'type': 'str', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Actual data (different field order, some fields missing)
raw_data = {
    'users': pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],  # Different order
        'id': [1, 2, 3],
        'phone': ['123-456', '234-567', '345-678']  # Extra field
        # Missing 'age' and 'email' fields
    })
}

# Align data structure
aligned_data = Metadater.align(metadata, raw_data)

# View alignment results
print("Field order after alignment:", list(aligned_data['users'].columns))
# Output: ['id', 'name', 'age', 'email', 'phone']

print("\nData after alignment:")
print(aligned_data['users'])
# id    name     age  email       phone
# 1     Alice    NaN  NaN         123-456
# 2     Bob      NaN  NaN         234-567
# 3     Charlie  NaN  NaN         345-678
```

## Advanced Examples

### Handling Field Order Differences

```python
from petsard.metadater import Metadater
import pandas as pd

# Define standard field order
config = {
    'id': 'standard_order',
    'schemas': {
        'products': {
            'id': 'products',
            'attributes': {
                'product_id': {'name': 'product_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'price': {'name': 'price', 'type': 'float', 'nullable': False},
                'category': {'name': 'category', 'type': 'str', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Data with messy field order
messy_data = {
    'products': pd.DataFrame({
        'category': ['Electronics', 'Books', 'Clothing'],
        'product_id': [101, 102, 103],
        'price': [299.99, 19.99, 49.99],
        'name': ['Laptop', 'Novel', 'T-Shirt']
    })
}

# Align data
aligned_data = Metadater.align(metadata, messy_data)

print("Before alignment:", list(messy_data['products'].columns))
print("After alignment:", list(aligned_data['products'].columns))
# Before alignment: ['category', 'product_id', 'price', 'name']
# After alignment: ['product_id', 'name', 'price', 'category']
```

### Supplementing Missing Fields

```python
from petsard.metadater import Metadater
import pandas as pd

# Define complete schema
config = {
    'id': 'complete_schema',
    'schemas': {
        'employees': {
            'id': 'employees',
            'attributes': {
                'emp_id': {'name': 'emp_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'department': {'name': 'department', 'type': 'str', 'nullable': True},
                'salary': {'name': 'salary', 'type': 'float', 'nullable': True},
                'hire_date': {'name': 'hire_date', 'type': 'datetime', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Data with only partial fields
incomplete_data = {
    'employees': pd.DataFrame({
        'emp_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
        # Missing department, salary, hire_date
    })
}

# Align and supplement missing fields
aligned_data = Metadater.align(metadata, incomplete_data)

print("Fields after alignment:", list(aligned_data['employees'].columns))
print("\nMissing fields supplemented with NaN:")
print(aligned_data['employees'])
#    emp_id     name  department  salary hire_date
# 0       1    Alice         NaN     NaN       NaT
# 1       2      Bob         NaN     NaN       NaT
# 2       3  Charlie         NaN     NaN       NaT
```

### Multi-Table Alignment

```python
from petsard.metadater import Metadater
import pandas as pd

# Define multi-table schema
config = {
    'id': 'multi_table',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False}
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

# Data for multiple tables
raw_data = {
    'users': pd.DataFrame({
        'username': ['alice', 'bob'],  # Different order
        'user_id': [1, 2]
    }),
    'orders': pd.DataFrame({
        'amount': [100.0, 200.0],  # Different order
        'user_id': [1, 2],
        'order_id': [101, 102]
    })
}

# Align all tables
aligned_data = Metadater.align(metadata, raw_data)

print("Users table after alignment:", list(aligned_data['users'].columns))
print("Orders table after alignment:", list(aligned_data['orders'].columns))
```

### Loader Internal Usage Scenario

```python
from petsard.metadater import Metadater
import pandas as pd

# Simulate Loader's internal process
def load_data_with_schema(filepath, schema_config):
    """Simulate how Loader uses Metadater.align()"""
    
    # 1. Create metadata from configuration
    metadata = Metadater.from_dict(schema_config)
    
    # 2. Read raw data
    raw_data = {'data': pd.read_csv(filepath)}
    
    # 3. Align data structure
    aligned_data = Metadater.align(metadata, raw_data)
    
    return aligned_data['data'], metadata

# Usage example
schema_config = {
    'id': 'my_schema',
    'schemas': {
        'data': {
            'id': 'data',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': True}
            }
        }
    }
}

# data, schema = load_data_with_schema('data.csv', schema_config)
```

### Handling Type Conversion

```python
from petsard.metadater import Metadater
import pandas as pd

# Define strict type schema
config = {
    'id': 'typed_schema',
    'schemas': {
        'measurements': {
            'id': 'measurements',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': False},
                'is_valid': {'name': 'is_valid', 'type': 'bool', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# Data with potentially incorrect types
raw_data = {
    'measurements': pd.DataFrame({
        'id': ['1', '2', '3'],  # String type int
        'value': [1, 2, 3],  # Int type float
        'is_valid': [1, 0, 1]  # Int type bool
    })
}

# Alignment will attempt type conversion
aligned_data = Metadater.align(metadata, raw_data)

print("Data types after alignment:")
print(aligned_data['measurements'].dtypes)
# id           int64
# value      float64
# is_valid      bool
```

### Usage in Data Pipeline

```python
from petsard.metadater import Metadater
import pandas as pd

# Define standardization process
class DataPipeline:
    def __init__(self, schema_config):
        self.metadata = Metadater.from_dict(schema_config)
    
    def process(self, raw_data):
        """Standardized data processing workflow"""
        # 1. Align data structure
        aligned = Metadater.align(self.metadata, raw_data)
        
        # 2. Check differences
        diff = Metadater.diff(self.metadata, aligned)
        if diff:
            print("Warning: Data structure still has differences", diff)
        
        # 3. Return standardized data
        return aligned

# Use pipeline
schema_config = {
    'id': 'standard',
    'schemas': {
        'data': {
            'id': 'data',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': True}
            }
        }
    }
}

pipeline = DataPipeline(schema_config)

# Process data from different sources
sources = [
    {'data': pd.DataFrame({'value': [1.5, 2.5], 'id': [1, 2]})},
    {'data': pd.DataFrame({'id': [3, 4], 'value': [3.5, 4.5]})},
]

standardized_data = [pipeline.process(source) for source in sources]
```

## Notes

- **Alignment Operations**:
  - Field order rearranged according to metadata definition
  - Missing fields supplemented with NaN (or corresponding type null values)
  - Extra fields preserved at the end (fields not defined in metadata)
  - Type conversion attempted but not all conversions guaranteed to succeed
  
- **Non-Destructive Operation**:
  - Original input data not modified
  - Returns new DataFrame copies
  - Extra fields not removed
  
- **Type Conversion**:
  - Automatic attempts to convert to defined types
  - Conversion failures may retain original type or raise errors
  - Datetime type conversion requires correct format
  
- **Null Value Handling**:
  - Supplemented fields use NaN (numeric) or None (object)
  - Datetime types use NaT (Not a Time)
  - nullable setting doesn't affect alignment process, only validation
  
- **Performance Considerations**:
  - Large dataset alignment may be time-consuming
  - Frequent type conversions affect performance
  - Recommend one-time alignment during data loading phase
  
- **When to Use**:
  - Standardization after data loading
  - Before merging data from different sources
  - Ensuring data meets downstream module requirements
  - Standardization step in data pipeline
  
- **Relationship with Other Methods**:
  - Usually used after `diff()`
  - Loader internally calls this method automatically
  - Used with `from_dict()` or `from_data()` to create metadata
  
- **Error Handling**:
  - Type conversion failures may raise exceptions
  - Use try-except to handle possible errors
  - Check degree of differences with `diff()` before alignment
  
- **Best Practices**:
  - Align data early in data pipeline
  - Validate results meet expectations after alignment
  - Log warnings and errors during alignment process
  - Consider encapsulating alignment operations as independent functions