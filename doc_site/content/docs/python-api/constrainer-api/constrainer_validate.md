---
title: "validate()"
weight: 353
---

Validate data against constraints without modifying it.

## Syntax

```python
def validate(
    data: pd.DataFrame,
    return_details: bool = True,
    max_examples_per_rule: int = 6
) -> dict
```

## Parameters

- `data`: DataFrame to validate
- `return_details`: Whether to return detailed violation records (default True)
- `max_examples_per_rule`: Maximum violation examples per rule (default 6)

## Return Value

Validation result dictionary:

```python
{
    'total_rows': 100,           # Total rows
    'passed_rows': 85,           # Passed rows
    'failed_rows': 15,           # Failed rows
    'pass_rate': 0.85,           # Pass rate
    'is_fully_compliant': False, # Fully compliant
    'constraint_violations': {   # Violation statistics
        'field_constraints': {
            'Rule 1: age >= 18': {
                'failed_count': 10,
                'fail_rate': 0.1,
                'violation_examples': [0, 5, 12]
            }
        }
    },
    'violation_details': DataFrame  # Violation data (optional)
}
```

## Differences from Other Methods

| Method | Modifies Data | Returns |
|--------|---------------|---------|
| validate() | ❌ | Validation report |
| apply() | ✅ | Filtered data |
| resample_until_satisfy() | ✅ | Regenerated data |

## Basic Example

```python
from petsard import Constrainer
import pandas as pd

# Prepare data
df = pd.DataFrame({
    'age': [25, 15, 45, 70, 35],
    'performance': [5, 3, 4, 2, 5]
})

# Validate
constrainer = Constrainer(config)
result = constrainer.validate(df)

print(f"Pass rate: {result['pass_rate']:.2%}")
print(f"Fully compliant: {result['is_fully_compliant']}")
```

## View Violation Details

```python
result = constrainer.validate(df, return_details=True)

# Check violation statistics
for constraint_type, violations in result['constraint_violations'].items():
    print(f"\n{constraint_type}:")
    for rule_name, stats in violations.items():
        print(f"  {rule_name}: {stats['failed_count']} violations")

# View violation data
if not result['is_fully_compliant']:
    print(result['violation_details'])
```

## Batch Validation

```python
# Validate multiple batches
batches = {'batch_1': df1, 'batch_2': df2, 'batch_3': df3}

for name, data in batches.items():
    result = constrainer.validate(data, return_details=False)
    print(f"{name}: {result['pass_rate']:.1%}")
```

## Validate Synthetic Data

```python
# Generate synthetic data
synthetic = synthesizer.sample(num_rows=1000)

# Validate quality
result = constrainer.validate(synthetic)

if result['pass_rate'] < 0.95:
    # Poor quality, regenerate
    better_data = constrainer.resample_until_satisfy(
        data=pd.DataFrame(),
        target_rows=1000,
        synthesizer=synthesizer
    )
```

## Notes

- Does not modify input data
- Suitable for data quality checks and monitoring
- `return_details=False` saves memory
- Violation marker columns prefixed with `__violated_`
- Validation results stored in `constrainer.validation_result`