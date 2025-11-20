---
title: "Schema YAML"
type: docs
weight: 700
prev: docs/petsard-yaml
next: docs/error-handling
---

YAML configuration format for data structure definition.

{{< callout type="info" >}}
**Usage**: Schema YAML in PETsARD is used through Loader. For how to reference and use Schema in Loader, please refer to Loader YAML documentation. This section focuses on how to configure Schema structure and parameters.
{{< /callout >}}

## Basic Structure

A complete Schema YAML file contains the following parts:

```yaml
# Schema identification
id: <schema_id>              # Required: Schema identifier
name: <schema_name>          # Optional: Schema name
description: <description>   # Optional: Schema description

# Field definitions
attributes:                  # Or use fields
  <field_name>:             # Field name
    type: <data_type>       # Data type
    description: <text>     # Field description
    # ... other parameters
```

## Example: Adult Income Dataset

The following is a Schema definition example for the Adult Income (Census) dataset:

```yaml
# Schema identification
id: adult-income
name: "Adult Income Dataset"
description: "1994 Census database for income prediction (>50K or <=50K)"

# Field definitions
attributes:
  age:
    type: integer
    description: "Age of the individual"

  workclass:
    type: string
    category: true
    description: "Employment type"
    na_values: "?"

  fnlwgt:
    type: integer
    description: "Final weight (number of people the census believes the entry represents)"

  education:
    type: string
    category: true
    description: "Highest level of education"
    na_values: "?"

  educational-num:
    type: integer
    description: "Number of education years"

  marital-status:
    type: string
    category: true
    description: "Marital status"

  occupation:
    type: string
    category: true
    description: "Occupation"
    na_values: "?"

  relationship:
    type: string
    category: true
    description: "Relationship to household"

  race:
    type: string
    category: true
    description: "Race"

  gender:
    type: string
    category: true
    description: "Biological sex"

  capital-gain:
  type: integer
  description: "Capital gains"

  capital-loss:
  type: integer
  description: "Capital losses"

  hours-per-week:
    type: integer
    description: "Hours worked per week"

  native-country:
    type: string
    category: true
    description: "Country of origin"

  income:
    type: string
    category: true
    description: "Income class (target variable)"
```

### Example Explanation

This Schema definition demonstrates several important configuration concepts:

#### 1. Schema-Level Information

```yaml
id: adult-income
name: "Adult Income Dataset"
description: "1994 Census database for income prediction (>50K or <=50K)"
```

- **`id`**: Required, used to identify this Schema
- **`name`**: Optional, provides a readable name
- **`description`**: Optional, explains the purpose of this dataset

#### 2. Numeric Fields

```yaml
age:
  type: integer
  description: "Age of the individual"

hours-per-week:
  type: integer
  description: "Hours worked per week"
```

- Use `type: integer` to define integer fields
- `description` explains the business meaning of the field

#### 3. Categorical Fields

```yaml
workclass:
  type: string
  category: true
  description: "Employment type"
  na_values: "?"

gender:
  type: string
  category: true
  description: "Biological sex"
```

- **`category: true`**: Marks as categorical data, system will select appropriate processing methods
- **`na_values`**: Defines custom missing value markers (e.g., `"?"` represents missing values in this dataset)

#### 4. Special Case: Numeric but Treated as Categorical

In some cases, numeric fields may be more suitable for categorical data processing:

```yaml
# Example: Rating levels (numeric but limited options)
rating:
  type: integer
  category: true
  description: "Rating level (1-5)"

# Example: Zip codes (numeric but represents area classification)
zip_code:
  type: integer
  category: true
  description: "Zip code"
```

Setting `category: true` affects:
- **Preprocessor**: Selects categorical data processing methods (e.g., Label Encoding)
- **Synthesizer**: Uses synthesis strategies appropriate for categorical data
- **Statistics**: Calculates category distribution instead of numeric statistics

{{< callout type="info" >}}
Whether to treat numeric fields as categorical depends on data characteristics and business requirements. Generally, when a numeric field has limited unique values and no clear mathematical relationship between values, it can be considered as categorical.
{{< /callout >}}

## Type System

PETsARD uses a simplified type system:

| Type | Description | Examples |
|------|-------------|----------|
| `int` / `integer` | Integer | `25`, `-10`, `1000` |
| `float` | Float | `3.14`, `-0.5`, `1000.00` |
| `str` / `string` | String | `"text"`, `"A"`, `"123"` |
| `date` | Date | `2024-01-01` |
| `datetime` | Datetime | `2024-01-01 10:30:00` |

{{< callout type="info" >}}
**Type Aliases**:
- `integer` and `int` are interchangeable
- `string` and `str` are interchangeable
- System internally uses simplified types (`int`, `float`, `str`, `date`, `datetime`)
{{< /callout >}}

## Advanced Topics

### Attribute Parameters

Common parameters include:
- `type`: Data type
- `type_attr`: Type attributes (nullable, category, precision, etc.)
- `description`: Field description
- `logical_type`: Logical type (email, phone, etc.)
- `na_values`: Custom missing value markers
- `constraints`: Field constraint conditions

### Statistics

Setting `enable_stats: true` enables statistics calculation.

## Important Notes

- **Field Names**: Both `attributes` and `fields` can be used, system will auto-recognize
- **Auto-Inference**: If no Schema is provided, system will automatically infer structure from data
- **Type Conversion**: System will attempt automatic type conversion for compatible types
- **Missing Values**: Custom missing value markers can be defined via `na_values`
- **Categorical Data**: Setting `category: true` affects data processing and synthesis strategies