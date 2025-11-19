---
title: "ConstrainerAdapter"
weight: 4
---

ConstrainerAdapter handles constraint application for synthetic data, integrating Constrainer with the execution framework.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/constraineradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: ConstrainerAdapter main class
> - Blue box: Core constraint modules
> - Purple box: Various constraint handlers
> - `..>`: Dependency relationship
> - `-->`: Management relationship

## Main Features

- Unified constraint processing interface
- Automatic YAML configuration format conversion
- Supports two constraint modes:
  - Simple constraints: Direct data filtering
  - Resampling constraints: Repeated generation until conditions satisfied
- Integrates Synthesizer and Postprocessor
- Automatic field combination rule format handling

## Method Reference

### `__init__(config: dict)`

Initialize ConstrainerAdapter instance.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - **Configuration approach (choose one):**
    1. **Using YAML file (recommended):**
       - `constraints_yaml`: str - Path to YAML file containing all constraint configurations
    2. **Using individual parameters:**
       - `nan_groups`: Null value handling rules
       - `field_constraints`: Field constraint conditions
       - `field_combinations`: Field combination rules
       - `field_proportions`: Field proportion maintenance rules
  - Resampling parameters (optional, compatible with both configuration approaches):
    - `target_rows`: Target row count
    - `sampling_ratio`: Sampling ratio (default 10.0)
    - `max_trials`: Maximum attempts (default 300)
    - `verbose_step`: Progress display frequency (default 10)

**Note:** `constraints_yaml` and individual constraint parameters (nan_groups, field_constraints, etc.) cannot be used simultaneously, or it will raise `ConfigError`.

### `run(input: dict)`

Execute constraint processing.

**Parameters:**
- `input`: dict, required
  - Input parameter dictionary
  - Required fields:
    - `data`: pd.DataFrame - Data to constrain
  - Optional fields:
    - `synthesizer`: Synthesizer - For resampling
    - `postprocessor`: Postprocessor - For data restoration

**Returns:**
No direct return value. Use `get_result()` to retrieve results.

### `get_result()`

Retrieve data after constraint processing.

**Returns:**
- `pd.DataFrame`: Data meeting constraint conditions

## Usage Examples

### Approach 1: Using YAML File (Recommended)

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# Using YAML file configuration
config = {
    'constraints_yaml': 'config/constraints.yaml',
    # Optional: resampling parameters
    'target_rows': 1000,
    'sampling_ratio': 10.0
}

adapter = ConstrainerAdapter(config)

# Prepare input
input_data = {
    'data': df
}

# Execute constraints
adapter.run(input_data)

# Get result
constrained_data = adapter.get_result()
```

**Example constraints.yaml:**
```yaml
nan_groups:
  workclass: delete

field_constraints:
  - "age >= 18 & age <= 65"
  - "hours_per_week >= 1 & hours_per_week <= 99"

field_combinations:
  -
    - education: workclass
    - Doctorate: [Prof-specialty, Exec-managerial]
```

### Approach 2: Using Individual Parameters

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# Directly specify constraint configuration in code
config = {
    'nan_groups': {
        'workclass': 'delete'
    },
    'field_constraints': [
        "age >= 18 & age <= 65"
    ]
}

adapter = ConstrainerAdapter(config)

# Prepare input
input_data = {
    'data': df
}

# Execute constraints
adapter.run(input_data)

# Get result
constrained_data = adapter.get_result()
```

### Using Resampling

```python
from petsard.adapter import ConstrainerAdapter
import pandas as pd

# Configuration with resampling parameters
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",
        "salary >= 60000"
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [80000, 90000, 100000]}
        )
    ],
    # Resampling parameters
    'target_rows': 1000,
    'sampling_ratio': 20.0,
    'max_trials': 100,
    'verbose_step': 10
}

adapter = ConstrainerAdapter(config)

# Prepare input (including synthesizer)
input_data = {
    'data': initial_data,
    'synthesizer': synthesizer,  # Trained Synthesizer instance
    'postprocessor': postprocessor  # Optional
}

# Execute resampling constraints
adapter.run(input_data)

# Get result
result = adapter.get_result()
print(f"Final row count: {len(result)}")
```

### Complete Workflow Example

```python
from petsard.adapter import (
    LoaderAdapter,
    PreprocessorAdapter,
    SynthesizerAdapter,
    PostprocessorAdapter,
    ConstrainerAdapter
)

# 1. Load data
loader_config = {'filepath': 'data.csv'}
loader = LoaderAdapter(loader_config)
loader.run({})
data = loader.get_result()
schema = loader.get_metadata()

# 2. Preprocess
preprocessor_config = {'method': 'default'}
preprocessor = PreprocessorAdapter(preprocessor_config)
preprocessor.run({'data': data, 'metadata': schema})
processed_data = preprocessor.get_result()

# 3. Synthesize
synthesizer_config = {'method': 'default', 'sample_num_rows': 1000}
synthesizer = SynthesizerAdapter(synthesizer_config)
synthesizer.run({'data': processed_data, 'metadata': schema})
synthetic_data = synthesizer.get_result()

# 4. Postprocess
postprocessor_config = {'method': 'default'}
postprocessor = PostprocessorAdapter(postprocessor_config)
postprocessor.run({
    'data': synthetic_data,
    'preprocessor': preprocessor.processor
})
postprocessed_data = postprocessor.get_result()

# 5. Constrain
constrainer_config = {
    'field_constraints': [
        "age >= 18 & age <= 65"
    ],
    'field_proportions': [
        {'fields': 'category', 'mode': 'all', 'tolerance': 0.1}
    ],
    # Resampling parameters
    'target_rows': 800,
    'sampling_ratio': 15.0
}

constrainer = ConstrainerAdapter(constrainer_config)
constrainer.run({
    'data': postprocessed_data,
    'synthesizer': synthesizer.synthesizer,
    'postprocessor': postprocessor.processor
})

# Get final result
final_data = constrainer.get_result()
print(f"Final data row count: {len(final_data)}")
```

