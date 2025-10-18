---
title: "Describer API"
weight: 350
---

Data description module that provides statistical summaries and insights from datasets.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/describer-api/describer-class-diagram.mmd" >}}

> **Legend:**
> - Blue box: Main class
> - Orange box: Implementation classes
> - Light purple box: Configuration classes
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

```python
from petsard.evaluator import Describer

# Basic description
describer = Describer(method='describe')
describer.create()
results = describer.eval(data={'data': df})

# Compare mode
describer = Describer(method='describe', mode='compare')
describer.create()
results = describer.eval(data={'base': df1, 'target': df2})
```

## Constructor (__init__)

Initialize a Describer instance for data description and analysis.

### Syntax

```python
def __init__(
    method: str,
    mode: str = "describe",
    **kwargs
)
```

### Parameters

- **method** : str, required
    - Evaluation method to use
    - Typically use "describe" for Describer
    - Default: No default value, must be specified

- **mode** : str, optional
    - Operation mode for the describer
    - "describe": Single dataset description (default)
    - "compare": Dataset comparison
    - Default: `"describe"`

- **\*\*kwargs** : dict, optional
    - Additional parameters passed to the underlying evaluator
    - For describe mode: supports DescriberDescribe parameters
    - For compare mode: supports DescriberCompare parameters

### Returns

- **Describer**
    - Initialized Describer instance

### Examples

```python
from petsard.evaluator import Describer

# Basic description mode
describer = Describer(method='describe')

# Compare mode with additional parameters
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)

# Custom describe methods
describer = Describer(
    method='describe',
    describe_method=['mean', 'median', 'std', 'corr']
)
```

## Notes

- **Mode selection**: Choose "describe" for single dataset analysis, "compare" for comparing multiple datasets
- **Parameter naming**: Compare mode recommends using `base`/`target` instead of the legacy `ori`/`syn` (still backward compatible)
- **Method flexibility**: Supports various statistical methods through describe_method parameter
- **Recommendation**: Use YAML configuration for complex setups
- **Backward compatibility**: Maintains compatibility with existing Evaluator interface
- **Documentation note**: This documentation is for internal development team reference only