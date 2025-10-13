---
title: "fit()"
weight: 2
---

Train the synthesis model.

## Syntax

```python
def fit(data: pd.DataFrame)
```

## Parameters

- **data** : pd.DataFrame, required
    - Dataset for training
    - Must be a pandas DataFrame
    - Cannot be None

## Returns

None. Updates the synthesizer's internal state.

## Description

The `fit()` method is used to train the synthesis model. This method uses the provided dataset to learn the statistical properties and patterns of the data for subsequent synthetic data generation.

This method performs the following operations:
1. Validates the input data
2. Passes data to the underlying synthesizer implementation
3. Executes the model training process
4. Saves the trained model state

The specific training process details depend on the selected synthesis method:
- **GaussianCopula**: Learns marginal distributions and correlation structure
- **CTGAN/CopulaGAN**: Trains generative adversarial networks
- **TVAE**: Trains variational autoencoder
- **Custom methods**: Executes custom training logic

## Example

```python
from petsard import Synthesizer, Metadater
import pandas as pd

# Prepare training data
df = pd.read_csv('training_data.csv')
metadata = Metadater.from_data(df)

# Initialize and train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# After training, can generate synthetic data
synthetic_data = synthesizer.sample()
```

## Notes

- Must call `create()` before calling `fit()`
- Training time depends on data size, complexity, and chosen synthesis method
- Deep learning methods (CTGAN, TVAE) typically require longer training time
- Training process may consume significant memory, especially for large datasets
- Some synthesizers (like CTGAN) may benefit from GPU acceleration
- After training, model state is saved internally in the synthesizer
- Can call `sample()` multiple times without retraining
- To retrain, simply call `fit()` method again