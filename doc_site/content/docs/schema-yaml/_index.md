---
title: "Schema YAML"
weight: 200
---

YAML configuration format for data structure definitions.

## Overview

Schema defines the structure and types of data, processed by the Metadater module. It adopts a three-layer architecture corresponding to actual data:

| Configuration Level | Corresponding Data | Description |
|---------|---------|------|
| **Metadata** | Datasets | Manages datasets with multiple tables |
| **Schema** | Table | Defines single table structure |
| **Attribute** | Field | Describes single field attributes |

## Usage

Schema is used in Loader with two definition methods:

### 1. External File Reference

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml  # Reference external file
```

### 2. Inline Definition

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema:                   # Inline schema definition
      id: user_data
      fields:                 # Field definitions
        user_id:              # Field name
          type: int64
          nullable: false
        username:
          type: object
          nullable: true
```

## Schema Structure

```yaml
id: <schema_id>           # Required: Structure identifier
fields:                   # Required: Field attribute definitions
  <field_name>:           # Field name as key
    type: <data_type>     # Required: Data type
    nullable: <boolean>   # Optional: Allow null (default true)
    logical_type: <type>  # Optional: Logical type hint
    stats: <dict>         # Optional: Statistics (auto-generated)
stats: <dict>             # Optional: Table statistics (auto-generated)
```

## Supported Data Types

### Basic Types
- `int64`: 64-bit integer
- `float64`: 64-bit floating point
- `object`: String or object
- `bool`: Boolean
- `datetime64`: Date and time
- `category`: Categorical

### Logical Types (logical_type)
Used to provide additional semantic information:
- `email`: Email address
- `url`: URL
- `ip_address`: IP address
- `phone`: Phone number
- `postal_code`: Postal code
- `category`: Categorical data

## Basic Examples

### Simple Structure (External File)

```yaml
# schemas/simple_schema.yaml
id: simple_data
fields:
  user_id:
    type: int64
    nullable: false
  username:
    type: object
  age:
    type: int64
    nullable: true
```

### Complete Structure (Inline)

```yaml
Loader:
  load_transaction:
    filepath: data/transactions.csv
    schema:
      id: transaction_data
      fields:
        transaction_id:
          type: int64
          nullable: false
          
        customer_email:
          type: object
          logical_type: email
          
        amount:
          type: float64
          nullable: false
          
        transaction_date:
          type: datetime64
          
        product_category:
          type: category
          
        status:
          type: category
          nullable: true
```

## Automatic Inference

If no schema is provided, the system will automatically infer the structure from data:

```yaml
Loader:
  auto_infer:
    filepath: data/auto.csv
    # No schema specified, automatic inference
```

## Data Type Mapping

| Pandas dtype | Schema type |
|-------------|-------------|
| int8, int16, int32, int64 | int64 |
| uint8, uint16, uint32, uint64 | int64 |
| float16, float32, float64 | float64 |
| object, string | object |
| bool | bool |
| datetime64 | datetime64 |
| category | category |

## Important Notes

1. **Field order**: Field order in Schema does not affect data loading
2. **Missing fields**: Missing fields in data will be filled with default values (nullable=true)
3. **Extra fields**: Extra fields in data will be preserved
4. **Type conversion**: System will attempt to automatically convert compatible types

## Advanced Usage

### Multi-table Structure

When processing multiple tables, the same schema can be reused across different Loaders:

```yaml
Loader:
  train_data:
    filepath: data/train.csv
    schema: schemas/common_schema.yaml
    
  test_data:
    filepath: data/test.csv
    schema: schemas/common_schema.yaml
    
  validation_data:
    filepath: data/validation.csv
    schema: schemas/common_schema.yaml
```

### Partial Definition

You can define only key fields, with the rest inferred by the system:

```yaml
schema:
  id: partial_schema
  fields:
    # Define only important fields
    primary_key:
      type: int64
      nullable: false
    # Other fields will be auto-inferred
```

## Statistics (Stats)

When creating Schema using `Metadater.from_data()`, if `enable_stats=True` is set, the system will automatically calculate and store statistics.

### Field Statistics (Attribute.stats)

Each field will contain the following statistical information:

```yaml
fields:
  age:
    type: int64
    nullable: true
    stats:                    # Auto-generated statistics
      count: 1000            # Non-null count
      null_count: 50         # Null count
      unique_count: 65       # Unique value count
      min: 18                # Minimum (numeric)
      max: 95                # Maximum (numeric)
      mean: 35.5             # Mean (numeric)
      median: 34.0           # Median (numeric)
      std: 12.3              # Standard deviation (numeric)
      q1: 26.0               # First quartile
      q3: 44.0               # Third quartile
      most_common:           # Most common values (categorical)
        - ["adult", 450]
        - ["senior", 300]
```

### Table Statistics (Schema.stats)

Schema-level statistics:

```yaml
id: user_table
stats:                       # Auto-generated table statistics
  row_count: 1000           # Total rows
  column_count: 12          # Total columns
  memory_usage: 98304       # Memory usage (bytes)
  null_columns:             # Columns with nulls
    - age
    - address
  numeric_columns:          # Numeric columns
    - age
    - salary
  categorical_columns:      # Categorical columns
    - gender
    - department
```

### Programmatic Access to Statistics

```python
from petsard.metadater import Metadater

# Create from data and calculate statistics
metadata = Metadater.from_data(
    data=df,
    enable_stats=True  # Enable statistics calculation
)

# Access statistics
schema = metadata.schemas["table_name"]
print(f"Total rows: {schema.stats.row_count}")

# Field statistics
age_attr = schema.fields["age"]
print(f"Average age: {age_attr.stats.mean}")
print(f"Null count: {age_attr.stats.null_count}")
```

### Notes

1. **Performance considerations**: Calculating statistics will increase processing time, especially for large datasets
2. **Privacy protection**: Statistics may contain sensitive information (e.g., min, max values), use with caution
3. **Update timing**: Statistics are calculated at creation time and do not auto-update
4. **Storage format**: Statistics are stored in YAML and can be used for auditing and analysis

## Related Documentation

- [Metadater API](/docs/experimental-new-format/python-api/metadater-api): Programmatic Schema operations
- [Loader API](/docs/experimental-new-format/python-api/loader-api): Data loader configuration