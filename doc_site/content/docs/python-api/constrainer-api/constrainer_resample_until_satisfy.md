---
title: "resample_until_satisfy()"
weight: 354
---

Repeatedly resample until constraints are satisfied and target row count is reached.

## Syntax

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

## Parameters

- **data** : pd.DataFrame, required
    - Input dataframe to apply constraints to
    - Required parameter
    - If partially constrained data already exists, it serves as the base for further supplementation
    
- **target_rows** : int, required
    - Target number of rows
    - Required parameter
    - Final returned dataframe will contain this number of rows
    
- **synthesizer** : Synthesizer, required
    - Synthesizer instance for generating synthetic data
    - Required parameter
    - Must be a synthesizer already trained via [`fit()`](../synthesizer-api/synthesizer_fit.md)
    
- **postprocessor** : Postprocessor, optional
    - Postprocessor for data transformation
    - Used to convert synthetic data back to original format
    - Default value: `None`
    
- **max_trials** : int, optional
    - Maximum number of attempts
    - Stops even if target row count not met after reaching this number
    - Default value: `300`
    
- **sampling_ratio** : float, optional
    - Multiple of target rows to generate each time
    - Used to compensate for data loss from constraint filtering
    - Default value: `10.0` (generate 10 times the data)
    
- **verbose_step** : int, optional
    - Display progress every N attempts
    - Set to `0` to disable progress display
    - Default value: `10`

## Return Value

- **pd.DataFrame**
    - Dataframe satisfying all constraints with target row count
    - If max_trials reached without satisfaction, returns collected data (may be less than target_rows)

## Attributes

The following attribute is set after execution:

- **resample_trails** : int
    - Number of attempts required to reach target
    - Can be used to evaluate constraint strictness

## Description

The [`resample_until_satisfy()`](constrainer_resample_until_satisfy.md) method is suitable for situations with strict constraints where filtered data is insufficient. It will:

1. First apply constraints to input data
2. Calculate amount of data needed for supplementation
3. Iteratively:
   - Generate new synthetic data using synthesizer
   - Apply postprocessor (if present)
   - Apply all constraint conditions
   - Accumulate data meeting conditions
   - Check if target row count is reached
4. After reaching target, randomly sample target number of rows

### Resampling Flow

```
Start
  ↓
Apply constraints to input data
  ↓
Sufficient? ──Yes──> Random sample target_rows rows ──> Complete
  ↓ No
Start iteration (trials = 0)
  ↓
Generate target_rows × sampling_ratio rows of synthetic data
  ↓
Apply postprocessor (if present)
  ↓
Apply all constraint conditions
  ↓
Accumulate data meeting conditions
  ↓
trials += 1
  ↓
Data sufficient? ──Yes──> Random sample target_rows rows ──> Complete
  ↓ No
trials < max_trials? ──Yes──> Back to "Generate synthetic data"
  ↓ No
Return collected data (warning)
```

## Basic Examples

### Simple Resampling

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# Prepare original data
df = pd.DataFrame({
    'age': [25, 30, 45, 55, 60],
    'salary': [50000, 60000, 80000, 90000, 95000]
})

# Train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit(df)

# Configure strict constraints
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",  # Limit age range
        "salary >= 60000 & salary <= 85000"  # Limit salary range
    ]
}

constrainer = Constrainer(config)

# Resample until reaching 100 rows
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),  # Start from empty
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50,
    sampling_ratio=20.0  # Generate 2000 rows each time
)

print(f"Target rows: 100")
print(f"Actual rows: {len(result)}")
print(f"Attempts: {constrainer.resample_trails}")
# Target rows: 100
# Actual rows: 100
# Attempts: 3
```

### Using Postprocessor

```python
from petsard import Constrainer, Synthesizer, Preprocessor, Postprocessor
import pandas as pd

# Prepare and preprocess data
df = pd.DataFrame({
    'age': [25, 30, 45, 55],
    'category': ['A', 'B', 'A', 'C']
})

preprocessor = Preprocessor('default')
processed_data = preprocessor.fit_transform(df)

# Train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit(processed_data)

# Create postprocessor
postprocessor = Postprocessor('default')
postprocessor.fit(df)  # Train with original data

# Configure constraints
config = {
    'field_constraints': [
        "age >= 20 & age <= 50"
    ],
    'field_proportions': [
        {'fields': 'category', 'mode': 'all', 'tolerance': 0.1}
    ]
}

constrainer = Constrainer(config)

# Resample (with postprocessing)
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=200,
    synthesizer=synthesizer,
    postprocessor=postprocessor,  # Convert encoded data back to original format
    max_trials=100,
    verbose_step=20  # Show progress every 20 attempts
)

