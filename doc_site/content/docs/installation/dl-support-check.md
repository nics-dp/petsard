---
title: Deep Learning Support Check
type: docs
weight: 6
prev: docs/installation/package-predownload
next: docs/installation
---

For environments that need to use **deep learning synthesizers**.

Deep learning support check is used to confirm whether the system environment can fully leverage PETsARD's synthetic data generation performance. PETsARD uses PyTorch as the deep learning framework, supporting both CPU and GPU computing modes. In CPU mode, all computations are performed by the processor, suitable for small-scale datasets or testing environments, but slower when processing large datasets. In GPU mode, computations utilize the parallel computing power of NVIDIA graphics cards, significantly improving synthetic data generation speed. Particularly when processing tens of thousands of records or more, the performance difference can be dozens of times. Through simple detection commands, you can quickly confirm the current computing mode of the system and determine whether GPU environment setup is needed. If the system has an NVIDIA graphics card but detection shows only CPU support, it usually indicates that CUDA drivers need to be installed or updated.

> This documentation focuses on NVIDIA GPU environments and does not consider macOS environments.

## Decision Criteria

Determine whether deep learning support is needed:

- **Using deep learning synthesizers (CTGAN, TVAE, etc.)**: GPU support is required
- **Using non-deep learning synthesizers (GaussianCopula, etc.)**: Can operate without GPU support
- **Using evaluation features only**: Can operate without GPU support

## Step 1: Check NVIDIA GPU Driver

If the command executes successfully, it will display GPU model, driver version, memory usage, and other information. If the command fails, it indicates that NVIDIA drivers are not installed or the system does not have an NVIDIA graphics card.

```bash
# Check NVIDIA GPU status (only for systems with NVIDIA graphics cards)
nvidia-smi
```

## Step 2: Check PyTorch and CUDA Support

```bash
# Complete detection command
python -c "
import torch
print('=== PyTorch Environment Information ===')
print(f'PyTorch Version: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU Count: {torch.cuda.device_count()}')
    print(f'GPU Name: {torch.cuda.get_device_name(0)}')
else:
    print('Currently only CPU mode is supported')
"
```

**How to interpret the results:**

- `CUDA Available: True` → Can use GPU acceleration, suitable for large-scale data processing
- `CUDA Available: False` → Can only use CPU, suitable for small-scale data or testing
- `GPU Name` → Shows the actual GPU model being used
