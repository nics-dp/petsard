---
title: "Splitter API"
type: docs
weight: 1070
---

Data splitting module for creating training and validation sets with overlap control.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/splitter-api/splitter-class-diagram.mmd" >}}

> **Legend:**
> - Blue box: Main class
> - Orange box: Subclass implementations
> - Light purple box: Configuration and data classes
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

```python
from petsard import Splitter

# Basic splitting
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# Strict overlap control
splitter = Splitter(
    num_samples=5,
    train_split_ratio=0.7,
    max_overlap_ratio=0.1  # Maximum 10% overlap
)
```

## Constructor (__init__)

Initialize a data splitter instance.

### Syntax

```python
def __init__(
    num_samples: int = 1,
    train_split_ratio: float = 0.8,
    random_state: int | float | str = None,
    max_overlap_ratio: float = 1.0,
    max_attempts: int = 30
)
```

### Parameters

- **num_samples** : int, optional
    - Number of times to resample the data
    - Default: `1`
    - Must be positive integer

- **train_split_ratio** : float, optional
    - Ratio of data for training set
    - Default: `0.8`
    - Range: `0.0` to `1.0`

- **random_state** : int | float | str, optional
    - Seed for reproducibility
    - Default: `None`
    - Can be integer, float, or string

- **max_overlap_ratio** : float, optional
    - Maximum allowed overlap ratio between samples
    - Default: `1.0` (100% - allows complete overlap)
    - Range: `0.0` to `1.0`
    - Set to `0.0` for no overlap between samples

- **max_attempts** : int, optional
    - Maximum attempts for sampling with overlap control
    - Default: `30`
    - Used when overlap control is active

### Returns

- **Splitter**
    - Initialized splitter instance

### Examples

```python
from petsard import Splitter

# Basic splitter with default settings
splitter = Splitter()

# Multiple samples with reproducibility
splitter = Splitter(
    num_samples=5,
    train_split_ratio=0.8,
    random_state=42
)

# Strict overlap control
splitter = Splitter(
    num_samples=3,
    max_overlap_ratio=0.1,  # Max 10% overlap
    max_attempts=50
)

# No overlap between samples
splitter = Splitter(
    num_samples=5,
    max_overlap_ratio=0.0,  # Completely non-overlapping
    random_state="experiment_v1"
)
```

## Notes

- The functional API returns tuples directly from the `split()` method
- Uses functional programming patterns with immutable data structures
- For detailed split method usage, see the split() documentation
- Recommend using YAML configuration for complex experiments
- Bootstrap sampling is used internally for generating multiple samples