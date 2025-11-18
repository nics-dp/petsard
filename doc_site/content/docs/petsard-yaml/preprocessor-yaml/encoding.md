---
title: "Encoding"
weight: 3
---

Converts categorical variables into numerical format for machine learning algorithms to process.

## Background

Most synthesis algorithms only support synthesis of numerical fields. Even when they directly support categorical field synthesis, it usually involves built-in preprocessing and post-processing transformation within the synthesizer itself. The CAPE team designed PETsARD precisely to control these unpredictable behaviors from third-party packages.

**PETsARD recommends actively encoding any fields containing categorical variables**:
- Categorical variables: Default to Uniform Encoding
- Technical details can be found in Datacebo's official documentation on [Uniform Encoding](https://datacebo.com/blog/improvement-uniform-encoder/)

## Usage Examples

Click the button below to run the complete example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_encoder.ipynb)

### Customizing Encoding for Specific Fields

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  encoding-specific:
    sequence:
      - encoder
    config:
      encoder:
        gender: 'encoder_onehot'          # One-Hot encoding
        education: 'encoder_label'        # Label encoding
        native-country: 'encoder_uniform' # Uniform encoding
        income: None                      # No encoding

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

### Time Encoding: Date Difference Calculation

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://best-practices_multi-table

Preprocessor:
  date_diff:
    sequence:
      - encoder
    config:
      encoder:
        first_apply_apply_date:
          method: 'encoder_datediff'
          baseline_date: 'established_date' # Baseline date field
          diff_unit: 'days'                 # Unit: days/weeks/months/years

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

| Processor | Description | Applicable Type | Output |
|-----------|-------------|-----------------|--------|
| `encoder_uniform` | Uniform encoding | Categorical | Continuous values |
| `encoder_label` | Label encoding | Categorical | Integer |
| `encoder_onehot` | One-Hot encoding | Categorical | Multiple columns (0/1) |
| `encoder_datediff` | Date difference calculation | Datetime | Numeric (time difference) |

## Processor Details

### encoder_uniform

**Uniform Encoding**: Assigns numerical ranges based on category frequency.

**Features**:
- Preserves category frequency information
- Outputs continuous values (between 0.0 and 1.0)
- High-frequency categories get larger numerical ranges

**Encoding Example**:
```
Original data: ['high', 'low', 'medium', 'low', 'low']
Frequency: low(60%), medium(20%), high(20%)

Encoding result:
- low → random value in 0.0-0.6
- medium → random value in 0.6-0.8
- high → random value in 0.8-1.0
```

### encoder_label

**Label Encoding**: Maps categories to consecutive integers.

**Features**:
- Simple and direct mapping
- Outputs integers (0, 1, 2, ...)
- Does not preserve order relationships between categories

**Encoding Example**:
```
Original data: ['Male', 'Female', 'Male', 'Other']

Encoding result:
- Male → 0
- Female → 1
- Other → 2
```

### encoder_onehot

**One-Hot Encoding**: Creates independent binary fields for each category.

**Features**:
- Each category becomes a new field
- Outputs multiple fields (0 or 1)
- Does not assume order relationships between categories

**Encoding Example**:
```
Original data: ['Red', 'Blue', 'Red', 'Green']

Encoding result (3 new fields):
| color_Red | color_Blue | color_Green |
|-----------|------------|-------------|
|     1     |      0     |      0      |
|     0     |      1     |      0      |
|     1     |      0     |      0      |
|     0     |      0     |      1      |
```

### encoder_datediff

**Date Difference Calculation**: Calculates time difference between target date and baseline date.

**Parameters**:
- **baseline_date** (`str`, required): Baseline date field name
- **diff_unit** (`str`, optional): Time difference unit
  - `'days'`: Days (default)
  - `'weeks'`: Weeks
  - `'months'`: Months
  - `'years'`: Years
- **absolute_value** (`bool`, optional): Whether to take absolute value
  - Default: `False`

**Features**:
- Converts absolute time to relative time
- Suitable for time series data
- Requires baseline date field

## Processing Logic

### Categorical Encoding (Uniform/Label/OneHot)

- **Training phase (fit)**: Learn category mapping rules
- **Transform phase (transform)**: Convert categories to numerical values based on mapping rules
- **Inverse transform phase (inverse_transform)**: Restore numerical values to categories based on mapping rules

### Date Difference Calculation (DateDiff)

- **Training phase (fit)**: Record baseline date field
- **Transform phase (transform)**: Calculate difference from baseline date
- **Inverse transform phase (inverse_transform)**: Restore absolute date from difference

## Default Behavior

Default encoding for different data types:

| Data Type | Default Processor | Description |
|-----------|------------------|-------------|
| Numerical | None | No encoding |
| Categorical | `encoder_uniform` | Uniform encoding |
| Datetime | None | No encoding |

## Encoding Method Comparison

| Method | Advantages | Disadvantages | Use Cases |
|--------|-----------|---------------|-----------|
| **Uniform** | Preserves frequency information<br/>Continuous values benefit synthesis | Requires sufficient samples | Default choice<br/>Synthetic data |
| **Label** | Simple and efficient<br/>Space-saving | Implies order relationship | Ordinal categories<br/>Pre-discretization |
| **OneHot** | No order assumption<br/>Clear representation | Creates many fields for high cardinality | Low cardinality categories<br/>Independent categories |
| **DateDiff** | Easy to handle relative time<br/>Suitable for time series | Requires baseline date | Event times<br/>Time series |

## Notes

- **OneHot Field Count**: Creates multiple new fields based on category count
- **High Cardinality Issue**: Avoid using OneHot when category count is too high
- **Encoding Order**: Recommended to execute after outlier handling and before scaling
- **Time Encoding**: encoder_datediff suitable for handling relative time relationships
- **Restoration Accuracy**: Uniform encoding may have slight errors during restoration
- **Mutually Exclusive with discretizing**: Cannot use encoder and discretizing simultaneously