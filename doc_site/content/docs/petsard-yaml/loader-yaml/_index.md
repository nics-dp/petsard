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
  - Can be a local YAML file path (string) or complete Schema YAML (dict)

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
| `schema` | `string\|dict` | Data structure definition | `schemas/user.yaml` or inline dict |
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
      # Complete Schema YAML structure
      # For detailed configuration, refer to Schema YAML documentation
      id: employee_schema
      name: Employee Data Schema
      # ... other Schema configurations
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

### Complete Example with Schema

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
    # Using external Schema file
    schema: schemas/customer_schema.yaml
    
  # Or using inline Schema
  employee_data_loader:
    filepath: data/employees.csv
    schema:
      # Place complete Schema YAML structure here
      # For specific Schema configuration, refer to Schema YAML documentation
```

## Schema Configuration

The schema parameter accepts two formats:

1. **String**: Path to an external Schema YAML file
   - Example: `schema: schemas/data_schema.yaml`

2. **Dictionary**: Inline complete Schema YAML structure
   - Define the complete Schema directly in the Loader configuration

For detailed Schema configuration, available parameters, and attribute definitions, refer to the Schema YAML documentation.

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
- For detailed Schema configuration, refer to the Schema YAML documentation