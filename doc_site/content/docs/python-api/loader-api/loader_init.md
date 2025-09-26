---
title: "init"
weight: 311
---

Initialize a data loader instance.

## Syntax

```python
def __init__(
    filepath: str = None,
    column_types: dict = None,
    header_names: list = None,
    na_values: str | list | dict = None,
    schema: Schema | dict | str = None
)
```

## Parameters

- **filepath** : str, required
    - Data file path
    - Required parameter

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

## Returns

- **Loader**
    - Initialized loader instance

## Basic Examples

```python
from petsard import Loader

# Load CSV file
loader = Loader('data.csv')

# Use schema YAML
loader = Loader('data.csv', schema='schema.yaml')

# Use schema dictionary
schema_dict = {
    'id': 'my_schema',
    'name': 'My Schema'
}
loader = Loader('data.csv', schema=schema_dict)
```

## Notes

- Recommend using YAML configuration file rather than direct Python API
- File paths support both relative and absolute paths
- For supported file formats, refer to Loader YAML documentation
- Initialization only creates configuration, actual data loading requires calling `load()` method
- Excel format requires `openpyxl` package
- This documentation is for internal development team reference only, backward compatibility is not guaranteed