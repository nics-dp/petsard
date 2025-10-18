---
title: "Benchmarker API"
weight: 315
---

## Overview

The Benchmarker module provides download and management functionality for benchmark datasets and their schema files. Through the `benchmark://` protocol, predefined benchmark datasets and YAML schema files can be conveniently accessed.

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

Handles configuration management for benchmark datasets and schema files.

```python
from petsard.loader.benchmarker import BenchmarkerConfig

# For data files
config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)

# For schema files
schema_config = BenchmarkerConfig(
    benchmark_name="adult-income_schema",
    filepath_raw="benchmark://adult-income_schema"
)
```

#### Attributes

- `benchmark_name`: Benchmark dataset or schema name
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
2. **Configuration Creation**: Create configuration based on dataset/schema name
3. **Data Download**: Download dataset or schema from remote source
4. **SHA-256 Verification**: Verify file integrity (logs warning on mismatch, doesn't block)
5. **Local Storage**: Save to `benchmark/` directory

## Error Handling

- **BenchmarkDatasetsError**
  - Thrown when download fails
  - Thrown when dataset doesn't exist
  - Thrown on network connection issues
- **SHA-256 Verification**
  - Logs warning on mismatch (doesn't block execution)
  - Allows using modified local files for development

## Important Notes

- Datasets and schema files are cached locally in `benchmark/` directory after download
- First use requires network connection
- Recommended to use through LoaderAdapter rather than direct calls
- Using YAML configuration files is the recommended approach
- Supports both CSV data files and YAML schema files
- SHA-256 verification failures log warnings but don't block execution (as of v2.0.0)