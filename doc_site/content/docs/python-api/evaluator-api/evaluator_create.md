---
title: "create()"
weight: 1
---

Initialize the evaluator instance and prepare for evaluation.

## Syntax

```python
def create() -> None
```

## Parameters

None

## Return Value

None

## Description

The `create()` method is used to initialize the evaluator instance. This method must be called after `__init__()` and before `eval()`.

This method performs the following operations based on the evaluation method specified during initialization:
1. Load the corresponding evaluation module
2. Configure evaluation parameters
3. Initialize the evaluator
4. Prepare the evaluation environment

Different evaluation methods perform different initialization operations:
- **Anonymeter**: Initialize privacy risk evaluator
- **SDMetrics**: Initialize data quality evaluator
- **MLUtility**: Initialize machine learning utility evaluator
- **Stats**: Initialize statistical evaluator
- **Custom**: Load and initialize custom evaluator

## Basic Examples

```python
from petsard import Evaluator

# Initialize privacy risk evaluator
evaluator = Evaluator('anonymeter-singlingout')
evaluator.create()  # Initialize evaluator

# Initialize data quality evaluator
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()  # Initialize evaluator

# Initialize machine learning utility evaluator
evaluator = Evaluator(
    'mlutility',
    task_type='classification',
    target='income'
)
evaluator.create()  # Initialize evaluator
```

## Notes

- **Required Step**: This method must be called before `eval()`
- **Single Call**: Each evaluator instance only needs to call `create()` once
- **Parameter Setting**: All evaluation parameters must be set during `__init__()`, `create()` does not accept parameters
- **Error Handling**: If the evaluation method does not exist or parameters are incorrect, an exception will be raised at this stage
- **Resource Initialization**: Some evaluators may load models or allocate resources at this stage
- **Best Practice**: Use YAML configuration files rather than direct Python API