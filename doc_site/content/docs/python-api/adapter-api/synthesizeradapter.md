---
title: "SynthesizerAdapter"
weight: 3
---

SynthesizerAdapter handles synthetic data generation using various generative models with pipeline integration.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/synthesizeradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: SynthesizerAdapter main class
> - Blue box: Core synthesis module
> - Light pink box: LoaderAdapter used for custom data mode
> - `..>`: Dependency relationship

## Main Features

- Unified interface for synthetic data generation
- Support for multiple SDV synthesis methods (built-in methods not listed due to potential SDV version changes)
- Automatic model training and sampling
- Metadata and privacy preservation support

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

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- Results are cached until next run() call