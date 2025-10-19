---
title: "Preprocessor YAML (WIP)"
weight: 130
---

YAML configuration file format for the Preprocessor module, used for data preprocessing.

## Usage Examples

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor-yaml.ipynb)

### Using Default Preprocessing

```yaml
Preprocessor:
  demo:
    method: 'default'
```

### Using Custom Processing Sequence

```yaml
Preprocessor:
  custom:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
```

### Customizing Processors for Specific Fields

```yaml
Preprocessor:
  custom_fields:
    method: 'default'
    config:
      missing:
        age: 'missing_mean'
        income: 'missing_median'
      outlier:
        age: 'outlier_zscore'
        income: 'outlier_iqr'
      encoder:
        gender: 'encoder_onehot'
        education: 'encoder_label'
      scaler:
        age: 'scaler_minmax'
        income: 'scaler_standard'
```

## Main Parameters

- **method** (`string`, required)
  - Preprocessing method
  - Available values: `'default'` (default processing sequence)

- **sequence** (`list`, optional)
  - Custom processing sequence
  - Available values: `'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`
  - Default value: `['missing', 'outlier', 'encoder', 'scaler']`

- **config** (`dict`, optional)
  - Custom processor configuration for each field
  - Structure: `{processing_type: {field_name: processing_method}}`

## Processing Sequence

Preprocessor supports the following processing steps, executed in order:

1. **[missing]({{< ref "missing-handling" >}})**: Missing value handling
2. **[outlier]({{< ref "outlier-handling" >}})**: Outlier handling
3. **[encoder]({{< ref "encoding" >}})**: Categorical variable encoding
4. **[scaler]({{< ref "scaling" >}})**: Numerical normalization
5. **[discretizing]({{< ref "discretizing" >}})**: Discretization (mutually exclusive with encoder)

## Default Processing Methods

| Processing Type | Numerical | Categorical | Datetime |
|-----------------|-----------|-------------|----------|
| **missing** | `missing_mean` | `missing_drop` | `missing_drop` |
| **outlier** | `outlier_iqr` | None | `outlier_iqr` |
| **encoder** | None | `encoder_uniform` | None |
| **scaler** | `scaler_standard` | None | `scaler_standard` |
| **discretizing** | `discretizing_kbins` | `encoder_label` | `discretizing_kbins` |

## Feature Documentation

For detailed processor descriptions, please refer to each feature page:

- [Missing Value Handling]({{< ref "missing-handling" >}})
- [Outlier Handling]({{< ref "outlier-handling" >}})
- [Encoding]({{< ref "encoding" >}})
- [Scaling]({{< ref "scaling" >}})
- [Discretizing]({{< ref "discretizing" >}})

## Precision Preservation

Preprocessor automatically preserves the precision of numerical fields:

- **Precision Retention**: The `type_attr.precision` in the schema will not be changed during transformation
- **Automatic Application**: Rounding is automatically applied according to precision after transformation
- **Memory Mechanism**: Precision information is recorded in Status for use by subsequent modules

## Execution Instructions

- Experiment names (second level) can be freely named; descriptive names are recommended
- Multiple experiments can be defined and will be executed sequentially
- Preprocessing results are passed to the Synthesizer module

## Notes

- `discretizing` and `encoder` cannot be used simultaneously
- `discretizing` must be the last step in the sequence
- Some outlier handlers (such as `outlier_isolationforest`, `outlier_lof`) are global transformations and will be applied to all fields
- Custom config will override default settings
- Precision is automatically applied after preprocessing transformation to ensure numerical consistency
- For detailed processor parameter settings, please refer to each feature page and the Processor API documentation