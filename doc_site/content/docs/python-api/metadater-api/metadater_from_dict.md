---
title: "from_dict()"
weight: 322
---

Create metadata structure from configuration dictionary.

## Syntax

```python
@staticmethod
def from_dict(config: dict) -> Metadata
```

## Parameters

- **config** : dict, required
  - Metadata configuration dictionary
  - Required parameter
  - Must conform to Metadata/Schema/Attribute structure specifications

## Returns

- **Metadata**
  - Metadata object created from configuration
  - Contains all defined Schemas and Attributes

## Description

The `from_dict()` method creates Metadata objects from structured configuration dictionaries, suitable for:

1. Converting after loading from YAML configuration files (used internally by Loader)
2. Programmatic schema definition
3. Dynamic data structure definition generation

The configuration dictionary structure should correspond to the hierarchical relationships of Metadata, Schema, and Attribute.

## Basic Example

```python
from petsard.metadater import Metadater

# Define single table schema
config = {
    'id': 'my_dataset',
    'name': 'User Dataset',
    'schemas': {
        'users': {
            'id': 'users',
            'name': 'Users Table',
            'attributes': {
                'id': {
                    'name': 'id',
                    'type': 'int',
                    'nullable': False
                },
                'name': {
                    'name': 'name',
                    'type': 'str',
                    'nullable': False
                },
                'age': {
                    'name': 'age',
                    'type': 'int',
                    'nullable': True
                }
            }
        }
    }
}

# Create metadata
metadata = Metadater.from_dict(config)

# Verify results
print(f"Dataset ID: {metadata.id}")
print(f"Dataset name: {metadata.name}")
print(f"Contains tables: {list(metadata.schemas.keys())}")
```

## Advanced Examples

### Multi-Table Definition

```python
from petsard.metadater import Metadater

# Define schema with multiple tables
config = {
    'id': 'ecommerce_db',
    'name': 'E-commerce Database',
    'description': 'Contains user, order, and product data',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False},
                'email': {'name': 'email', 'type': 'str', 'nullable': False, 'logical_type': 'email'},
                'created_at': {'name': 'created_at', 'type': 'datetime', 'nullable': False}
            }
        },
        'orders': {
            'id': 'orders',
            'attributes': {
                'order_id': {'name': 'order_id', 'type': 'int', 'nullable': False},
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'amount': {'name': 'amount', 'type': 'float', 'nullable': False},
                'status': {'name': 'status', 'type': 'str', 'nullable': False}
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# View table structures
for table_name, schema in metadata.schemas.items():
    print(f"\nTable: {table_name}")
    print(f"  Field count: {len(schema.attributes)}")
    for attr_name in schema.attributes:
        print(f"    - {attr_name}")
```

### Definition with Logical Types

```python
from petsard.metadater import Metadater

# Define schema with special logical types
config = {
    'id': 'contact_info',
    'schemas': {
        'contacts': {
            'id': 'contacts',
            'attributes': {
                'id': {
                    'name': 'id',
                    'type': 'int',
                    'nullable': False
                },
                'email': {
                    'name': 'email',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'email'  # Mark as email
                },
                'phone': {
                    'name': 'phone',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'phone_number'  # Mark as phone number
                },
                'website': {
                    'name': 'website',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'url'  # Mark as URL
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# View logical types
contacts_schema = metadata.schemas['contacts']
for attr_name, attr in contacts_schema.attributes.items():
    logical_type = attr.logical_type or '(none)'
    print(f"{attr_name}: type={attr.type}, logical_type={logical_type}")
```

### Custom Null Value Representations

```python
from petsard.metadater import Metadater

# Define schema with custom null representations
config = {
    'id': 'survey_data',
    'schemas': {
        'responses': {
            'id': 'responses',
            'attributes': {
                'respondent_id': {
                    'name': 'respondent_id',
                    'type': 'int',
                    'nullable': False
                },
                'age': {
                    'name': 'age',
                    'type': 'int',
                    'nullable': True,
                    'na_values': ['unknown', 'N/A', '-1']  # Custom null representations
                },
                'income': {
                    'name': 'income',
                    'type': 'float',
                    'nullable': True,
                    'na_values': ['prefer not to say', '-999']
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# View null value settings
responses_schema = metadata.schemas['responses']
for attr_name, attr in responses_schema.attributes.items():
    na_values = getattr(attr, 'na_values', None)
    if na_values:
        print(f"{attr_name}: custom null values = {na_values}")
```

### Loading from YAML and Converting

```python
from petsard.metadater import Metadater
import yaml

# Read YAML configuration file
with open('schema_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Convert to Metadata object
metadata = Metadater.from_dict(config)

print(f"Loaded from YAML: {metadata.id}")
```

**schema_config.yaml example:**
```yaml
id: example_schema
name: Example Data Structure
schemas:
  users:
    id: users
    attributes:
      user_id:
        name: user_id
        type: int
        nullable: false
      username:
        name: username
        type: str
        nullable: false
```

## Notes

- **Configuration Structure**:
  - Must include `id` and `schemas` fields
  - `schemas` is a dictionary with table names as keys
  - Each schema must include `id` and `attributes`
  - Each attribute must include `name`, `type`, `nullable`
  
- **Type Support**:
  - Basic types: `'int'`, `'float'`, `'str'`, `'bool'`, `'datetime'`
  - Ensure type strings are correct, otherwise validation may fail
  
- **Field Names**:
  - The `name` field defines the actual field name
  - Dictionary keys can differ from `name`, but consistency is recommended
  
- **Optional Fields**:
  - `name`, `description`: Optional fields at Metadata/Schema level
  - `logical_type`: Optional field at Attribute level
  - `na_values`: Custom null representations (optional)
  
- **YAML Relationship**:
  - This method is commonly used to process configurations read from YAML files
  - Loader internally uses this method to handle the `schema` parameter
  - Direct use of YAML configuration is recommended over manual dictionary creation
  
- **Validation Recommendations**:
  - Verify metadata structure meets expectations after creation
  - Large configurations should be split into multiple YAML files for management
  
- **Error Handling**:
  - Configuration format errors will raise exceptions
  - Use try-except to handle configuration loading errors