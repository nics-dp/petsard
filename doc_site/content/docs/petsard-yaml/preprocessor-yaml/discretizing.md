---
title: "Discretizing"
type: docs
weight: 645
prev: docs/petsard-yaml/preprocessor-yaml/scaling
next: docs/petsard-yaml/preprocessor-yaml
---

Converts continuous numerical data into discrete categories or intervals, mutually exclusive with encoding (encoder).

## Usage Examples

### Custom K-bins Parameters

```yaml
Preprocessor:
  custom:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing
    config:
      discretizing:
        age:
          method: 'discretizing_kbins'
          n_bins: 10                    # Divide into 10 bins
        income:
          method: 'discretizing_kbins'
          n_bins: 5                     # Divide into 5 bins
```

## Available Processors

| Processor | Description | Applicable Type | Output |
|-----------|-------------|-----------------|--------|
| `discretizing_kbins` | K-bins discretization | Numerical | Integer labels |
| `encoder_label` | Label encoding | Categorical | Integer labels |

**Note**: In the discretizing sequence, categorical data will automatically use `encoder_label` for encoding.

## Processor Details

### discretizing_kbins

**K-bins Discretization**: Divides continuous values into k equal-width intervals.

**Parameters**:
- **n_bins** (`int`, optional)
  - Number of bins (k value)
  - Default value: `5`
  - Example: `n_bins: 10`

**Features**:
- Equal-width binning
- Outputs integer labels (0, 1, 2, ...)
- Reduces data dimensionality and complexity

**Discretization Example**:
```
Original values: [18, 25, 35, 45, 55, 65]
n_bins = 5

Bin division:
[18-27.4) → 0
[27.4-36.8) → 1
[36.8-46.2) → 2
[46.2-55.6) → 3
[55.6-65] → 4

Discretized result: [0, 0, 1, 2, 3, 4]
```

## Processing Logic

### Numerical Data (discretizing_kbins)

- **Training phase (fit)**: Calculate and store bin boundaries
- **Transform phase (transform)**: Map values to integer labels based on bin boundaries
- **Inverse transform phase (inverse_transform)**: Restore integer labels to bin midpoint values

### Categorical Data (encoder_label)

- **Training phase (fit)**: Create mapping from categories to integers
- **Transform phase (transform)**: Convert categories to integers based on mapping
- **Inverse transform phase (inverse_transform)**: Restore integers to categories based on mapping

## Default Behavior

Default processing when using discretizing sequence:

| Data Type | Default Processor | Description |
|-----------|------------------|-------------|
| Numerical | `discretizing_kbins` | K-bins discretization (k=5) |
| Categorical | `encoder_label` | Label encoding |
| Datetime | `discretizing_kbins` | K-bins discretization (k=5) |

## Differences from encoder

| Feature | discretizing | encoder |
|---------|-------------|---------|
| **Numerical Output** | Discrete integers (0, 1, 2, ...) | Continuous values or multiple columns |
| **Use Case** | Discretization needs | General encoding needs |
| **Categorical Handling** | Label encoding | Multiple encodings (Uniform/Label/OneHot) |
| **With scaler** | Usually not used | Usually used together |
| **Sequence Position** | Must be last step | Before scaler |

## Usage Restrictions

### 1. Mutually Exclusive with encoder

```yaml
# ❌ Wrong: Cannot use both
Preprocessor:
  wrong:
    method: 'default'
    sequence:
      - missing
      - encoder       # Error!
      - discretizing  # Mutually exclusive with encoder
```

```yaml
# ✅ Correct: Use only one
Preprocessor:
  correct:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # Correct
```

### 2. Must Be Last Step

```yaml
# ❌ Wrong: Steps after discretizing
Preprocessor:
  wrong:
    method: 'default'
    sequence:
      - missing
      - discretizing
      - scaler        # Error! discretizing must be last
```

```yaml
# ✅ Correct: discretizing is the last step
Preprocessor:
  correct:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # Correct: last step
```

## Notes

- **Mutual Exclusivity**: Cannot be used with encoder simultaneously
- **Position Restriction**: Must be the last step in the sequence
- **Restoration Precision**: Restoration uses bin midpoints, won't fully restore original values
- **Number of Bins**: n_bins should be adjusted based on data range and requirements
- **Synthesizer Impact**: Some synthesizers (like PAC-Synth, DPCTGAN) may produce floating-point numbers, which the system will automatically round
- **Use Case**: Suitable for situations requiring discretized output, such as certain privacy protection algorithms
- **NA Handling**: During post-processing, NA values will be removed before restoration