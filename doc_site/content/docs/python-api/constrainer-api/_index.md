---
title: "Constrainer API"
type: docs
weight: 1100
---

Synthetic data constraint processing module.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/constrainer-api/constrainer-class-diagram.mmd" >}}

## Basic Usage

```python
from petsard import Constrainer

# Initialize from YAML config
constrainer = Constrainer(config)

# Apply constraints
constrained_data = constrainer.apply(synthetic_data)

# Validate data
validation_result = constrainer.validate(data)
```

## Constructor

```python
def __init__(config: dict)
```

**Parameters**
- `config`: Constraint configuration dictionary (usually loaded from YAML)

**Example**

```python
config = {
    'nan_groups': {...},
    'field_constraints': [...],
    'field_combinations': [...],
    'field_proportions': [...]
}
constrainer = Constrainer(config)
```

## apply()

Apply all constraints to data.

```python
def apply(df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame
```

**Parameters**
- `df`: Input DataFrame
- `target_rows`: Target row count (optional, for internal use)

**Returns**
- DataFrame meeting all constraints

**Example**

```python
result = constrainer.apply(synthetic_data)
```

## validate()

Validate data against constraints without modifying it.

```python
def validate(
    data: pd.DataFrame,
    return_details: bool = True,
    max_examples_per_rule: int = 6
) -> dict
```

**Parameters**
- `data`: DataFrame to validate
- `return_details`: Whether to return detailed violation records
- `max_examples_per_rule`: Maximum violation examples per rule

**Returns**
- Validation result dictionary containing:
    - `total_rows`: Total row count
    - `passed_rows`: Passed row count
    - `failed_rows`: Failed row count
    - `pass_rate`: Pass rate
    - `is_fully_compliant`: Whether fully compliant
    - `constraint_violations`: Violation statistics
    - `violation_details`: Violation data (optional)

**Example**

```python
result = constrainer.validate(data)
print(f"Pass rate: {result['pass_rate']:.2%}")

if not result['is_fully_compliant']:
    print(result['violation_details'])
```

## resample_until_satisfy()

Resample until constraints are met and target row count is reached.

```python
def resample_until_satisfy(
    data: pd.DataFrame,
    target_rows: int,
    synthesizer,
    postprocessor=None,
    max_trials: int = 300,
    sampling_ratio: float = 10.0,
    verbose_step: int = 10
) -> pd.DataFrame
```

**Parameters**
- `data`: Initial data
- `target_rows`: Target row count
- `synthesizer`: Synthesizer instance
- `postprocessor`: Postprocessor (optional)
- `max_trials`: Maximum trials
- `sampling_ratio`: Sampling multiplier per trial
- `verbose_step`: Progress display interval

**Returns**
- DataFrame meeting constraints and target row count

**Example**

```python
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=1000,
    synthesizer=synthesizer,
    max_trials=50
)
print(f"Trials: {constrainer.resample_trails}")
```

## register()

Register custom constraint type.

```python
@classmethod
def register(cls, name: str, constraint_class: type)
```

**Parameters**
- `name`: Constraint type name
- `constraint_class`: Class inheriting from BaseConstrainer

**Example**

```python
class CustomConstrainer(BaseConstrainer):
    def apply(self, df):
        # Custom logic
        return df

Constrainer.register('custom', CustomConstrainer)
```

## Method Comparison

| Method | Purpose | Modifies Data |
|--------|---------|---------------|
| apply() | Apply and filter constraints | ✅ |
| validate() | Validate data quality | ❌ |
| resample_until_satisfy() | Generate constraint-compliant data | ✅ |

## Notes

- Constraint configuration should be defined in YAML files
- Constraints use strict AND logic combination
- validate() does not modify data, only checks
- resample_until_satisfy() is suitable for strict constraints