print(f"Final row count: {len(result)}")
print(f"Attempts: {constrainer.resample_trails}")
print("\nCategory distribution:")
print(result['category'].value_counts())
```

## Advanced Examples

### Expanding from Existing Data

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# Already have partial data meeting constraints
existing_data = pd.DataFrame({
    'age': [28, 35, 42],
    'performance': [5, 5, 4],
    'education': ['PhD', 'Master', 'PhD']
})

# Configure constraints
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",
        "performance >= 4"
    ],
    'field_combinations': [
        (
            {'education': 'performance'},
            {'PhD': [4, 5], 'Master': [4, 5]}
        )
    ]
}

constrainer = Constrainer(config)

# Expand from existing data to 100 rows
result = constrainer.resample_until_satisfy(
    data=existing_data,  # Use existing data as base
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50
)

print(f"Original data: {len(existing_data)} rows")
print(f"Final data: {len(result)} rows")
print(f"Added data: {len(result) - len(existing_data)} rows")
```

### Monitoring Resampling Process

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# Configure very strict constraints
config = {
    'field_constraints': [
        "age >= 30 & age <= 35",  # Very narrow range
        "salary >= 70000 & salary <= 75000",
        "performance == 5"  # Must be highest score
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [70000, 75000]}  # Only allow PhD
        )
    ]
}

constrainer = Constrainer(config)

# Resample and monitor process
print("Starting resampling...")
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=50,
    synthesizer=synthesizer,
    max_trials=200,
    sampling_ratio=50.0,  # Increase sampling ratio due to strict constraints
    verbose_step=10  # Show progress every 10 attempts
)
# Trial 10: Got 15 rows, need 35 more
# Trial 20: Got 28 rows, need 22 more
# Trial 30: Got 41 rows, need 9 more
# Trial 40: Got 50 rows, need 0 more

print(f"\nComplete!")
print(f"Target rows: 50")
print(f"Actual rows: {len(result)}")
print(f"Total attempts: {constrainer.resample_trails}")
print(f"Average valid data per attempt: {len(result) / constrainer.resample_trails:.2f} rows")
```

### Handling Sampling Failure

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# Configure nearly impossible-to-satisfy constraints
config = {
    'field_constraints': [
        "age == 25 & salary == 100000"  # Extremely specific condition
    ]
}

constrainer = Constrainer(config)

# Attempt resampling
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50,
    sampling_ratio=100.0,
    verbose_step=10
)

if len(result) < 100:
    print(f"Warning: Only collected {len(result)} rows (target 100 rows)")
    print(f"Attempts reached limit: {constrainer.resample_trails}")
    print("Suggestion: Relax constraints or increase max_trials/sampling_ratio")
else:
    print(f"Successfully collected {len(result)} rows")
```

### Optimizing Sampling Parameters

```python
from petsard import Constrainer, Synthesizer
import pandas as pd
import time

config = {
    'field_constraints': [
        "age >= 25 & age <= 45"
    ]
}

constrainer = Constrainer(config)

# Test different sampling_ratio values
for ratio in [5.0, 10.0, 20.0, 50.0]:
    start_time = time.time()
    
    result = constrainer.resample_until_satisfy(
        data=pd.DataFrame(),
        target_rows=100,
        synthesizer=synthesizer,
        sampling_ratio=ratio,
        verbose_step=0  # Disable progress display
    )
    
    elapsed = time.time() - start_time
    
    print(f"Sampling Ratio: {ratio}")
    print(f"  Attempts: {constrainer.resample_trails}")
    print(f"  Execution time: {elapsed:.2f} seconds")
    print(f"  Success rate: {len(result) / (constrainer.resample_trails * 100 * ratio) * 100:.2f}%")
    print()
```

## Important Notes

- **Synthesizer State**: synthesizer must already be trained via [`fit()`](../synthesizer-api/synthesizer_fit.md)
- **Data Accumulation**: Automatically removes duplicate rows to ensure data diversity
- **Memory Usage**: Large sampling_ratio and multiple iterations consume more memory
- **Parameter Tuning**:
    - For strict constraints, increase sampling_ratio
    - For poor synthesizer quality, increase max_trials
    - For quick testing, reduce target_rows
- **Failure Handling**: Reaching max_trials issues warning but still returns collected data
- **Randomness**: Final sampling uses fixed seed (random_state=42) to ensure reproducibility
- **Performance Considerations**: Each iteration fully applies all constraints; may be slow for large datasets
- **Progress Display**: Set verbose_step=0 to disable progress output
- **Proportion Maintenance**: field_proportions automatically uses target_rows as target
- **Initial Data**: Providing initial data can accelerate collection process

## Related Methods

- [`__init__()`](_index.md#constructor-__init__): Initialize constraint configuration
- [`apply()`](constrainer_apply.md): Single application of constraints
- [`register()`](constrainer_register.md): Register custom constraint types