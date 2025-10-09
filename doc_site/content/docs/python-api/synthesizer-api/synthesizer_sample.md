---
title: "sample()"
weight: 364
---

Generate synthetic data.

## Syntax

```python
def sample() -> pd.DataFrame
```

## Parameters

None

## Returns

- **pd.DataFrame**
    - The generated synthetic data
    - Same columns as original training data

## Description

The `sample()` method is used to generate synthetic data from a trained model. This method must be called after training is completed with `fit()`.

This method performs the following operations:
1. Checks if model is trained
2. Generates synthetic data rows (number determined by configuration)
3. Returns the generated synthetic data as a DataFrame

## Example

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# Load and prepare data
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# Initialize, create and train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# Generate synthetic data
synthetic_data = synthesizer.sample()
print(f"Generated {len(synthetic_data)} synthetic rows")

# Save to file if needed
synthetic_data.to_csv('synthetic_data.csv', index=False)
```

## Notes

- Must complete `fit()` training before calling `sample()`
- The number of rows generated is determined during `create()` or `fit()` based on metadata or training data
- Large data generation may require significant time and memory
- Some synthesizers may have generation quantity limits
- To specify the number of rows to generate, set `sample_num_rows` parameter when initializing the Synthesizer