---
title: "apply()"
weight: 352
---

Apply configured constraints to input data.

## Syntax

```python
def apply(
    df: pd.DataFrame,
    target_rows: int = None
) -> pd.DataFrame
```

## Parameters

- **df** : pd.DataFrame, required
    - Input dataframe to apply constraints to
    - Required parameter

- **target_rows** : int, optional
    - Target number of rows
    - Used internally by `\1`
    - Used for target row count setting in field proportion constraints
    - Default value: `None`

## Return Value

- **pd.DataFrame**
    - Dataframe after applying all constraint conditions
    - May have fewer rows than input dataframe (due to constraint filtering)

## Description

The `\1` method applies all configured constraint conditions sequentially in the following order:

1. **NaN Groups** (`nan_groups`): Handle null value related rules
2. **Field Constraints** (`field_constraints`): Check field value domain constraints
3. **Field Combinations** (`field_combinations`): Validate field combination rules
4. **Field Proportions** (`field_proportions`): Maintain field proportion distributions

Each stage filters data rows that don't meet conditions, ultimately returning data that satisfies all constraints simultaneously.

### Constraint Application Flow

```
Input Data (N rows)
    ↓
NaN Groups Processing (delete/erase/copy)
    ↓
Field Constraints Filtering (value domain checks)
    ↓
Field Combinations Filtering (combination rules)
    ↓
Field Proportions Filtering (proportion maintenance)
    ↓
Output Data (≤N rows)
```

## Basic Examples

### Simple Constraint Application

```python
from petsard import Constrainer
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'age': [25, 15, 45, 70, 35],
    'performance': [5, 3, 4, 2, 5],
    'education': ['PhD', 'Bachelor', 'Master', 'Bachelor', 'PhD']
})

# Configure constraints
config = {
    'field_constraints': [
        "age >= 18 & age <= 65",
        "performance >= 4"
    ]
}

# Apply constraints
constrainer = Constrainer(config)
result = constrainer.apply(df)

print(f"Original rows: {len(df)}")
print(f"After constraints: {len(result)}")
# Original rows: 5
# After constraints: 2 (only data with age 25 and 35 satisfy conditions)
```

### Multiple Constraint Application

```python
from petsard import Constrainer
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'name': ['Alice', None, 'Charlie', 'David'],
    'age': [25, 30, 45, 55],
    'salary': [50000, 60000, 80000, 90000],
    'education': ['Bachelor', 'Master', 'PhD', 'Master']
})

# Configure multiple constraints
config = {
    'nan_groups': {
        'name': 'delete'  # Delete rows where name is null
    },
    'field_constraints': [
        "age >= 20 & age <= 50"  # Age restriction
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {
                'PhD': [70000, 80000, 90000],  # PhD salary range
                'Master': [50000, 60000, 70000]  # Master salary range
            }
        )
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)

print("Data after applying constraints:")
print(result)
# Only retains data that simultaneously satisfies:
# 1. name is not null
# 2. age is between 20-50
# 3. education-salary combination follows rules
```

## Advanced Examples

### With Field Proportion Constraints

```python
from petsard import Constrainer
import pandas as pd

# Prepare data (imbalanced categories)
df = pd.DataFrame({
    'category': ['A'] * 80 + ['B'] * 15 + ['C'] * 5,
    'value': range(100)
})

print("Original distribution:")
print(df['category'].value_counts())
# A    80
# B    15
# C     5

# Configure field proportion constraints
config = {
    'field_proportions': [
        {
            'fields': 'category',
            'mode': 'all',
            'tolerance': 0.1  # Allow 10% deviation
        }
    ]
}

constrainer = Constrainer(config)
# Note: Usually target_rows is automatically set by resample_until_satisfy
# Set manually here for demonstration
result = constrainer.apply(df, target_rows=50)

print("\nDistribution after constraints:")
print(result['category'].value_counts())
# Will maintain original proportion (80:15:5), but total around 50 rows
```

### Complex Condition Combinations

```python
from petsard import Constrainer
import pandas as pd

# Prepare employee data
df = pd.DataFrame({
    'workclass': ['Private', None, 'Government', 'Private', 'Self-emp'],
    'occupation': ['Manager', 'Sales', None, 'Tech', 'Manager'],
    'age': [35, 28, 45, 22, 50],
    'hours_per_week': [40, 35, 50, 65, 38],
    'income': ['>50K', '<=50K', '>50K', '<=50K', '>50K'],
    'education': ['Master', 'Bachelor', 'PhD', 'Bachelor', 'Master']
})

config = {
    'nan_groups': {
        'workclass': 'delete',  # Delete rows where workclass is null
        'occupation': {
            'erase': ['income']  # Clear income when occupation is null
        }
    },
    'field_constraints': [
        "age >= 18 & age <= 65",
        "hours_per_week >= 20 & hours_per_week <= 60",
        "(education == 'PhD' & income == '>50K') | education != 'PhD'"
    ],
    'field_combinations': [
        (
            {'education': 'income'},
            {
                'PhD': ['>50K'],  # PhD must have high income
                'Master': ['>50K', '<=50K']  # Master can be high or low
            }
        )
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)

print(f"Original data: {len(df)} rows")
print(f"After constraints: {len(result)} rows")
print("\nData after constraints:")
print(result)
```

## Important Notes

- **Data Copy**: Method copies input dataframe, does not modify original data
- **Order Matters**: Constraints are applied in fixed order, cannot be adjusted
- **Data Reduction**: Constraints typically filter data, returned row count may significantly decrease
- **AND Logic**: All constraints combined with AND, data must satisfy all to be retained
- **target_rows**: General users don't need to manually set this parameter, used internally by `\1`
- **Empty Results**: If constraints are too strict, may return empty dataframe
- **Performance Considerations**: Complex constraints on large datasets may require longer execution time
- **Field Proportions**: Proportion maintenance only occurs when field_proportions is configured and target_rows is provided
- **Validation Recommendation**: Recommended to test constraint reasonableness with small samples before applying

## Related Methods

- `\1`: Initialize constraint configuration
- `\1`: Resample repeatedly until constraints satisfied
- `\1`: Register custom constraint types