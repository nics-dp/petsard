---
title: "Installation: Environment Check"
type: docs
weight: 1
prev: docs
next: docs/getting-started
---

Choose the appropriate installation method based on network connectivity and Docker support. Docker Prebuilt is recommended for consistent environments and simplified deployment. If deep learning features are needed, verify CUDA support.

{{< mermaid-file file="content/docs/installation/environment-check-flow.mmd" >}}

**Legend:**

- Light blue box: Flow start point
- Light purple box: Decision nodes
- Light green box: Action nodes

## Choose Installation Method

Based on your environment conditions, please select the appropriate installation method:

### Environments with Network Connection

- **[Docker Prebuilt](docker-prebuilt)** - Environments with Docker support (Recommended)
  - No local Python environment setup required
  - Fast deployment with high environment consistency

- **[PyPI Install](pypi-install)** - Environments without Docker support
  - Direct installation to local Python environment
  - Supports multiple dependency group options
  - Recommended to use uv for installation

### Environments without Network Connection

- **[Docker Offline Deployment](docker-offline-deployment)** - Environments with Docker support
  - Build/pull image in network-connected environment first
  - Export and transfer to offline environment

- **[Package Pre-download](package-predownload)** - Environments without Docker support
  - Pre-download all dependency packages
  - Transfer to offline environment for installation

### Deep Learning Support

- **[Deep Learning Support Check](dl-support-check)** - Environments using deep learning synthesizers
  - Check NVIDIA GPU driver status
  - Verify PyTorch and CUDA support
  - Confirm system computing mode (CPU/GPU)

### Next Steps

After verifying installation:

1. Check the [Getting Started](../getting-started) guide for detailed usage examples
2. Create a YAML configuration file to start using PETsARD
3. Explore PETsARD YAML documentation to learn about configuration