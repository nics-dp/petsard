---
title: "Reporter API"
type: docs
weight: 1130
---

Report generation module that supports multiple report formats for output and file storage.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/reporter-api/reporter-class-diagram.mmd" >}}

> **Legend:**
> - Blue box: Factory class
> - Light purple box: Abstract base class
> - Orange box: Subclass implementations
> - Light purple box (others): Configuration and enumeration classes
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

```python
from petsard import Reporter

# Save synthetic data
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report(processed)

# Generate evaluation report
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report(processed)

# Save timing information
reporter = Reporter(method='save_timing', time_unit='minutes')
processed = reporter.create({'timing_data': timing_df})
reporter.report(processed)
```

## Constructor (__new__)

Initialize a reporter instance. Reporter uses the factory pattern (via `__new__` method) to automatically create and return the appropriate reporter instance based on the specified method parameter.

### Syntax

```python
Reporter(**kwargs)
```

### Parameters

- **method** : str, required
    - Report generation method
    - Required parameter
    - Supported methods:
        - `'save_data'`: Save datasets as CSV
        - `'save_report'`: Generate evaluation reports
        - `'save_timing'`: Save timing information
        - `'save_validation'`: Save validation results

- **output** : str, optional
    - Output filename prefix
    - Default: `'petsard'`

- **naming_strategy** : str, optional
    - File naming strategy
    - Options:
        - `'traditional'`: Use traditional naming format (default)
        - `'compact'`: Use compact naming format

#### save_data Method Parameters

- **source** : str | List[str], required for save_data
    - Target module or experiment name
    - Specifies the source module for data to be saved
    - Can be a single string or list of strings

#### save_report Method Parameters

- **granularity** : str | List[str], required for save_report
    - Report granularity level
    - Single granularity: `'global'`, `'columnwise'`, `'pairwise'`, `'details'`, `'tree'`
    - Multiple granularities: `['global', 'columnwise']` or `['details', 'tree']`

- **eval** : str | List[str], optional
    - Target evaluation experiment name
    - Used to filter results for specific evaluation experiments
    - Can be a single string or list of strings

#### save_timing Method Parameters

- **time_unit** : str, optional
    - Time unit
    - Options: `'seconds'`, `'minutes'`, `'hours'`, `'days'`
    - Default: `'seconds'`

- **module** : str | List[str], optional
    - Filter timing information by specific module
    - Can be a single string or list of strings

### Returns

- **BaseReporter**
    - Returns the appropriate reporter instance based on the method parameter
    - Actual classes:
        - `ReporterSaveData`: Data saving mode
        - `ReporterSaveReport`: Evaluation report mode
        - `ReporterSaveTiming`: Timing information mode
        - `ReporterSaveValidation`: Validation result mode

### Examples

```python
from petsard import Reporter

# Save synthetic data
reporter = Reporter(method='save_data', source='Synthesizer')

# Generate evaluation report (single granularity)
reporter = Reporter(method='save_report', granularity='global')

# Generate evaluation report (multiple granularities)
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)

# Use compact naming strategy
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact'
)

# Save timing information (specify time unit)
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)

# Custom output filename prefix
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    output='my_experiment'
)
```

## Functional Design Pattern

Reporter adopts a functional "throw and catch" design pattern with the following characteristics:

- **Stateless Design**: `create()` processes data but does not store it in instance variables
- **Pure Function Operations**: `report()` receives processed data and generates output files
- **Memory Efficiency**: Does not maintain internal state, reducing memory usage
- **Flexible Flow**: Allows flexible data processing workflows

### Workflow

```python
# Step 1: Initialize reporter
reporter = Reporter(method='save_report', granularity='global')

# Step 2: Process data (create returns processed data)
processed_data = reporter.create({
    ('Evaluator', 'eval1_[global]'): results
})

# Step 3: Generate report (report receives processed data)
reporter.report(processed_data)
```

## Granularity Types

Reporter supports multiple report granularities for different levels of evaluation analysis:

### Traditional Granularities
- **global**: Overall summary statistics
- **columnwise**: Column-by-column analysis
- **pairwise**: Pairwise relationships between columns

