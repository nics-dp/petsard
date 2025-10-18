---
title: Installation
type: docs
weight: 1
prev: docs
next: docs/getting-started
---

## Environment Check

{{< mermaid-file file="content/docs/installation/environment-check-flow.mmd" >}}

**Legend:**

- Light blue box: Flow start point
- Light purple box: Decision nodes
- Light green box: Action nodes

## Choose Installation Method

Based on your environment conditions, please select the appropriate installation method:

### Environments with Network Connection

- **[Docker Build](docker-build)** - Environments with Docker support (Recommended)
  - No local Python environment setup required
  - Fast deployment with high environment consistency

- **[PyPI Install](pip-install)** - Environments without Docker support
  - Direct installation to local Python environment
  - Supports multiple dependency group options
  - Recommended to use uv for installation

### Environments without Network Connection

- **[Docker Export](docker-export)** - Environments with Docker support
  - Build/pull image in network-connected environment first
  - Export and transfer to offline environment

- **[Package Pre-download](package-predownload)** - Environments without Docker support
  - Pre-download all dependency packages
  - Transfer to offline environment for installation

## Quick Start

### Using Docker (Recommended)

Verify the Docker image is working correctly:

```bash
# Pull the latest version
docker pull ghcr.io/nics-dp/petsard:latest

# Verify installation
docker run --rm ghcr.io/nics-dp/petsard:latest python -c "
import petsard
print('✅ PETsARD installed successfully!')
"
```

- Interactive Development

```bash
# Start interactive Python session
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-dp/petsard:latest

# Inside container, you can run:
# from petsard import Executor
# print('PETsARD is ready!')
```

### Using PyPI Install

Verify local installation is successful:

```bash
# Install PETsARD (uv recommended, pip also works)
uv pip install petsard
# or
pip install petsard

# Verify installation
python -c "
import petsard
print('✅ PETsARD installed successfully!')
"
```

### Next Steps

After verifying installation:

1. Check the [Getting Started](../getting-started) guide for detailed usage examples
2. Create a YAML configuration file to start using PETsARD
3. Explore PETsARD YAML documentation to learn about configuration