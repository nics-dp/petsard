---
title: "create()"
weight: 362
---

Process report data and return processed data ready for output.

## Syntax

```python
def create(data: dict) -> dict | pd.DataFrame | None
```

## Parameters

- **data** : dict, required
    - Report data dictionary
    - Key-value structure:
        - **Key**: Experiment tuple `(module_name, experiment_name, ...)`
        - **Value**: Data to report (`pd.DataFrame` or `None`)
    - Special keys:
        - `'exist_report'`: For merging previous results (dict format)
        - `'timing_data'`: Timing data for save_timing mode

## Returns

- **dict | pd.DataFrame | None**
    - Return type depends on reporter mode:
        - **save_data mode**: Returns processed DataFrame dictionary `{expt_name: DataFrame}`
        - **save_report mode**: Returns dictionary with granularity-specific results `{'Reporter': {...}}`
        - **save_timing mode**: Returns DataFrame with timing information
        - **save_validation mode**: Returns validation result dictionary
        - **No data processed**: Returns `None` or empty dictionary

## Description

The `create()` method is the first step in Reporter's functional design, used to process input data without storing it in instance variables. Based on the configuration during initialization, this method performs the following operations:

1. **Validate input data format** (via `_verify_create_input()`)
2. **Transform data based on reporter type**
3. **Apply filter conditions** (source, eval, granularity, etc.)
4. **Return processed data** for use by the `report()` method

### Data Validation Rules

Input data undergoes strict validation:
- Experiment tuples must have an even number of elements (module names and experiment names in pairs)
- Module names must be valid PETsARD modules
- Duplicate module names are not allowed
- DataFrame values must be `pd.DataFrame` or `None`

## Basic Examples

### save_data Mode

```python
from petsard import Reporter

# Initialize reporter
reporter = Reporter(method='save_data', source='Synthesizer')

# Prepare data (using tuple as key)
data_dict = {
    ('Synthesizer', 'exp1'): synthetic_df
}

# Process data
processed = reporter.create(data_dict)

# processed contains processed DataFrame dictionary
print(type(processed))  # <class 'dict'>
print(processed.keys())  # dict_keys(['Synthesizer[exp1]'])
```

### save_report Mode

```python
from petsard import Reporter

# Initialize reporter (single granularity)
reporter = Reporter(method='save_report', granularity='global')

# Prepare evaluation results (note experiment name includes granularity marker)
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results_df
}

# Process data
processed = reporter.create(eval_data)

# Generate report
reporter.report(processed)
```

### save_timing Mode

```python
from petsard import Reporter
import pandas as pd

# Initialize reporter
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)

# Prepare timing data (using special key 'timing_data')
timing_data = {
    'timing_data': timing_df
}

# Process data
processed = reporter.create(timing_data)

# processed is a processed DataFrame
print(type(processed))  # <class 'pandas.core.frame.DataFrame'>
```

## Advanced Examples

### Multi-Granularity Reports

```python
from petsard import Reporter

# Initialize multi-granularity reporter
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)

# Prepare data for multiple granularities
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
}

# Process data
processed = reporter.create(eval_data)

# processed contains processed results for all granularities
# Structure: {'Reporter': {'[global]': {...}, '[columnwise]': {...}, '[details]': {...}}}
```

### Merge Previous Reports

```python
from petsard import Reporter
import pandas as pd

# Read previous reports
previous_global = pd.read_csv('previous_global.csv')
previous_columnwise = pd.read_csv('previous_columnwise.csv')

# Initialize reporter
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)

# Prepare data and merge previous results
eval_data = {
    ('Evaluator', 'eval2_[global]'): new_global_results,
    ('Evaluator', 'eval2_[columnwise]'): new_columnwise_results,
    'exist_report': {  # Special key for merging
        '[global]': previous_global,
        '[columnwise]': previous_columnwise
    }
}

# Process data (merges new and old results)
processed = reporter.create(eval_data)

# Generate merged report
reporter.report(processed)
```

### Using Compact Naming Strategy

```python
from petsard import Reporter

# Use compact naming strategy
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# Prepare data
data_dict = {
    ('Synthesizer', 'experiment_1'): df1,
    ('Synthesizer', 'experiment_2'): df2
}

# Process data
processed = reporter.create(data_dict)

# Generate report (filenames will use compact format)
reporter.report(processed)
# Output: petsard_Sy.experiment_1.csv
#         petsard_Sy.experiment_2.csv
```

