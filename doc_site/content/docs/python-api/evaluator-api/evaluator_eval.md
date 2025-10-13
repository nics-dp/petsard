---
title: "eval()"
weight: 2
---

Execute data evaluation and return evaluation results.

## Syntax

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## Parameters

- **data** : dict, required
    - Data dictionary for evaluation
    - Different data combinations are required depending on the evaluation method:
        - **Anonymeter & MLUtility**:
            - `'ori'`: Original data used for synthesis (`pd.DataFrame`)
            - `'syn'`: Synthetic data (`pd.DataFrame`)
            - `'control'`: Control data not used for synthesis (`pd.DataFrame`)
        - **SDMetrics & Stats**:
            - `'ori'`: Original data (`pd.DataFrame`)
            - `'syn'`: Synthetic data (`pd.DataFrame`)

## Return Value

- **dict[str, pd.DataFrame]**
    - Evaluation result dictionary containing different keys depending on the evaluation method:
        - `'global'`: Overall dataset evaluation results (single-row DataFrame)
        - `'columnwise'`: Per-column evaluation results (each row represents a column)
        - `'pairwise'`: Column pair evaluation results (each row represents a column pair)
        - `'details'`: Other detailed information

## Description

The `eval()` method is used to execute the actual evaluation operation. This method must be called after `create()`.

Return results for different evaluation methods:

### Privacy Risk Assessment (Anonymeter)

Returns evaluation results containing risk scores and confidence intervals:
- `'risk'`: Privacy risk score (0-1)
- `'risk_CI_btm'`: Risk confidence interval lower bound
- `'risk_CI_top'`: Risk confidence interval upper bound
- `'attack_rate'`: Main attack success rate
- `'baseline_rate'`: Baseline attack success rate
- `'control_rate'`: Control group attack success rate

### Data Quality Assessment (SDMetrics)

**Diagnostic Report** returns:
- `'Score'`: Overall diagnostic score
- `'Data Validity'`: Data validity score
- `'Data Structure'`: Data structure score

**Quality Report** returns:
- `'Score'`: Overall quality score
- `'Column Shapes'`: Column distribution similarity
- `'Column Pair Trends'`: Column relationship preservation

### Machine Learning Utility Assessment (MLUtility)

Returns model performance comparison results:
- **Dual Model Control Mode**:
    - `'ori_score'`: Original data model score
    - `'syn_score'`: Synthetic data model score
    - `'difference'`: Score difference
    - `'ratio'`: Score ratio
- **Domain Transfer Mode**:
    - `'syn_to_ori_score'`: Synthetic data model score on original data

### Statistical Assessment (Stats)

Returns statistical comparison results:
- Statistics for each column (original and synthetic)
- Difference or percentage change between them
- Overall score

## Example

```python
from petsard import Evaluator
import pandas as pd

# Prepare data
ori_data = pd.read_csv('original.csv')
syn_data = pd.read_csv('synthetic.csv')

# Default evaluation
evaluator = Evaluator('default')
evaluator.create()
eval_result = evaluator.eval({
    'ori': ori_data,
    'syn': syn_data
})

# View results
print(f"Evaluation score: {eval_result['global']['Score'].values[0]:.4f}")
```

## Notes

- **Data Requirements**: Ensure provided data meets evaluation method requirements
- **Data Format**: All data must be in `pd.DataFrame` format
- **Column Consistency**: ori, syn, control data should have the same column structure
- **Missing Value Handling**: Some evaluation methods automatically handle missing values, refer to specific method documentation
- **Memory Usage**: Large datasets may require more memory, consider batch processing
- **Execution Time**: Privacy risk assessment and machine learning utility assessment may require longer execution time
- **Best Practice**: Use YAML configuration files rather than direct Python API