---
title: "Processor API"
weight: 330
---

Data processing module supporting both preprocessing and postprocessing operations.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/processor-api/processor-class-diagram.mmd" >}}

> **Legend:**
> - Blue boxes: Main classes
> - Orange boxes: Sub-processor classes
> - Light purple boxes: Configuration and data classes
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

### Preprocessing

```python
from petsard import Processor

# Create processor
processor = Processor(metadata=schema)

# Fit and transform data
processor.fit(data)
processed_data = processor.transform(data)
```

### Postprocessing

```python
# Use the same processor instance for postprocessing
restored_data = processor.inverse_transform(synthetic_data)
```

### Complete Workflow

```python
from petsard import Loader, Processor, Synthesizer

# 1. Load data
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 2. Preprocessing
processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# 3. Synthesize data
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data)
synthetic_data = synthesizer.data_syn

# 4. Postprocessing (restoration)
restored_data = processor.inverse_transform(synthetic_data)
```

## Constructor (__init__)

Initialize a data processor instance.

### Syntax

```python
def __init__(
    metadata: Schema,
    config: dict = None
)
```

### Parameters

- **metadata** : Schema, required
    - Data structure definition (Schema object)
    - Required parameter
    - Provides metadata and type information for data fields

- **config** : dict, optional
    - Custom data processing configuration
    - Default: `None`
    - Used to override default processing procedures
    - Structure: `{processor_type: {field_name: processing_method}}`

### Returns

- **Processor**
    - Initialized processor instance

### Usage Examples

```python
from petsard import Loader, Processor

# Load data and schema
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# Basic usage - use default configuration
processor = Processor(metadata=schema)

# Use custom configuration
custom_config = {
    'missing': {
        'age': 'missing_mean',
        'income': 'missing_median'
    },
    'outlier': {
        'age': 'outlier_zscore',
        'income': 'outlier_iqr'
    },
    'encoder': {
        'gender': 'encoder_onehot',
        'education': 'encoder_label'
    },
    'scaler': {
        'age': 'scaler_minmax',
        'income': 'scaler_standard'
    }
}
processor = Processor(metadata=schema, config=custom_config)
```

## Processing Sequence

Processor supports the following processing steps:

1. **missing**: Missing value handling
2. **outlier**: Outlier detection and handling
3. **encoder**: Categorical variable encoding
4. **scaler**: Numerical normalization
5. **discretizing**: Discretization (mutually exclusive with encoder)

Default sequence: `['missing', 'outlier', 'encoder', 'scaler']`

## Default Processing Methods

| Processor Type | Numerical | Categorical | Datetime |
|---------------|-----------|-------------|----------|
| **missing** | `MissingMean` | `MissingDrop` | `MissingDrop` |
| **outlier** | `OutlierIQR` | None | `OutlierIQR` |
| **encoder** | None | `EncoderUniform` | None |
| **scaler** | `ScalerStandard` | None | `ScalerStandard` |
| **discretizing** | `DiscretizingKBins` | `EncoderLabel` | `DiscretizingKBins` |

## Preprocessing vs Postprocessing

| Operation | Preprocessing Method | Postprocessing Method | Description |
|-----------|---------------------|----------------------|-------------|
| Training | `fit()` | - | Learn data statistics |
| Transform | `transform()` | - | Apply preprocessing transformations |
| Restore | - | `inverse_transform()` | Apply postprocessing restoration |

**Note**: Preprocessing and postprocessing use the same Processor instance to ensure transformation consistency.

## Available Processors

### Missing Value Processors

- `missing_mean`: Fill with mean value
- `missing_median`: Fill with median value
- `missing_mode`: Fill with mode value
- `missing_simple`: Fill with specified value
- `missing_drop`: Drop rows with missing values

### Outlier Processors

- `outlier_zscore`: Z-Score method (threshold 3)
- `outlier_iqr`: Interquartile Range method (1.5 IQR)
- `outlier_isolationforest`: Isolation Forest algorithm
- `outlier_lof`: Local Outlier Factor algorithm

### Encoders

- `encoder_uniform`: Uniform encoding (allocate range by frequency)
- `encoder_label`: Label encoding (integer mapping)
- `encoder_onehot`: One-Hot encoding
- `encoder_date`: Date format conversion

### Scalers

- `scaler_standard`: Standardization (mean 0, std 1)
- `scaler_minmax`: Min-Max scaling (range [0, 1])
- `scaler_zerocenter`: Zero centering (mean 0)
- `scaler_log`: Logarithmic transformation
- `scaler_log1p`: log(1+x) transformation
- `scaler_timeanchor`: Time anchor scaling
  - **Single reference mode** (`reference: str`): Transform anchor field to time difference from reference field
  - **Multiple reference mode** (`reference: list[str]`): Keep anchor field as datetime, transform multiple reference fields to time differences from anchor
  - Supported time units: `'D'` (days) or `'S'` (seconds)

### Discretization

- `discretizing_kbins`: K-bins discretization

## Notes

- **Recommended Practice**: Use YAML configuration files instead of direct Python API usage
- **Processing Order**:
  - Preprocessing: Must call `fit()` before `transform()`
  - Postprocessing: Must complete preprocessing before calling `inverse_transform()`
- **Sequence Constraints**:
  - `discretizing` and `encoder` cannot be used together
  - `discretizing` must be the last step in the sequence
  - Maximum of 4 processing steps supported
- **Global Transformation**: Some processors (e.g., `outlier_isolationforest`, `outlier_lof`) apply to all fields
- **Instance Reuse**: Preprocessing and postprocessing should use the same Processor instance
- **Schema Usage**: Recommended to use Schema for defining data structure. See Metadater API documentation for detailed settings
- **Documentation Note**: This documentation is for internal development team reference only and does not guarantee backward compatibility