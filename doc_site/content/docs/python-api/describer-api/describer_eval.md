---
title: "eval()"
weight: 2
---

Evaluate data and generate statistical descriptions or comparisons.

## Syntax

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## Parameters

- **data** : dict, required
    - Input data dictionary
    - For describe mode: `{"data": pd.DataFrame}`
    - For compare mode: `{"ori": pd.DataFrame, "syn": pd.DataFrame}`
    - Additional keys may be supported based on configuration

## Returns

- **dict[str, pd.DataFrame]**
    - Dictionary containing evaluation results
    - Keys depend on the granularity of analysis:
        - `"global"`: Overall statistics
        - `"columnwise"`: Column-level statistics
        - `"pairwise"`: Pairwise column relationships (correlations, etc.)

## Description

The `eval()` method performs statistical evaluation on the provided data. The behavior depends on the mode:

- **Describe mode**: Generates comprehensive statistical summaries for single dataset
- **Compare mode**: Compares multiple datasets and calculates differences

The method automatically determines which statistics to calculate based on data types and configuration.

## Basic Examples

### Describe Mode

```python
from petsard.evaluator import Describer
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'numeric': [1, 2, 3, 4, 5],
    'category': ['A', 'B', 'A', 'C', 'B']
})

# Initialize and evaluate
describer = Describer(method='describe')
describer.create()
results = describer.eval(data={'data': df})

# Access results
print(results['global'])      # Overall statistics
print(results['columnwise'])  # Per-column statistics
```

### Compare Mode

```python
from petsard.evaluator import Describer
import pandas as pd

# Create original and synthetic data
ori_df = pd.DataFrame({
    'value': [1, 2, 3, 4, 5],
    'type': ['A', 'B', 'A', 'C', 'B']
})

syn_df = pd.DataFrame({
    'value': [1.1, 2.2, 2.9, 4.1, 5.2],
    'type': ['A', 'B', 'A', 'C', 'B']
})

# Initialize in compare mode
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)
describer.create()

# Evaluate comparison
results = describer.eval(data={'ori': ori_df, 'syn': syn_df})

# Access comparison results
print(results['global'])      # Global comparison score
print(results['columnwise'])  # Column-wise comparisons
```

## Notes

- **Data preparation**: Ensure data is properly cleaned before evaluation
- **Memory usage**: Large datasets may consume significant memory during evaluation
- **Data types**: Different statistics are calculated for numerical vs categorical columns
- **Missing values**: NaN values are handled automatically based on the statistical method
- **Performance**: Pairwise statistics (correlations) can be computationally expensive for wide datasets
- **Mode consistency**: The data structure must match the configured mode (describe vs compare)