---
title: "SDV Custom Methods"
weight: 132
---

Flexibly use SDV synthesis methods via custom_method approach, with full control over all parameters including CPU/GPU selection and training parameters.

{{< callout type="info" >}}
**Difference from Built-in Integration**: This method provides complete parameter control, while [Built-in SDV Methods](../sdv-methods) use fixed default values.
{{< /callout >}}

## Example Usage

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Synthesizer:
  exp_gaussiancopula:
    method: custom_method
    module_path: sdv-custom-methods.py
    class_name: SDV_GaussianCopula
    device: cpu                      # Specify compute device
    default_distribution: truncnorm  # Customize distribution type
    enforce_rounding: true

Evaluator:
  eval_quality:
    method: sdmetrics-single_table-quality_report

Reporter:
  save_report:
    method: save_report
    granularity: global
```

## Prerequisites

### 1. Install SDV

```bash
pip install sdv
```

### 2. Download Script

Download [`sdv-custom-methods.py`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.py) to the same directory as your YAML file.

### 3. Check CUDA Availability (Optional)

```bash
python check_cuda.py
```

## Supported Methods

### 1. SDV_GaussianCopula

Fast statistical method suitable for large datasets and rapid prototyping.

**Features:**
- No training iterations required, fastest method
- CPU-only (does not use GPU)
- Customizable distribution types for numerical columns

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | `string` | `cpu` | Compute device (only `cpu` supported) |
| `default_distribution` | `string` | `truncnorm` | Default distribution for numerical columns |
| `numerical_distributions` | `dict` | `{}` | Specify distributions for specific columns |
| `enforce_min_max_values` | `bool` | `true` | Enforce numerical range constraints |
| `enforce_rounding` | `bool` | `true` | Round integer columns |

**Available Distribution Types:**
- `truncnorm`: Truncated normal distribution
- `beta`: Beta distribution
- `gamma`: Gamma distribution
- `uniform`: Uniform distribution
- `norm`: Normal distribution

**Example:**

```yaml
exp_gaussiancopula:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_GaussianCopula
  device: cpu
  default_distribution: truncnorm
  numerical_distributions:
    age: beta
    hours-per-week: gamma
```

### 2. SDV_CTGAN

GAN-based deep learning method providing highest quality synthetic data.

**Features:**
- High-quality synthetic data
- GPU acceleration support
- Full control over training parameters

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | `string` | `cpu` | Compute device (`cpu` or `cuda`) |
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `discriminator_steps` | `int` | `1` | Discriminator updates per generator update |
| `generator_lr` | `float` | `0.0002` | Generator learning rate |
| `discriminator_lr` | `float` | `0.0002` | Discriminator learning rate |
| `generator_dim` | `list` | `[256, 256]` | Generator hidden layer sizes |
| `discriminator_dim` | `list` | `[256, 256]` | Discriminator hidden layer sizes |
| `enforce_rounding` | `bool` | `true` | Round integer columns |
| `verbose` | `bool` | `false` | Show training progress |

**Example:**

```yaml
exp_ctgan:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_CTGAN
  device: cuda        # Use GPU acceleration
  epochs: 100         # Fewer epochs for quick testing
  batch_size: 500
  verbose: true       # Show training progress
```

### 3. SDV_CopulaGAN

Hybrid model combining statistical methods and GANs.

**Features:**
- Balances statistical accuracy and generation quality
- Better marginal distribution fitting
- GPU acceleration support

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | `string` | `cpu` | Compute device (`cpu` or `cuda`) |
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `default_distribution` | `string` | `beta` | Default distribution for numerical columns |
| `numerical_distributions` | `dict` | `{}` | Specify distributions for specific columns |
| `discriminator_steps` | `int` | `1` | Discriminator updates per generator update |
| `generator_lr` | `float` | `0.0002` | Generator learning rate |
| `discriminator_lr` | `float` | `0.0002` | Discriminator learning rate |
| `enforce_rounding` | `bool` | `true` | Round integer columns |
| `verbose` | `bool` | `false` | Show training progress |

**Example:**

```yaml
exp_copulagan:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_CopulaGAN
  device: cpu
  epochs: 200
  default_distribution: beta
