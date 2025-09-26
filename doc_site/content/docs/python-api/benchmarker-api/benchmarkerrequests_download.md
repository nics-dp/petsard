---
title: "download()"
weight: 331
---

Downloads the specified benchmark dataset to local storage.

## Syntax

```python
def download() -> None
```

## Description

The `download()` method downloads the specified benchmark dataset from AWS S3 bucket and saves it to the local `benchmark/` directory. The download process includes integrity verification.

## Returns

No return value. The dataset is saved in the `benchmark/` directory after download.

## Basic Example

```python
from petsard.loader.benchmarker import BenchmarkerConfig, BenchmarkerRequests

# Create configuration
config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)

# Create downloader and execute download
downloader = BenchmarkerRequests(config.get_benchmarker_config())
downloader.download()
```

## Download Process

1. **Check local cache**: Check if the dataset already exists in `benchmark/` directory
2. **Create directory**: Create `benchmark/` directory if it doesn't exist
3. **Download data**: Download dataset from AWS S3
4. **Verify integrity**: Verify downloaded data using SHA256
5. **Save file**: Save data to local storage

## Error Handling

```python
from petsard.exceptions import BenchmarkDatasetsError

try:
    downloader.download()
except BenchmarkDatasetsError as e:
    print(f"Download failed: {e}")
```

Possible error causes:
- Network connection failure
- Dataset does not exist
- SHA256 verification failure
- Insufficient disk space

## Notes

- First download requires network connection
- Datasets are cached locally, repeated downloads are skipped
- Large dataset downloads may take considerable time
- Recommended to use indirectly through LoaderAdapter rather than direct calls