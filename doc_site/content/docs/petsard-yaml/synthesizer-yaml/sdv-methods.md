---
title: "SDV Methods"
weight: 131
---

PETsARD integrates the [SDV (Synthetic Data Vault)](https://sdv.dev/) package, providing various advanced synthetic data generation algorithms.

## Methods Overview

| Method Name | method Setting | Use Case | Speed |
|-------------|----------------|----------|-------|
| GaussianCopula | `default` or `sdv-single_table-gaussiancopula` | Quick prototyping, large datasets | Fast |
| CTGAN | `sdv-single_table-ctgan` | High-quality synthetic data | Slow |
| CopulaGAN | `sdv-single_table-copulagan` | Mixed data (continuous + discrete) | Slow |
| TVAE | `sdv-single_table-tvae` | Stable training process | Medium |

## Detailed SDV Methods

### 1. GaussianCopula

Classical statistical distribution-based method, suitable for quick synthetic data generation.

**Features:**
- Fast execution
- Suitable for numerical data
- Customizable distribution types

**Configuration Example:**
```yaml
Synthesizer:
  gaussian_synthesis:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm  # Default distribution
    numerical_distributions:          # Column-specific distributions
      age: beta
      income: gamma
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `default_distribution` | `string` | `truncnorm` | Default numerical distribution type |
| `numerical_distributions` | `dict` | `{}` | Column-specific distribution settings |

### 2. CTGAN

Deep learning method based on GAN (Generative Adversarial Network).

**Features:**
- High-quality synthetic data
- Suitable for complex data patterns
- Requires longer training time

**Configuration Example:**
```yaml
Synthesizer:
  ctgan_synthesis:
    method: sdv-single_table-ctgan
    epochs: 300
    batch_size: 500
    discriminator_steps: 1
    generator_lr: 0.0002
    discriminator_lr: 0.0002
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `discriminator_steps` | `int` | `1` | Discriminator training steps |
| `generator_lr` | `float` | `0.0002` | Generator learning rate |
| `discriminator_lr` | `float` | `0.0002` | Discriminator learning rate |

### 3. CopulaGAN

Hybrid model combining Copula statistical methods and GAN.

**Features:**
- Combines advantages of statistics and deep learning
- Better marginal distribution simulation
- Suitable for mixed-type data

**Configuration Example:**
```yaml
Synthesizer:
  copulagan_synthesis:
    method: sdv-single_table-copulagan
    epochs: 300
    batch_size: 500
    discriminator_steps: 1
    default_distribution: beta
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `discriminator_steps` | `int` | `1` | Discriminator training steps |
| `default_distribution` | `string` | `beta` | Default distribution type |

### 4. TVAE

Generative model based on VAE (Variational Autoencoder).

**Features:**
- Stable training process
- Better convergence
- Suitable for medium-scale data

**Configuration Example:**
```yaml
Synthesizer:
  tvae_synthesis:
    method: sdv-single_table-tvae
    epochs: 500
    batch_size: 1000
    encoder_layers: [256, 256]
    decoder_layers: [256, 256]
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `encoder_layers` | `list` | `[128, 128]` | Encoder layer configuration |
| `decoder_layers` | `list` | `[128, 128]` | Decoder layer configuration |

## Default Method

Using `method: default` automatically selects the GaussianCopula method:

```yaml
Synthesizer:
  default_synthesis:
    method: default  # Equivalent to sdv-single_table-gaussiancopula
```

## Common Parameters

All SDV methods support the following common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enforce_rounding` | `bool` | `True` | Force integer column rounding |
| `enforce_min_max_values` | `bool` | `True` | Enforce value bounds (TVAE and GaussianCopula only) |

## Available Distribution Types

For GaussianCopula and CopulaGAN, the following distribution types can be specified:

- `norm`: Normal distribution
- `truncnorm`: Truncated normal distribution (default)
- `beta`: Beta distribution
- `gamma`: Gamma distribution
- `uniform`: Uniform distribution
- `gaussian_kde`: Gaussian kernel density estimation

## Method Selection Guide

| Scenario | Recommended Method | Reason |
|----------|-------------------|---------|
| Quick prototyping | GaussianCopula | Fast execution, acceptable results |
| High-quality synthesis | CTGAN | Best generation quality, but time-consuming |
| Mixed-type data | CopulaGAN | Balances statistics and deep learning advantages |
| Medium-scale data | TVAE | Stable training, fast convergence |
| Large datasets | GaussianCopula | Deep learning methods may be too time-consuming |

## Complete Example

### Comparing Multiple SDV Methods

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income

Synthesizer:
  # Fast method
  exp1_gaussian:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm
  
  # High-quality method
  exp2_ctgan:
    method: sdv-single_table-ctgan
    epochs: 300
    batch_size: 500
  
  # Balanced method
  exp3_copulagan:
    method: sdv-single_table-copulagan
    epochs: 200
    default_distribution: beta
  
  # VAE method
  exp4_tvae:
    method: sdv-single_table-tvae
    epochs: 400
    batch_size: 1000

Evaluator:
  eval_quality:
    method: sdmetrics-single_table-quality_report

Reporter:
  save_comparison:
    method: save_report
    granularity: global
```

## Important Notes

1. **Computational Resources**: Deep learning methods (CTGAN, CopulaGAN, TVAE) benefit from GPU acceleration
2. **Training Time**: Deep learning methods may require hours of training
3. **Memory Usage**: Large datasets with deep learning methods may require substantial memory
4. **Parameter Tuning**: Deep learning method parameters significantly impact results; careful tuning is recommended