```

### 4. SDV_TVAE

VAE-based generative model with stable training process.

**Features:**
- Stable training process
- Better convergence
- GPU acceleration support

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | `string` | `cpu` | Compute device (`cpu` or `cuda`) |
| `epochs` | `int` | `300` | Training epochs |
| `batch_size` | `int` | `500` | Batch size |
| `encoder_layers` | `list` | `[128, 128]` | Encoder hidden layer sizes |
| `decoder_layers` | `list` | `[128, 128]` | Decoder hidden layer sizes |
| `embedding_dim` | `int` | `128` | Embedding dimension size |
| `l2scale` | `float` | `0.00001` | L2 regularization coefficient |
| `loss_factor` | `int` | `2` | Reconstruction loss factor |
| `enforce_min_max_values` | `bool` | `true` | Enforce numerical range constraints |
| `enforce_rounding` | `bool` | `true` | Round integer columns |
| `verbose` | `bool` | `false` | Show training progress |

**Example:**

```yaml
exp_tvae:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_TVAE
  device: cpu
  epochs: 300
  batch_size: 1000
  encoder_layers: [256, 256]
  decoder_layers: [256, 256]
```

## Device Parameter Explanation

### CPU Mode (Default)

```yaml
device: cpu  # Use CPU for training
```

**Characteristics:**
- No GPU hardware required
- Suitable for small datasets
- Slower training speed

### CUDA Mode (Requires GPU)

```yaml
device: cuda  # Use GPU for training
```

**Characteristics:**
- Requires NVIDIA GPU
- Significantly faster training (2-10x speedup)
- Suitable for large datasets and long training

**CUDA Validation Mechanism:**
- If `cuda` is specified but not available, program will **immediately terminate** with error message
- Use `check_cuda.py` to check CUDA availability beforehand

### Method Support

| Method | CPU | CUDA |
|--------|-----|------|
| SDV_GaussianCopula | ✓ | ✗ (will warn and use CPU) |
| SDV_CTGAN | ✓ | ✓ |
| SDV_CopulaGAN | ✓ | ✓ |
| SDV_TVAE | ✓ | ✓ |

## Parameter Tuning Recommendations

### Quick Testing Configuration

```yaml
epochs: 10-50        # Quick results
batch_size: 500      # Standard batch size
verbose: true        # Observe training progress
```

### Production Configuration

```yaml
epochs: 300-500      # Sufficient training
batch_size: 500-1000 # Adjust based on memory
verbose: false       # Reduce output
device: cuda         # Use GPU if available
```

### Memory Optimization

```yaml
batch_size: 250-500  # Reduce batch size
epochs: 300          # Maintain sufficient training
```

## FAQ

### Q: How do I know if my environment supports CUDA?

Run the check script:

```bash
python check_cuda.py
```

### Q: What if CTGAN/CopulaGAN/TVAE training is too slow?

1. **Reduce epochs**: Lower from 300 to 50-100 for testing
2. **Use GPU**: Set `device: cuda` (if available)
3. **Increase batch_size**: Can speed up each epoch

### Q: Can GaussianCopula use GPU?

No, GaussianCopula is a pure statistical method without neural networks, so it doesn't support GPU. If `device: cuda` is set, the system will warn and automatically use CPU.

### Q: How to choose the right method?

| Need | Recommended Method |
|------|-------------------|
| Quick testing | SDV_GaussianCopula |
| Highest quality | SDV_CTGAN (requires GPU) |
| Balanced quality/speed | SDV_CopulaGAN |
| Training stability | SDV_TVAE |
| No GPU environment | SDV_GaussianCopula or reduce epochs |

## File Sources

- **Script**: [`sdv-custom-methods.py`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.py)
- **YAML Example**: [`sdv-custom-methods.yaml`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.yaml)
- **Check Script**: [`check_cuda.py`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/check_cuda.py)
- **Jupyter Notebook**: [`sdv-custom-methods.ipynb`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.ipynb)

## Related Documentation

- [Built-in SDV Methods](../sdv-methods): Simplified version with fixed defaults
- [Custom Method Guide](../custom-synthesis): General guide for custom synthesis methods