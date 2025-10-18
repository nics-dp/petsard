---
title: Docker Export
type: docs
weight: 4
prev: docs/installation
---

# Docker Export

Suitable for environments **without network connection** but **with Docker support**.

This method requires building or pulling the Docker image in an environment with network access, then exporting it as a file, and finally importing it in the offline environment.

## Step 1: Prepare Docker Image in Network-Connected Environment

### Option A: Using Pre-built Image (Recommended)

```bash
# Pull the latest version
docker pull ghcr.io/nics-dp/petsard:latest

# Export image to file
docker save ghcr.io/nics-dp/petsard:latest -o petsard-latest.tar
```

### Option B: Local Build

If you have the PETsARD source code, you can build your own container:

```bash
# Clone the repository
git clone https://github.com/nics-dp/petsard.git
cd petsard

# Build standard version (default - without Jupyter)
docker build -t petsard:latest .

# Export image to file
docker save petsard:latest -o petsard-latest.tar
```

### Build Version with Jupyter Lab

```bash
# Build and run version with Jupyter Lab
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# Export image
docker save petsard:jupyter -o petsard-jupyter.tar
```

## Step 2: Transfer Image File

Transfer the exported `.tar` file (e.g., `petsard-latest.tar`) to the offline environment via USB drive, internal network, or other means.

## Step 3: Import Image in Offline Environment

```bash
# Import Docker image
docker load -i petsard-latest.tar

# Verify image was successfully imported
docker images | grep petsard
```

## Next Steps

After installation, you can:

* Check the [Getting Started](../getting-started) guide for detailed examples
* Visit the PETsARD YAML documentation to learn about configuration
* Explore benchmark datasets for testing
* Review example configurations in the GitHub repository