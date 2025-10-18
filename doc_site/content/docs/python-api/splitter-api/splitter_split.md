---
title: "split()"
weight: 352
---

Splits data into training and validation sets with enhanced overlap control.

## Syntax

```python
def split(
    data: pd.DataFrame = None,
    metadata: SchemaMetadata = None,
    exist_train_indices: list[set] = None
) -> tuple[dict, dict, list[set]]
```

## Parameters

- **data** : pd.DataFrame, required
    - The dataset to split
    - Must be a pandas DataFrame
    - Cannot be None

- **metadata** : SchemaMetadata, optional
    - Metadata for the dataset
    - Contains schema information about the data
    - Will be updated with split information
    - Default: `None`

- **exist_train_indices** : list[set], optional
    - List of existing training index sets to avoid overlap with
    - Each set contains training indices from a previous split
    - Used to ensure new splits don't overlap with existing ones
    - Default: `None`

## Returns

- **tuple[dict, dict, list[set]]**
    - A tuple containing three elements:
        - `split_data` (`dict`): Dictionary of format `{sample_num: {'train': df, 'validation': df}}`
        - `metadata_dict` (`dict`): Dictionary of format `{sample_num: {'train': metadata, 'validation': metadata}}`
        - `train_indices` (`list[set]`): List of training index sets for each sample

## Description

The `split()` method performs data splitting using functional programming patterns with enhanced overlap control. It generates multiple train/validation splits based on the configuration provided during initialization.

The method performs the following operations:
1. Validates input data
2. Generates training indices based on overlap control settings
3. Creates training and validation DataFrames
4. Updates metadata if provided
5. Returns results as immutable data structures

## Example

```python
from petsard import Splitter
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'feature1': range(100),
    'feature2': range(100, 200),
    'target': [0, 1] * 50
})

# Basic split
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# Access results
for i in range(1, 4):
    train_df = split_data[i]['train']
    val_df = split_data[i]['validation']
    print(f"Sample {i}: Train={len(train_df)}, Val={len(val_df)}")
```

## Notes

- This method follows functional programming principles returning immutable data structures
- Sample numbers start from 1, not 0
- When `max_overlap_ratio` is set to 0.0, samples will have no overlap
- If the method cannot generate valid samples within `max_attempts`, it will raise an exception
- Metadata is optional but recommended for maintaining data lineage
- Returned DataFrames are copies, not references to the original data