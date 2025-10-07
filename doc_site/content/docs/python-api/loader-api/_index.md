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

## Constructor (__init__)

Initialize a data loader instance.

### Syntax

```python
def __init__(
    filepath: str = None,
    column_types: dict = None,
    header_names: list = None,
    na_values: str | list | dict = None,
    schema: Schema | dict | str = None
)
```

### Parameters

- **filepath** : str, required
    - Data file path
    - Required parameter
    - Supports both relative and absolute paths

- **column_types** : dict, optional
    - **Deprecated** - will be removed in v2.0.0
    - Use `schema` parameter instead

- **header_names** : list, optional
    - **Deprecated** - will be removed in v2.0.0
    - Column names for headerless data
    - Default: `None`

- **na_values** : str | list | dict, optional
    - **Deprecated** - will be removed in v2.0.0
    - Use `schema` parameter instead

- **schema** : Schema | dict | str, optional
    - Data structure definition configuration
    - Can be Schema object, dictionary, or YAML file path
    - Default: `None` (auto-inferred)
    - For detailed Schema configuration, refer to Metadater API documentation

### Returns

- **Loader**
    - Initialized loader instance

### Examples

```python
from petsard import Loader

# Basic usage - Load CSV file
loader = Loader('data.csv')

# Use schema YAML configuration file
loader = Loader('data.csv', schema='schema.yaml')

# Use schema dictionary
schema_dict = {
    'id': 'my_schema',
    'name': 'My Schema'
}
loader = Loader('data.csv', schema=schema_dict)

# Load data
data, schema = loader.load()
```

For detailed parameter configuration, please refer to the Loader YAML documentation.

## Supported Formats

- **CSV**: `.csv`, `.tsv`
- **Excel**: `.xlsx`, `.xls`, `.xlsm`, `.xlsb` *
- **OpenDocument**: `.ods`, `.odf`, `.odt` *
- **Benchmark**: `benchmark://` protocol

\* Excel and OpenDocument formats require additional packages, see Loader YAML documentation for detailed configuration.

## Notes

- **Deprecated parameters**: `column_types`, `na_values`, and `header_names` parameters are deprecated and will be removed in v2.0.0
- **Recommendation**: Use YAML configuration file rather than direct Python API
- **Schema usage**: Recommend using Schema to define data structure, for detailed configuration refer to Metadater API documentation
- **Loading process**: Initialization only creates configuration, actual data loading requires calling `load()` method
- **Excel support**: Excel format requires `openpyxl` package
- **Documentation note**: This documentation is for internal development team reference only, backward compatibility is not guaranteed
- **File formats**: For supported file formats, refer to Loader YAML documentation