---
title: "Field Proportions"
type: docs
weight: 674
prev: docs/petsard-yaml/constrainer-yaml/field_combinations
next: docs/petsard-yaml/constrainer-yaml
---

Maintain the distribution proportions of the original data during constraint filtering.

## Feature Description

Ideally, synthesizers should automatically preserve the proportion distribution of each field. However, depending on different synthesis principles (such as CTGAN, TVAE, etc.), synthetic data may not perfectly maintain the original distribution proportions. This feature provides an **effective post-processing mechanism** that uses constraint filtering to **guarantee a certain degree of proportion maintenance**, ensuring that synthetic data maintains distribution characteristics similar to the original data even after being filtered through various constraint conditions.

**Use Cases**:
- Distribution of certain fields in synthetic data deviates from the original data
- Need to ensure the missing value proportion of specific fields matches the original
- Multiple constraint conditions may cause certain categories to be excessively filtered out

## Usage Examples

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_proportions.ipynb)

```yaml
field_proportions:
  - fields: 'education'      # Target field: education
    mode: 'all'              # Mode: maintain distribution of all values (including NA)
    tolerance: 0.1           # Tolerance: allow 10% deviation

  - fields: 'workclass'      # Target field: workclass
    mode: 'missing'          # Mode: only maintain proportion of missing values (NA)
    tolerance: 0.03          # Tolerance: allow 3% deviation
```

## Syntax Format

### Single Field

```yaml
- fields: 'field_name'
  mode: 'all' | 'missing'
  tolerance: 0.1  # Optional, default 0.1
```

---

### Multi-Field Combination

```yaml
-
  fields:
    - field_name1
    - field_name2
  mode: 'all'
  tolerance: 0.15
```

## Parameter Description

### mode

- **`'all'`**: Maintain distribution of all values (including NA)
- **`'missing'`**: Only maintain proportion of missing values (NA)

### tolerance

- Allowed deviation range from original proportions (0.0-1.0)
- Default: `0.1` (10%)
- Example: Original 30%, tolerance 0.1 → allows 27%-33%

## Important Notes

- **Only supports categorical variables**: This feature is designed to maintain distribution proportions of categorical data and is not suitable for continuous numeric data
  - Fields must have `type` set to `'category'` or a categorical logical type in the schema
  - Numeric, datetime, and other continuous types are not supported
- Maintains distribution through iterative removal of excess data
- High cardinality fields (too many values) have limited maintenance effect
- Multiple rules may conflict, recommend using more relaxed tolerance
- Null values (NA) are also maintained in 'all' mode