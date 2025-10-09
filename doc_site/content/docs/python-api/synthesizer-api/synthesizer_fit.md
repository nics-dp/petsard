---
title: "fit()"
weight: 363
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

## Basic Example

```python
from petsard import Synthesizer
import pandas as pd

# Prepare training data
df = pd.read_csv('training_data.csv')

# Initialize and train synthesizer
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit(data=df)

# After training, can generate synthetic data
synthesizer.sample(sample_num_rows=1000)
```

## Advanced Examples

### Training with CTGAN

```python
from petsard import Synthesizer, Metadater

# Load data
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# Use CTGAN
synthesizer = Synthesizer(
    method='sdv-single_table-ctgan',
    epochs=300,  # CTGAN-specific parameter
    batch_size=500
)
synthesizer.create(metadata=metadata)

# Train model
synthesizer.fit(data=df)

# Generate synthetic data
synthesizer.sample(sample_num_rows=len(df))
```

### Monitoring Training Progress

```python
import logging

# Set up logging to monitor training
logging.basicConfig(level=logging.INFO)

synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)

# Training will output progress information (if supported by synthesizer)
synthesizer.fit(data=df)
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