---
title: "LoaderAdapter"
weight: 391
---

LoaderAdapter handles data loading and automatically processes `benchmark://` protocol for benchmark dataset downloads.

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
- Automatic detection and handling of `benchmark://` protocol
- Integration of Loader and Benchmarker functionality
- Returns data and Schema metadata

## Method Reference

### `__init__(config: dict)`

Initializes LoaderAdapter instance with automatic benchmark:// protocol handling.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - Must contain `filepath` key
  - Supports `benchmark://` protocol

**Internal Processing:**
1. **Protocol Detection**: Checks if filepath uses `benchmark://` protocol
2. **Benchmarker Configuration**: Creates BenchmarkerConfig for benchmark protocol
3. **Path Conversion**: Converts benchmark:// path to local path
4. **Loader Initialization**: Creates Loader instance with processed configuration

### `run(input: dict)`

Executes data loading, including automatic benchmark dataset download.

**Parameters:**
- `input`: dict, required
  - Input parameter dictionary
  - LoaderAdapter typically receives empty dictionary `{}`

**Execution Flow:**
1. **Benchmark Processing** (if using benchmark:// protocol)
   - Downloads benchmark dataset
   - Saves to local `benchmark/` directory
   
2. **Data Loading**
   - Calls internal Loader instance's load() method
   - Loads data and obtains Schema metadata

**Returns:**

No direct return value. Data is stored in internal attributes:
- Use `get_result()` to get data
- Use `get_metadata()` to get metadata

### `get_result()`

Gets the loaded data.

**Returns:**
- `pd.DataFrame`: Loaded data

### `get_metadata()`

Gets the data's Schema metadata.

**Returns:**
- `Schema`: Data metadata

## Usage Examples

### Basic Loading

```python
from petsard.adapter import LoaderAdapter

# Regular file loading
adapter = LoaderAdapter({
    "filepath": "data/users.csv",
    "schema": "schemas/user.yaml"
})

# Execute loading
adapter.run({})

# Get results
data = adapter.get_result()
metadata = adapter.get_metadata()
```

### Benchmark Dataset Loading

```python
# Using benchmark:// protocol
adapter = LoaderAdapter({
    "filepath": "benchmark://adult-income",
    "schema": "schemas/adult-income.yaml"
})

# Automatically download and load
adapter.run({})
data = adapter.get_result()
metadata = adapter.get_metadata()
```

### Error Handling

```python
try:
    adapter = LoaderAdapter(config)
    adapter.run({})
except BenchmarkDatasetsError as e:
    print(f"Failed to download benchmark dataset: {e}")
except Exception as e:
    print(f"Loading failed: {e}")
```

## Supported Benchmark Datasets

Currently supports the following benchmark datasets:

- `benchmark://adult-income` - UCI Adult Income dataset

## Workflow

1. **Protocol Detection**: Check if using `benchmark://` protocol
2. **Benchmarker Processing** (for benchmark protocol)
   - Create BenchmarkerConfig
   - Download dataset locally
   - Convert path to local path
3. **Loader Initialization**: Create Loader with processed configuration
4. **Data Loading**: Call Loader.load() to load data

## Notes

- This is an internal API, not recommended for direct use
- Prefer using YAML configuration files and Executor
- benchmark:// protocol is case-insensitive
- Datasets are downloaded to `benchmark/` directory
- First use requires network connection
- Benchmark datasets are cached after first download
- Large dataset downloads may take considerable time
- `method` parameter is deprecated and will be automatically removed