## Workflow

### Simple Constraint Mode

```
Input Data
  ↓
Apply constraints
  ↓
Return data meeting conditions
```

### Resampling Constraint Mode

```
Input Data
  ↓
Apply constraints
  ↓
Sufficient data? ──Yes──> Return result
  ↓ No
Start iteration
  ↓
Generate new data using Synthesizer
  ↓
Restore data using Postprocessor (if present)
  ↓
Apply constraints
  ↓
Accumulate data meeting conditions
  ↓
Target reached? ──Yes──> Return result
  ↓ No
Below max attempts? ──Yes──> Continue iteration
  ↓ No
Return collected data (warning)
```

## Configuration Conversion

ConstrainerAdapter automatically converts YAML configuration format:

### field_combinations Conversion

List format in YAML configuration is automatically converted to tuples:

```yaml
# YAML format
field_combinations:
  -
    - education: income
    - Doctorate: ['>50K']
```

Converted to:

```python
# Python format
field_combinations = [
    (
        {'education': 'income'},
        {'Doctorate': ['>50K']}
    )
]
```

## Constraint Mode Selection

### When to Use Simple Constraints (apply)

- Data is already sufficient
- Constraint conditions are not too strict
- No need for repeated data generation
- Configuration **does not include** `target_rows`, `synthesizer`, or other resampling parameters

```python
config = {
    'field_constraints': ["age >= 18"]
}
# Only filters data, does not regenerate
```

### When to Use Resampling Constraints (resample_until_satisfy)

- Specific amount of data needed
- Strict constraint conditions, insufficient data after filtering
- Configuration **includes** resampling parameters
- Input **includes** `synthesizer`

```python
config = {
    'field_constraints': ["age >= 18"],
    'target_rows': 1000,
    'sampling_ratio': 20.0
}
input_data = {
    'data': df,
    'synthesizer': trained_synthesizer  # Key: provide synthesizer
}
# Repeatedly generates until reaching 1000 rows
```

## Input Data Source

ConstrainerAdapter automatically retrieves data from previous modules:

| Preceding Module | Data Source |
|-----------------|-------------|
| Splitter | `train` data |
| Loader | Complete data |
| Preprocessor | Preprocessed data |
| Synthesizer | Synthetic data |
| Postprocessor | Postprocessed data |

## Important Notes

- **Internal API**: This is an internal API, direct use not recommended
- **Recommended Practice**: Use YAML configuration files and Executor
- **Constraint Order**: Applied sequentially: nan_groups → field_constraints → field_combinations → field_proportions
- **Synthesizer Requirement**: When using resampling, synthesizer must be trained via `fit()`
- **Memory Considerations**: Large sampling_ratio consumes more memory
- **Result Caching**: Results are cached until next run() call
- **Automatic Conversion**: field_combinations automatically converted from list format to tuple format
- **AND Logic**: All constraint conditions combined with AND

## Error Handling

### Configuration Errors

```python
# Error: config is None
adapter = ConstrainerAdapter(None)
# Raises ConfigError

# Error: Using both constraints_yaml and individual parameters
config = {
    'constraints_yaml': 'constraints.yaml',
    'nan_groups': {'age': 'delete'}  # Conflict!
}
adapter = ConstrainerAdapter(config)
# Raises ConfigError: Cannot specify both 'constraints_yaml' and individual constraint parameters

# Error: YAML file does not exist
config = {'constraints_yaml': 'non_existent.yaml'}
adapter = ConstrainerAdapter(config)
# Raises ConfigError: Constraints YAML file not found

# Error: field_combinations incorrect format
config = {
    'field_combinations': 'invalid'  # Should be list
}
# Raises validation error
```

### Execution Errors

```python
# Error: Using resampling without providing synthesizer
config = {'target_rows': 1000}
adapter = ConstrainerAdapter(config)
adapter.run({'data': df})  # Missing synthesizer
# Cannot resample, can only use simple filtering

# Error: Untrained synthesizer
adapter.run({
    'data': df,
    'synthesizer': untrained_synthesizer  # fit() not called
})
# Raises error
```

## Performance Considerations

### Constraint Complexity

- **Simple conditions**: `age >= 18` (fast)
- **Medium conditions**: `age >= 18 & salary > 50000` (moderate)
- **Complex conditions**: Multiple nested parentheses, multiple combination rules (slower)

### Resampling Performance

Factors affecting resampling performance:

1. **Constraint Strictness**: Stricter requires more iterations
2. **sampling_ratio**: Larger generates more data each time
3. **target_rows**: Larger target requires more time
4. **Synthesizer Speed**: Depends on synthesis method used

### Optimization Recommendations

```python
# 1. Adjust sampling_ratio
# Non-strict constraints: Use smaller value (5-10)
# Strict constraints: Use larger value (20-50)
config = {
    'sampling_ratio': 20.0  # Adjust based on constraint strictness
}

# 2. Set reasonable max_trials
config = {
    'max_trials': 100  # Avoid infinite loops
}

# 3. Use verbose_step to monitor progress
config = {
    'verbose_step': 10  # Show progress every 10 attempts
}