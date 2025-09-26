---
title: "Loader YAML"
weight: 110
---

YAML configuration file format for the Loader module.

## Main Parameters

- **filepath** (`string`, required)
  - Data file path
  - Supports local file paths

- **schema** (`string | dict`, optional)
  - Data structure definition
  - Can be external file path or inline definition

- **header_names** (`list`, optional)
  - Column names for headerless data

## Supported File Formats

| Format | Extensions | Description | Requirements |
|--------|------------|-------------|--------------|
| **CSV** | `.csv`, `.tsv` | Comma/tab-separated files | - |
| **Excel** | `.xlsx`, `.xls` | Excel spreadsheets | Requires `openpyxl` |
| **OpenDocument** | `.ods`, `.odf`, `.odt` | OpenDocument formats | Requires `openpyxl` |

\* Excel and OpenDocument formats require the `openpyxl` package, see installation instructions.

## Parameter Details

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `filepath` | `string` | Data file path | `data/users.csv` |

### Optional Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `schema` | `string\|dict` | Data structure definition | `schemas/user.yaml` |
| `header_names` | `list` | Column names for headerless data | See examples below |

### Deprecated Parameters

| Parameter | Alternative | Removal Version |
|-----------|-------------|-----------------|
| `column_types` | Use `schema` | v2.0.0 |
| `na_values` | Use `schema` | v2.0.0 |

## Usage Examples

### Basic Loading

```yaml
Loader:
  load_csv:
    filepath: data/users.csv
```

### Using External Schema

```yaml
Loader:
  load_with_schema:
    filepath: data/customers.csv
    schema: schemas/customer_schema.yaml
```

### Headerless CSV

```yaml
Loader:
  load_no_header:
    filepath: data/no_header.csv
    header_names:
      - id
      - name
      - age
      - salary
      - department
```

### Inline Schema Definition

```yaml
Loader:
  load_with_inline_schema:
    filepath: data/employees.csv
    schema:
      id: employee_schema
      name: Employee Data Schema
      attributes:
        id:
          type: int64
          enable_null: false
        name:
          type: string
        salary:
          type: float64
          precision: 2
```

### Multiple Loading Experiments

```yaml
Loader:
  # Load training data
  load_train:
    filepath: data/train.csv
    schema: schemas/data_schema.yaml
    
  # Load test data
  load_test:
    filepath: data/test.csv
    schema: schemas/data_schema.yaml
    
  # Load validation data
  load_validation:
    filepath: data/validation.csv
    schema: schemas/data_schema.yaml
```

### Complete Example

```yaml
Loader:
  customer_data_loader:
    filepath: data/customers.csv
    header_names:
      - id
      - name
      - age
      - income
      - registration_date
      - city
      - vip_status
    schema:
      id: customer_schema
      name: Customer Data Schema
      description: Schema for customer data
      attributes:
        id:
          type: int64
          enable_null: false
        name:
          type: string
          enable_null: false
        age:
          type: int64
          min: 0
          max: 120
        income:
          type: float64
          precision: 2
          min: 0
        registration_date:
          type: datetime64
        city:
          type: category
          logical_type: category
        vip_status:
          type: boolean
          enable_null: false
```

## Schema Configuration

Schema defines the structure and types of data, which can be provided in three ways:

1. **External YAML file**: Provide file path
2. **Inline definition**: Define directly in YAML
3. **Auto-inference**: System auto-infers when not provided

For detailed Schema configuration, refer to Metadater YAML documentation.

## Execution Notes

- Experiment names (second level) can be freely named, descriptive names are recommended
- Multiple experiments can be defined and will be executed sequentially
- Results from each experiment will be passed to the next module

## Important Notes

- File paths support both relative and absolute paths
- Schema configuration priority: parameter specification > auto-inference
- CSV files without headers must provide `header_names` parameter
- `column_types` and `na_values` parameters are deprecated, use `schema` instead
- Excel and OpenDocument formats require the `openpyxl` package