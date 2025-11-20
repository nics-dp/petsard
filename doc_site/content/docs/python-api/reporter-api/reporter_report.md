---
title: "report()"
weight: 364
---

Generate and save report files in CSV format.

## Syntax

```python
def report(processed_data: dict | pd.DataFrame | None = None) -> dict | None
```

## Parameters

- **processed_data** : dict | pd.DataFrame | None, required
    - Output from the `create()` method
    - Required parameter
    - Type depends on reporter mode:
        - **save_data**: DataFrame dictionary `{expt_name: DataFrame}`
        - **save_report**: Granularity result dictionary `{'Reporter': {...}}`
        - **save_timing**: Timing information DataFrame
        - **save_validation**: Validation result dictionary

## Returns

- **dict | None**
    - Returns processed report data
    - save_data: Returns saved data dictionary
    - save_report: Returns original processed_data
    - save_timing: Returns empty dictionary or processed_data
    - No data: Returns empty dictionary `{}`

## Description

The `report()` method is the second step in Reporter's functional design, used to save data processed by `create()` as CSV files. This method will:

1. **Receive processed data**
2. **Generate filename based on naming strategy** (using `_generate_report_filename()`)
3. **Write data to CSV file** (via `_save()` method)
4. **Save to current working directory**

### Filename Generation Logic

Report filenames consist of:
- **Output prefix**: From `output` parameter (default 'petsard')
- **Naming strategy**: traditional or compact
- **Experiment information**: Module name, experiment name, granularity, etc.

## Output Filename Formats

Filename format depends on the `naming_strategy` parameter:

### Traditional Strategy (Default)

| Method | Format | Example |
|--------|--------|---------|
| **save_data** | `{output}_{module-expt_name-pairs}.csv` | `petsard_Synthesizer[exp1].csv` |
| **save_report** | `{output}_Reporter[{eval}_{granularity}].csv` | `petsard_Reporter[eval1_global].csv` |
| **save_timing** | `{output}_timing_report.csv` | `petsard_timing_report.csv` |
| **save_validation** | `{output}_validation_report.csv` | `petsard_validation_report.csv` |

### Compact Strategy

| Method | Format | Example |
|--------|--------|---------|
| **save_data** | `{output}_{module}.{experiment}.csv` | `petsard_Sy.exp1.csv` |
| **save_report** | `{output}.report.{module}.{experiment}.{G}.csv` | `petsard.report.Ev.eval1.G.csv` |
| **save_timing** | `{output}_timing_report.csv` | `petsard_timing_report.csv` |
| **save_validation** | `{output}_validation_report.csv` | `petsard_validation_report.csv` |

**Granularity Abbreviations (Compact Mode):**
- G = Global
- C = Columnwise
- P = Pairwise
- D = Details
- T = Tree

## Basic Examples

### save_data Mode

```python
from petsard import Reporter

# Initialize reporter
reporter = Reporter(method='save_data', source='Synthesizer')

# Prepare and process data
data_dict = {
    ('Synthesizer', 'exp1'): synthetic_df
}
processed = reporter.create(data_dict)

# Generate report file
reporter.report(processed)
# Output: petsard_Synthesizer[exp1].csv
```

### save_report Mode

```python
from petsard import Reporter

# Initialize reporter
reporter = Reporter(method='save_report', granularity='global')

# Prepare and process data
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results
}
processed = reporter.create(eval_data)

# Generate report file
reporter.report(processed)
# Output: petsard_Reporter[eval1_global].csv
```

### save_timing Mode

```python
from petsard import Reporter

# Initialize reporter
reporter = Reporter(
    method='save_timing',
    time_unit='minutes'
)

# Prepare and process data
timing_data = {'timing_data': timing_df}
processed = reporter.create(timing_data)

# Generate report file
reporter.report(processed)
# Output: petsard_timing_report.csv
```

## Advanced Examples

### Using Compact Naming Strategy

```python
from petsard import Reporter

# Use compact naming
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# Process data
data_dict = {
    ('Synthesizer', 'experiment_1'): df1
}
processed = reporter.create(data_dict)

# Generate report with compact filename
reporter.report(processed)
# Output: petsard_Sy.experiment_1.csv (more concise)
```

### Custom Output Filename Prefix

```python
from petsard import Reporter

# Custom prefix
reporter = Reporter(
    method='save_report',
    granularity='global',
    output='my_experiment'
)

# Process data
eval_data = {
    ('Evaluator', 'eval1_[global]'): results
}
processed = reporter.create(eval_data)

# Generate report with custom prefix
reporter.report(processed)
# Output: my_experiment_Reporter[eval1_global].csv
```

### Multi-Granularity Report Generation

```python
from petsard import Reporter

# Multi-granularity reporter
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)

# Prepare multi-granularity data
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
}
processed = reporter.create(eval_data)

# Generate separate report for each granularity
reporter.report(processed)
# Output:
# - petsard_Reporter[eval1_global].csv
# - petsard_Reporter[eval1_columnwise].csv
# - petsard_Reporter[eval1_details].csv
```

### Batch Process Multiple Experiments

