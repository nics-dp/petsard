---
title: "Save Evaluation Reports"
type: docs
weight: 702
prev: docs/petsard-yaml/reporter-yaml/save-data
next: docs/petsard-yaml/reporter-yaml/save-validation
---

Use the `save_report` method to generate evaluation result reports with multiple granularity levels.

## Usage Example

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-data.ipynb)
> **Note**: If using Colab, please see the [runtime setup guide](/petsard/docs/#colab-execution-guide).

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Evaluator:
  validity_check:
    method: sdmetrics-diagnosticreport
  fidelity_check:
    method: sdmetrics-qualityreport
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    n_cols: 3
    max_attempts: 4000
  classification_utility:
    method: mlutility
    task_type: classification
    target: income
    random_state: 42
Reporter:
  save_report:
    method: save_report         # Required: Fixed as save_report
    granularity:                # Required: Specify report granularity levels
      - global                  # Overall summary statistics
      - columnwise              # Per-column analysis
      - details                 # Detailed breakdown
    # eval:                     # Optional: Target evaluation experiment names (default: all evaluations)
    # output: petsard           # Optional: Output filename prefix (default: petsard)
    # naming_strategy: traditional  # Optional: Filename naming strategy, traditional or compact (default: traditional)
```

## Parameter Description

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `method` | `string` | Fixed as `save_report` | `save_report` |
| `granularity` | `string` or `list` | Report detail level | `global` or `["global", "columnwise"]` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `eval` | `string` or `list` | All | Target evaluation experiment names | `eval1` or `["eval1", "eval2"]` |
| `output` | `string` | `petsard` | Output file name prefix | `evaluation_results` |
| `naming_strategy` | `string` | `traditional` | Filename naming strategy | `compact` |

## Granularity Types

Different evaluation methods support different granularity levels:

- **global (Overall Summary Statistics)**: Provides dataset-level overall evaluation metrics
- **details (Detailed Breakdown)**: Provides complete evaluation details and additional metrics
- **columnwise (Per-Column Analysis)**: Provides detailed evaluation metrics for each column
- **pairwise (Column Pairwise Relationships)**: Analyzes correlations and associations between columns
- **tree (Hierarchical Tree Structure)**: Presents evaluation results in hierarchical relationships

### Supported Evaluators

| Evaluator | global | details | columnwise | pairwise | tree |
|-----------|--------|---------|------------|----------|------|
| mlutility | ✓ | ✓ | - | - | - |
| anonymeter | ✓ | ✓ | - | - | - |
| sdmetrics | ✓ | - | ✓ | ✓ | - |
| mpuccs | ✓ | ✓ | - | - | ✓ |
| describer | ✓ | - | ✓ | ✓ | - |

## Output Format

All reports will be saved in CSV format, following the naming strategy described on the main page.

### CSV File Content

Report file column structures vary by granularity:

**Global Granularity:**
- `metric_name`: Metric name
- `value`: Metric value
- `category`: Metric category

**Columnwise Granularity:**
- `column`: Column name
- `metric_name`: Metric name
- `value`: Metric value

**Pairwise Granularity:**
- `column_1`: First column
- `column_2`: Second column
- `metric_name`: Metric name
- `value`: Metric value

## Common Questions

### Q: How to choose the appropriate granularity?

**A:** Choose based on analysis needs:
- **Quick Overview**: Use `global`
- **Column-level Analysis**: Use `columnwise`
- **Correlation Analysis**: Use `pairwise`

### Q: Can I generate all granularities at once?

**A:** Yes, list all required granularities in the `granularity` parameter:

### Q: How to filter specific evaluation experiments?

**A:** Use the `eval` parameter to specify:

```yaml
Reporter:
  save_specific:
    method: save_report
    granularity: global
    eval: my_evaluation  # Only process this evaluation
```

### Q: What if report files are too large?

**A:** Consider:
1. Select only needed granularities
2. Use `eval` parameter to filter
3. Generate reports in batches
4. Use compression tools for output files

## Notes

- **Granularity Matching**: Granularity markers in data must match configuration
- **Memory Usage**: `details` and `tree` granularities may produce larger files
- **Evaluation Order**: Must execute Evaluator before generating reports
- **Naming Conflicts**: Use different `output` prefixes to avoid file overwrites
- **Data Integrity**: Ensure evaluation results contain required granularity information
- **Naming Strategy**: See main page for detailed filename format descriptions