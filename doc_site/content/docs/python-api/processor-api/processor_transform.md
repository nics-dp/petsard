---
title: "transform()"
weight: 333
---

Execute data preprocessing transformations.

## Syntax

```python
def transform(
    data: pd.DataFrame
) -> pd.DataFrame
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset to be transformed
    - Required parameter
    - Should have the same structure as training data

## Returns

- **pd.DataFrame**
    - Transformed data
    - All preprocessing steps applied

## Description

The `transform()` method performs actual data transformation. This method will:

1. Execute each processing step according to the training sequence
2. Sequentially apply missing value handling, outlier processing, encoding, scaling, etc.
3. Return transformed data

This method must be called after `fit()`.

## Basic Example

```python
from petsard import Loader, Processor

# Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Train processor
processor = Processor(metadata=schema)
processor.fit(data)

# Transform data
processed_data = processor.transform(data)

print(f"Original data shape: {data.shape}")
print(f"Processed shape: {processed_data.shape}")
```

## Transform Different Datasets

```python
from petsard import Processor

# Train on training set
processor = Processor(metadata=schema)
processor.fit(train_data)

# Transform training set
train_processed = processor.transform(train_data)

# Use same transformer for test set
test_processed = processor.transform(test_data)
```

## Check Transformation Results

```python
import pandas as pd
from petsard import Processor

processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# Compare before and after
print("Before transformation:")
print(data.describe())
print("\nAfter transformation:")
print(processed_data.describe())

# Check missing values
print(f"\nMissing values before: {data.isna().sum().sum()}")
print(f"Missing values after: {processed_data.isna().sum().sum()}")
```

## Transformation Workflow

```
Start
  ↓
Check if trained
  ↓
Copy input data
  ↓
Execute processing in sequence:
  1. Missing: Fill missing values
     ↓
  2. Outlier: Handle outliers
     ↓
  3. Encoder: Encode categorical variables
     ↓ (Mediator adjusts columns)
  4. Scaler: Normalize numerical values
     ↓
Return processed data
  ↓
End
```

## Processing Steps Explained

### 1. Missing Value Handling
- Fill using statistics learned during training
- Examples: mean, median, mode

### 2. Outlier Processing
- Identify and handle anomalous values
- Use thresholds calculated during training

### 3. Encoding
- Convert categorical variables to numerical
- May increase number of columns (e.g., One-Hot encoding)

### 4. Scaling
- Normalize numerical ranges
- Use parameters learned during training (mean, std, etc.)

## Notes

- Must call `fit()` to train processor first
- Transformed data must have same column structure as training data
- Some encoding methods (e.g., One-Hot) change the number of columns
- Data types after transformation may differ from original
- Returns a copy of the data, does not modify original
- Can be called repeatedly to transform multiple datasets
- All transformations use the same training parameters
- Outlier processing may remove some data rows