```python
from petsard import Reporter

# Initialize reporter
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# Prepare data for multiple experiments
experiments = {
    ('Synthesizer', 'exp1'): synthetic_df1,
    ('Synthesizer', 'exp2'): synthetic_df2,
    ('Synthesizer', 'exp3'): synthetic_df3
}

# Process all data
processed = reporter.create(experiments)

# Generate all reports at once
reporter.report(processed)
# Output:
# - petsard_Sy.exp1.csv
# - petsard_Sy.exp2.csv
# - petsard_Sy.exp3.csv
```

### Filter Specific Module Timing Report

```python
from petsard import Reporter

# Only report timing for specific modules
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']  # Only include these two modules
)

# Prepare timing data (contains all modules)
timing_data = {'timing_data': all_timing_df}
processed = reporter.create(timing_data)

# Generate filtered report
reporter.report(processed)
# Output: petsard_timing_report.csv (only includes Loader and Synthesizer)
```

## Complete Workflow Examples

### Typical Usage Pattern

```python
from petsard import Reporter
import pandas as pd

# Step 1: Initialize reporter
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact',
    output='my_analysis'
)

# Step 2: Prepare evaluation data
evaluation_results = pd.DataFrame({
    'metric': ['accuracy', 'precision', 'recall'],
    'value': [0.85, 0.82, 0.88]
})

# Step 3: Create data dictionary
data_dict = {
    ('Evaluator', 'eval1_[global]'): evaluation_results
}

# Step 4: Process data
processed_data = reporter.create(data_dict)

# Step 5: Generate report
reporter.report(processed_data)
# Output: my_analysis.report.Ev.eval1.G.csv

print("✓ Report generated successfully")
```

### Chained Call Pattern

```python
from petsard import Reporter

# Initialize
reporter = Reporter(method='save_data', source='Synthesizer')

# Chained call: create -> report
reporter.report(
    reporter.create({
        ('Synthesizer', 'exp1'): synthetic_df
    })
)
# Complete processing and report generation in one line
```

## File Operations

### Output Location

Report files are saved in the **current working directory**:

```python
import os
from petsard import Reporter

# Change to specified directory
os.chdir('/path/to/output/directory')

# Generate report
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create(data_dict)
reporter.report(processed)
# Files will be saved in /path/to/output/directory/
```

### File Overwrite Behavior

Files with the same name will be **overwritten**. Use different `output` prefixes or experiment names to avoid overwriting:

```python
from petsard import Reporter
import datetime

# Use timestamp to avoid overwriting
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    output=f'petsard_{timestamp}'
)

processed = reporter.create(data_dict)
reporter.report(processed)
# Output: petsard_20241016_153000_Synthesizer[exp1].csv
```

### CSV Format Details

All report files are saved with the following settings:
- **Format**: CSV (comma-separated)
- **Encoding**: UTF-8
- **Index**: No index column (`index=False`)
- **Header**: Includes column names

## Error Handling

### Handling None Data

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# create() returns None (no data)
processed = reporter.create({})

# report() gracefully handles None
result = reporter.report(processed)
# Returns empty dictionary, no file generated, no error
print(result)  # {}
```

### Handling Invalid Data

```python
from petsard import Reporter

reporter = Reporter(method='save_data', source='Synthesizer')

try:
    # Pass wrong data type
    reporter.report("invalid_data")
except Exception as e:
    print(f"Error: {e}")
```

### Handling Warning Messages

For save_report mode, warnings are logged when no matching data is found:

```python
from petsard import Reporter

reporter = Reporter(
    method='save_report',
    granularity='global'
)

# Data mismatch (wrong granularity)
data = {
    ('Evaluator', 'eval1_[columnwise]'): results  # Expected [global]
}
processed = reporter.create(data)

# Warning logged but no error
reporter.report(processed)
# Log: WARNING - No CSV file will be saved...
```

## Multi-Granularity Processing Details

### Single Granularity (Backward Compatible)

```python
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create(eval_data)
reporter.report(processed)
# processed structure:
# {
#     'Reporter': {
#         'eval_expt_name': 'global',
#         'granularity': 'global',
#         'report': DataFrame
#     }
# }
```

### Multiple Granularities (New Format)

```python
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)
processed = reporter.create(eval_data)
reporter.report(processed)
# processed structure:
# {
#     'Reporter': {
#         'global': {
#             'eval_expt_name': 'global',
#             'granularity': 'global',
#             'report': DataFrame
#         },
#         'columnwise': {
#             'eval_expt_name': 'columnwise',
#             'granularity': 'columnwise',
#             'report': DataFrame
#         }
#     }
# }
```

## Notes

- **Must call create() first**: Calling `report()` directly without first calling `create()` will result in errors or invalid output
- **File overwrite**: Files with the same name will be overwritten; use with caution
- **Current directory**: Files are saved in the current working directory, not the project root
- **CSV format**: All reports are saved in CSV format
- **Encoding**: UTF-8 encoding is used by default
- **None handling**: When processed_data is None or contains warnings, no file is generated
- **Memory release**: After report generation, the passed processed_data can be garbage collected
- **Multiple file generation**: Multi-granularity or multi-experiment mode generates multiple files
- **Filename restrictions**: Filename length and special characters are subject to operating system limitations
- **Logging**: File saving is logged at INFO level
- **Naming strategy**: Filename format is determined by `naming_strategy` during initialization and cannot be modified in the report() phase

## Related Documentation

- Reporter API Home: Complete Reporter module description
- `create()` Method: Data processing method
- Reporter YAML: YAML configuration explanation