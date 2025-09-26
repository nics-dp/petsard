---
title: "Loader API"
weight: 340
---

Data loading module that supports various file formats.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/loader-api/loader-class-diagram.mmd" >}}

> **Legend:**
> - Blue box: Main class
> - Orange box: Subclass implementations
> - Light purple box: Configuration and data classes
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

```python
from petsard import Loader

# Load CSV file
loader = Loader('data.csv')
data, schema = loader.load()

# Use custom schema
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()
```

## Main Classes

### Loader

Main data loading class.

#### Constructor

```python
Loader(
    filepath: str,
    column_types: dict = None,  # Deprecated - use schema instead
    header_names: list = None,  # Deprecated - will be removed in v2.0.0
    na_values: Any = None,       # Deprecated - use schema instead
    schema: Schema | dict | str = None
)
```

#### Parameters

- `filepath`: Data file path
- `schema`: Schema configuration (can be Schema object, dictionary, or YAML path)

For detailed parameter configuration, please refer to the Loader YAML documentation.

### LoaderConfig

Loader's internal configuration class containing file path parsing and validation logic.

### LoaderFileExt

File extension mapping class for determining file types.

## Supported Formats

- **CSV**: `.csv`, `.tsv`
- **Excel**: `.xlsx`, `.xls`, `.xlsm`, `.xlsb` *
- **OpenDocument**: `.ods`, `.odf`, `.odt` *
- **Benchmark**: `benchmark://` protocol

\* Excel and OpenDocument formats require additional packages, see Loader YAML documentation for detailed configuration.

## Notes

- `column_types`, `na_values`, and `header_names` parameters are deprecated and will be removed in v2.0.0
- Recommend using Schema to define data structure
- For detailed Schema configuration, refer to Metadater API documentation
- Excel format requires `openpyxl` package