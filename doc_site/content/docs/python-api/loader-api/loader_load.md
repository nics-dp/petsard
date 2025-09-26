---
title: "load"
weight: 312
---

Load data and return DataFrame and Schema.

## Syntax

```python
def load() -> tuple[pd.DataFrame, Schema]
```

## Parameters

None

## Returns

- **tuple[pd.DataFrame, Schema]**
    - A tuple containing two elements:
        - `data` (`pd.DataFrame`): Loaded data table
        - `schema` (`Schema`): Data structure metadata

## Description

The `load()` method is used to actually load data. This method must be called after `__init__()`.

This method performs the following operations based on the configuration during initialization:
1. Merge legacy parameters into schema
2. Read data using pandas reader module
3. Process and validate schema through metadater
4. Return processed DataFrame and Schema

## Basic Examples

```python
from petsard import Loader

# Initialize loader
loader = Loader('data.csv')

# Load data
data, schema = loader.load()

# View results
print(f"Data shape: {data.shape}")
print(f"Schema ID: {schema.id}")
print(f"Number of attributes: {len(schema.attributes)}")
```

## Notes

- Recommend using YAML configuration file rather than direct Python API
- Must call `__init__()` to initialize loader first
- For detailed Schema information, refer to Metadater API documentation
- For large files, recommend using appropriate parameters to save memory
- Returned DataFrame is a copy, not a reference, modifications won't affect the original file
- Excel format requires `openpyxl` package