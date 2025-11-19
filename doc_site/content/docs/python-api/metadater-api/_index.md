---
title: "Metadater API"
weight: 320
---

Data structure metadata manager, providing metadata definition, inference, comparison, and alignment functionality for datasets.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/metadater-api/metadater-class-diagram.mmd" >}}

> **Legend:**
> - Blue boxes: Main operation classes
> - Orange boxes: Configuration classes
> - Light blue boxes: Data abstraction classes
> - `..>`: Create/operate relationship
> - `*--`: Composition relationship
> - `-->`: Call relationship

## Module Overview

The Metadater module provides a three-tier data structure description system:

### Configuration Classes

Define static configuration of data structures:

- [`Metadata`](#metadata): Dataset-level metadata configuration
- [`Schema`](#schema): Table-level structure configuration
- [`Attribute`](#attribute): Field-level attribute configuration

### Operation Classes

Provide class methods to operate on configuration objects:

- [`Metadater`](#metadater): Multi-table operations (corresponds to [`Metadata`](#metadata))
- [`SchemaMetadater`](#schemametadater): Single-table operations (corresponds to [`Schema`](#schema))
- [`AttributeMetadater`](#attributemetadater): Single-field operations (corresponds to [`Attribute`](#attribute))

### Data Abstraction Classes

High-level abstractions combining data with configuration:

- [`Datasets`](#datasets): Multi-table dataset (data + [`Metadata`](#metadata))
- [`Table`](#table): Single table (data + [`Schema`](#schema))
- [`Field`](#field): Single field (data + [`Attribute`](#attribute))

### Schema Inference Tools

- [`SchemaInferencer`](#schemainferencer): Infer Schema changes after Processor transformations
- [`ProcessorTransformRules`](#processortransformrules): Define Processor Schema transformation rules
- [`TransformRule`](#transformrule): Data class for single transformation rule

## Basic Usage

### Through Loader (Recommended)

Metadater is primarily used as an internal component, typically accessed through Loader's schema parameter:

```python
# Defined in YAML
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

### Direct Metadater Usage

For direct metadata operations:

```python
from petsard.metadater import Metadater
import pandas as pd

# Automatically infer structure from data
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# Create metadata from dictionary
config = {'schemas': {'users': {...}}}
metadata = Metadater.from_dict(config)

# Compare data differences
diff = Metadater.diff(metadata, new_data)

# Align data structure
aligned = Metadater.align(metadata, new_data)
```

### Using Data Abstraction Layer

Object-oriented operations combining data with metadata:

```python
from petsard.metadater import Datasets, Table, Field

# Create dataset abstraction
datasets = Datasets.create(data={'users': df}, metadata=metadata)

# Get table
table = datasets.get_table('users')
print(f"Table has {table.row_count} rows, {table.column_count} columns")

# Get field
field = table.get_field('age')
print(f"Field type: {field.dtype}, null count: {field.null_count}")

# Validate data
is_valid, errors = datasets.validate()
if not is_valid:
    print("Validation failed:", errors)
```

## Configuration Classes

### Metadata

Top-level configuration class managing entire dataset:

```python
from petsard.metadater import Metadata, Schema

metadata = Metadata(
    id="my_dataset",
    name="My Dataset",
    description="Dataset description",
    schemas={
        'users': Schema(...),
        'orders': Schema(...),
    }
)
```

**Main Properties**:
- `id`: Dataset identifier
- `name`: Dataset name (optional)
- `description`: Dataset description (optional)
- `schemas`: Table structure dictionary `{table_name: Schema}`
- `enable_stats`: Whether to enable statistics
- `stats`: Dataset statistics (DatasetsStats)

### Schema

Middle-level configuration class describing single table:

```python
from petsard.metadater import Schema, Attribute

schema = Schema(
    id="users",
    name="User Table",
    description="User information",
    attributes={
        'user_id': Attribute(name='user_id', type='int'),
        'email': Attribute(name='email', type='str', logical_type='email'),
    }
)
```

**Main Properties**:
- `id`: Table identifier
- `name`: Table name (optional)
- `description`: Table description (optional)
- `attributes`: Field attribute dictionary `{field_name: Attribute}`
- `primary_key`: Primary key field list
- `enable_stats`: Whether to enable statistics
- `stats`: Table statistics (TableStats)

### Attribute

Bottom-level configuration class defining single field:

```python
from petsard.metadater import Attribute

attribute = Attribute(
    name="age",
    type="int",
    type_attr={
        "nullable": True,
        "category": False,
    },
    logical_type=None,
    description="User age",
)
```

**Main Properties**:
- `name`: Field name
- `type`: Data type (`int`, `float`, `str`, `date`, `datetime`)
- `type_attr`: Type attribute dictionary
  - `nullable`: Whether null values are allowed
  - `category`: Whether it's categorical data
  - `precision`: Numeric precision (decimal places)
  - `format`: Datetime format
  - `width`: String width (for leading zeros)
- `logical_type`: Logical type (e.g., `email`, `phone`, `url`)
- `enable_stats`: Whether to enable statistics
- `stats`: Field statistics (FieldStats)
- `is_constant`: Mark fields with all identical values (auto-detected)

## Operation Classes

### Metadater

Multi-table operation class providing class methods:

#### Creation Methods

- [`from_data(data, enable_stats=False)`](metadater_from_data): Automatically infer and create Metadata from data
- [`from_dict(config)`](metadater_from_dict): Create Metadata from configuration dictionary
- `from_metadata(metadata)`: Copy Metadata configuration

#### Operation Methods

- [`diff(metadata, data)`](metadater_diff): Compare differences between Metadata and actual data
- [`align(metadata, data, strategy=None)`](metadater_align): Align data structure according to Metadata
- `get(metadata, name)`: Get specified Schema from Metadata
- `add(metadata, schema)`: Add Schema to Metadata
- `update(metadata, schema)`: Update Schema in Metadata
- `remove(metadata, name)`: Remove Schema from Metadata

### SchemaMetadater

Single-table operation class providing class methods:

#### Creation Methods

- `from_data(data, enable_stats=False, base_schema=None)`: Create Schema from DataFrame
- `from_dict(config)`: Create Schema from configuration dictionary
- `from_yaml(filepath)`: Load Schema from YAML file
- `from_metadata(schema)`: Copy Schema configuration

#### Operation Methods

- `diff(schema, data)`: Compare differences between Schema and DataFrame
- `align(schema, data, strategy=None)`: Align DataFrame according to Schema
- `get(schema, name)`: Get specified Attribute from Schema
- `add(schema, attribute)`: Add Attribute to Schema
- `update(schema, attribute)`: Update Attribute in Schema
- `remove(schema, name)`: Remove Attribute from Schema

### AttributeMetadater

Single-field operation class providing class methods:

#### Creation Methods

- `from_data(data, enable_stats=True, base_attribute=None)`: Create Attribute from Series
- `from_dict(config)`: Create Attribute from configuration dictionary
- `from_metadata(attribute)`: Copy Attribute configuration

#### Operation Methods

- `diff(attribute, data)`: Compare differences between Attribute and Series
- `align(attribute, data, strategy=None)`: Align Series according to Attribute
- `validate(attribute, data)`: Validate if Series conforms to Attribute definition
- `cast(attribute, data)`: Convert data type according to Attribute definition

## Data Abstraction Classes

### Datasets

Multi-table dataset abstraction combining data with Metadata:

```python
from petsard.metadater import Datasets

# Create dataset
datasets = Datasets.create(
    data={'users': df1, 'orders': df2},
    metadata=metadata  # Optional, auto-inferred
)

# Get information
print(f"Table count: {datasets.table_count}")
print(f"Table names: {datasets.table_names}")

# Operate on tables
table = datasets.get_table('users')
tables = datasets.get_tables()

# Validate and align
is_valid, errors = datasets.validate()
aligned_data = datasets.align()
diff = datasets.diff()
```

### Table

Single table abstraction combining DataFrame with Schema:

```python
from petsard.metadater import Table

# Create table
table = Table.create(
    data=df,
    schema=schema  # Optional, auto-inferred
)

# Get information
print(f"Row count: {table.row_count}")
print(f"Column count: {table.column_count}")
print(f"Column names: {table.columns}")

# Operate on fields
field = table.get_field('age')
fields = table.get_fields()

# Validate and align
is_valid, errors = table.validate()
aligned_df = table.align()
diff = table.diff()
```

### Field

Single field abstraction combining Series with Attribute:

```python
from petsard.metadater import Field

# Create field
field = Field.create(
    data=series,
    attribute=attribute  # Optional, auto-inferred
)

# Get information
print(f"Field name: {field.name}")
print(f"Data type: {field.dtype}")
print(f"Expected type: {field.expected_type}")
print(f"Null count: {field.null_count}")
print(f"Unique count: {field.unique_count}")

# Validate and align
is_valid = field.is_valid
errors = field.get_validation_errors()
aligned_series = field.align()
```

## Schema Inference Tools

### SchemaInferencer

Infer Schema changes after Processor transformations:

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# Infer Preprocessor output Schema
output_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# Infer Schema changes across entire pipeline
pipeline_schemas = inferencer.infer_pipeline_schemas(
    loader_schema=loader_schema,
    pipeline_config=pipeline_config
)

# Get inference history
history = inferencer.get_inference_history()
```

### ProcessorTransformRules

Define Processor Schema transformation rules:

```python
from petsard.metadater import ProcessorTransformRules

# Get transformation rule
rule = ProcessorTransformRules.get_rule('encoder_label')

# Apply rule to Attribute
transformed_attr = ProcessorTransformRules.apply_rule(attribute, rule)

# Apply dynamic transformation info
transformed_attr = ProcessorTransformRules.apply_transform_info(
    attribute, transform_info
)
```

### TransformRule

Data class for single transformation rule:

```python
from petsard.metadater import TransformRule

rule = TransformRule(
    processor_type='encoder',
    processor_method='encoder_label',
    input_types=['categorical', 'string'],
    output_type='int',
    output_logical_type='encoded_categorical',
    affects_nullable=True,
    nullable_after=False,
)
```

## Use Cases

### 1. Schema Management During Data Loading

Loader internally uses Metadater to handle schema:

```python
# Loader internal process (simplified)
metadata = Metadater.from_dict(schema_config)  # Load from YAML
data = pd.read_csv(filepath)                    # Read data
aligned_data = Metadater.align(metadata, {'table': data})  # Align data structure
```

### 2. Data Structure Validation

Use data abstraction layer for validation:

```python
# Create dataset abstraction
datasets = Datasets.create(data={'users': df}, metadata=expected_metadata)

# Validate data
is_valid, errors = datasets.validate()

if not is_valid:
    for table_name, table_errors in errors.items():
        print(f"Table {table_name} validation failed:")
        for field_name, field_errors in table_errors.items():
            print(f"  - {field_name}: {field_errors}")
```

### 3. Unifying Multiple Dataset Structures

Ensure multiple datasets have the same structure:

```python
# Define standard structure
standard_metadata = Metadater.from_data({'users': reference_data})

# Align other datasets
aligned_data1 = Metadater.align(standard_metadata, {'users': data1})
aligned_data2 = Metadater.align(standard_metadata, {'users': data2})
```

### 4. Infer Schema After Processor Transformations

Predict Schema changes before pipeline execution:

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# Infer Preprocessor output
preprocessed_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# Check field type changes
for col_name, attr in preprocessed_schema.attributes.items():
    original_type = loader_schema.attributes[col_name].type
    new_type = attr.type
    if original_type != new_type:
        print(f"Field {col_name} type changed: {original_type} → {new_type}")
```

## Type System

Metadater uses a simplified type system:

### Basic Types

- `int`: Integer type
- `float`: Float type
- `str`: String type
- `date`: Date type
- `datetime`: Datetime type

### Logical Types

Optional semantic types for more precise data description:

- `email`: Email address
- `phone`: Phone number
- `url`: URL
- `encoded_categorical`: Encoded categorical data
- `onehot_encoded`: One-hot encoded
- `standardized`: Standardized numerical values
- `normalized`: Normalized numerical values
- Other custom logical types

### Type Attributes

`type_attr` dictionary contains additional type information:

- `nullable`: Whether null values are allowed (`True`/`False`)
- `category`: Whether it's categorical data (`True`/`False`)
- `precision`: Numeric precision (decimal places)
- `format`: Datetime format string
- `width`: String width (for leading zeros)

## Notes

- **Primarily Internal Use**: Metadater is mainly for internal PETsARD module use; general users can access it through Loader's `schema` parameter
- **Class Method Design**: All operation class methods are class methods and don't require instantiation
- **Immutable Design**: Configuration objects use dataclass design; modifications return new objects
- **Auto-Inference**: `from_data()` automatically infers field types, null handling, and statistics
- **Alignment Behavior**: `align()` adjusts field order, supplements missing fields, and converts data types according to configuration
- **Difference Detection**: `diff()` detects differences in field names, types, null value handling, etc.
- **Statistics**: Set `enable_stats=True` to enable detailed statistics calculation
- **YAML Configuration**: For detailed Schema YAML configuration, see [Schema YAML Documentation](../../schema-yaml/)

## API Documentation

### Metadater Methods

- [`from_data()`](metadater_from_data): Automatically infer and create Metadata from data
- [`from_dict()`](metadater_from_dict): Create Metadata from configuration dictionary
- [`diff()`](metadater_diff): Compare differences between Metadata and actual data
- [`align()`](metadater_align): Align data structure according to Metadata

### Other APIs

For detailed API documentation, refer to individual method pages.