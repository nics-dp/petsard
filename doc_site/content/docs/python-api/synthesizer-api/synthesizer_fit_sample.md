---
title: "fit_sample()"
weight: 4
---

Perform training and generation in sequence.

## Syntax

```python
def fit_sample(data: pd.DataFrame) -> pd.DataFrame
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset for training
    - Must be a pandas DataFrame
    - Cannot be None

## Returns

- **pd.DataFrame**
    - The generated synthetic data
    - Same columns as original training data

## Description

The `fit_sample()` method combines the functionality of `fit()` and `sample()`, completing model training and synthetic data generation in a single call. This is the most commonly used method, particularly suitable for standard synthetic data generation workflows.

This method performs the following operations:
1. Trains the model using provided data (equivalent to calling `fit()`)
2. Generates synthetic data from the trained model (equivalent to calling `sample()`)
3. Returns the generated synthetic data

## Example

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# Load data
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# Train and generate in one step
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthetic_data = synthesizer.fit_sample(data=df)

# Access synthetic data
print(f"Generated {len(synthetic_data)} synthetic rows")

# Save to file if needed
synthetic_data.to_csv('synthetic_output.csv', index=False)
```

## Notes

- Must call `create()` before using `fit_sample()`
- This method overwrites any previous training state
- Each call retrains the model, even with identical data
- For multiple generations with different quantities, recommend using `fit()` and `sample()` separately
- Training time depends on data size and chosen synthesis method
- Suitable for one-time training and generation needs
- The number of rows generated is determined during `create()` or from training data