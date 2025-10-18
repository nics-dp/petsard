---
title: "inverse_transform()"
weight: 334
---

Execute data postprocessing restoration, converting processed data back to original format.

## Syntax

```python
def inverse_transform(
    data: pd.DataFrame
) -> pd.DataFrame
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset to be restored (typically synthetic data)
    - Required parameter
    - Should be data that went through the same preprocessing steps

## Returns

- **pd.DataFrame**
    - Restored data
    - All inverse transformation steps applied
    - Data format close to original

## Description

The `inverse_transform()` method performs inverse data transformation. This method will:

1. Execute restoration operations in reverse order of preprocessing sequence
2. Sequentially apply inverse scaling, inverse encoding, restore missing values, etc.
3. Align data types to original schema
4. Return data in format close to original

This method must be called after `fit()` and `transform()`.

## Basic Example

```python
from petsard import Loader, Processor, Synthesizer

# 1. Load and preprocess data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# 2. Synthesize data
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data)
synthetic_data = synthesizer.data_syn

# 3. Postprocess restoration
restored_data = processor.inverse_transform(synthetic_data)

print(f"Original data shape: {data.shape}")
print(f"Restored data shape: {restored_data.shape}")
```

## Complete Workflow

```python
from petsard import Loader, Processor, Synthesizer
import pandas as pd

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Preprocessing
processor = Processor(metadata=schema)
processor.fit(data, sequence=['missing', 'outlier', 'encoder', 'scaler'])
processed_data = processor.transform(data)

# Synthesis
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data, sample_num_rows=len(data))
synthetic_data = synthesizer.data_syn

# Postprocessing restoration
# Restoration sequence automatically becomes: ['scaler', 'encoder', 'missing']
restored_data = processor.inverse_transform(synthetic_data)

# Compare data distributions
print("Original data descriptive statistics:")
print(data.describe())
print("\nRestored data descriptive statistics:")
print(restored_data.describe())
```

## Restoration Workflow

```
Start
  ↓
Check if trained
  ↓
Set missing value restoration parameters
  ↓
Reverse preprocessing sequence (remove outlier)
  ↓
Execute restoration in reverse order:
  4. Scaler: Inverse scale to original range
     ↓ (Mediator adjusts columns)
  3. Encoder: Decode categorical variables
     ↓ (Mediator adjusts columns)
  1. Missing: Insert NA proportionally
     ↓
Align data types to schema
  ↓
Return restored data
  ↓
End
```

## Restoration Steps Explained

### 1. Inverse Scaling
- Restore normalized values to original range
- Use scaling parameters learned during preprocessing
- Examples: inverse standardization, inverse min-max scaling

### 2. Inverse Encoding
- Convert numerical values back to categorical labels
- One-Hot encoding restored to single column
- Use mapping table created during preprocessing

### 3. Restore Missing Values
- According to missing value ratio in original data
- Randomly select positions to insert `NA` values
- Calculate missing ratio independently for each column

### 4. Align Data Types
- Adjust data types according to schema definition
- Ensure categorical, numerical, datetime types are correct
- Handle special datetime formats

## Missing Value Restoration Mechanism

```python
# System automatically calculates and restores missing values
# Assume original data has 10% missing values

# During preprocessing, record:
# - Global missing value ratio: 10%
# - age column missing value ratio: 15%
# - income column missing value ratio: 5%

# During postprocessing, restore:
# 1. Randomly select 10% of data rows
# 2. In age column, set 15% of these rows to NA
# 3. In income column, set 5% of these rows to NA
```

## Notes

- Must complete `fit()` and `transform()` first
- Input data should be data processed with same preprocessing
- Outlier processing is not restored (step is skipped)
- Missing value positions are random, not exactly same as original data
- One-Hot encoding reduces number of columns
- Restored data types align to original schema
- Returns a copy of data, does not modify input
- Datetime data converted to appropriate format
- Floating point numbers from some synthesizers are rounded to integers (for discretizing cases)