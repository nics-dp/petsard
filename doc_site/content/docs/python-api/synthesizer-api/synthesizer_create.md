---
title: "create()"
weight: 1
---

Create and initialize the synthesizer.

## Syntax

```python
def create(metadata: SchemaMetadata = None)
```

## Parameters

- **metadata** : SchemaMetadata, optional
    - Schema metadata for the dataset
    - Contains data structure definitions
    - Default: `None`

## Returns

None. Initializes the synthesizer's internal state.

## Description

The `create()` method is used to create and initialize a synthesizer instance. This method sets up the synthesizer's internal implementation based on the synthesis method specified during initialization (e.g., SDV, custom methods).

This method performs the following operations:
1. Selects the appropriate synthesizer implementation based on the `method` parameter
2. Passes metadata to the implementation class
3. Initializes the synthesizer's internal state
4. Prepares the synthesizer for subsequent training (`fit()`) operations

## Example

```python
from petsard import Synthesizer, Metadater

# Create metadata from data
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# Create synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)

# Now ready for training
synthesizer.fit(data=df)
```

## Notes

- Must call `create()` before calling `fit()` or `fit_sample()`
- The metadata parameter is optional but recommended to ensure proper data structure handling
- For SDV synthesizers, metadata is automatically converted to SDV-required format
- Custom synthesizers must implement a compatible interface to receive metadata
- This method does not return a value but updates the synthesizer's internal state
- Calling `create()` repeatedly will reinitialize the synthesizer