---
title: "Outlier Handling"
weight: 2
---

Identifies and handles outliers in data.

## Usage Examples

Click the button below to run the complete example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_outlier-handling.ipynb)

### Example 1: Field-Specific Outlier Methods

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  outlier-field-specific:
    sequence:
      - outlier
    config:
      outlier:
        age: 'outlier_zscore'       # Uses Z-Score method for age field
        fnlwgt: 'outlier_iqr'       # Uses IQR method for fnlwgt field
        education-num: None         # Skip outlier handling for this field

        # Note:
        # - Fields set to None: No outlier handling will be applied
        # - Fields not listed (e.g., capital-gain, capital-loss, hours-per-week):
        #   Will use the default method (outlier_iqr)

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

### Example 2: Global Outlier Method

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: 'benchmark://adult-income'
    schema: 'benchmark://adult-income_schema'

Preprocessor:
  outlier-global-simple:
    sequence:
      - outlier
    config:
      # Simplified syntax: apply one global method to ALL numerical fields
      outlier: 'outlier_isolationforest'

      # Available global methods:
      # - 'outlier_isolationforest': Isolation Forest algorithm
      # - 'outlier_lof': Local Outlier Factor algorithm

      # This is equivalent to:
      # outlier:
      #   age: 'outlier_isolationforest'
      #   fnlwgt: 'outlier_isolationforest'
      #   education-num: 'outlier_isolationforest'
      #   capital-gain: 'outlier_isolationforest'
      #   capital-loss: 'outlier_isolationforest'
      #   hours-per-week: 'outlier_isolationforest'

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

| Processor | Description | Applicable Type | Global Processing |
|-----------|-------------|-----------------|-------------------|
| `outlier_zscore` | Z-Score method (\|z\| > 3) | Numerical | ❌ |
| `outlier_iqr` | Interquartile range method (1.5 IQR) | Numerical | ❌ |
| `outlier_isolationforest` | Isolation Forest algorithm | Numerical | ✅ |
| `outlier_lof` | Local Outlier Factor algorithm | Numerical | ✅ |

## Processor Details

### outlier_zscore

Uses Z-Score statistical method to identify outliers.

**Criteria**:
- \|Z-Score\| > 3 is considered an outlier
- Z-Score = (x - μ) / σ

### outlier_iqr

Uses Interquartile Range (IQR) method to identify outliers.

**Criteria**:
- Below Q1 - 1.5 × IQR
- Above Q3 + 1.5 × IQR
- IQR = Q3 - Q1

### outlier_isolationforest

Uses sklearn's Isolation Forest algorithm.

**Features**:
- Global transformation (applies to all numerical fields)
- Suitable for multi-dimensional outlier detection
- Automatically learns outlier patterns

### outlier_lof

Uses Local Outlier Factor (LOF) algorithm.

**Features**:
- Global transformation (applies to all numerical fields)
- Density-based outlier detection
- Considers local data distribution

## Processing Logic

### General Outlier Handling (Z-Score, IQR)

- **Training phase (fit)**: Calculate statistical parameters (mean, standard deviation, quartiles)
- **Transform phase (transform)**:
  1. Identify outliers
  2. Remove rows containing outliers
- **Inverse transform phase (inverse_transform)**: ⚠️ Cannot be restored (outlier handling is irreversible)

### Global Outlier Handling (Isolation Forest, LOF)

- **Training phase (fit)**: Train model using all numerical fields
- **Transform phase (transform)**:
  1. Predict outliers using the model
  2. Remove rows marked as outliers
- **Inverse transform phase (inverse_transform)**: ⚠️ Cannot be restored (outlier handling is irreversible)

## Default Behavior

Default outlier handling for different data types:

| Data Type | Default Processor | Description |
|-----------|------------------|-------------|
| Numerical | `outlier_iqr` | Uses interquartile range method |
| Categorical | None | No outlier handling |
| Datetime | `outlier_iqr` | Uses interquartile range method |

The system will automatically:
1. Detect the global processor
2. Replace all numerical field processors with the global processor
3. Log warning messages

## Notes

- **Irreversibility**: Outlier handling cannot be restored during post-processing
- **Data Reduction**: Outlier handling removes some data rows
- **Global Override**: When using global processors, all numerical field settings will be overridden
- **Processing Order**: Recommended to execute after missing value handling and before encoding
- **Categorical Data**: Outlier handling is not applicable to categorical data
- **Impact Assessment**: Removing too many outliers may affect data distribution and model effectiveness
- **Synthetic Data**: The range of synthetic data during post-processing may differ slightly from original data

## Method Selection Recommendations

| Situation | Recommended Method | Reason |
|-----------|-------------------|--------|
| Single field anomaly | `outlier_zscore` or `outlier_iqr` | Simple, effective, easy to explain |
| Multi-dimensional outliers | `outlier_isolationforest` | Considers inter-field correlations |
| Density-based detection | `outlier_lof` | Suitable for non-uniform distribution data |
| When uncertain | `outlier_iqr` | Robust and widely applicable |