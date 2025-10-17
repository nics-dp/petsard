---
title: "Metadater API"
weight: 320
---

Data structure metadata manager, providing metadata definition, comparison, and alignment functionality for datasets.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/metadater-api/metadater-class-diagram.mmd" >}}

> **Legend:**
> - Blue boxes: Main operation classes
> - Orange boxes: Operation subclasses
> - Light blue boxes: Data configuration classes
> - `..>`: Create/operate relationship
> - `*--`: Composition relationship
> - `-->`: Call relationship

## Basic Usage

Metadater is primarily used as an internal component, typically accessed through Loader's schema parameter:

```python
# Defined in YAML
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

For direct use of Metadater class methods:

```python
from petsard.metadater import Metadater
import pandas as pd

# Automatically infer structure from data
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# Create metadata from dictionary
config = {'tables': {...}}
metadata = Metadater.from_dict(config)

# Compare data differences
diff = Metadater.diff(metadata, new_data)

# Align data structure
aligned = Metadater.align(metadata, new_data)
```

## Class Method Description

Metadater provides static class methods (`@classmethod` or `@staticmethod`) that can be used without instantiation:

### Creating Metadata

- [`from_data()`](metadater_from_data.md): Automatically infer and create Metadata from data
- [`from_dict()`](metadater_from_dict.md): Create Metadata from configuration dictionary

### Comparison and Alignment

- [`diff()`](metadater_diff.md): Compare differences between Metadata and actual data
- [`align()`](metadater_align.md): Align data structure according to Metadata

## Data Structure

### Metadata
Top level, manages entire dataset:
- `id`: Dataset identifier
- `name`: Dataset name (optional)
- `description`: Dataset description (optional)
- `schemas`: Table structure dictionary `{table_name: Schema}`

### Schema  
Middle level, describes single table:
- `id`: Table identifier
- `name`: Table name (optional)
- `description`: Table description (optional)
- `attributes`: Field attribute dictionary `{field_name: Attribute}`

### Attribute
Bottom level, defines single field:
- `name`: Field name
- `type`: Data type (`int`, `float`, `str`, `bool`, `datetime`, etc.)
- `nullable`: Whether null values are allowed (`True`/`False`)
- `logical_type`: Logical type (optional, e.g., `email`, `phone`, `url`, etc.)
- `na_values`: Custom null value representations (optional)

## Use Cases

### 1. Schema Management During Data Loading

Loader internally uses Metadater to handle schema:

```python
# Loader internal process (simplified)
schema = Metadater.from_dict(schema_config)  # Load from YAML
data = pd.read_csv(filepath)                  # Read data
aligned_data = Metadater.align(schema, data)  # Align data structure
```

### 2. Data Structure Validation

Compare expected structure with actual data:

```python
# Define expected schema
expected_schema = Metadater.from_dict(config)

# Compare actual data
diff = Metadater.diff(expected_schema, {'users': actual_data})

if diff:
    print("Structure differences found:", diff)
```

### 3. Unifying Multiple Dataset Structures

Ensure multiple datasets have the same structure:

```python
# Define standard structure
standard_schema = Metadater.from_data({'users': reference_data})

# Align other datasets
aligned_data1 = Metadater.align(standard_schema, {'users': data1})
aligned_data2 = Metadater.align(standard_schema, {'users': data2})
```

## Notes

- **Primarily Internal Use**: Metadater is mainly for internal PETsARD module use; general users can access it through Loader's `schema` parameter
- **Class Method Design**: All methods are class methods and don't require Metadater instantiation
- **Auto-Inference**: `from_data()` automatically infers field types and nullability
- **Alignment Behavior**: `align()` adjusts field order, supplements missing fields, and converts data types according to schema
- **Difference Detection**: `diff()` detects differences in field names, types, null value handling, etc.
- **YAML Configuration**: For detailed Schema YAML configuration, see [Schema YAML Documentation](../../schema-yaml/)
- **Documentation Notice**: This documentation is for internal development team reference only and does not guarantee backward compatibility