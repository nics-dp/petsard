---
title: Data Describing
type: docs
weight: 1
prev: docs/data-preparation
next: docs/data-preparation/multi-table-relationships
---

Applicable to **all data preparation workflows as the starting point**.

Use the Describer module to generate statistical description reports for datasets, helping you examine basic statistical information, identify data quality issues, understand data distribution characteristics, and assess whether data is suitable for synthesis.

> Describer is the first step of data preparation. It is strongly recommended to execute this before any data integration or constraint definition.

## Generate Statistical Reports Using Describer

### Basic Usage

```yaml
Loader:
  data:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Describer:
  profile_data:
    method: describe  # or use default (will auto-determine as describe)
    source: Loader
```

### Parameter Description

- **`method`**: Evaluation method
  - `describe`: Single dataset statistical description
  - `compare`: Dataset comparison analysis (requires two data sources)
  - `default`: Automatically determines based on source count (recommended)
  - Default: `default`

- **`source`**: Data source module
  - Single source (describe mode): Directly specify module name, such as `Loader`
  - Two sources (compare mode): Use dictionary format to specify `base` and `target`
  - Available values: `Loader`, `Splitter`, `Preprocessor`, `Synthesizer`, `Postprocessor`, `Constrainer`

## Generated Statistical Reports

Describer generates statistical reports at three levels:

### 1. Global Level

Overall dataset statistics:
- Number of records (total records)
- Number of columns
- Memory usage
- Data type distribution (numeric, categorical, datetime)

### 2. Columnwise Level

**Numeric Column Statistics**:
- Mean
- Standard deviation (std)
- Median
- Minimum (min)
- Maximum (max)
- Quartiles (Q1, Q3)
- Missing value ratio

**Categorical Column Statistics**:
- Number of unique values (nunique)
- Most frequent value
- Frequency
- Missing value ratio

**Datetime Column Statistics**:
- Time range (earliest, latest date)
- Time interval distribution

### 3. Pairwise Level

Correlation analysis between columns:
- Correlation coefficient matrix between numeric columns
- Identification of highly correlated column pairs
- Association strength between categorical columns

## Data Quality Check

Use Describer reports for data quality assessment:

**Missing Value Check**
- Observe missing value ratio for each column
- High missing value ratio (>30%) may affect synthesis quality
- Consider using nan_groups constraints to define handling rules

**Outlier Check**
- Review minimum and maximum values of numeric columns
- Observe relationship between standard deviation and quartiles
- Extreme values may need handling in preprocessing stage

**Category Distribution Check**
- Check number of unique values in categorical columns
- Evaluate category balance (whether there are dominant categories)
- Minority categories (<1%) may disappear after synthesis

**Data Correlation Check**
- Identify highly correlated columns (correlation coefficient >0.9)
- Consider whether dimensionality reduction or feature selection is needed
- Understand dependencies between columns

## Compare Original Data with Synthetic Data

When you need to compare two datasets (e.g., original data vs. synthetic data):

```yaml
Loader:
  original:
    filepath: 'original_data.csv'
    schema: 'data_schema.yaml'

Synthesizer:
  synthetic:
    method: custom_data
    filepath: 'synthetic_data.csv'
    schema: 'data_schema.yaml'

Describer:
  compare_data:
    method: compare  # or use default (will auto-determine as compare)
    source:
      base: Loader      # Base data (original data)
      target: Synthesizer  # Comparison target (synthetic data)
```

### Comparison Report Content

**Global Level (with Score)**:
- Overall similarity score
- Difference in number of records
- Overall comparison of column statistics

**Columnwise Level**:
- Difference or percentage change in statistics for each column
- Distribution similarity (JS divergence)
- Change in missing value ratio

### Custom Comparison Method

```yaml
Describer:
  custom_comparison:
    method: compare
    source:
      base: Loader
      target: Synthesizer
    stats_method:             # Custom statistical methods
      - mean
      - std
      - nunique
      - jsdivergence
    compare_method: diff      # Use difference instead of percentage change
    aggregated_method: mean
    summary_method: mean
```

**Available Statistical Methods**:
- Numeric: `mean`, `std`, `median`, `min`, `max`
- Categorical: `nunique`, `jsdivergence`

**Comparison Methods**:
- `pct_change`: Percentage change `(target - base) / abs(base)` (default)
- `diff`: Absolute difference `target - base`

## Practical Recommendations

**Checking Order**:
1. Execute Describer to generate statistical report
2. Review Global level to understand overall situation
3. Check Columnwise level to identify problematic columns
4. Observe Pairwise level to understand column associations

**Decision Making**:
- If multi-table data needs are found → Refer to [Multi-table Relationships](../multi-table-relationships)
- If constraints are needed → Refer to [Business Logic Constraints](../business-logic-constraints)
- If data quality is good → Proceed directly to [Getting Started](../../getting-started)

**Quality Standards**:
- Missing value ratio recommended <20%
- Outlier ratio recommended <5%
- Category balance recommended dominant category <80%
- Highly correlated column pairs recommended for further analysis

## Notes

- Describer does not modify original data, only generates statistical reports
- source parameter is required and must explicitly specify data source
- compare mode must use dictionary format to specify `base` and `target`
- Statistical methods automatically filter applicable calculations based on data type
- Inapplicable statistical methods will return NaN
