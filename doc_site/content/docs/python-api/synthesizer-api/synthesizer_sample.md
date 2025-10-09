---
title: "sample()"
weight: 364
---

Generate synthetic data.

## Syntax

```python
def sample(
    sample_num_rows: int = None,
    reset_sampling: bool = False,
    output_file_path: str = None
)
```

## Parameters

- **sample_num_rows** : int, optional
    - Number of rows to generate
    - Default: `None` (uses original data row count)
    - Must be a positive integer

- **reset_sampling** : bool, optional
    - Whether to reset sampling state
    - Default: `False`
    - Set to `True` for reproducible results

- **output_file_path** : str, optional
    - Output file path
    - Default: `None` (does not save to file)
    - Supports CSV format

## Returns

None. Generated data is stored in the `data_syn` attribute.

## Description

The `sample()` method is used to generate synthetic data from a trained model. This method must be called after training is completed with `fit()`.

This method performs the following operations:
1. Checks if model is trained
2. Generates specified number of synthetic data rows
3. Applies precision rounding (if defined in schema)
4. Stores results in `data_syn` attribute
5. Optionally saves data to file

## Basic Example

```python
from petsard import Synthesizer

# Initialize, create and train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# Generate same number of rows as original data
synthesizer.sample()
synthetic_data = synthesizer.data_syn

# Generate specific number of rows
synthesizer.sample(sample_num_rows=1000)
print(f"Generated {len(synthesizer.data_syn)} synthetic rows")
```

## Advanced Examples

### Generate and Save to File

```python
from petsard import Synthesizer

# Train synthesizer
synthesizer = Synthesizer(method='sdv-single_table-gaussiancopula')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# Generate and save to file
synthesizer.sample(
    sample_num_rows=5000,
    output_file_path='synthetic_data.csv'
)

print(f"Synthetic data saved to synthetic_data.csv")
```

### Multiple Sampling

```python
# First sampling
synthesizer.sample(sample_num_rows=1000)
first_batch = synthesizer.data_syn.copy()

# Second sampling (results will differ)
synthesizer.sample(sample_num_rows=1000)
second_batch = synthesizer.data_syn.copy()

# Use reset for reproducible results
synthesizer.sample(sample_num_rows=1000, reset_sampling=True)
third_batch = synthesizer.data_syn.copy()

synthesizer.sample(sample_num_rows=1000, reset_sampling=True)
fourth_batch = synthesizer.data_syn.copy()

# third_batch and fourth_batch should be identical
```

### Batch Generation for Large Datasets

```python
# For large datasets, generate in batches
batch_size = 10000
total_rows = 100000
all_synthetic = []

for i in range(0, total_rows, batch_size):
    synthesizer.sample(sample_num_rows=batch_size)
    all_synthetic.append(synthesizer.data_syn)
    print(f"Generated {i + batch_size} / {total_rows} rows")

# Combine all batches
import pandas as pd
final_synthetic = pd.concat(all_synthetic, ignore_index=True)
```

## Notes

- Must complete `fit()` training before calling `sample()`
- Generated data overwrites previous results in `data_syn` attribute
- Large data generation may require significant time and memory
- `reset_sampling` parameter may not be effective for all synthesizers
- Output file will overwrite existing file with same name
- Precision rounding is automatically applied based on schema settings
- Some synthesizers may have generation quantity limits