---
title: "fit_sample()"
weight: 365
---

Perform training and generation in sequence.

## Syntax

```python
def fit_sample(
    data: pd.DataFrame,
    sample_num_rows: int = None,
    reset_sampling: bool = False,
    output_file_path: str = None
)
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset for training
    - Must be a pandas DataFrame
    - Cannot be None

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

The `fit_sample()` method combines the functionality of `fit()` and `sample()`, completing model training and synthetic data generation in a single call. This is the most commonly used method, particularly suitable for standard synthetic data generation workflows.

This method performs the following operations:
1. Trains the model using provided data (equivalent to calling `fit()`)
2. Generates synthetic data from the trained model (equivalent to calling `sample()`)
3. Applies precision rounding (if defined in schema)
4. Stores results in the `data_syn` attribute
5. Optionally saves data to file

## Basic Example

```python
from petsard import Synthesizer
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Train and generate in one step
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df)

# Access synthetic data
synthetic_data = synthesizer.data_syn
print(f"Generated {len(synthetic_data)} synthetic rows")
```

## Advanced Examples

### Specify Generation Quantity

```python
from petsard import Synthesizer, Metadater

# Prepare data and metadata
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# Train and generate specific amount of data
synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(
    data=df,
    sample_num_rows=10000  # Generate 10000 rows
)

print(f"Original data: {len(df)} rows")
print(f"Synthetic data: {len(synthesizer.data_syn)} rows")
```

### Direct Save Results

```python
# Train, generate and save to file
synthesizer = Synthesizer(method='sdv-single_table-gaussiancopula')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(
    data=df,
    sample_num_rows=5000,
    output_file_path='synthetic_output.csv'
)

print("Synthetic data saved to synthetic_output.csv")
```

### Complete Workflow Example

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# 1. Load data
df = pd.read_csv('original_data.csv')
print(f"Loaded data: {df.shape}")

# 2. Create metadata
metadata = Metadater.from_data(df)

# 3. Configure synthesizer
synthesizer = Synthesizer(
    method='sdv-single_table-ctgan',
    epochs=300,
    batch_size=500
)

# 4. Create synthesizer instance
synthesizer.create(metadata=metadata)

# 5. Train and generate
synthesizer.fit_sample(
    data=df,
    sample_num_rows=len(df) * 2,  # Generate double amount
    reset_sampling=True,  # Ensure reproducibility
    output_file_path='synthetic_double.csv'
)

# 6. Validate results
print(f"Synthetic data: {synthesizer.data_syn.shape}")
print(f"Column consistency: {set(df.columns) == set(synthesizer.data_syn.columns)}")
```

## Notes

- Must call `create()` before using `fit_sample()`
- This method overwrites any previous training state
- Each call retrains the model, even with identical data
- For multiple generations with different quantities, recommend using `fit()` and `sample()` separately
- Training time depends on data size and chosen synthesis method
- Generated data overwrites previous results in `data_syn` attribute
- Suitable for one-time training and generation needs
- Not suitable for scenarios requiring fine-tuning or multiple sampling