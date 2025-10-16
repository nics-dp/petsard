---
title: "register()"
weight: 356
---

Register a new constraint condition type.

## Syntax

```python
@classmethod
def register(
    cls,
    name: str,
    constraint_class: type
)
```

## Parameters

- **name** : str, required
    - Constraint condition type name
    - Required parameter
    - Used to identify this constraint type in the configuration dictionary
    
- **constraint_class** : type, required
    - Class implementing the constraint condition
    - Required parameter
    - Must inherit from `BaseConstrainer`

## Return Value

None

## Description

[`register()`](constrainer_register.md) is a class method that allows users to extend Constrainer functionality by registering custom constraint types.

### Built-in Constraint Types

Constrainer has the following constraint types registered by default:

- `nan_groups`: [`NaNGroupConstrainer`](../../api/constrainer.md#nan_groups-configuration)
- `field_constraints`: [`FieldConstrainer`](../../api/constrainer.md#field_constraints-configuration)
- `field_combinations`: [`FieldCombinationConstrainer`](../../api/constrainer.md#field_combinations-configuration)
- `field_proportions`: [`FieldProportionsConstrainer`](../../api/constrainer.md#field_proportions-configuration)

### Custom Constraint Class Requirements

Custom constraint classes must:

1. Inherit from `BaseConstrainer` abstract base class
2. Implement `validate_config(df: pd.DataFrame) -> bool` method
3. Implement `apply(df: pd.DataFrame) -> pd.DataFrame` method
4. Accept configuration parameter in `__init__`

## Basic Examples

### Create Simple Custom Constraint

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class MinRowsConstrainer(BaseConstrainer):
    """Ensure data has at least specified number of rows"""
    
    def __init__(self, config: dict):
        self.min_rows = config.get('min_rows', 10)
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """Validate configuration validity"""
        return isinstance(self.min_rows, int) and self.min_rows > 0
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply constraint"""
        if len(df) < self.min_rows:
            raise ValueError(f"Data row count {len(df)} less than minimum requirement {self.min_rows}")
        return df

# Register custom constraint
Constrainer.register('min_rows', MinRowsConstrainer)

# Use custom constraint
config = {
    'min_rows': {'min_rows': 50},
    'field_constraints': [
        "age >= 18"
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### Create Field Range Constraint

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class FieldRangeConstrainer(BaseConstrainer):
    """Constrain field range based on percentiles"""
    
    def __init__(self, config: dict):
        """
        config: {
            'field_name': {
                'lower_percentile': 5,  # Remove values below 5%
                'upper_percentile': 95  # Remove values above 95%
            }
        }
        """
        self.config = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """Validate configuration"""
        for field, params in self.config.items():
            if field not in df.columns:
                return False
            if not (0 <= params.get('lower_percentile', 0) <= 100):
                return False
            if not (0 <= params.get('upper_percentile', 100) <= 100):
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply percentile constraints"""
        result = df.copy()
        
        for field, params in self.config.items():
            lower_p = params.get('lower_percentile', 0)
            upper_p = params.get('upper_percentile', 100)
            
            lower_val = result[field].quantile(lower_p / 100)
            upper_val = result[field].quantile(upper_p / 100)
            
            mask = (result[field] >= lower_val) & (result[field] <= upper_val)
            result = result[mask]
        
        return result.reset_index(drop=True)

# Register constraint
Constrainer.register('field_range', FieldRangeConstrainer)

# Use
config = {
    'field_range': {
        'salary': {
            'lower_percentile': 10,  # Remove lowest 10%
            'upper_percentile': 90   # Remove highest 10%
        },
        'age': {
            'lower_percentile': 5,
            'upper_percentile': 95
        }
    }
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

## Advanced Examples

### Create Dependency Constraint

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class DependencyConstrainer(BaseConstrainer):
    """Constrain dependencies between fields"""
    
    def __init__(self, config: list):
        """
        config: [
            {
                'if': {'field': 'status', 'value': 'active'},
                'then': {'field': 'last_login', 'condition': 'IS NOT pd.NA'}
            }
        ]
        """
        self.rules = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """Validate configuration"""
        for rule in self.rules:
            if_field = rule['if']['field']
            then_field = rule['then']['field']
            if if_field not in df.columns or then_field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply dependency constraints"""
        result = df.copy()
        
        for rule in self.rules:
            if_field = rule['if']['field']
            if_value = rule['if']['value']
            then_field = rule['then']['field']
            then_condition = rule['then']['condition']
            
            # Create condition mask
            if_mask = result[if_field] == if_value
            
            if then_condition == 'IS NOT pd.NA':
                then_mask = result[then_field].notna()
            elif then_condition == 'IS pd.NA':
                then_mask = result[then_field].isna()
            else:
                # Can extend other conditions
                continue
            
            # Retain rows satisfying "if...then..." rules
            result = result[~if_mask | (if_mask & then_mask)]
        
        return result.reset_index(drop=True)

# Register constraint
Constrainer.register('dependency', DependencyConstrainer)

# Use
config = {
    'dependency': [
        {
            'if': {'field': 'employed', 'value': 'yes'},
            'then': {'field': 'salary', 'condition': 'IS NOT pd.NA'}
        },
        {
            'if': {'field': 'has_children', 'value': 'yes'},
            'then': {'field': 'num_children', 'condition': 'IS NOT pd.NA'}
        }
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### Create Statistical Distribution Constraint

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd
import numpy as np

class OutlierConstrainer(BaseConstrainer):
    """Remove statistical outliers"""
    
    def __init__(self, config: dict):
        """
        config: {
            'field_name': {
                'method': 'iqr',  # or 'zscore'
                'threshold': 1.5  # IQR multiple or Z-score threshold
            }
        }
        """
        self.config = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """Validate configuration"""
        for field in self.config.keys():
            if field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers"""
        result = df.copy()
        
        for field, params in self.config.items():
            method = params.get('method', 'iqr')
            threshold = params.get('threshold', 1.5)
            
            if method == 'iqr':
                Q1 = result[field].quantile(0.25)
                Q3 = result[field].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                mask = (result[field] >= lower_bound) & (result[field] <= upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs((result[field] - result[field].mean()) / result[field].std())
                mask = z_scores < threshold
            
            else:
                continue
            
            result = result[mask]
        
        return result.reset_index(drop=True)

# Register constraint
Constrainer.register('outlier', OutlierConstrainer)

# Use
config = {
    'outlier': {
        'salary': {
            'method': 'iqr',
            'threshold': 1.5
        },
        'age': {
            'method': 'zscore',
            'threshold': 3
        }
    }
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### Combine Built-in and Custom Constraints

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

# Define custom constraint class
class UniqueValueConstrainer(BaseConstrainer):
    """Ensure values in specified fields are unique"""
    
    def __init__(self, config: list):
        self.unique_fields = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        for field in self.unique_fields:
            if field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for field in self.unique_fields:
            result = result.drop_duplicates(subset=[field])
        return result.reset_index(drop=True)

# Register
Constrainer.register('unique_values', UniqueValueConstrainer)

# Combine built-in and custom constraints
config = {
    # Built-in constraints
    'nan_groups': {
        'name': 'delete'
    },
    'field_constraints': [
        "age >= 18 & age <= 65"
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [70000, 80000, 90000]}
        )
    ],
    
    # Custom constraints
    'unique_values': ['email', 'id']
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

## Important Notes

- **Class Method**: register() is a class method (@classmethod), can be called without instance
- **Inheritance Requirement**: Custom classes must inherit from `BaseConstrainer`, otherwise raises ValueError
- **Global Registration**: Registered constraint types are globally available, affecting all Constrainer instances
- **Override Built-in**: Can register same name to override built-in constraint types (not recommended)
- **Execution Order**: Custom constraints execute in the order they appear in config
- **Error Handling**: Recommend adding comprehensive error handling and validation in custom constraints
- **Performance Considerations**: Complex custom constraints may impact overall performance
- **Testing Recommendation**: Thoroughly test custom constraint correctness before actual use
- **Documentation**: Write clear docstrings for custom constraint classes

## Related Methods

- [`__init__()`](_index.md#constructor-__init__): Initialize constraint configuration
- [`apply()`](constrainer_apply.md): Apply constraint conditions
- [`resample_until_satisfy()`](constrainer_resample_until_satisfy.md): Resample repeatedly until constraints satisfied