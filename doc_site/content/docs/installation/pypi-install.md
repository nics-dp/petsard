---
title: PyPI Install
type: docs
weight: 3
prev: docs/installation
---

# PyPI Install

Suitable for environments **with network connection** but **without Docker support**.

## Available Dependency Groups

PETsARD provides different dependency groups for various use cases:

| Group | Included Features |
|-------|-------------------|
| **Default** | Core functionality: configuration, data loading, synthesis, evaluation, benchmark dataset downloads (pyyaml, pandas, anonymeter, sdmetrics, sdv, torch, requests, etc.) |
| **Data Science** (`ds`) | Basic functionality + Jupyter Notebook support (for Docker environments with Jupyter) |
| **Complete** (`all`) | Data science functionality + xlsx file support |
| **Development** (`dev`) | Complete functionality + development and testing utilities (pytest, ruff, coverage, etc.) |

## Method 1: PyPI Installation (Recommended)

PETsARD is available on [PyPI](https://pypi.org/project/petsard/).

### Method 1-a: Using uv (Fastest, Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer.

**Step 1: Install uv** (skip if already installed)

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

**Step 2: Install PETsARD**

```bash
# Default installation (recommended for most users)
uv pip install petsard

# With dependency groups
uv pip install petsard[ds]   # For Docker environments with Jupyter
uv pip install petsard[all]  # With xlsx file support
uv pip install petsard[dev]  # For development
```

### Method 1-b: Using pip

```bash
# Default installation (recommended for most users)
pip install petsard

# With dependency groups
pip install petsard[ds]   # For Docker environments with Jupyter
pip install petsard[all]  # With xlsx file support
pip install petsard[dev]  # For development
```

### Method 1-c: Installing from TestPyPI (For Testing)

To install pre-release or test versions from [TestPyPI](https://test.pypi.org/):

```bash
# Using pip
pip install --index-url https://test.pypi.org/simple/ petsard

# Using uv
uv pip install --index-url https://test.pypi.org/simple/ petsard

# With dependency groups (may need additional --extra-index-url for dependencies)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ petsard[ds]
```

**Note:** TestPyPI is used for testing package releases. For production use, install from the main PyPI (methods 1-a or 1-b above).

#### Installation in Restricted Network Environments

If you're installing in a restricted network environment (e.g., behind a corporate firewall or proxy), you may encounter SSL certificate verification issues. In such cases, you can use the `--trusted-host` parameter to bypass certificate verification:

```bash
pip install petsard[ds] \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org
```

**For Jupyter Notebook users**, the syntax is the same:

```python
%pip install petsard[ds] \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org
```

**Understanding `--trusted-host` parameters:**

- `--trusted-host pypi.org` - Trusts the main PyPI index server
- `--trusted-host files.pythonhosted.org` - Trusts PyPI's package file storage server

These parameters tell pip to skip SSL certificate verification for the specified hosts. This is useful when:
- Corporate networks intercept SSL/TLS traffic for security inspection
- Self-signed certificates are in use
- Certificate validation fails due to proxy configurations

**Note:** Only use `--trusted-host` in trusted network environments, as it reduces security by disabling certificate verification. Consider configuring proper SSL certificates or using a private PyPI mirror for production environments.

## Method 2: Source Installation

For development or custom builds:

```bash
# Clone the repository
git clone https://github.com/nics-dp/petsard.git
cd petsard

# Install with pyproject.toml (recommended)
pip install --group all -e .

# Or install specific dependency groups
pip install --group ds -e .    # Data science features
pip install --group dev -e .   # Development tools
```

**Recommended tools for development:**
* `pyenv` - Python version management
* `uv` - Package management

## Next Steps

After installation, you can:

* Check the [Getting Started](../getting-started) guide for detailed examples
* Visit the PETsARD YAML documentation to learn about configuration
* Explore benchmark datasets for testing
* Review example configurations in the GitHub repository