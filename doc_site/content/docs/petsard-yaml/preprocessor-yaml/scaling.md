---
title: "Scaling"
weight: 4
---

Normalizes numerical data to a specific range or distribution to improve machine learning algorithm performance.

## Usage Examples

### Customizing Scaling for Specific Fields

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  scaling-specific:
    sequence:
      - scaler
    config:
      scaler:
        age: 'scaler_minmax'          # Min-Max scaling
        fnlwgt: 'scaler_standard'     # Standardization
        educational-num: 'scaler_log' # Log transformation
        capital-loss: None            # No scaling for categorical field

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

### Time Anchor Scaling

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  time_scaling:
    sequence:
      - scaler
    config:
      scaler:
        created_at:
          method: 'scaler_timeanchor'
          reference: 'event_time'      # Reference time field
          unit: 'D'                    # Unit: days

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

## Available Processors

| Processor | Description | Applicable Type | Output Range |
|-----------|-------------|-----------------|--------------|
| `scaler_standard` | Standardization | Numerical | Mean 0, Std 1 |
| `scaler_minmax` | Min-Max scaling | Numerical | [0, 1] |
| `scaler_zerocenter` | Zero centering | Numerical | Mean 0 |
| `scaler_log` | Log transformation | Positive values | log(x) |
| `scaler_log1p` | log(1+x) transformation | Non-negative values | log(1+x) |
| `scaler_timeanchor` | Time anchor scaling | Datetime | Time difference |

## Processor Details

### scaler_standard

**Standardization**: Transforms to a distribution with mean 0 and standard deviation 1.

**Formula**:
```
x' = (x - μ) / σ
```

**Features**:
- Preserves data distribution shape
- Eliminates scale effects
- Suitable for most machine learning algorithms

### scaler_minmax

**Min-Max Scaling**: Linear scaling to [0, 1] range.

**Formula**:
```
x' = (x - min) / (max - min)
```

**Features**:
- Preserves data distribution shape
- Fixed output range
- Sensitive to outliers

### scaler_zerocenter

**Zero Centering**: Adjusts mean to 0 while preserving original standard deviation.

**Formula**:
```
x' = x - μ
```

**Features**:
- Only adjusts position, not scale
- Preserves original data variance
- Suitable when original scale needs to be maintained

### scaler_log

**Log Transformation**: Applies logarithmic transformation to values.

**Formula**:
```
x' = log(x)
```

**Features**:
- Only applicable to positive numbers
- Compresses large values, expands small values
- Suitable for handling skewed distributions

**Note**: Data must be positive, otherwise it will produce errors.

### scaler_log1p

**log(1+x) Transformation**: A variant of log transformation suitable for data containing zeros.

**Formula**:
```
x' = log(1 + x)
```

**Features**:
- Applicable to non-negative numbers (including 0)
- Better numerical stability
- Uses exp(x') - 1 for inverse transformation

### scaler_timeanchor

**Time Anchor Scaling**: Calculates time difference from a reference time.

**Parameters**:
- **reference** (`str` or `list[str]`, required): Reference time field name(s)
  - **Single reference** (`str`): Transforms anchor field to time difference from reference field
  - **Multiple references** (`list[str]`): Keeps anchor as datetime, transforms all reference fields to time differences from anchor
- **unit** (`str`, optional): Time difference unit
  - `'D'`: Days (default)
  - `'S'`: Seconds

**Features**:
- Converts absolute time to relative time
- Supports one-to-one or one-to-many time relationships
- Suitable for multi-timepoint data (e.g., company establishment date vs. multiple application/approval dates)

**Usage Patterns**:

1. **Single Reference Mode** (one reference field)
```yaml
scaler:
  created_at:
    method: 'scaler_timeanchor'
    reference: 'event_time'  # Single reference field
    unit: 'D'
```
Result: `created_at` is transformed to day difference from `event_time` (numerical), `event_time` remains as datetime

2. **Multiple Reference Mode** (multiple reference fields)
```yaml
scaler:
  established_date:
    method: 'scaler_timeanchor'
    reference:  # Multiple reference fields (list)
      - 'first_apply_date'
      - 'approval_date'
      - 'tracking_date'
    unit: 'D'
```
Result: `established_date` remains as datetime (anchor), three reference fields are transformed to day differences from anchor (numerical)

## Processing Logic

### Statistical Scaling (Standard/MinMax/ZeroCenter)

- **Training phase (fit)**: Calculate statistical parameters (mean, standard deviation, min, max)
- **Transform phase (transform)**: Scale data using statistical parameters
- **Inverse transform phase (inverse_transform)**: Unscale using statistical parameters

### Log Transformation (Log/Log1p)

- **Training phase (fit)**: No training needed
- **Transform phase (transform)**: Apply logarithmic function
- **Inverse transform phase (inverse_transform)**: Apply exponential function

### Time Anchor (TimeAnchor)

- **Training phase (fit)**: Record reference field
- **Transform phase (transform)**: Calculate difference from reference time
- **Inverse transform phase (inverse_transform)**: Add back reference time to restore absolute time

## Default Behavior

Default scaling for different data types:

| Data Type | Default Processor | Description |
|-----------|------------------|-------------|
| Numerical | `scaler_standard` | Standardization |
| Categorical | None | No scaling |
| Datetime | `scaler_standard` | Standardization (timestamp) |

## Scaling Method Comparison

| Method | Advantages | Disadvantages | Use Cases |
|--------|-----------|---------------|-----------|
| **Standard** | Highly versatile<br/>Preserves distribution | No fixed range | Most situations<br/>Neural networks |
| **MinMax** | Fixed range<br/>Easy to understand | Sensitive to outliers | Fixed range needed<br/>Image processing |
| **ZeroCenter** | Preserves scale<br/>Simple | Doesn't change scale | Need to preserve original scale |
| **Log** | Handles skewness<br/>Compresses large values | Only for positive numbers | Income, population<br/>Right-skewed distribution |
| **Log1p** | Allows zero values<br/>Stable | Slight compression | Count data<br/>Non-negative numbers |
| **TimeAnchor** | Relative time<br/>Easy to process | Requires reference field | Time series<br/>Event times |

## Notes

- **Processing Order**: Scaling is usually the last preprocessing step (after encoding)
- **Log Limitation**: scaler_log can only be used for positive numbers, otherwise it produces NaN
- **Outlier Impact**: MinMax is sensitive to outliers, recommend handling outliers first
- **Reference Field**: TimeAnchor's reference field must exist and be datetime type
- **Restoration Accuracy**: All scaling methods can be precisely restored (within numerical precision)
- **Synthetic Data**: Scaled values of synthetic data may slightly exceed training data range
- **With discretizing**: If using discretizing, scaler is typically not needed