---
title: "create()"
weight: 1
---

Initialize and prepare the evaluator for data description.

## Syntax

```python
def create() -> None
```

## Parameters

This method takes no parameters.

## Returns

- **None**
    - This method does not return a value

## Description

The `create()` method initializes the internal evaluator implementation based on the configured mode and parameters. This method must be called before using `eval()` to perform evaluations.

The initialization process includes:
- Creating the appropriate evaluator class (DataDescriber or Stats)
- Configuring statistical methods based on mode
- Setting up comparison parameters if in compare mode
- Preparing internal data structures for evaluation

## Basic Examples

### Describe Mode

```python
from petsard.evaluator import Describer

# Initialize describer
describer = Describer(
    method='describe',
    describe_method=['mean', 'median', 'std', 'corr']
)

# Create the evaluator
describer.create()

# Now ready to evaluate data
results = describer.eval(data={'data': df})
```

### Compare Mode

```python
from petsard.evaluator import Describer

# Initialize in compare mode
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)

# Create the evaluator
describer.create()

# Now ready to compare datasets
results = describer.eval(data={'ori': ori_df, 'syn': syn_df})
```

### With Custom Parameters

```python
from petsard.evaluator import Describer

# Initialize with custom parameters
describer = Describer(
    method='describe',
    describe_method=['mean', 'std', 'min', 'max', 'corr'],
    percentile=0.95  # Calculate 95th percentile
)

# Create the evaluator
describer.create()

# Evaluate data
results = describer.eval(data={'data': df})
```

## Notes

- **Required step**: Always call `create()` before `eval()`
- **One-time initialization**: Only needs to be called once per Describer instance
- **Mode-specific**: The created evaluator depends on the configured mode
- **Performance**: Creation is lightweight, actual computation happens in `eval()`
- **Error handling**: Will raise an error if configuration is invalid
- **State management**: Creates internal state that persists across multiple `eval()` calls