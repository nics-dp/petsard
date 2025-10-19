---
title: "Loader YAML"
weight: 110
---

YAML configuration file format for the Loader module.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/loader-yaml/loader-yaml.ipynb)

### Basic Loading

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
```

### Using Schema File
Schema defines the structure and types of the data.

```yaml
Loader:
  load_with_schema:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml
```

### Multiple Data Loading

```yaml
Loader:
  # Load training data
  load_train:
    filepath: benchmark/adult-income_ori.csv
    schema: benchmark/adult-income_schema.yaml

  # Load test data
  load_test:
    filepath: benchmark/adult-income_control.csv
    schema: benchmark/adult-income_schema.yaml

  # Load synthesizing data
  load_synthesizer:
    filepath: benchmark/adult-income_syn.csv
    schema: benchmark/adult-income_schema.yaml
```

## Main Parameters

- **filepath** (`string`, required)
  - Data file path
  - Supports local file paths

- **schema** (`string | dict`, optional)
  - Data structure definition
  - Can be a local YAML file path (string) or complete Schema YAML (dict)

## Supported File Formats

| Format | Extensions | Description | Requirements |
|--------|------------|-------------|--------------|
| **CSV** | `.csv`, `.tsv` | Comma/tab-separated files | - |
| **Excel** | `.xlsx`, `.xls` | Excel spreadsheets | Requires `openpyxl` |
| **OpenDocument** | `.ods`, `.odf`, `.odt` | OpenDocument formats | Requires `openpyxl` |
| **Benchmark** | `benchmark://` | Benchmark dataset protocol | Requires network (first download) |

\* Excel and OpenDocument formats require the `openpyxl` package, see installation instructions.

## Parameter Details

### Required Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `filepath` | `string` | N/A | Data file path | `data/users.csv` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `schema` | `string\|dict` | `null` | Data structure definition | `schemas/user.yaml` or inline dict |
| `nrows` | `int` | `null` | Number of rows to read for quick testing or reducing memory usage | `100` |
| `column_types` | `dict` | `null` | **Deprecated in v2.0.0** Specify column types, format: `{type: [colname]}` | `{"category": ["gender"]}` |
| `header_names` | `list` | `null` | **Deprecated in v2.0.0** Specify column names for data without headers | `["age", "income"]` |
| `na_values` | `string\|list\|dict` | `null` | **Deprecated in v2.0.0** Additional NA/NaN recognition strings | `"N/A"` or `{"age": ["unknown"]}` |

## Precision Handling

Loader automatically handles precision for numeric fields:

- **Auto-Inference**: Automatically detects decimal places for each numeric field when no schema is provided
- **Precision Recording**: Inference results are stored in `type_attr.precision` of the schema
- **Auto-Application**: Data is rounded according to precision after loading
- **Manual Specification**: Precision can be manually set in schema via `type_attr.precision`

## Related Information

- **Benchmark Datasets**: Use the benchmark:// protocol to automatically download and load standardized datasets, see benchmark:// documentation.
- **Schema**: Schema defines the structure, types, and constraints of the data, see Schema YAML documentation.

## Execution Notes

- Experiment names (second level) can be freely named, descriptive names are recommended
- Multiple experiments can be defined and will be executed sequentially
- Results from each experiment will be passed to the next module

## Important Notes

- File paths support both relative and absolute paths
- Schema configuration priority: parameter specification > auto-inference
- `column_types`, `na_values`, and `header_names` parameters are deprecated, will be removed in v2.0.0
- Excel and OpenDocument formats require the `openpyxl` package
- For detailed Schema configuration, refer to the Schema YAML documentation