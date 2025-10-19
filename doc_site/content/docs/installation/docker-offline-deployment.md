---
title: Docker Offline Deployment
type: docs
weight: 4
prev: docs/installation/pypi-install
next: docs/installation/package-predownload
---

Suitable for environments **without network connection** but **with Docker support**.

This method requires building or pulling the Docker image in an environment with network access, then exporting it as a file, and finally importing it in the offline environment.

> If your environment **has network connection**, please refer to [Docker Prebuilt](../docker-prebuilt) method directly, without the need for export/import steps.

## Step 1: Prepare Docker Image in Network-Connected Environment

### Method A: Export Pre-built Image (Recommended)

First pull the pre-built image (see [Docker Prebuilt](../docker-prebuilt) for details), then export it:

```bash
# Pull the latest version (skip if already done)
docker pull ghcr.io/nics-dp/petsard:latest

# Export image to file
docker save ghcr.io/nics-dp/petsard:latest -o petsard-latest.tar
```

### Method B: Build and Export Image

If you need to customize or modify the container, you can build your own image:

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