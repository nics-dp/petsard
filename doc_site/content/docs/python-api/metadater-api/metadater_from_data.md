---
title: "from_data()"
weight: 321
---

Automatically infer and create metadata structure from data.

## Syntax

```python
@classmethod
def from_data(
    cls,
    data: dict[str, pd.DataFrame],
    enable_stats: bool = False,
    **kwargs
) -> Metadata
```

## Parameters

- **data** : dict[str, pd.DataFrame], required
  - Dictionary of data tables where keys are table names and values are DataFrames
  - Required parameter
  
- **enable_stats** : bool, optional
  - Whether to calculate statistics (min, max, mean, etc.)
  - Default: `False`
  - Enabling this increases processing time but provides more complete metadata

- ****kwargs** : optional
  - Additional Metadata parameters (e.g., `id`, `name`, etc.)

## Returns

- **Metadata**
  - Automatically inferred metadata object
  - Contains Schema definitions for all tables

## Description

The `from_data()` method automatically analyzes data content and creates a corresponding Metadata object.

The inference process includes:
1. Detecting data type for each field (int, float, str, bool, datetime, etc.)
2. Determining if fields allow null values (nullable)
3. Identifying logical types (email, phone, etc., if applicable)
4. Calculating statistical information if `enable_stats` is enabled

## Basic Example

```python
from petsard.metadater import Metadater
import pandas as pd

# Prepare single table data
data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'email': ['alice@example.com', 'bob@example.com', None]
    })
}

# Automatically infer structure
metadata = Metadater.from_data(data)

# View results
print(f"Dataset ID: {metadata.id}")
print(f"Number of tables: {len(metadata.schemas)}")

# Access specific table schema
user_schema = metadata.schemas['users']
print(f"Number of fields: {len(user_schema.attributes)}")

# View field attributes
for attr_name, attr in user_schema.attributes.items():
    print(f"- {attr_name}: {attr.type}, enable_null={attr.enable_null}")
```

## Advanced Examples

### Multi-table Data Inference

```python
from petsard.metadater import Metadater
import pandas as pd

# Prepare multiple tables
data = {
    'users': pd.DataFrame({
        'user_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    }),
    'orders': pd.DataFrame({
        'order_id': [101, 102, 103],
        'user_id': [1, 2, 1],
        'amount': [100.5, 200.0, 150.75],
        'order_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
    })
}

# Infer multi-table structure
metadata = Metadater.from_data(data)

print(f"Tables included: {list(metadata.schemas.keys())}")
print(f"\nUsers table fields:")
for attr_name in metadata.schemas['users'].attributes:
    print(f"  - {attr_name}")
    
print(f"\nOrders table fields:")
for attr_name in metadata.schemas['orders'].attributes:
    print(f"  - {attr_name}")
```

### Enable Statistical Information

```python
from petsard.metadater import Metadater
import pandas as pd

# Prepare numerical data
data = {
    'sales': pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5],
        'price': [10.5, 20.0, 15.5, 30.0, 25.5],
        'quantity': [100, 200, 150, 300, 250]
    })
}

# Enable statistical information
metadata = Metadater.from_data(data, enable_stats=True)

# Statistical information will be included in schema (if implementation supports)
sales_schema = metadata.schemas['sales']
print(f"Sales table statistics enabled")
```

### Handling Data with Null Values

```python
from petsard.metadater import Metadater
import pandas as pd
import numpy as np

# Data with null values
data = {
    'employees': pd.DataFrame({
        'emp_id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'department': ['IT', 'HR', None, 'IT'],  # Has null
        'salary': [50000, 60000, 55000, np.nan]  # Has null
    })
}

# Infer structure
metadata = Metadater.from_data(data)

# Check which fields allow null values
emp_schema = metadata.schemas['employees']
for attr_name, attr in emp_schema.attributes.items():
    nullable_status = "nullable" if attr.enable_null else "not nullable"
    print(f"{attr_name}: {nullable_status}")

# Example output:
# emp_id: not nullable
# name: not nullable
# department: nullable
# salary: nullable
```

### Override Default Metadata Properties

```python
from petsard.metadater import Metadater
import pandas as pd

# Prepare data
data = {
    'customers': pd.DataFrame({
        'customer_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
}

# Override default ID and name
metadata = Metadater.from_data(
    data,
    id="customer_dataset_v1",
    name="Customer Database",
    description="Main customer information dataset"
)

print(f"Metadata ID: {metadata.id}")
print(f"Metadata Name: {metadata.name}")
print(f"Description: {metadata.description}")
```

## Notes

- **Automatic Inference Rules**:
  - Field types are inferred based on actual data content
  - If a field contains any null values (NaN, None), then `enable_null = True`
  - Table names (dictionary keys) become Schema `id`
  - Default `id` and `name` can be overridden via `**kwargs`
  
- **Data Type Support**:
  - Numeric types: `int`, `float`
  - Text types: `str`
  - Boolean type: `bool`
  - Datetime types: `datetime`
  
- **Performance Considerations**:
  - Large dataset inference may take longer
  - `enable_stats=True` increases processing time
  - Recommended to test with small samples first
  
- **Usage Recommendations**:
  - Suitable for quickly creating initial schema
  - Recommended to review inferred results and adjust as needed
  - Complex logical types may require manual definition
  
- **Integration with Loader**:
  - Loader internally uses this method to handle data loading without schema
  - General users can work through Loader's `schema` parameter without directly calling this method