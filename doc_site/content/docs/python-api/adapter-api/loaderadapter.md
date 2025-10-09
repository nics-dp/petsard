---
title: "LoaderAdapter"
weight: 391
---

LoaderAdapter handles data loading and automatically processes `benchmark://` protocol for benchmark dataset and schema file downloads.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/loaderadapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: LoaderAdapter main class
> - Blue box: Core loading module
> - Purple box: Benchmark dataset handler module
> - Light pink box: Configuration classes
> - `..>`: Dependency relationship
> - `-->`: Has relationship

## Main Features

- Unified interface for data loading
- Automatic detection and handling of `benchmark://` protocol for both data and schema
- Integration of Loader and Benchmarker functionality
- Returns data and Schema metadata
- Supports CSV data files and YAML schema files

## Method Reference

### `__init__(config: dict)`

Initializes LoaderAdapter instance with automatic benchmark:// protocol handling.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - Must contain `filepath` key
  - Supports `benchmark://` protocol

### `run(input: dict)`

Executes data loading, including automatic benchmark dataset download.

**Parameters:**
- `input`: dict, required
  - Input parameter dictionary
  - LoaderAdapter typically receives empty dictionary `{}`

**Returns:**
No direct return value. Use `get_result()` and `get_metadata()` to get results.

### `get_result()`

Gets the loaded data.

**Returns:**
- `pd.DataFrame`: Loaded data

### `get_metadata()`

Gets the data's Schema metadata.

**Returns:**
- `Schema`: Data metadata

## Usage Example

```python
from petsard.adapter import LoaderAdapter

# Regular file loading
adapter = LoaderAdapter({
    "filepath": "data/users.csv",
    "schema": "schemas/user.yaml"
})

# Or using benchmark:// protocol
# adapter = LoaderAdapter({
#     "filepath": "benchmark://adult-income",
#     "schema": "benchmark://adult-income_schema"
# })

# Execute loading
adapter.run({})

# Get results
data = adapter.get_result()
metadata = adapter.get_metadata()
```

## Workflow

1. **Protocol Detection**: Check if filepath/schema uses `benchmark://` protocol
2. **Benchmarker Processing** (for benchmark protocol)
   - Download files locally
   - Verify SHA-256 (warning on mismatch)
   - Convert paths to local paths
3. **Data Loading**: Load data and metadata

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- Benchmark files are cached after first download
- Results are cached until next run() call