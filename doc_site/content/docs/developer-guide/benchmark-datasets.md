---
title: Benchmark Dataset Maintenance
type: docs
weight: 82
prev: docs/developer-guide/development-guidelines
---

This document explains how to maintain PETsARD's benchmark datasets.

## Storage Location

All benchmark datasets are stored in:
- **Service**: AWS S3
- **Organization**: NICS-RA (National Institute of Cyber Security)
- **Bucket**: `petsard-benchmark`

## File Verification

### SHA-256 Checksum (Reference Only)

Each dataset has a SHA-256 checksum for file integrity verification:

```python
from petsard.loader.benchmarker import digest_sha256

hasher = digest_sha256(filepath)
hash_value = hasher.hexdigest()
```

The system verifies the first seven characters of the SHA-256 hash. If verification fails, an error is thrown.

## Maintenance Process

### Adding New Datasets

1. Upload the dataset file to the S3 bucket
2. Calculate and record the SHA-256 checksum
3. Update `petsard/loader/benchmark_datasets.yaml` with:
   - Dataset name
   - Filename
   - SHA-256 hash (first 7 characters)

### Updating Existing Datasets

1. Replace the file in S3
2. Recalculate the SHA-256 checksum
3. Update the hash value in `benchmark_datasets.yaml`

## Configuration File

The `benchmark_datasets.yaml` file contains the dataset registry with SHA-256 checksums for verification.
