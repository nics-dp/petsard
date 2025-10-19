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

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/getting-started/use-cases/data-preprocessing/encoding-category.ipynb)

### Using Default Encoding

```yaml
Preprocessor:
  demo:
    method: 'default'
    # Categorical fields: Use uniform encoding
    # Numerical fields: No encoding
```

### Customizing Encoding for Specific Fields

```yaml
Preprocessor:
  custom:
    method: 'default'
    config:
      encoder:
        gender: 'encoder_onehot'       # One-Hot encoding
        education: 'encoder_label'     # Label encoding
        country: 'encoder_uniform'     # Uniform encoding
        age: None                      # No encoding for numerical field
```

### Date Encoding

```yaml
Preprocessor:
  date_encoding:
    method: 'default'
    config:
      encoder:
        created_at: 'encoder_date'
        doc_date:
          method: 'encoder_date'
          input_format: '%MinguoY-%m-%d'  # Minguo calendar format
          date_type: 'date'
```

## Available Processors

| Processor | Description | Applicable Type | Output |
|-----------|-------------|-----------------|--------|
| `encoder_uniform` | Uniform encoding | Categorical | Continuous values |
| `encoder_label` | Label encoding | Categorical | Integer |
| `encoder_onehot` | One-Hot encoding | Categorical | Multiple columns (0/1) |
| `encoder_date` | Date format conversion | Datetime | datetime |

## Processor Details

### encoder_uniform

**Uniform Encoding**: Assigns numerical ranges based on category frequency.

**Features**:
- Preserves category frequency information
- Outputs continuous values (between 0.0 and 1.0)
- High-frequency categories get larger numerical ranges

**Example**:
```yaml
config:
  encoder:
    education: 'encoder_uniform'
```

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

**Example**:
```yaml
config:
  encoder:
    gender: 'encoder_label'
```

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

**Example**:
```yaml
config:
  encoder:
    color: 'encoder_onehot'
```

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

### encoder_date

**Date Format Conversion**: Parses and standardizes datetime data.

**Parameters**:
- **input_format** (`str`, optional): Input date format
  - Default: Auto-detect
  - Supports Minguo calendar: `%MinguoY`
  
- **date_type** (`str`, optional): Output type
  - `'date'`: Date only
  - `'datetime'`: Date and time (default)
  - `'datetime_tz'`: With timezone
  
- **tz** (`str`, optional): Timezone
  - Example: `'Asia/Taipei'`
  
- **numeric_convert** (`bool`, optional): Whether to convert numeric timestamps
  - Default: `False`
  
- **invalid_handling** (`str`, optional): Invalid date handling
  - `'error'`: Raise error (default)
  - `'erase'`: Set to NA
  - `'replace'`: Use replacement rules

**Examples**:
```yaml
config:
  encoder:
    # Basic usage
    created_at: 'encoder_date'
    
    # Minguo calendar format
    doc_date:
      method: 'encoder_date'
      input_format: '%MinguoY-%m-%d'
      date_type: 'date'
    
    # With timezone
    event_time:
      method: 'encoder_date'
      date_type: 'datetime_tz'
      tz: 'Asia/Taipei'
      invalid_handling: 'erase'
```

## Processing Logic

### Categorical Encoding (Uniform/Label/OneHot)

```
Training phase (fit):
  Learn category mapping rules

Transform phase (transform):
  Convert categories to numerical values based on mapping rules

Inverse transform phase (inverse_transform):
  Restore numerical values to categories based on mapping rules
```

### Date Encoding (Date)

```
Training phase (fit):
  No training needed

Transform phase (transform):
  Parse and convert to standard date format

Inverse transform phase (inverse_transform):
  Keep date format or convert to date string
```

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
| **Date** | Standardizes date format<br/>Supports multiple inputs | Requires correct format settings | Datetime data |

## Complete Example

```yaml
Loader:
  load_data:
    filepath: 'data.csv'
    schema: 'schema.yaml'

Preprocessor:
  encode_data:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
    config:
      encoder:
        # Using different encoding methods
        gender: 'encoder_onehot'           # Binary category: One-Hot
        education: 'encoder_label'         # Ordinal category: Label
        occupation: 'encoder_uniform'      # Multi-category: Uniform
        
        # Date processing
        birth_date:
          method: 'encoder_date'
          input_format: '%MinguoY/%m/%d'
          date_type: 'date'
        
        # No encoding for numerical fields
        age: None
        income: None
```

## Notes

- **OneHot Field Count**: Creates multiple new fields based on category count
- **High Cardinality Issue**: Avoid using OneHot when category count is too high
- **Encoding Order**: Recommended to execute after outlier handling and before scaling
- **Minguo Calendar Support**: Use `%MinguoY` format marker
- **Timezone Handling**: datetime_tz type preserves timezone information
- **Restoration Accuracy**: Uniform encoding may have slight errors during restoration
- **Mutually Exclusive with discretizing**: Cannot use encoder and discretizing simultaneously

## Related Documentation

- [Processor API - fit()]({{< ref "/docs/python-api/processor-api/processor_fit" >}})
- [Processor API - transform()]({{< ref "/docs/python-api/processor-api/processor_transform" >}})
- [Processor API - inverse_transform()]({{< ref "/docs/python-api/processor-api/processor_inverse_transform" >}})
- [Scaling]({{< ref "scaling" >}})
- [Discretizing]({{< ref "discretizing" >}})