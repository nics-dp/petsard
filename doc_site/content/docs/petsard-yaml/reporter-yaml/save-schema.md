---
title: "Save Schema"
weight: 3
---

Use the `save_schema` method to export schema information from specified source modules to CSV (default) or YAML files.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-schema.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: 'default'
Synthesizer:
  default:
    method: 'default'
Postprocessor:
  default:
    method: 'default'

Reporter:
  save_schema:
    method: save_schema  # Required: Fixed to save_schema method
    source:              # Required: Specify modules to extract schema from
      - Loader
      - Preprocessor
      - Synthesizer
      - Postprocessor
    yaml_output: true    # Optional: Output individual YAML files (default: false)
    # output: petsard    # Optional: Output file name prefix (default: petsard)
```

## Main Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `method` | `string` | Fixed as `save_schema` (case-insensitive) | `save_schema` or `SAVE_SCHEMA` |
| `source` | `string` or `list` | Target module name(s) | `Loader` or `["Loader", "Preprocessor"]` |

#### source Parameter Details

The `source` parameter specifies which modules' schemas to export. Supported formats:

1. **Single Module**: Export schema from one module
   ```yaml
   source: Preprocessor
   ```

2. **Multiple Modules**: Export schemas from multiple modules
   ```yaml
   source:
     - Loader
     - Preprocessor
     - Synthesizer
   ```

**Supported Modules**:
- `Loader`: Original data schema
- `Splitter`: Split data schema
- `Preprocessor`: Preprocessed data schema
- `Synthesizer`: Synthetic data schema
- `Postprocessor`: Postprocessed data schema
- `Constrainer`: Constrained data schema

**Reference Notes**:
- **Execution Order**: Can only reference modules executed before the current Reporter
- **Module Names**: Must exactly match module names defined in the YAML configuration
- **Data Availability**: Schema extraction requires the module to have successfully executed

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `output` | `string` | `petsard` | Output file name prefix | `my_experiment` |
| `yaml_output` | `boolean` | `false` | Whether to output YAML format additionally | `true`, `false` |

## Output Format

### Default CSV Format (Summary)

Schema information is output as CSV format by default, with one row per source (experiment) and all column attributes expanded:

**Filename format:**
```
{output}_schema_{source1-source2-...}_summary.csv
```

The filename includes all source module names connected by hyphens, similar to the `save_data` method.

**Examples:**
- With `output: "petsard"` and `source: ["Loader", "Preprocessor", "Synthesizer"]`:
  ```
  petsard_schema_Loader-Preprocessor-Synthesizer_summary.csv
  ```
- With `output: "petsard"` and `source: "Loader"`:
  ```
  petsard_schema_Loader_summary.csv
  ```

**CSV Structure**:
- First column: `source` (source experiment name)
- Remaining columns: `{column_name}_{attribute_name}`, for example:
  - `age_dtype`: Data type of age column
  - `age_nullable`: Whether age column allows null values
  - `age_min`, `age_max`, `age_mean`: Statistics for age column
  - `workclass_categories`: Category values for workclass column

**Advantages**:
- Easy to compare schema differences across experiments
- Can be opened directly with Excel or other tools for analysis
- Suitable for version control and diff comparison

### Optional YAML Format

When `yaml_output: true` is set, individual YAML files for each experiment will be output additionally:

```
{output}_schema_{full_experiment_name}.yaml
```

**Example output filenames**:
- `petsard_schema_Loader[load_benchmark_with_schema].yaml`
- `petsard_schema_Loader[load_benchmark_with_schema]_Preprocessor[scaler].yaml`

**Usage**:
```yaml
Reporter:
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
    yaml_output: true  # Output YAML files additionally
```

## Use Cases

1. Data Transformation Tracking: Track how data structure changes through the processing pipeline
2. Quality Assurance: Verify that synthetic data maintains expected structure
3. Documentation Generation: Generate comprehensive data documentation for your project

## Common Questions

### Q: What's the difference between save_schema and save_data?

**A:**
- `save_schema`: Exports data structure information (column types, statistics) in CSV format by default (flattened table), optionally YAML
- `save_data`: Exports actual data content in CSV format

### Q: Can I specify a custom save path?

**A:** Yes, use the `output` parameter with a relative path. Files will be saved relative to the current working directory.

### Q: Why isn't my module's schema being saved?

**A:** Check:
1. Module name is spelled correctly in `source`
2. Module has been executed before Reporter
3. Module has data available (not empty or failed)

## Notes

- **File Overwrite**: Files with the same name will be overwritten
- **Module Execution**: Only modules that have successfully executed can have their schemas exported
- **Encoding**: All CSV and YAML files use UTF-8 encoding
- **Case Insensitivity**: The `method` parameter is case-insensitive (`save_schema`, `SAVE_SCHEMA`, or `Save_Schema` all work)
- **Performance**: Schema extraction is fast and doesn't require loading full datasets
- **Comparison**: CSV format is especially suitable for comparing data structure changes across experiments
- **Missing Values**: If a column in one source doesn't have a certain attribute (e.g., changed from numeric to categorical), that field will be left empty (NA)