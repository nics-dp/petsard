---
title: "Evaluator API"
weight: 350
---

Synthetic data quality evaluation module, providing privacy risk measurement, data quality assessment, and machine learning utility analysis.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/evaluator-api/evaluator-class-diagram.mmd" >}}

> **Legend:**
> - Blue boxes: Main classes
> - Orange boxes: Subclass implementations
> - Light purple boxes: Configuration and data classes
> - Light green boxes: Input data
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship
> - `-->`: Data flow

## Basic Usage

```python
from petsard import Evaluator

# Privacy risk assessment
evaluator = Evaluator('anonymeter-singlingout')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
privacy_risk = eval_result['global']

# Data quality assessment
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data
})
quality_score = eval_result['global']

# Machine learning utility assessment (new version)
evaluator = Evaluator('mlutility', task_type='classification', target='income')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
ml_utility = eval_result['global']
```

## Constructor (__init__)

Initialize evaluator instance.

### Syntax

```python
def __init__(
    method: str,
    **kwargs
)
```

### Parameters

- **method** : str, required
    - Evaluation method name
    - Required parameter
    - Supported methods:
        - **Privacy Risk Assessment**:
            - `'anonymeter-singlingout'`: Singling out risk
            - `'anonymeter-linkability'`: Linkability risk
            - `'anonymeter-inference'`: Inference risk
        - **Data Quality Assessment**:
            - `'sdmetrics-diagnosticreport'`: Data diagnostic report
            - `'sdmetrics-qualityreport'`: Data quality report
        - **Machine Learning Utility Assessment (Legacy)**:
            - `'mlutility-classification'`: Classification utility (multiple models)
            - `'mlutility-regression'`: Regression utility (multiple models)
            - `'mlutility-cluster'`: Clustering utility (K-means)
        - **Machine Learning Utility Assessment (New, Recommended)**:
            - `'mlutility'`: Unified interface (requires task_type parameter)
        - **Statistical Assessment**:
            - `'stats'`: Statistical difference comparison
        - **Default Method**:
            - `'default'`: Uses sdmetrics-qualityreport
        - **Custom Method**:
            - `'custom_method'`: Custom evaluator

- **kwargs** : dict, optional
    - Additional parameters for specific evaluators
    - May include depending on evaluation method:
        - **MLUtility Parameters**:
            - `task_type`: Task type ('classification', 'regression', 'clustering')
            - `target`: Target column name
            - `experiment_design`: Experiment design approach
            - `resampling`: Imbalanced data handling method
        - **Anonymeter Parameters**:
            - `n_attacks`: Number of attack attempts
            - `n_cols`: Number of columns per query
            - `secret`: Column to be inferred (inference risk)
            - `aux_cols`: Auxiliary information columns (linkability risk)
        - **Custom Method Parameters**:
            - `module_path`: Custom module path
            - `class_name`: Custom class name

### Return Value

- **Evaluator**
    - Initialized evaluator instance

### Usage Examples

```python
from petsard import Evaluator

# Default evaluation
evaluator = Evaluator('default')
evaluator.create()
eval_result = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

## Supported Evaluation Types

Please refer to PETsARD YAML documentation for details.

## Notes

- **Method Selection**: Choose evaluation method suitable for your needs, different methods focus on different aspects
- **Data Requirements**: Different evaluation methods require different input data combinations
    - Anonymeter and MLUtility: Require ori, syn, control three datasets
    - SDMetrics and Stats: Only require ori and syn two datasets
- **Best Practice**: Use YAML configuration files rather than direct Python API
- **Method Call Order**: Must call `create()` before calling `eval()`
- **MLUtility Version**: Recommend using new MLUtility (with task_type) rather than legacy separate interfaces
- **Documentation Note**: This documentation is for internal development team reference only, backward compatibility is not guaranteed