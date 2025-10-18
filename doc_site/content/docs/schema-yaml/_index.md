---
title: "Schema YAML"
weight: 200
---

YAML configuration format for data structure definition.

## Usage Examples

### External File Reference

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml  # Reference external file
```

### Inline Definition

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema:                   # Inline schema definition
      id: user_data
      attributes:             # Field definitions (also can be written as fields)
        user_id:
          type: int64
          enable_null: false
        username:
          type: string
          enable_null: true
```

### Automatic Inference

If no schema is provided, the system will automatically infer structure from data:

```yaml
Loader:
  auto_infer:
    filepath: data/auto.csv
    # No schema specified, will be inferred
```

## Main Structure

```yaml
id: <schema_id>           # Required: Schema identifier
attributes:               # Required: Attribute definitions (also can be written as fields)
  <attribute_name>:       # Field name as key
    type: <data_type>     # Required: Data type
    enable_null: <bool>   # Optional: Allow null values (default: true)
    logical_type: <type>  # Optional: Logical type hint
```

{{< callout type="info" >}}
`attributes` can also be written as `fields`.
{{< /callout >}}

## Attribute Parameter List

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `name` | `string` | Field name (automatically set when used as key) | `"user_id"`, `"age"` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `type` | `string` | `null` | Data type, auto-inferred if not specified | `"int64"`, `"string"`, `"float64"` |
| `enable_null` | `boolean` | `true` | Allow null values | `true`, `false` |
| `category` | `boolean` | `null` | Whether it's categorical data | `true`, `false` |
| `logical_type` | `string` | `null` | Logical type annotation for validation | `"email"`, `"url"`, `"phone"` |
| `description` | `string` | `null` | Field description text | `"User unique identifier"` |
| `type_attr` | `dict` | `null` | Additional type attributes (precision, format, etc.) | `{"precision": 2}`, `{"format": "%Y-%m-%d"}` |
| `na_values` | `list` | `null` | Custom missing value markers | `["?", "N/A", "unknown"]` |
| `default_value` | `any` | `null` | Default fill value | `0`, `"Unknown"`, `false` |
| `constraints` | `dict` | `null` | Field constraint conditions | `{"min": 0, "max": 100}` |
| `enable_optimize_type` | `boolean` | `true` | Enable type optimization | `true`, `false` |
| `enable_stats` | `boolean` | `true` | Calculate statistics | `true`, `false` |
| `cast_errors` | `string` | `"coerce"` | Type conversion error handling | `"raise"`, `"coerce"`, `"ignore"` |
| `null_strategy` | `string` | `"keep"` | Null value handling strategy | `"keep"`, `"drop"`, `"fill"` |

### System Auto-Generated Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `stats` | `FieldStats` | Field statistics (auto-calculated when `enable_stats=True`) |
| `created_at` | `datetime` | Creation timestamp (auto-recorded by system) |
| `updated_at` | `datetime` | Update timestamp (auto-recorded by system) |

{{< callout type="info" >}}
**Auto-Inference Mechanism**:
- When using `Metadater.from_data()`, parameters like `type`, `logical_type`, `enable_null` are automatically inferred from data
- When manually creating Schema, only `name` is required, all other parameters are optional
- Explicitly specifying `type` is recommended to ensure data processing accuracy
{{< /callout >}}

## Advanced Usage

### Reusing Schema Across Tables

```yaml
Loader:
  train_data:
    filepath: data/train.csv
    schema: schemas/common_schema.yaml
    
  test_data:
    filepath: data/test.csv
    schema: schemas/common_schema.yaml
```

### Partial Definition

Define only key fields, others will be inferred:

```yaml
schema:
  id: partial_schema
  attributes:
    primary_key:
      type: int64
      enable_null: false
    # Other fields will be inferred
```

## Statistics

When using `Metadater.from_data()` with `enable_stats=True`, the system automatically calculates statistics.

### Field Statistics Example

```yaml
attributes:
  age:
    type: int64
    enable_null: true
    stats:
      row_count: 1000
      na_count: 50
      unique_count: 65
      mean: 35.5
      median: 34.0
```

### Programmatic Access

```python
from petsard.metadater import Metadater
import pandas as pd

# Create with statistics
data = {'users': pd.DataFrame({...})}
metadata = Metadater.from_data(
    data=data,
    enable_stats=True
)

# Access statistics
schema = metadata.schemas["users"]
age_attr = schema.attributes["age"]
print(f"Average age: {age_attr.stats.mean}")
```

## Related Documentation

- **Data Types**: See [Data Types](/docs/schema-yaml/data-types) for details
- **Logical Types**: See [Logical Types](/docs/schema-yaml/logical-types) for details
- **Architecture**: Schema uses a three-layer architecture design, see [Schema Architecture](/docs/schema-yaml/architecture) for details
- **Data Alignment**: Schema can be used for data alignment and validation, see [Metadater API](/docs/python-api/metadater-api) documentation
- **Loader Integration**: How Schema is used during data loading, see [Loader YAML](/docs/petsard-yaml/loader-yaml) documentation

## Important Notes

- Field order does not affect data loading
- Missing fields in data will be filled with default values (enable_null=true)
- Extra fields in data will be retained
- The system will attempt automatic type conversion for compatible types
- `attributes` can also be written as `fields`
- Logical types are only for validation, do not change storage format
- Statistics calculation increases processing time, use carefully with large datasets