### Extended Granularities
- **details**: Detailed breakdown with additional metrics
- **tree**: Hierarchical tree structure analysis

### Multi-Granularity Support

Reporter supports processing multiple granularities in a single operation:

```python
# Process multiple granularities simultaneously
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)
result = reporter.create(evaluation_data)
reporter.report(result)  # Generates separate reports for each granularity
```

When using multiple granularities:
- Each granularity produces a separate report file
- Report filenames include granularity information
- Results for all granularities can be collected at once

## Naming Strategies

Reporter supports two file naming strategies:

### Traditional Strategy (Default)

Uses the original naming format for backward compatibility:
- Includes complete module and experiment information
- Uses square brackets to mark special information
- Suitable for scenarios requiring detailed filename information

**Examples:**
- `petsard_Synthesizer[exp1].csv`
- `petsard_Reporter[eval1_global].csv`
- `petsard_timing_report.csv`

### Compact Strategy

Uses a simplified naming format:
- Uses module abbreviations (e.g., Sy = Synthesizer, Ev = Evaluator)
- Uses dots to separate parts
- Generates more concise and readable filenames

**Examples:**
- `petsard_Sy.exp1.csv`
- `petsard.report.Ev.eval1.G.csv` (G = Global)
- `petsard_timing_report.csv`

**Naming Strategy Examples:**

```python
# Traditional strategy example
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='traditional'
)
# Output: petsard_Reporter[eval1_global].csv

# Compact strategy example
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact'
)
# Output: petsard.report.Ev.eval1.G.csv
```

## Example Scenarios

### Save Synthetic Data

```python
from petsard import Reporter

# Save synthetic data
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report(processed)
# Generates: petsard_Synthesizer[exp1].csv
```

### Generate Evaluation Report (Single Granularity)

```python
from petsard import Reporter

# Generate global evaluation report
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create({('Evaluator', 'eval1_[global]'): global_results})
reporter.report(processed)
# Generates: petsard_Reporter[eval1_global].csv
```

### Generate Evaluation Report (Multiple Granularities)

```python
from petsard import Reporter

# Generate multi-granularity evaluation report
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)
processed = reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
})
reporter.report(processed)
# Generates:
# - petsard_Reporter[eval1_global].csv
# - petsard_Reporter[eval1_columnwise].csv
# - petsard_Reporter[eval1_details].csv
```

### Save Timing Information

```python
from petsard import Reporter

# Save timing information for specific modules
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)
processed = reporter.create({'timing_data': timing_df})
reporter.report(processed)
# Generates: petsard_timing_report.csv
```

### Use Compact Naming Strategy

```python
from petsard import Reporter

# Use compact naming
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact',
    output='results'
)
processed = reporter.create({('Synthesizer', 'exp1'): df})
reporter.report(processed)
# Generates: results_Sy.exp1.csv (more concise filename)
```

## Version Compatibility

### Features Planned for Removal in v2.0

The following features are marked as deprecated and will be removed in version 2.0:

- **ReporterMap Class**: Use `ReporterMethod` enum instead
- **ReporterSaveReportMap Class**: Use `ReportGranularity` enum instead
- **Tuple-based Experiment Naming System**: Will be replaced by `ExperimentConfig` system

Users are advised to start migrating to the new API to ensure future compatibility.

## Notes

- **Factory Pattern**: Reporter uses the `__new__` method to implement the factory pattern, automatically creating the appropriate reporter class
- **Recommendation**: Use YAML configuration file rather than direct Python API
- **Method Call Order**: Must call `create()` before calling `report()`
- **Data Processing**: Data returned by `create()` must be passed to the `report()` method
- **File Output**: Report files are saved in the current working directory
- **File Overwrite**: Files with the same name will be overwritten; use with caution
- **Documentation Note**: This documentation is for internal development team reference only, backward compatibility is not guaranteed
- **Memory Efficiency**: Functional design ensures large amounts of data are not retained in instances
- **Multi-Granularity Processing**: When using multiple granularities, each granularity produces a separate report file
- **Naming Strategy Selection**: Choose the appropriate naming strategy based on project needs; traditional maintains backward compatibility, compact is more concise