---
title: "SplitterAdapter"
weight: 2
---

SplitterAdapter handles data splitting for training/validation sets with overlap control functionality.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/splitteradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: SplitterAdapter main class
> - Blue box: Core splitting module
> - Light pink box: LoaderAdapter used for custom data mode
> - `..>`: Dependency relationship

## Main Features

- Unified interface for data splitting
- Bootstrap sampling with overlap control
- Support for multiple sample generation
- Returns split data, metadata, and training indices
- Integration with pipeline system

## Method Reference

### `__init__(config: dict)`

Initializes SplitterAdapter instance with splitting configuration.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - Keys: `num_samples`, `train_split_ratio`, `random_state`, `max_overlap_ratio`, `max_attempts`

### `run(input: dict)`

Executes data splitting operation.

**Parameters:**
- `input`: dict, required
  - Must contain:
    - `data`: pd.DataFrame - Dataset to split
    - `metadata`: Schema - Data metadata
    - `exist_train_indices`: list[set] (optional) - Existing training indices to avoid overlap

**Returns:**
No direct return value. Use `get_result()` to get split results.

### `get_result()`

Gets the splitting results.

**Returns:**
- `tuple[dict, dict, list[set]]`: Split data, metadata, and training indices

### `set_input(data, metadata, exist_train_indices=None)`

Sets input data for the splitter.

**Parameters:**
- `data`: pd.DataFrame - Dataset to split
- `metadata`: Schema - Data metadata
- `exist_train_indices`: list[set] (optional) - Existing training indices

## Usage Example

```python
from petsard.adapter import SplitterAdapter

# Configure splitter
adapter = SplitterAdapter({
    "num_samples": 3,
    "train_split_ratio": 0.8,
    "random_state": 42
})

# Set input
adapter.set_input(data=df, metadata=schema)

# Execute splitting
adapter.run({
    "data": df,
    "metadata": schema
})

# Get results
split_data, metadata_dict, train_indices = adapter.get_result()
```

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- Sample numbering starts from 1, not 0
- Results are cached until next run() call