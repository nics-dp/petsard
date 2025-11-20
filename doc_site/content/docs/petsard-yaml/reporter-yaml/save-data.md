---
title: "Save Data"
type: docs
weight: 701
prev: docs/petsard-yaml/reporter-yaml
next: docs/petsard-yaml/reporter-yaml/save-report
---

Use the `save_data` method to save synthetic data or outputs from other modules as CSV files.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-data.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: default

Synthesizer:
  default:
    method: default

  petsard-gaussian-copula:
    method: petsard-gaussian-copula

Postprocessor:
  default:
    method: default
Reporter:
  save_all_step:
    method: save_data  # Required: Fixed to save_data method
    source:            # Required: Specify data sources to save
      - Splitter.ori              # Save splitter's original data
      - Splitter.control          # Save splitter's control group data
      - Preprocessor              # Save preprocessed data
      - Synthesizer.default       # Save default synthesizer results
      - Synthesizer.petsard-gaussian-copula  # Save petsard-gaussian-copula synthesizer results
      - Postprocessor            # Save postprocessed data
    # output: petsard  # Optional: Output file name prefix (default: petsard)
    # naming_strategy: traditional  # Optional: Filename naming strategy, can be traditional or compact (default: traditional)
```

## Main Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `method` | `string` | Fixed as `save_data` | `save_data` |
| `source` | `string` or `list` | Target module or experiment name | `Synthesizer` or `["Synthesizer", "Loader"]` |

#### source Parameter Details

The `source` parameter specifies which data sources to save. Supported formats:

1. **Single Module**: Save all outputs from a module
   ```yaml
   source: Synthesizer
   ```

2. **Specific Experiment**: Save output from a specific experiment
   ```yaml
   source: Synthesizer.petsard-gaussian-copula
   ```

3. **Multiple Sources**: Save outputs from multiple modules or experiments
   ```yaml
   source:
     - Splitter.ori
     - Preprocessor
     - Synthesizer.default
   ```

**Reference Notes**:

- **Splitter Special Outputs**: Can specify `.ori` (original complete data), `.control` (control group data), `.train` (training set), `.test` (test set) subsets
- **Experiment Name Matching**: When referencing experiments, names must exactly match those defined in the YAML
- **Dependencies**: Can only reference modules executed before the current Reporter

**Important Note**: When referencing `Postprocessor`, it automatically includes postprocessed results from all upstream synthesizers. For example, in the above example with two synthesizers (`default` and `petsard-gaussian-copula`), referencing `Postprocessor` will automatically save postprocessed results from both synthesizers.

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `output` | `string` | `petsard` | Output file name prefix | `my_experiment` |
| `naming_strategy` | `string` | `traditional` | Filename naming strategy, see main page for details | `compact` |

## Output Format

All data will be saved in CSV format, following the naming strategy described on the main page.

**CSV File Content:**
- All columns from original data
- Maintains data types and structure
- Uses UTF-8 encoding
- Includes header row

## Common Questions

### Q: How to avoid file overwrites?

**A:** Use different `output` prefixes or experiment names

### Q: Can I specify a save path?

**A:** There are two ways:

1. **Use output parameter with relative path**: Files will be saved to the specified path under the current working directory

2. **Use different experiment names**: Define meaningful experiment names in YAML, which will be automatically reflected in the output filenames

## Notes

- **File Overwrite**: Files with the same name will be overwritten; use different `output` prefixes
- **Memory Limitations**: Large datasets may require more memory
- **Encoding Format**: All files use UTF-8 encoding
- **Data Integrity**: All columns and data types are preserved during save
- **Experiment Tracking**: Use meaningful experiment names and output prefixes
- **Naming Strategy**: See main page for detailed filename format descriptions

