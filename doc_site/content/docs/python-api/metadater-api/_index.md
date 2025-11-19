---
title: "Metadater API"
weight: 320
---

Data structure metadata manager, providing metadata definition, inference, comparison, and alignment functionality for datasets.

## Module Overview

Metadater uses a three-tier architecture:

### Configuration Classes

Define static configuration of data structures:

- **`Metadata`**: Dataset-level configuration
- **`Schema`**: Table-level configuration
- **`Attribute`**: Field-level configuration

### Operation Classes

Provide class methods to operate on configuration:

- **`Metadater`**: Multi-table operations
- **`SchemaMetadater`**: Single-table operations
- **`AttributeMetadater`**: Single-field operations

### Data Abstraction Classes

High-level abstractions combining data with configuration:

- **`Datasets`**: Multi-table dataset (data + Metadata)
- **`Table`**: Single table (data + Schema)
- **`Field`**: Single field (data + Attribute)

### Schema Inference Tools

- **`SchemaInferencer`**: Infer Schema changes after Processor transformations
- **`ProcessorTransformRules`**: Define transformation rules
- **`TransformRule`**: Data class for single transformation rule

## Basic Usage

### Through Loader (Recommended)

```python
# Defined in YAML
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

### Direct Metadater Usage

```python
from petsard.metadater import Metadater
import pandas as pd

# Infer from data
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# Create from dictionary
config = {'schemas': {'users': {...}}}
metadata = Metadater.from_dict(config)

# Compare differences
diff = Metadater.diff(metadata, new_data)

# Align data
aligned = Metadater.align(metadata, new_data)
```

## Configuration Classes

### Metadata

Dataset-level configuration:

```python
from petsard.metadater import Metadata, Schema

metadata = Metadata(
    id="my_dataset",
    schemas={'users': Schema(...)}
)
```

**Main Properties**:
- `id`: Dataset identifier
- `schemas`: Table structure dictionary `{table_name: Schema}`
- `enable_stats`: Whether to enable statistics
- `stats`: Dataset statistics (DatasetsStats)

### Schema

Table-level configuration:

```python
from petsard.metadater import Schema, Attribute

schema = Schema(
    id="users",
    attributes={
        'user_id': Attribute(name='user_id', type='int'),
        'email': Attribute(name='email', type='str'),
    }
)
```

**Main Properties**:
- `id`: Table identifier
- `attributes`: Field attribute dictionary `{field_name: Attribute}`
- `primary_key`: Primary key field list
- `enable_stats`: Whether to enable statistics
- `stats`: Table statistics (TableStats)

### Attribute

Field-level configuration:

```python
from petsard.metadater import Attribute

attribute = Attribute(
    name="age",
    type="int",
    type_attr={
        "nullable": True,
        "category": False,
    }
)
```

**Main Properties**:
- `name`: Field name
- `type`: Data type (`int`, `float`, `str`, `date`, `datetime`)
- `type_attr`: Type attribute dictionary
  - `nullable`: Whether null values are allowed
  - `category`: Whether it's categorical data
  - `precision`: Numeric precision
  - `format`: Datetime format
  - `width`: String width
- `logical_type`: Logical type (`email`, `phone`, `url`, etc.)
- `enable_stats`: Whether to enable statistics
- `is_constant`: Field with all identical values

## Operation Classes

### Metadater

Class methods for multi-table operations:

#### Creation Methods

- **`from_data(data, enable_stats=False)`**: Infer and create Metadata from data
- **`from_dict(config)`**: Create Metadata from configuration dictionary
- **`from_metadata(metadata)`**: Copy Metadata

#### Operation Methods

- **`diff(metadata, data)`**: Compare differences
- **`align(metadata, data, strategy=None)`**: Align data
- **`get(metadata, name)`**: Get specified Schema
- **`add(metadata, schema)`**: Add Schema
- **`update(metadata, schema)`**: Update Schema
- **`remove(metadata, name)`**: Remove Schema

### SchemaMetadater

Class methods for single-table operations:

#### Creation Methods

- **`from_data(data, enable_stats=False, base_schema=None)`**: Create Schema from DataFrame
- **`from_dict(config)`**: Create Schema from configuration dictionary
- **`from_yaml(filepath)`**: Load Schema from YAML file
- **`from_metadata(schema)`**: Copy Schema

#### Operation Methods

- **`diff(schema, data)`**: Compare differences
- **`align(schema, data, strategy=None)`**: Align data
- **`get(schema, name)`**: Get Attribute
- **`add(schema, attribute)`**: Add Attribute
- **`update(schema, attribute)`**: Update Attribute
- **`remove(schema, name)`**: Remove Attribute

### AttributeMetadater

Class methods for single-field operations:

#### Creation Methods

- **`from_data(data, enable_stats=True, base_attribute=None)`**: Create Attribute from Series
- **`from_dict(config)`**: Create Attribute from configuration dictionary
- **`from_metadata(attribute)`**: Copy Attribute

#### Operation Methods

- **`diff(attribute, data)`**: Compare differences
- **`align(attribute, data, strategy=None)`**: Align data
- **`validate(attribute, data)`**: Validate data
- **`cast(attribute, data)`**: Convert data type

## Data Abstraction Classes

### Datasets

Multi-table dataset abstraction:

```python
from petsard.metadater import Datasets

