---
title: "fit()"
weight: 332
---

Train the processor to learn statistical properties of the data.

## Syntax

```python
def fit(
    data: pd.DataFrame,
    sequence: list = None
) -> None
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset for training
    - Required parameter
    - Processor learns statistical properties from this data

- **sequence** : list, optional
    - Custom processing sequence
    - Default: `['missing', 'outlier', 'encoder', 'scaler']`
    - Available values: `'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`

## Returns

None (method modifies instance state)

## Description

The [`fit()`](processor_fit.md:1) method trains the processor. This method will:

1. Analyze statistical properties of the data (mean, standard deviation, categories, etc.)
2. Create transformation rules for each processor
3. Prepare for subsequent [`transform()`](processor_transform.md:1) operations

This method must be called before [`transform()`](processor_transform.md:1).

## Basic Example

```python
from petsard import Loader, Processor

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Create and train processor
processor = Processor(metadata=schema)
processor.fit(data)

# Transform data
processed_data = processor.transform(data)
```

## Custom Processing Sequence

```python
from petsard import Processor

# Use only missing value handling and encoding
processor = Processor(metadata=schema)
processor.fit(data, sequence=['missing', 'encoder'])

# Use complete sequence
processor = Processor(metadata=schema)
processor.fit(
    data,
    sequence=['missing', 'outlier', 'encoder', 'scaler']
)
```

## Using Discretization

```python
from petsard import Processor

# Use discretization (cannot be used with encoder simultaneously)
processor = Processor(metadata=schema)
processor.fit(
    data,
    sequence=['missing', 'outlier', 'discretizing']
)
```

## Training Workflow

```
Start
  ↓
Validate sequence validity
  ↓
Create Mediator for each step
  ↓
Train processors in sequence order:
  - missing: Learn fill values (mean, median, etc.)
  - outlier: Learn outlier thresholds
  - encoder: Learn category mappings
  - scaler: Learn scaling parameters (mean, std, etc.)
  ↓
Set training complete flag
  ↓
End
```

## Notes

- Must call this method before [`transform()`](processor_transform.md:1)
- Training data should have the same structure as data to be transformed later
- `discretizing` and `encoder` cannot be used together
- `discretizing` must be the last step in the sequence
- Maximum of 4 processing steps supported
- Some processors (e.g., `outlier_isolationforest`) perform global transformation
- Statistical information learned during training is saved in the processor instance
- Calling [`fit()`](processor_fit.md:1) again will overwrite previous training results