### Filter Specific Evaluation Experiments

```python
from petsard import Reporter

# Only process specific evaluation experiments
reporter = Reporter(
    method='save_report',
    granularity='global',
    eval='eval1'  # Only process eval1 results
)

# Prepare data for multiple experiments
eval_data = {
    ('Evaluator', 'eval1_[global]'): eval1_results,
    ('Evaluator', 'eval2_[global]'): eval2_results  # This will be filtered out
}

# Process data (only eval1 will be processed)
processed = reporter.create(eval_data)

# Generate report
reporter.report(processed)
```

### Multi-Step Pipeline Data

```python
from petsard import Reporter

# Save data that has gone through multiple processing steps
reporter = Reporter(method='save_data', source='Synthesizer')

# Multi-step experiment tuple
data_dict = {
    ('Loader', 'load1', 'Synthesizer', 'syn1'): synthetic_data
}

# Process data
processed = reporter.create(data_dict)

# processed keys will contain complete experiment path
# e.g., 'Loader[load1]_Synthesizer[syn1]'
```

## Data Format Requirements

### Experiment Tuple Format

Experiment tuples must follow this format:

```python
# Single step: (module_name, experiment_name)
('Synthesizer', 'exp1')
('Evaluator', 'eval1_[global]')

# Multi-step: (module1, experiment1, module2, experiment2, ...)
('Loader', 'data_load', 'Synthesizer', 'syn1')
('Loader', 'load1', 'Evaluator', 'eval1_[global]')
```

**Important Rules:**
- Tuple length must be even
- Odd positions are module names
- Even positions are experiment names
- Module names cannot be duplicated

### Special Keys

#### exist_report

Used for merging previous report results:

```python
{
    ('Evaluator', 'eval1_[global]'): new_data,
    'exist_report': {
        '[global]': previous_report_df,
        '[columnwise]': previous_columnwise_df
    }
}
```

#### timing_data

save_timing mode specific:

```python
{
    'timing_data': timing_dataframe
}
```

## Error Handling

### Invalid Data Format

```python
from petsard import Reporter

reporter = Reporter(method='save_data', source='Synthesizer')

# Error: key is not a tuple
invalid_data = {
    'Synthesizer_exp1': df  # Should be ('Synthesizer', 'exp1')
}

# Error will be caught and logged in _verify_create_input()
processed = reporter.create(invalid_data)
# Invalid data will be removed, may return empty dictionary
```

### Missing Required Data

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# Empty data dictionary
empty_data = {}

processed = reporter.create(empty_data)
# Returns result with warnings
# {'Reporter': {'[global]': {'report': None, 'warnings': '...'}}}
```

### Granularity Mismatch

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# Data contains wrong granularity marker
wrong_granularity = {
    ('Evaluator', 'eval1_[columnwise]'): data  # Expected [global]
}

processed = reporter.create(wrong_granularity)
# Data will be ignored, returns warning
```

## DataFrame Value Handling

### None Values

The `create()` method accepts `None` as DataFrame values:

```python
data_dict = {
    ('Evaluator', 'eval1_[global]'): None  # None is allowed
}

processed = reporter.create(data_dict)
# None values are handled appropriately without errors
```

### Data Validation

Input data undergoes strict validation:

```python
# Valid data types
valid_data = {
    ('Synthesizer', 'exp1'): pd.DataFrame(),  # ✓
    ('Evaluator', 'eval1_[global]'): None,    # ✓
}

# Invalid data types (will be removed)
invalid_data = {
    ('Synthesizer', 'exp1'): "string",        # ✗
    ('Evaluator', 'eval1_[global]'): [1,2,3], # ✗
}
```

## Notes

- **Functional Design**: `create()` does not store data in instance variables; the return value must be passed to the `report()` method
- **Data Validation**: Method validates input data format; invalid formats are logged and removed
- **Memory Efficiency**: When processing large amounts of data, batch processing is recommended to save memory
- **Return Type**: Return type varies based on reporter type
- **Must Call report()**: `create()` only processes data; must call `report()` to generate output files
- **Granularity Matching**: For save_report mode, granularity markers in data must match the granularity specified during initialization
- **Naming Convention**: Experiment tuple naming affects final filenames
- **Module Name Validation**: Only accepts valid PETsARD module names
- **Stateless Operation**: Each call to `create()` is independent and unaffected by previous calls