datasets = Datasets.create(
    data={'users': df},
    metadata=metadata
)

# Basic operations
table = datasets.get_table('users')
is_valid, errors = datasets.validate()
aligned_data = datasets.align()
```

**Main Properties**:
- `table_count`: Number of tables
- `table_names`: List of table names

**Main Methods**:
- `get_table(name)`: Get table
- `get_tables()`: Get all tables
- `validate()`: Validate data
- `align()`: Align data
- `diff()`: Compare differences

### Table

Single table abstraction:

```python
from petsard.metadater import Table

table = Table.create(data=df, schema=schema)

# Basic operations
field = table.get_field('age')
is_valid, errors = table.validate()
```

**Main Properties**:
- `row_count`: Number of rows
- `column_count`: Number of columns
- `columns`: Column names

**Main Methods**:
- `get_field(name)`: Get field
- `get_fields()`: Get all fields
- `validate()`: Validate data
- `align()`: Align data

### Field

Single field abstraction:

```python
from petsard.metadater import Field

field = Field.create(data=series, attribute=attribute)

# Basic information
print(field.dtype, field.null_count, field.unique_count)
```

**Main Properties**:
- `name`: Field name
- `dtype`: Data type
- `expected_type`: Expected type
- `null_count`: Number of null values
- `unique_count`: Number of unique values

**Main Methods**:
- `is_valid`: Validation status
- `get_validation_errors()`: Get errors
- `align()`: Align data

## Schema Inference Tools

### SchemaInferencer

Infer Schema changes after Processor transformations:

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# Infer Preprocessor output
output_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# Infer pipeline Schema changes
pipeline_schemas = inferencer.infer_pipeline_schemas(
    loader_schema=loader_schema,
    pipeline_config=pipeline_config
)
```

### ProcessorTransformRules

Define Processor transformation rules:

```python
from petsard.metadater import ProcessorTransformRules

# Get transformation rule
rule = ProcessorTransformRules.get_rule('encoder_label')

# Apply rule
transformed_attr = ProcessorTransformRules.apply_rule(attribute, rule)
```

## Type System

### Basic Types

- **`int`**: Integer
- **`float`**: Float
- **`str`**: String
- **`date`**: Date
- **`datetime`**: Datetime

### Logical Types

Optional semantic types:

- `email`, `phone`, `url`
- `encoded_categorical`, `onehot_encoded`
- `standardized`, `normalized`

### Type Attributes

`type_attr` contains additional type information:

- `nullable`: Whether null values are allowed
- `category`: Whether it's categorical data
- `precision`: Numeric precision (decimal places)
- `format`: Datetime format
- `width`: String width (leading zeros)

## Notes

- **Primarily Internal Use**: Mainly for internal PETsARD module use; general users access through Loader
- **Class Method Design**: All methods are class methods and don't require instantiation
- **Immutable Design**: Configuration objects return new objects when modified
- **Auto-Inference**: `from_data()` automatically infers types, nulls, and statistics
- **Statistics**: Set `enable_stats=True` to enable detailed statistics