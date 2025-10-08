---
title: "SplitterAdapter"
weight: 363
---

SplitterAdapter handles data splitting for training/validation sets with overlap control functionality.

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
  - Supports all Splitter initialization parameters
  - Keys: `num_samples`, `train_split_ratio`, `random_state`, `max_overlap_ratio`, `max_attempts`

**Internal Processing:**
1. **Configuration Validation**: Validates all splitting parameters
2. **Splitter Initialization**: Creates internal Splitter instance

### `run(input: dict)`

Executes data splitting operation.

**Parameters:**
- `input`: dict, required
  - Input parameter dictionary
  - Must contain:
    - `data`: pd.DataFrame - Dataset to split
    - `metadata`: Schema - Data metadata
    - `exist_train_indices`: list[set] (optional) - Existing training indices to avoid overlap

**Execution Flow:**
1. **Input Validation**: Validates required input parameters
2. **Data Splitting**: 
   - Performs bootstrap sampling
   - Controls overlap between samples
   - Generates training/validation splits
3. **Metadata Update**: Updates metadata for each split

**Returns:**

No direct return value. Results are stored in internal attributes:
- Use `get_result()` to get split results

### `get_result()`

Gets the splitting results.

**Returns:**
- `tuple[dict, dict, list[set]]`: 
  - Split data dictionary
  - Metadata dictionary  
  - Training indices list

### `set_input(data, metadata, exist_train_indices=None)`

Sets input data for the splitter.

**Parameters:**
- `data`: pd.DataFrame - Dataset to split
- `metadata`: Schema - Data metadata
- `exist_train_indices`: list[set] (optional) - Existing training indices

## Usage Examples

### Basic Splitting

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

### Overlap Control

```python
# Configure with overlap control
adapter = SplitterAdapter({
    "num_samples": 5,
    "train_split_ratio": 0.7,
    "max_overlap_ratio": 0.1,  # Max 10% overlap
    "max_attempts": 50
})

# Set input with existing indices
adapter.set_input(
    data=df,
    metadata=schema,
    exist_train_indices=existing_indices
)

# Execute
adapter.run({
    "data": df,
    "metadata": schema,
    "exist_train_indices": existing_indices
})
```

### Error Handling

```python
try:
    adapter = SplitterAdapter(config)
    adapter.run(input_dict)
except ConfigError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Splitting failed: {e}")
```

## Workflow

1. **Configuration**: Initialize with splitting parameters
2. **Input Setting**: Provide data, metadata, and optional existing indices
3. **Splitting Execution**: Perform bootstrap sampling with overlap control
4. **Result Retrieval**: Get split data, metadata, and indices

## Integration with Pipeline

```yaml
# YAML pipeline configuration
pipeline:
  - module: loader
    config:
      filepath: "data.csv"
  - module: splitter
    config:
      num_samples: 5
      train_split_ratio: 0.8
      max_overlap_ratio: 0.0
  - module: synthesizer
    config:
      method: "ctgan"
```

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- Sample numbering starts from 1, not 0
- `max_overlap_ratio=0.0` ensures completely non-overlapping samples
- Bootstrap sampling may fail if overlap constraints are too strict
- Metadata is automatically updated with split information
- Results are cached until next run() call