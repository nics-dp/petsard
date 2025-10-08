---
title: "Splitter YAML"
weight: 120
---

YAML configuration format for the Splitter module.

## Main Parameters

- **num_samples** (`integer`, optional)
  - Number of times to resample the data
  - Default: 1

- **train_split_ratio** (`float`, optional)
  - Ratio of data for training set
  - Default: 0.8

## Parameter Details

### Required Parameters

Splitter has no required parameters, all parameters are optional.

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `num_samples` | `integer` | `1` | Number of times to resample | `5` |
| `train_split_ratio` | `float` | `0.8` | Ratio of data for training set (0.0 to 1.0) | `0.7` |
| `random_state` | `integer\|string` | `null` | Seed for reproducibility | `42` or `"exp_v1"` |
| `max_overlap_ratio` | `float` | `1.0` | Maximum overlap ratio between samples (0.0 to 1.0) | `0.1` |
| `max_attempts` | `integer` | `30` | Maximum attempts for sampling with overlap control | `50` |

## Usage Examples

### Basic Splitting

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
```

### Controlled Overlap

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  controlled_overlap:
    num_samples: 10
    train_split_ratio: 0.8
    max_overlap_ratio: 0.8  # Allow 80% overlap
    max_attempts: 500
    random_state: 42
```

### No Overlap Splitting

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  no_overlap:
    num_samples: 2
    train_split_ratio: 0.01
    max_overlap_ratio: 0.0  # Completely non-overlapping
    max_attempts: 100000
    random_state: 42
```

{{< callout type="warning" >}}
**Note**: This example demonstrates the no-overlap configuration. Since this package uses a sampling-then-comparison algorithm, achieving complete non-overlap (`max_overlap_ratio: 0.0`) is extremely difficult. This feature aims to provide sampling diversity. In practice, we recommend allowing minimal overlap (e.g., `max_overlap_ratio: 0.8`) to ensure execution efficiency.
{{< /callout >}}

## Use Cases

The Splitter module is primarily designed to meet the requirements of the Evaluator module for splitting datasets into training and test sets. For detailed post-split evaluation configuration, please refer to the Evaluator YAML documentation.

## Related Documentation

- **Bootstrap Sampling**: Splitter uses bootstrap sampling to generate multiple train/validation splits.
- **Overlap Control**: The `max_overlap_ratio` parameter precisely controls the degree of overlap between samples.
- **Sample Independence**: For more complete experimental split testing, you can set `max_overlap_ratio` based on `train_split_ratio` (e.g., `train_split_ratio: 0.8` can use `max_overlap_ratio: 0.8`).

## Execution Notes

- Multiple split experiments can be defined and will be executed sequentially
- Split results are passed to the next module (e.g., Synthesizer)
- Sample numbering starts from 1 (not 0)

## Important Notes

- Overly strict overlap constraints may cause sampling failures, adjust `max_attempts` accordingly
- Set `random_state` for reproducible results