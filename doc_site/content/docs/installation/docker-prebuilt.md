---
title: Docker Prebuilt
type: docs
weight: 210
prev: docs/installation
next: docs/installation/pypi-install
---

Suitable for environments **with network connection** and **Docker support**.

> If your environment is **without network connection**, please refer to [Docker Offline Deployment](../docker-offline-deployment) method.

## Method: Using Pre-built Docker Container (Recommended)

PETsARD provides pre-built Docker containers, allowing you to use it without local Python environment setup.

```bash
# Pull the latest version
docker pull ghcr.io/nics-dp/petsard:latest

# Run interactive container
docker run -it --rm ghcr.io/nics-dp/petsard:latest
```

**Available Tags:**
- `latest` - Latest stable version (from main branch)
- `dev` - Development version (from dev branch)
