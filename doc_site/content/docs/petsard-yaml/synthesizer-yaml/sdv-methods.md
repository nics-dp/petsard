---
title: "SDV Methods"
type: docs
weight: 655
prev: docs/petsard-yaml/synthesizer-yaml/sdv-custom-methods
next: docs/petsard-yaml/synthesizer-yaml
---

PETsARD integrates the [SDV (Synthetic Data Vault)](https://sdv.dev/) package, providing various advanced synthetic data generation algorithms.

{{< callout type="warning" >}}
**Optional Feature Notice**

The SDV methods described on this page are **optional features**, provided for reference only.

**Usage Requirements**:
1. Requires separate installation: `pip install 'sdv>=1.26.0,<2'`
2. Please verify that SDV's license terms suit your use case
3. **Not recommended**: We suggest prioritizing the built-in `petsard-gaussian_copula`

**Alternatives**:
- [PETsARD Gaussian Copula](../petsard-gaussian-copula) - Built-in implementation, no external dependencies
- [Custom Methods](../custom-method) - Integrate other packages
{{< /callout >}}

{{< callout type="info" >}}
**Note**: This document only provides YAML configuration examples, without Jupyter notebook examples.
{{< /callout >}}

## Usage Examples

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Synthesizer:
  gaussian:
    method: sdv-single_table-gaussiancopula

  ctgan:
    method: sdv-single_table-ctgan

  copulagan:
    method: sdv-single_table-copulagan

  tvae:
    method: sdv-single_table-tvae
```

## Methods Overview

| Method | method Setting | Features | GPU |
|--------|----------------|----------|-----|
| GaussianCopula (SDV) | `sdv-single_table-gaussiancopula` | Fast, suitable for large data | ✗ |
| CTGAN | `sdv-single_table-ctgan` | High quality, complex patterns | ✓ |
| CopulaGAN | `sdv-single_table-copulagan` | Balances statistics & deep learning | ✓ |
| TVAE | `sdv-single_table-tvae` | Stable training, fast convergence | ✓ |

## Method Details

### GaussianCopula

Classical statistical distribution-based method, fast execution suitable for quick prototyping.

**Features**:
- ✓ Fast, suitable for large data
- ✓ Low computational requirements
- ✗ Primarily captures linear correlations

### CTGAN

GAN-based deep learning method with best generation quality.

**Features**:
- ✓ High-quality synthetic data
- ✓ Suitable for complex patterns
- ✗ Longer training time

**Default Parameters**:
- `epochs`: 300
- `batch_size`: 500
- `generator_lr`: 0.0002
- `discriminator_lr`: 0.0002

### CopulaGAN

Combines Copula statistics with GAN, suitable for mixed-type data.

**Features**:
- ✓ Balances statistics & deep learning
- ✓ Better marginal distribution simulation
- ✓ Suitable for continuous & discrete mixed data

**Default Parameters**:
- `epochs`: 300
- `batch_size`: 500
- `default_distribution`: beta

### TVAE

VAE-based generative model with stable training process.

**Features**:
- ✓ Stable training process
- ✓ Better convergence
- ✓ Suitable for medium-scale data

**Default Parameters**:
- `epochs`: 300
- `batch_size`: 500
- `encoder_layers`: [128, 128]
- `decoder_layers`: [128, 128]

## Automatic Features

### Schema Conversion

PETsARD automatically converts internal Schema to SDV Metadata

### Automatic Parameters

All methods automatically enable:
- `enforce_rounding`: Integer rounding
- `enforce_min_max_values`: Value range enforcement (GaussianCopula, TVAE)

### GPU Detection

Deep learning methods (CTGAN, CopulaGAN, TVAE) automatically detect and use GPU.

## Selection Guide

| Scenario | Recommended Method |
|----------|--------------------|
| Quick testing | GaussianCopula |
| High quality needs | CTGAN |
| Mixed-type data | CopulaGAN |
| Medium data | TVAE |
| Large data | GaussianCopula |

## Available Distributions

GaussianCopula and CopulaGAN support:

- `norm`: Normal distribution
- `truncnorm`: Truncated normal distribution (default)
- `beta`: Beta distribution
- `gamma`: Gamma distribution
- `uniform`: Uniform distribution
- `gaussian_kde`: Kernel density estimation

## Limitations

### Built-in Integration Limits

- ✗ Cannot adjust training parameters (epochs, batch_size, etc.)
- ✗ Cannot specify distribution types
- ✗ Cannot manually select CPU/GPU

## Important Notes

1. Deep learning methods train faster on GPU
2. Default 300 epochs, CPU training may be time-consuming
3. Large datasets with deep learning require significant memory
4. Built-in integration uses fixed parameters, cannot be adjusted