---
title: "Attribute Parameters"
weight: 2
---

Parameter reference manual for Attribute (field properties).

## Parameter List

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `string` | Field name (automatically set when used as key) |

### Basic Attributes

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `string` | `null` | Data type: `int`, `float`, `str`, `date`, `datetime` |
| `description` | `string` | `null` | Field description text |
| `logical_type` | `string` | `null` | Logical type annotation (e.g., `email`, `phone`) |

### Type Attributes (type_attr)

`type_attr` is a dictionary containing type-related settings:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type_attr.nullable` | `boolean` | `true` | Allow null values |
| `type_attr.category` | `boolean` | `false` | Whether categorical data |
| `type_attr.precision` | `integer` | `null` | Numeric precision (decimal places) |
| `type_attr.format` | `string` | `null` | Datetime format string (e.g., `"%Y-%m-%d"`) |
| `type_attr.width` | `integer` | `null` | String width (for leading zeros) |

{{< callout type="info" >}}
**Simplified Syntax**: Parameters in `type_attr` can be written directly at attribute level. For example, `nullable: false` is equivalent to `type_attr.nullable: false`.
{{< /callout >}}

### Data Processing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `na_values` | `list/string` | `null` | Custom missing value markers (e.g., `"?"`, `["?", "N/A"]`) |
| `default_value` | `any` | `null` | Default fill value |
| `cast_errors` | `string` | `"coerce"` | Type conversion error handling: `"raise"`, `"coerce"`, `"ignore"` |
| `null_strategy` | `string` | `"keep"` | Null value handling strategy: `"keep"`, `"drop"`, `"fill"` |

### Data Validation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `constraints` | `dict` | `null` | Field constraint conditions (`min`, `max`, `pattern`) |

### Performance & Statistics

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_optimize_type` | `boolean` | `true` | Enable type optimization (select smallest data type) |
| `enable_stats` | `boolean` | `true` | Calculate field statistics |

## System Auto-Generated

These parameters are automatically set by the system, **do not set manually**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `stats` | `FieldStats` | Field statistics (when `enable_stats=True`) |
| `is_constant` | `boolean` | Mark fields with all identical values |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Update timestamp |

## Common Examples

### Integer Field

```yaml
age:
  type: int
  nullable: false
  description: "Age"
```

### Categorical Field

```yaml
gender:
  type: str
  category: true
  description: "Gender"
```

### Float (Specify Precision)

```yaml
price:
  type: float
  precision: 2
  description: "Price (two decimal places)"
```

### Date Field

```yaml
birth_date:
  type: date
  format: "%Y-%m-%d"
  description: "Birth date"
```

### Custom Missing Values

```yaml
workclass:
  type: str
  category: true
  na_values: "?"
  description: "Employment type"
```

## Important Notes

- **Type Simplification**: Use `int`, `float`, `str`, `date`, `datetime` (legacy type names auto-converted)
- **Category Marking**: Correctly setting `category: true` affects data processing and synthesis strategies
- **Auto-Inference**: Unspecified parameters are automatically inferred from data
- **Performance**: For large datasets, disable `enable_stats` to improve speed