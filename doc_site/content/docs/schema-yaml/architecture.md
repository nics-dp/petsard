---
title: "Architecture"
type: docs
weight: 710
prev: docs/schema-yaml
next: docs/schema-yaml/attribute-parameters
---

Schema adopts a three-layer architecture to describe data structure.

## Three-Layer Architecture

| Level | Corresponding Data | Description |
|-------|-------------------|-------------|
| **Metadata** | Datasets | Manages multiple tables |
| **Schema** | Table | Defines single table |
| **Attribute** | Field | Describes single field |

## Architecture Relationships

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

| Schema Level | Python Data Type | Example |
|-------------|------------------|---------|
| Metadata | `dict[str, DataFrame]` | `{'users': df1, 'orders': df2}` |
| Schema | `pd.DataFrame` | `pd.DataFrame(...)` |
| Attribute | `pd.Series` | `df['user_id']` |

## Usage

### Single Table Scenario (Common)

Most cases involve only one table:

```yaml
id: my_dataset
schemas:
  users:              # Single table
    id: users
    attributes:
      user_id:
        type: int
      name:
        type: str
```

### Multi-Table Scenario

When dataset contains multiple related tables:

```yaml
id: ecommerce
schemas:
  users:              # First table
    id: users
    attributes: {...}
  orders:             # Second table
    id: orders
    attributes: {...}
  products:           # Third table
    id: products
    attributes: {...}
```

## Important Notes

- In practice, you typically only need to define Schema and Attributes
- Metadata level is automatically created by the system in single-table scenarios
- For detailed configuration parameters, see Attribute Parameters documentation