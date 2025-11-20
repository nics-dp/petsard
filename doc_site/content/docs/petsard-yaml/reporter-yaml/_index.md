---
title: "Reporter YAML"
type: docs
weight: 700
prev: docs/petsard-yaml/evaluator-yaml
next: docs/petsard-yaml
---

The Reporter module is responsible for outputting experiment results and supports multiple report formats including data storage, evaluation reports, and timing records.

## Usage Examples

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter.ipynb)
> **Note**: If using Colab, please see the [runtime setup guide](/petsard/docs/#colab-execution-guide).

```yaml
Loader:
  load_data:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  synthesize:
    method: default
Evaluator:
  fidelity_check:
    method: sdmetrics-qualityreport

Reporter:
  save_synthetic:
    method: save_data
    source: Synthesizer

  save_report:
    method: save_report
    granularity: global

  save_schema:
    method: save_schema
    source:
      - Loader
      - Synthesizer

  save_timing:
    method: save_timing
```

## Supported Report Methods

This module supports the following report output methods. For detailed parameters, please refer to each subpage:

1. **Save Data** - Save synthetic data or outputs from other modules as CSV files
2. **Generate Evaluation Reports** - Generate evaluation result reports with multiple granularity levels
3. **Save Schema Information** - Output data column schema information from specified modules
4. **Save Validation Results** - Export Constrainer validation results as structured CSV reports
5. **Save Timing Information** - Record execution time of each module

## Naming Strategy and Experiment Names

PETsARD adopts a unified experiment naming convention for identifying and tracking experiment processes.

### Naming Strategy Overview

The Reporter module supports two naming strategies, controlled via the `naming_strategy` parameter:

1. **TRADITIONAL**: Maintains backward compatibility with traditional naming format
2. **COMPACT**: Provides a more concise and readable naming format

### Experiment Name Format

#### Experiment Tuple

`full_expt_tuple` is a tuple composed of module name and experiment name:
```python
(module_name, experiment_name)
```

This format is primarily used by the Reporter system to identify and organize experiment results.

#### Experiment String

`full_expt_name` concatenates the module name and experiment name with a hyphen:
```
{module_name}-{experiment_name}
```

### File Naming Format

#### save_data Method

| Strategy | Format | Example |
|----------|--------|---------|
| Traditional | `{output}_{module}[{experiment}].csv` | `petsard_Synthesizer[exp1].csv` |
| Compact | `{output}_{module}_{experiment}.csv` | `petsard_Synthesizer_exp1.csv` |

#### save_report Method

| Strategy | Format | Example |
|----------|--------|---------|
| Traditional | `{output}_Reporter[{eval}_[{granularity}]].csv` | `petsard_Reporter[eval1_[global]].csv` |
| Compact | `{output}_{eval}_{granularity}.csv` | `petsard_eval1_global.csv` |

#### save_timing Method

All strategies use the same format:
```
{output}_timing_report.csv
```

### Module Abbreviation Table (Compact Strategy)

| Module Name | Abbr. | Example Filename |
|-------------|-------|------------------|
| Loader | Ld | `petsard_Ld.load_adult.csv` |
| Splitter | Sp | `petsard_Sp.train_test.csv` |
| Processor | Pr | `petsard_Pr.normalize.csv` |
| Synthesizer | Sy | `petsard_Sy.ctgan_baseline.csv` |
| Constrainer | Cn | `petsard_Cn.privacy_check.csv` |
| Evaluator | Ev | `petsard_Ev.utility_eval.csv` |
| Reporter | Rp | `petsard_Rp.summary.csv` |

### Granularity Abbreviation Table (Compact Strategy)

| Granularity Name | Abbr. | Example Filename |
|------------------|-------|------------------|
| global | G | `petsard_eval_privacy.G.csv` |
| columnwise | C | `petsard_eval_column.C.csv` |
| pairwise | P | `petsard_eval_correlation.P.csv` |
| details | D | `petsard_eval_detailed.D.csv` |
| tree | T | `petsard_eval_hierarchical.T.csv` |

### Naming Recommendations

1. **Module Names**
   - Use standard module names: 'Synthesizer', 'Evaluator', 'Processor', etc.
   - Case sensitivity must match exactly

2. **Experiment Names**
   - Use meaningful prefixes: 'exp', 'eval', 'test', etc.
   - Separate different parts with underscores: method name, parameter settings, etc.
   - Use square brackets for evaluation levels: [global], [columnwise], [pairwise]

3. **Parameter Encoding**
   - Use abbreviations for parameter names: method, batch, epoch, etc.
   - Use concise representations for values: 300, 0.1, etc.
   - Connect multiple parameters with underscores: method_a_batch500

4. **Strategy Selection**
   - **New Projects**: Recommended to use `compact` strategy for more concise filenames
   - **Existing Projects**: Use `traditional` strategy to maintain compatibility
   - **File Management**: `compact` strategy makes filenames easier to sort and categorize

## Common Parameters

All report methods support the following common parameters:

- **output** (`string`, optional) - Output file name prefix, defaults to `petsard`
- **naming_strategy** (`string`, optional) - Filename naming strategy, choose `traditional` (default) or `compact`

## Notes

- Reporter should be executed after all modules requiring reports have completed
- Files with the same name will be overwritten; use different `output` prefixes
- All reports are saved in CSV format with UTF-8 encoding
- Recommended to use `compact` naming strategy for new projects; use `traditional` for existing projects to ensure compatibility