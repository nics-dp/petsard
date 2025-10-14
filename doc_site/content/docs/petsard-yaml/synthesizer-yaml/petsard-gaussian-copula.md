---
title: "PETsARD Gaussian Copula"
weight: 1
math: true
---

An efficient Gaussian Copula synthesizer implemented with Numba JIT and PyTorch, supporting CPU/GPU hybrid computing and intelligent device selection.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/petsard-gaussian-copula.ipynb)

```yaml
Synthesizer:
  petsard-gaussian-copula:
    method: petsard-gaussian-copula
    sample_num_rows: 1000  # Number of rows to generate, default: training data row count
    use_gpu: auto          # Device selection, default: auto (automatic)
    gpu_threshold: 50000   # Threshold for auto mode, default: 50,000
```

## Parameters

- **method** (`string`, required) - Fixed value: `petsard-gaussian-copula`
- **sample_num_rows** (`integer`, optional) - Number of synthetic data rows to generate. If not specified, uses training data row count
- **use_gpu** (`string` or `boolean`, optional, default `"auto"`) - Device selection mode:
  - `"auto"` (default): Automatically selects device based on data size. Uses GPU when data exceeds `gpu_threshold` and GPU is available, otherwise uses CPU
  - `true`: Force GPU usage. Raises error if GPU is unavailable
  - `false`: Force CPU usage
- **gpu_threshold** (`integer`, optional, default `50,000`) - When `use_gpu="auto"`, use GPU if data exceeds this row count

## Algorithm Principles

Gaussian Copula separates marginal distributions from correlation structure through the following steps:

1. **Marginal Transformation** - Use empirical CDF to transform to uniform distribution: $u_i = F_i(X_i) = \frac{\text{rank}(X_i)}{n}$
2. **Gaussianization** - Use standard normal quantile function: $z_i = \Phi^{-1}(u_i)$
3. **Correlation Learning** - Learn correlation matrix in Gaussian space: $\Sigma = \text{corr}(\mathbf{Z})$
4. **Joint Sampling** - Sample from multivariate normal distribution: $\mathbf{Z}^* \sim \mathcal{N}(\mathbf{0}, \Sigma)$
5. **Inverse Transformation** - Transform back to original space: $u_i^* = \Phi(z_i^*), \quad X_i^* = F_i^{-1}(u_i^*)$

Mathematical representation: $H(\mathbf{X}) = \Phi_{\Sigma}\left(\Phi^{-1}(F_1(X_1)), \ldots, \Phi^{-1}(F_D(X_D))\right)$

## Implementation Features

### Hybrid Computing Architecture

PETsARD adopts **NumPy + Numba JIT + PyTorch** architecture, using the most suitable tool for each stage:

| Stage | Tool | Speedup |
|-------|------|---------|
| Transform | NumPy + Numba JIT | ~700x after JIT compilation |
| Correlation | NumPy | Fast and stable |
| Regularization | NumPy (Ledoit-Wolf) | Avoids eigenvalue decomposition |
| Sampling | NumPy | ~100x faster than PyTorch CPU |
| Inverse Transform | NumPy + Numba JIT | JIT-compiled linear interpolation |
| GPU Operations | PyTorch | Large dataset acceleration |

### Core Optimization Techniques

- **Numba JIT Compilation** - Custom rank calculation and linear interpolation, 2-3x faster than standard implementation, 10-100x faster after compilation
- **Intelligent Device Selection** - Small data (< 50K rows) uses CPU to avoid transfer overhead, large data uses GPU acceleration
- **Identity Fast Path** - Uses ultra-fast independent sampling when variables are detected as independent
- **Ledoit-Wolf Regularization** - Uses $\Sigma_{\text{reg}} = (1 - \lambda)\Sigma + \lambda I$, eigenvalue decomposition only when necessary

### Differences from Other Implementations

**Same**: Standard Gaussian Copula algorithm, using the same statistical methods

**Different**: PETsARD adds Numba JIT acceleration, PyTorch GPU support, intelligent device selection, and other engineering optimizations

## Data Requirements

- ✅ Categorical variables already encoded as integers (0, 1, 2, ...)
- ✅ All columns are numeric types (int, float, datetime)
- ❌ string/object types not accepted

Generation process uses float64, then automatically restores original types (rounding integers, converting datetime types, etc.).

## Performance and Limitations

### Performance Reference

- **Small data** (< 10K rows): Training ~1s, Generation ~0.5s
- **Medium data** (10K-50K rows): Training ~2-3s, Generation ~1s
- **Large data** (> 50K rows): Automatically switches to GPU, 2-5x speedup

{{< callout type="info" >}}
First run requires Numba JIT compilation (~2s), subsequent runs will be much faster.
{{< /callout >}}

### Limitations

- Primarily captures **linear correlations** (Pearson correlation coefficient), non-linear relationships may not be fully reproduced
- Complex conditional dependencies are simplified to joint Gaussian distribution
- Correlation matrix size is O(n²), requires significant memory for >1000 columns

## References

- Nelsen, R. B. (2006). An Introduction to Copulas (2nd ed.). Springer. https://doi.org/10.1007/0-387-28678-0