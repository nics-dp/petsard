---
title: "Synthesizer API"
weight: 340
---

Synthetic data generation module supporting multiple synthesis methods and providing data generation capabilities.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/synthesizer-api/synthesizer-class-diagram.mmd" >}}

> **Legend:**
> - Blue boxes: Main classes
> - Orange boxes: Subclass implementations
> - Light purple boxes: Configuration and data classes
> - `<|--`: Inheritance relationship
> - `*--`: Composition relationship
> - `..>`: Dependency relationship

## Basic Usage

```python
from petsard import Synthesizer

# Use default method (SDV GaussianCopula)
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df)
synthetic_data = synthesizer.data_syn

# Use specific SDV method
synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df, sample_num_rows=1000)
```

## Constructor (__init__)

Initialize a synthetic data generator instance.

### Syntax

```python
def __init__(
    method: str,
    **kwargs
)
```

### Parameters

- **method** : str, required
    - Synthesis method name
    - Required parameter
    - Supported methods:
        - `'default'`: Use SDV-GaussianCopula
        - `'sdv-single_table-{method}'`: Use SDV provided methods
            - `'copulagan'`: CopulaGAN generative model
            - `'ctgan'`: CTGAN generative model
            - `'gaussiancopula'`: Gaussian copula model
            - `'tvae'`: TVAE generative model
        - `'custom_method'`: Custom synthesis method (requires additional parameters)

- **kwargs** : dict, optional
    - Additional parameters passed to specific synthesizers
    - Custom methods require:
        - `module_path`: Custom module path
        - `class_name`: Custom class name

### Returns

- **Synthesizer**
    - Initialized synthesizer instance

### Usage Examples

```python
from petsard import Synthesizer

# Use default method
synthesizer = Synthesizer(method='default')

# Use SDV CTGAN
synthesizer = Synthesizer(method='sdv-single_table-ctgan')

# Use SDV GaussianCopula with parameters
synthesizer = Synthesizer(
    method='sdv-single_table-gaussiancopula',
    default_distribution='truncnorm'
)

# Use custom synthesizer
synthesizer = Synthesizer(
    method='custom_method',
    module_path='custom_synthesis.py',
    class_name='MySynthesizer'
)
```

## Default Parameters

All SDV synthesizers are initialized with the following default parameters to ensure numerical precision:

- **`enforce_rounding=True`**: Applied to all SDV synthesizer types to maintain integer precision for numerical columns
- **`enforce_min_max_values=True`**: Applied only to TVAE and GaussianCopula synthesizers to enforce value bounds

## Precision Rounding

All synthesizers automatically apply precision rounding based on schema metadata. When precision is specified in the schema (either v1.0 or v2.0 format), the synthesizer will round generated values to the specified decimal places.

This feature ensures synthetic data maintains the same numerical precision as the original data, which is critical for:
- Financial data (prices, amounts)
- Scientific measurements
- Statistical reporting
- Any precision-sensitive applications

## Notes

- **custom_data method**: The `'custom_data'` method is for loading external synthetic data, handled at the framework level without synthesizer instantiation
- **Best practice**: Use YAML configuration files instead of direct Python API
- **Method call order**: Must call `create()` before `fit()` or `fit_sample()`
- **Data output**: Generated synthetic data is stored in the `data_syn` attribute
- **Documentation**: This documentation is for internal development team reference only, backward compatibility is not guaranteed
- **Schema usage**: Recommend using SchemaMetadata to define data structure, see Metadater API documentation for detailed configuration