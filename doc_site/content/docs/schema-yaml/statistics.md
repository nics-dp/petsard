---
title: "Statistics"
weight: 6
---

When `enable_stats: true` is set, the system automatically calculates and records field statistics for data quality analysis, synthetic data validation, and feature understanding. For large datasets (over 1 million rows), calculations can be time-consuming; use with caution.

## Enable Statistics

### Global Setting

```yaml
id: my_schema
enable_stats: true  # Enable globally
attributes:
  age:
    type: int
```

### Per-field Setting

```yaml
attributes:
  age:
    type: int
    enable_stats: true   # Enable
  notes:
    type: str
    enable_stats: false  # Disable
```

## Statistical Items

### Common Statistics (All Fields)

| Item | Description |
|------|-------------|
| `row_count` | Total row count |
| `na_count` | Null value count |
| `na_percentage` | Null value percentage |
| `detected_type` | Detected data type |
| `actual_dtype` | pandas dtype |

### Numeric Statistics

Calculated only when `type` is `int` or `float` and `category: false`:

| Item | Description |
|------|-------------|
| `mean` | Mean value |
| `std` | Standard deviation |
| `min` | Minimum value |
| `max` | Maximum value |
| `median` | Median |
| `q1` | First quartile |
| `q3` | Third quartile |

### Categorical Statistics

Calculated only when `category: true`:

| Item | Description |
|------|-------------|
| `unique_count` | Unique value count |
| `mode` | Mode (most frequent value) |
| `mode_frequency` | Mode frequency |
| `category_distribution` | Category distribution (max 20) |

## Statistics Structure

```yaml
attributes:
  age:
    type: int
    enable_stats: true
    stats:
      row_count: 1000
      na_count: 50
      na_percentage: 0.05
      mean: 35.5
      std: 12.3
      min: 18
      max: 85
      median: 34.0
      q1: 27.0
      q3: 43.0