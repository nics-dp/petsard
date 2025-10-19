---
title: "Save Validation Results"
weight: 4
---

Use the `save_validation` method to export Constrainer validation results as CSV files, including summary statistics, violation statistics, and detailed violation records.

## Usage Example

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-validation.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Constrainer:
  external_constraints:
    method: auto
    constraints_yaml: adult-income_constraints.yaml
Reporter:
  save_validation:
    method: save_validation     # Required: Fixed to save_validation method
    # output: petsard           # Optional: Output file name prefix (default: petsard)
    # include_details: true     # Optional: Include detailed violation records (default: true)
```

## Main Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `method` | `string` | Fixed as `save_validation` (case-insensitive) | `save_validation` or `SAVE_VALIDATION` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `output` | `string` | `petsard` | Output file name prefix | `my_validation` |
| `include_details` | `boolean` | `true` | Include detailed violation records | `true`, `false` |

#### include_details Parameter Details

The `include_details` parameter controls whether to output detailed violation record files:

1. **Enable detailed records** (`true`):
   ```yaml
   include_details: true
   ```
   - Generates an additional `*_details.csv` file
   - Contains specific data rows for each violation
   - Shows up to 10 violation examples per rule
   - Includes columns: Constraint Type, Rule, Violation Index, and actual data fields

2. **Disable detailed records** (`false`):
   ```yaml
   include_details: false
   ```
   - Only generates summary and statistics files
   - Saves storage space
   - Suitable for scenarios requiring only statistical data

## Output Format

This Reporter generates up to 3 CSV files for each Constrainer validation result:

### 1. Summary File

**Filename format:**
```
{output}[Validation]_Constrainer[experiment_name]_summary.csv
```

**Example filenames:**
- Single source: `petsard_[Validation]_Constrainer[validate_constraints]_summary.csv`
- Multiple sources: `petsard_[Validation]_Source[synthetic_data]_Constrainer[validate_constraints]_summary.csv`

**File content:**
| Metric | Value |
|--------|-------|
| total_rows | Total number of data rows |
| passed_rows | Number of rows that passed validation |
| failed_rows | Number of rows that failed validation |
| pass_rate | Pass rate (floating point between 0-1) |
| is_fully_compliant | Whether fully compliant (True/False) |

### 2. Violations Statistics File

**Filename format:**
```
{output}[Validation]_Constrainer[experiment_name]_violations.csv
```

**File content:**
| Constraint Type | Rule | Failed Count | Fail Rate | Violation Examples | Error Message |
|----------------|------|--------------|-----------|-------------------|---------------|
| Constraint type | Rule name | Number of violations | Violation rate | Violation example indices | Error message |

**Example:**
| Constraint Type | Rule | Failed Count | Fail Rate | Violation Examples | Error Message |
|----------------|------|--------------|-----------|-------------------|---------------|
| range | age_range_check | 15 | 0.015000 | 42, 87, 123, 256, 489 | - |
| categories | workclass_valid_categories | 8 | 0.008000 | 12, 34, 56, 78 | - |

### 3. Detailed Violation Records File

**Filename format:**
```
{output}[Validation]_Constrainer[experiment_name]_details.csv
```

**Description:**
- Generated only when `include_details: true`
- Shows up to 10 violation examples per rule
- Contains complete violation data row content

**File content:**
| Constraint Type | Rule | Violation Index | [Original data columns...] |
|----------------|------|-----------------|---------------------------|
| Constraint type | Rule name | Violation index | Actual field values |

**Example:**
| Constraint Type | Rule | Violation Index | age | workclass | education | ... |
|----------------|------|-----------------|-----|-----------|-----------|-----|
| range | age_range_check | 1 | 15 | Private | HS-grad | ... |
| range | age_range_check | 2 | 95 | Self-emp | Masters | ... |
| categories | workclass_valid_categories | 1 | 45 | Unknown | Bachelors | ... |

## Filename Naming Rules

### Using default output (`petsard`)

The system automatically generates complete filenames based on experiment type:

1. **Single source Constrainer**:
   ```
   petsard_[Validation]_Constrainer[experiment_name]_[type].csv
   ```
   Example: `petsard_[Validation]_Constrainer[validate_constraints]_summary.csv`

2. **Multiple source Constrainer** (with specified source):
   ```
   petsard_[Validation]_Source[source_name]_Constrainer[experiment_name]_[type].csv
   ```
   Example: `petsard_[Validation]_Source[synthetic_data]_Constrainer[validate_constraints]_summary.csv`

### Using custom output

Directly uses the specified name:
```yaml
Reporter:
  save_validation:
    method: save_validation
    output: my_validation_report
```

Output files:
- `my_validation_report_summary.csv`
- `my_validation_report_violations.csv`
- `my_validation_report_details.csv` (if include_details is true)

## Use Cases

1. **Validation Report Generation**: Export data validation results as formal reports
2. **Quality Monitoring**: Continuously track data quality metrics
3. **Problem Diagnosis**: Identify data issues through detailed violation records
4. **Compliance Documentation**: Provide data compliance proof documents

## Common Questions

### Q: What's the difference between save_validation and save_report?

**A:**
- `save_validation`: Specifically exports Constrainer validation results, generating structured CSV reports (summary, statistics, detailed records)
- `save_report`: Exports utility metric evaluation results, supporting multiple formats (CSV, Markdown, HTML)

### Q: Why aren't my validation results being saved?

**A:** Check:
1. Have you executed Constrainer's `validate` method before Reporter
2. Did Constrainer successfully generate validation results
3. Is the validation result data structure correct

### Q: Will too many detailed violation records affect performance?

**A:** 
- The system automatically limits to 10 violation examples per rule
- If detailed records aren't needed, set `include_details: false` to save space
- Summary and statistics files are always generated, unaffected by this setting

### Q: Can I adjust the number of violation examples per rule?

**A:** Currently the system is fixed at 10 examples per rule. For more records, consider:
1. Using `save_data` to export complete validation result data
2. Or combining with Constrainer's `return_details=True` option to process manually

## Notes

- **File Overwrite**: Files with the same name will be overwritten, please backup as needed
- **Data Volume Control**: Detailed violation records are automatically limited to 10 examples per rule
- **Encoding**: All CSV files use UTF-8 encoding
- **Case Insensitivity**: The `method` parameter is case-insensitive (`save_validation`, `SAVE_VALIDATION`, or `Save_Validation` all work)
- **Execution Order**: Must be executed after Constrainer's validate method
- **Empty Value Handling**: If a validation result is empty or invalid, that result will be skipped with a warning logged