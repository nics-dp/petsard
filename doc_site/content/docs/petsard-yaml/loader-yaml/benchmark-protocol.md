---
title: "benchmark://"
weight: 112
---

Loader supports using the `benchmark://` protocol to automatically download and load benchmark datasets.

## Protocol Format

```yaml
Loader:
  experiment_name:
    filepath: benchmark://dataset-name
```

## Usage Examples

### Loading Adult Income Dataset

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
```

### Using with Schema

```yaml
Loader:
  load_with_schema:
    filepath: benchmark://adult-income
    schema: schemas/adult-income.yaml
```

## Available Benchmark Datasets

### Demographic Datasets

| Dataset Name | Protocol Path | Description |
|-------------|---------------|-------------|
| Adult Income | `benchmark://adult-income` | UCI Adult Income census dataset (48,842 rows, 15 columns) |
| Adult Income (Original) | `benchmark://adult-income_ori` | Original training data (for demo) |
| Adult Income (Control) | `benchmark://adult-income_control` | Control group data (for demo) |
| Adult Income (Synthetic) | `benchmark://adult-income_syn` | SDV Gaussian Copula synthetic data (for demo) |

### Best Practices Sample Datasets

| Dataset Name | Protocol Path | Description |
|-------------|---------------|-------------|
| Multi-table Companies | `benchmark://best-practices_multi-table_companies` | Multi-table example - Company data |
| Multi-table Applications | `benchmark://best-practices_multi-table_applications` | Multi-table example - Application data |
| Multi-table Tracking | `benchmark://best-practices_multi-table_tracking` | Multi-table example - Tracking data |
| Multi-timestamp | `benchmark://best-practices_multi-table` | Multi-timestamp example data |
| Categorical & High-cardinality | `benchmark://best-practices_categorical_high-cardinality` | Categorical and high-cardinality example data |

## Complete Pipeline Example

```yaml
---
Loader:
  # Using benchmark dataset
  benchmark:
    filepath: benchmark://adult-income
    
Preprocessor:
  preprocess:
    method: default
    
Synthesizer:
  synthesize:
    method: sdv-single-table
    model: gaussian_copula
    
Postprocessor:
  postprocess:
    method: default
    
Evaluator:
  quality_report:
    method: sdmetrics-qualityreport
    
Reporter:
  save_synthetic:
    method: save_data
    output_path: output/synthetic_adult.csv
  save_report:
    method: save_report
    granularity: global
...
```

## How It Works

1. **Protocol Detection**: Loader detects `benchmark://` protocol
2. **Automatic Download**: Downloads dataset from AWS S3 bucket
3. **Integrity Check**: Verifies data integrity using SHA256
4. **Local Cache**: Data is stored in `benchmark/` directory
5. **Data Loading**: Loads data using local path

## When to Use

Benchmark datasets are suitable for:

- **Testing New Algorithms**: Test on data with known characteristics
- **Parameter Tuning**: Compare effects of different parameter settings
- **Performance Benchmarking**: Compare with academic research results
- **Teaching Demonstrations**: Provide standardized example data

## Notes

- First use requires network connection to download data
- Datasets are cached locally in `benchmark/` directory
- Large dataset downloads may take considerable time
- Protocol names are case-insensitive (lowercase recommended)
- All datasets are verified with SHA256 to ensure integrity