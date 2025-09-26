---
title: "Benchmarker API"
weight: 390
---

## Overview

The Benchmarker module provides download and management functionality for benchmark datasets. Through the `benchmark://` protocol, predefined benchmark datasets can be conveniently accessed.

## Architecture

{{< mermaid-file file="content/docs/python-api/benchmarker-api/benchmarker-class-diagram.mmd" >}}

> **Legend:**
> - Purple box: Configuration classes (BenchmarkerConfig)
> - Light blue box: Request handler classes (BenchmarkerRequests)
> - Light red box: Exception classes (BenchmarkDatasetsError)
> - Yellow box: Class annotation notes
> - `-->`: Composition relationship
> - `..>`: Dependency relationship

## Main Classes

### BenchmarkerConfig

Handles configuration management for benchmark datasets.

```python
from petsard.loader.benchmarker import BenchmarkerConfig

config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)
```

#### Attributes

- `benchmark_name`: Benchmark dataset name
- `filepath_raw`: Raw file path (benchmark:// protocol)
- `benchmark_filename`: Local filename

### BenchmarkerRequests

Responsible for downloading benchmark datasets from remote sources.

```python
from petsard.loader.benchmarker import BenchmarkerRequests

downloader = BenchmarkerRequests(config.get_benchmarker_config())
downloader.download()
```

## Workflow

1. **Protocol Parsing**: Parse `benchmark://` protocol
2. **Configuration Creation**: Create configuration based on dataset name
3. **Data Download**: Download dataset from remote source
4. **Local Storage**: Save to `benchmark/` directory

## Error Handling

- **BenchmarkDatasetsError**
  - Thrown when download fails
  - Thrown when dataset doesn't exist
  - Thrown on network connection issues

## Important Notes

- Datasets are cached locally in `benchmark/` directory after download
- First use requires network connection
- Recommended to use through LoaderAdapter rather than direct calls
- Using YAML configuration files is the recommended approach