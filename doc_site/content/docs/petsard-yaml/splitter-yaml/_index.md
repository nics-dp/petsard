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

- **max_overlap_ratio** (`float`, optional)
  - Maximum allowed overlap ratio between samples
  - Default: 1.0 (allows complete overlap)

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
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
```

### Strict Overlap Control

```yaml
Splitter:
  strict_overlap:
    num_samples: 5
    train_split_ratio: 0.7
    max_overlap_ratio: 0.1  # Maximum 10% overlap
    max_attempts: 50
    random_state: 42
```

### No Overlap Splitting

```yaml
Splitter:
  no_overlap:
    num_samples: 4
    train_split_ratio: 0.75
    max_overlap_ratio: 0.0  # Completely non-overlapping
    max_attempts: 100
    random_state: "reproducible"
```

### Complete Pipeline Example

```yaml
# Complete experiment pipeline
Loader:
  load_data:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml

Splitter:
  split_data:
    num_samples: 5
    train_split_ratio: 0.8
    max_overlap_ratio: 0.0  # No overlap for privacy evaluation
    random_state: 12345

Synthesizer:
  generate_synthetic:
    method: ctgan
    epochs: 100

Evaluator:
  privacy_evaluation:
    metrics: ["anonymeter"]
  utility_evaluation:
    metrics: ["correlation", "ks_test"]
```

## Use Cases

### Privacy Evaluation

For privacy evaluation tasks like Anonymeter, use non-overlapping splits:

```yaml
Splitter:
  privacy_split:
    num_samples: 5
    train_split_ratio: 0.8
    max_overlap_ratio: 0.0  # Ensure sample independence
    random_state: 12345
```

### Cross-Validation

Controlled overlap for statistical validation:

```yaml
Splitter:
  cross_validation:
    num_samples: 10
    train_split_ratio: 0.7
    max_overlap_ratio: 0.3  # Allow 30% overlap
    random_state: "cross_val"
```

### Imbalanced Datasets

For imbalanced datasets, use larger sample sizes:

```yaml
Splitter:
  imbalanced_data:
    num_samples: 20
    train_split_ratio: 0.85
    max_overlap_ratio: 0.5
    max_attempts: 50
```

## Related Documentation

- **Bootstrap Sampling**: Splitter uses bootstrap sampling to generate multiple train/validation splits.
- **Overlap Control**: The `max_overlap_ratio` parameter precisely controls the degree of overlap between samples.
- **Sample Independence**: Privacy evaluation tasks typically require `max_overlap_ratio: 0.0` to ensure complete sample independence.

## Execution Notes

- Experiment names (second level) can be freely named, descriptive names are recommended
- Multiple split experiments can be defined and will be executed sequentially
- Split results are passed to the next module (e.g., Synthesizer)
- Sample numbering starts from 1 (not 0)

## Important Notes

- Setting `max_overlap_ratio` to 0.0 ensures completely non-overlapping samples
- Overly strict overlap constraints may cause sampling failures, adjust `max_attempts` accordingly
- For small datasets, use lower `max_overlap_ratio` to ensure diversity
- Always set `random_state` for reproducible results
- For imbalanced data, increase `num_samples` for better representation