---
title: Metadater
type: docs
weight: 53
prev: docs/api/executor
next: docs/api/splitter
---


```python
Metadater
```

Metadata management system providing data structure description and management capabilities. Adopts a three-layer architecture design with operation-configuration separation pattern.

## Architecture Design

### 📊 Three-Layer Mapping
| Config Layer | Data Mapping | Description |
|---------|---------|------|
| **Metadata** | Datasets | Manage multi-table datasets |
| **Schema** | Table | Define single table structure |  
| **Attribute** | Field | Describe field attributes |

### 🔧 Operation-Config Separation
- **Operation Classes**: `Metadater`, `SchemaMetadater`, `AttributeMetadater`
- **Config Classes**: `Metadata`, `Schema`, `Attribute` (frozen dataclasses)
- **Data Abstraction**: `Datasets`, `Table`, `Field`

## Basic Usage

### Infer from Data
```python
from petsard.metadater import Metadater, SchemaMetadater
import pandas as pd

# Single table
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# Automatic schema inference
schema = SchemaMetadater.from_data(df)

# Multi-table dataset
data = {
    'users': df,
    'orders': pd.DataFrame({
        'order_id': [101, 102],
        'user_id': [1, 2],
        'amount': [99.99, 149.99]
    })
}

# Create metadata
metadata = Metadater.from_data(data)
```

### Create from Configuration
```python
# Create from YAML config
config = {
    'id': 'my_dataset',
    'schemas': {
        'users': {
            'id': 'users',
            'fields': {  # Use fields in YAML
                'id': {
                    'type': 'int64',
                    'nullable': False
                },
                'email': {
                    'type': 'object',
                    'logical_type': 'email'
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)
```

## Main Methods

### `from_data()`

```python
Metadater.from_data(
    data: dict[str, pd.DataFrame],
    enable_stats: bool = False
) -> Metadata
```

Automatically infer and create metadata structure from data.

**Parameters**
- `data` (dict[str, pd.DataFrame]): Dictionary of data tables
- `enable_stats` (bool, optional): Whether to calculate statistics, defaults to `False`

**Returns**
- `Metadata`: Metadata object (includes statistics when `enable_stats=True`)

### `from_dict()`

```python
Metadater.from_dict(config: dict) -> Metadata
```

Create metadata from configuration dictionary.

**Parameters**
- `config` (dict): Metadata configuration

**Returns**
- `Metadata`: Metadata object

### `diff()`

```python
Metadater.diff(metadata: Metadata, data: dict[str, pd.DataFrame]) -> dict
```

Compare differences between metadata definition and actual data.

**Parameters**
- `metadata` (Metadata): Metadata definition
- `data` (dict[str, pd.DataFrame]): Actual data

**Returns**
- `dict`: Difference report

### `align()`

```python
Metadater.align(metadata: Metadata, data: dict[str, pd.DataFrame], strategy: dict = None) -> dict[str, pd.DataFrame]
```

Align data structure according to metadata definition.

**Parameters**
- `metadata` (Metadata): Metadata definition
- `data` (dict[str, pd.DataFrame]): Data to align
- `strategy` (dict, optional): Alignment strategy

**Returns**
- `dict[str, pd.DataFrame]`: Aligned data

## Data Structures

### Metadata (Top Level)
```python
@dataclass(frozen=True)
class Metadata:
    id: str                        # Dataset identifier
    schemas: dict[str, Schema]     # Table schemas dictionary
    stats: DatasetsStats | None    # Dataset statistics (generated when enable_stats=True)
    diffs: dict | None             # Difference records
    change_history: list | None    # Change history
```

### Schema (Middle Level)
```python
@dataclass(frozen=True)
class Schema:
    id: str                              # Table identifier
    attributes: dict[str, Attribute]     # Field attributes dictionary
    stats: TableStats | None             # Table statistics (generated when enable_stats=True)
```

### Attribute (Bottom Level)
```python
@dataclass(frozen=True)
class Attribute:
    name: str                # Field name
    type: str                # Data type
    nullable: bool           # Allow nulls
    logical_type: str | None # Logical type
    stats: FieldStats | None # Field statistics (generated when enable_stats=True)
```

## Data Abstraction Layer

### Field
```python
@dataclass
class Field:
    data: pd.Series      # Data series
    attribute: Attribute # Field attribute
    
    @classmethod
    def create(cls, data: pd.Series, attribute: Attribute = None) -> Field:
        """Create Field instance"""
```

### Table  
```python
@dataclass
class Table:
    data: pd.DataFrame  # Data frame
    schema: Schema      # Table schema
    
    @classmethod
    def create(cls, data: pd.DataFrame, schema: Schema = None) -> Table:
        """Create Table instance"""
```

### Datasets
```python
@dataclass
class Datasets:
    data: dict[str, pd.DataFrame]  # Tables dictionary
    metadata: Metadata              # Metadata
    
    @classmethod
    def create(cls, data: dict[str, pd.DataFrame], metadata: Metadata = None) -> Datasets:
        """Create Datasets instance"""
```

## Alignment Strategy

```python
strategy = {
    'add_missing_columns': True,    # Add missing columns
    'remove_extra_columns': False,  # Remove extra columns  
    'reorder_columns': True,        # Reorder columns
    'add_missing_tables': False     # Add missing tables
}
```

## Examples

### Basic Usage

```python
from petsard.metadater import Metadater
import pandas as pd

# Prepare data
data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com']
    })
}

# Create metadata from data
metadata = Metadater.from_data(data)

print(f"Dataset ID: {metadata.id}")
print(f"Number of tables: {len(metadata.schemas)}")

# Include statistics
metadata_with_stats = Metadater.from_data(data, enable_stats=True)
users_schema = metadata_with_stats.schemas['users']
print(f"Row count: {users_schema.stats.row_count if users_schema.stats else 'N/A'}")
```

### Difference Comparison

```python
# Modified data
new_data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3, 4],  # Extra row
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 40]  # Extra column
    })
}

# Compare differences
diff_result = Metadater.diff(metadata, new_data)

print(f"Missing tables: {diff_result.get('missing_tables', [])}")
print(f"Extra tables: {diff_result.get('extra_tables', [])}")
```

### Data Alignment

```python
# Inconsistent data
messy_data = {
    'users': pd.DataFrame({
        'id': ['1', '2', '3'],  # Wrong type
        'email': ['a@test.com', 'b@test.com', 'c@test.com'],
        'extra_col': [1, 2, 3]  # Extra column
    })
}

# Align data
aligned_data = Metadater.align(metadata, messy_data)

# aligned_data now conforms to metadata definition
```

### Using Data Abstraction Layer

```python
from petsard.metadater import Field, Table, Datasets

# Field level
series = pd.Series([1, 2, 3], name='numbers')
field = Field.create(series)
print(f"Field name: {field.name}")
print(f"Unique count: {field.unique_count}")

# Table level
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
table = Table.create(df)
print(f"Columns: {table.columns}")
print(f"Row count: {table.row_count}")

# Datasets level
data = {'table1': df}
datasets = Datasets.create(data)
print(f"Table names: {datasets.table_names}")
```

## YAML Schema Configuration

Define Schema in YAML:

```yaml
# schemas/user_schema.yaml
id: user_data
fields:  # Use fields to define field attributes
  user_id:
    type: int64
    nullable: false
  username:
    type: object
  email:
    type: object
    logical_type: email
```

Use in Loader:

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```