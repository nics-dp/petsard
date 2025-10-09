---
title: "SynthesizerAdapter"
weight: 393
---

SynthesizerAdapter handles synthetic data generation using various generative models with pipeline integration.

## Main Features

- Unified interface for synthetic data generation
- Support for multiple synthesis methods (CTGAN, TVAE, CopulaGAN, GaussianCopula)
- Automatic model training and sampling
- Metadata and privacy preservation support
- Integration with pipeline system

## Method Reference

### `__init__(config: dict)`

Initializes SynthesizerAdapter instance with synthesis configuration.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - Keys: `method`, `sample_size`, `epochs`, `batch_size`, `use_metadata`, `random_state`

### `run(input: dict)`

Executes synthetic data generation operation.

**Parameters:**
- `input`: dict, required
  - Must contain:
    - `data`: pd.DataFrame - Training data
    - `metadata`: Schema - Data metadata
    - `sample_size`: int (optional) - Number of synthetic samples to generate

**Returns:**
No direct return value. Use `get_result()` to get synthetic data.

### `get_result()`

Gets the synthetic data generation results.

**Returns:**
- `tuple[pd.DataFrame, Schema]`: Synthetic data and updated metadata

### `set_input(data, metadata)`

Sets input data for the synthesizer.

**Parameters:**
- `data`: pd.DataFrame - Training data
- `metadata`: Schema - Data metadata

## Usage Example

```python
from petsard.adapter import SynthesizerAdapter

# Configure synthesizer
adapter = SynthesizerAdapter({
    "method": "ctgan",
    "sample_size": 1000,
    "epochs": 300,
    "batch_size": 500,
    "random_state": 42
})

# Set input
adapter.set_input(data=df, metadata=schema)

# Execute synthesis
adapter.run({
    "data": df,
    "metadata": schema
})

# Get results
synthetic_data, synthetic_metadata = adapter.get_result()
```

## Integration with Pipeline

```yaml
# YAML pipeline configuration
pipeline:
  - module: loader
    config:
      filepath: "data.csv"
  - module: synthesizer
    config:
      method: "ctgan"
      sample_size: 1000
      epochs: 300
```

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- Results are cached until next run() call