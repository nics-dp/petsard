---
title: "Missing Value Handling"
weight: 1
---

Handles missing values (NA/NaN) in data.

## Background

Since most synthesis algorithms are based on probabilistic models, our research has found that most algorithms cannot directly support missing values (`None`, `np.nan`, `pd.NA`). Even if some algorithms claim to handle missing values, it's difficult to confirm whether their respective implementations are appropriate.

Therefore, **PETsARD recommends actively handling any fields containing missing values**:
- Numerical fields: Default to mean imputation
- Categorical/text/date fields: Default to direct deletion strategy

## Usage Examples

Click the button below to run the complete example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_missing-handling.ipynb)

### Example 1: Field-Specific Missing Value Methods

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  missing-field-specific:
    sequence:
      - missing
    config:
      missing:
        workclass: 'missing_drop'     # Drop rows with missing values
        education: 'missing_drop'     # Drop rows with missing values
        occupation: None              # Skip missing value handling for this field
        age: 'missing_mean'           # Fill with mean value

        # Notes:
        # - Fields set to None: Will not process missing values, keeping original NAs
        # - Unlisted fields: Will use default methods
        #   * Numerical fields (e.g., fnlwgt, capital-gain): Use missing_mean
        #   * Categorical fields: Use missing_drop

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

### Example 2: Using Custom Value Imputation

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  missing-custom-value:
    sequence:
      - missing
    config:
      missing:
        age:
          method: 'missing_simple'
          value: -1.0                 # Fill age missing values with -1.0
        hours-per-week:
          method: 'missing_simple'
          value: 0.0                  # Fill hours-per-week missing values with 0.0

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

## Available Processors

| Processor | Description | Applicable Data Type | Parameters |
|-----------|-------------|---------------------|------------|
| `missing_mean` | Fill with mean value | Numerical | None |
| `missing_median` | Fill with median value | Numerical | None |
| `missing_mode` | Fill with mode value | Categorical, Numerical | None |
| `missing_simple` | Fill with specified value | Numerical | `value` (default: 0.0) |
| `missing_drop` | Drop rows with missing values | All types | None |

## Parameter Description

### missing_simple

- **value** (`float`, optional)
  - Custom value used to fill missing values
  - Default value: `0.0`
  - Example: `value: -1.0`

## Processing Logic

### 1. Statistical Value Imputation (Mean/Median/Mode)

```
Training phase (fit):
  Calculate and store statistical values (mean/median/mode)

Transform phase (transform):
  Fill NA with stored statistical values

Inverse transform phase (inverse_transform):
  Randomly insert NA according to the missing ratio of original data
```

### 2. Custom Value Imputation (Simple)

```
Training phase (fit):
  Record the fill value

Transform phase (transform):
  Fill NA with specified value

Inverse transform phase (inverse_transform):
  Randomly insert NA according to the missing ratio of original data
```

### 3. Deletion (Drop)

```
Training phase (fit):
  No training needed

Transform phase (transform):
  Delete rows containing NA

Inverse transform phase (inverse_transform):
  Randomly insert NA according to the missing ratio of original data
```

## Default Behavior

Default missing value handling for different data types:

| Data Type | Default Processor | Description |
|-----------|------------------|-------------|
| Numerical | `missing_mean` | Fill with mean value |
| Categorical | `missing_drop` | Drop rows with missing values |
| Datetime | `missing_drop` | Drop rows with missing values |

## Schema Changes

The `nullable` attribute in schema reflects the actual presence of missing values:

### Loader Stage
- Automatically detected from data: `nullable = data.isnull().any()`
- If column has missing values → `nullable: true`
- If column has no missing values → `nullable: false`

### Preprocessor Stage (with missing value processing)
- Columns with `nullable: true` → After processing → `nullable: false`
- Columns with `nullable: false` → Remains `nullable: false`

**Example Schema Evolution**:

```yaml
# Loader Output (data has missing values)
workclass:
  type: string
  nullable: true          # Has missing values in original data

age:
  type: int64
  nullable: false         # No missing values in original data

# Preprocessor Output (after missing_drop)
workclass:
  type: string
  nullable: false         # Missing values removed

age:
  type: int64
  nullable: false         # Unchanged (no missing values originally)
```

## Notes

- **Processing Order**: Missing value handling is usually the first step
- **Mode Imputation**: If there are multiple modes, one will be randomly selected
- **Deletion Impact**: Using `missing_drop` may significantly reduce data volume
- **Restoration Mechanism**: During post-processing, NA will be randomly inserted according to the original ratio, but positions won't be exactly the same
- **Statistical Value Storage**: Statistical values calculated during training are used for all subsequent transformations
- **NA Recognition**: Automatically recognizes pandas NA values (`np.nan`, `None`, `pd.NA`)
- **Schema Alignment**: Each stage (Loader, Preprocessor, Synthesizer, Postprocessor, Constrainer) will align data according to its output schema
