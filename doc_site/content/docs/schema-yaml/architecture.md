---
title: "Schema Architecture"
weight: 201
---

Schema defines the structure and types of data, processed by the Metadater module. It adopts a three-layer architecture corresponding to actual data.

## Three-Layer Architecture

| Configuration Level | Corresponding Data | Description |
|---------|---------|------|
| **Metadata** | Datasets | Manages datasets with multiple tables |
| **Schema** | Table | Defines single table structure |
| **Attribute** | Field | Describes single field attributes |

## Metadata Level

Metadata is the top-level structure for managing datasets containing multiple tables.

### Structure Definition

```python
class Metadata:
    id: str                      # Dataset identifier
    name: str                    # Dataset name (optional)
    description: str             # Dataset description (optional)
    schemas: dict[str, Schema]   # Table structure dictionary {table_name: Schema}
```

### Use Cases

- **Single Table Scenario**: Most cases involve a dataset with only one table
- **Multi-Table Scenario**: When dataset contains multiple related tables (like relational databases)
- **Dataset Management**: Provides dataset-level identification and description

### Examples

```yaml
# Single table dataset
id: user_dataset
name: User Dataset
schemas:
  users:              # Single table
    id: users
    fields: {...}
```

```yaml
# Multi-table dataset
id: ecommerce_dataset
name: E-commerce Dataset
schemas:
  users:              # First table
    id: users
    fields: {...}
  orders:             # Second table
    id: orders
    fields: {...}
  products:           # Third table
    id: products
    fields: {...}
```

## Schema Level

Schema is the middle layer, defining the structure of a single table.

### Structure Definition

```python
class Schema:
    id: str                          # Table identifier
    name: str                        # Table name (optional)
    description: str                 # Table description (optional)
    attributes: dict[str, Attribute] # Field attribute dictionary {field_name: Attribute}
    stats: dict                      # Table statistics (optional, auto-generated)
```

### Use Cases

- **Table Definition**: Describes complete structure of a single table
- **Field Management**: Contains definitions for all fields in the table
- **Structure Validation**: Ensures data conforms to expected table structure

### YAML Representation

```yaml
# Complete Schema definition
id: users                  # Table identifier
name: User Table           # Table display name
description: System user data # Table description

fields:                    # Field definitions (Attributes)
  user_id:
    type: int64
    nullable: false
  
  username:
    type: object
    nullable: false
  
  email:
    type: object
    nullable: true
    logical_type: email

stats:                     # Table statistics (auto-generated)
  row_count: 1000
  column_count: 3
```

## Attribute Level

Attribute is the bottom layer, describing properties of a single field.

### Structure Definition

```python
class Attribute:
    name: str           # Field name
    type: str           # Data type
    nullable: bool      # Whether null values allowed
    logical_type: str   # Logical type (optional)
    description: str    # Field description (optional)
    na_values: list     # Custom null representations (optional)
    stats: dict         # Field statistics (optional, auto-generated)
```

### Use Cases

- **Field Definition**: Describes all properties of a single field
- **Type Constraints**: Defines field data type and null handling
- **Semantic Marking**: Provides additional semantic information via logical_type

### YAML Representation

```yaml
# Complete field definition
user_id:                    # Field name (key)
  type: int64               # Data type
  nullable: false           # No null values allowed
  description: User unique identifier

email:
  type: object              # String type
  nullable: true            # Null values allowed
  logical_type: email       # Marked as email
  description: Email address

age:
  type: int64
  nullable: true
  description: Age
  stats:                    # Field statistics (auto-generated)
    count: 950              # Non-null count
    null_count: 50          # Null count
    min: 18                 # Minimum
    max: 95                 # Maximum
    mean: 35.5              # Mean
```

## Architecture Level Relationships

```
Metadata (Dataset)
├── Schema (Table 1)
│   ├── Attribute (Field 1)
│   ├── Attribute (Field 2)
│   └── Attribute (Field 3)
├── Schema (Table 2)
│   ├── Attribute (Field 1)
│   └── Attribute (Field 2)
└── Schema (Table 3)
    └── Attribute (...)
```

## Actual Data Mapping

### Correspondence

| Schema Level | Actual Data | Python Type | Example |
|------------|---------|------------|------|
| Metadata | Dataset | dict[str, DataFrame] | `{'users': df1, 'orders': df2}` |
| Schema | Table | pd.DataFrame | `pd.DataFrame(...)` |
| Attribute | Field | pd.Series | `df['user_id']` |

## Role of Metadater Module

The Metadater module handles these three layers of architecture, providing the following functions:

- **Creating Metadata**: Auto-infer from data or create from configuration files
- **Structure Validation**: Compare actual data with expected structure
- **Data Alignment**: Adjust data structure according to metadata

## Usage Recommendations

- **Single Table Scenario**: Most cases only need to define field structure for one table
- **Multi-Table Scenario**: When dataset contains multiple related tables, define each under `schemas`
- **Minimal Definition**: Define only key fields (e.g., primary keys), let system auto-infer the rest