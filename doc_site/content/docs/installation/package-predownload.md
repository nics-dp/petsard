---
title: Package Pre-download
type: docs
weight: 5
prev: docs/installation
---

# Package Pre-download

Suitable for environments **without network connection** and **without Docker support**.

This method requires downloading all dependency packages in an environment with network access, then transferring them to the offline environment for installation.

## Step 1: Download Packages in Network-Connected Environment

We provide a wheel downloader tool to prepare all dependency packages in advance:

### Download Core Dependencies

```bash
# Download packages for Linux environment
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# Download packages for Windows environment
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os windows

# Download packages for macOS Intel environment
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os macos

# Download packages for macOS Apple Silicon environment
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os macos-arm
```

### Download Additional Dependency Groups

```bash
# Download data science related packages
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds

# Download complete packages (including all features)
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds all

# Download development tools
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups dev
```

**Parameter Descriptions:**

| Parameter | Description | Examples |
|-----------|-------------|----------|
| `--branch` | Git branch name | `main`, `dev` |
| `--python-version` | Python version | `3.10`, `3.11`, `3.11.5` |
| `--os` | Target operating system | `linux`, `windows`, `macos`, `macos-arm` |
| `--groups` | Optional dependency groups | `ds`, `all`, `dev` (can specify multiple separated by spaces) |

**Operating System Support:**
- `linux`: Linux 64-bit
- `windows`: Windows 64-bit
- `macos`: macOS Intel
- `macos-arm`: macOS Apple Silicon

**Dependency Group Descriptions:**
- **Default** (no specification needed): Core functionality for configuration, data loading, synthesis, and evaluation
- `ds`: Data science features + Jupyter Notebook support
- `all`: Complete features + extended support (benchmark datasets, Excel file support)
- `dev`: Testing and development tools

### Download Location

Downloaded packages are saved in the `wheels/` directory by default, structured as follows:

```
wheels/
├── petsard-x.y.z-py3-none-any.whl
├── pandas-x.y.z-cp311-cp311-linux_x86_64.whl
├── numpy-x.y.z-cp311-cp311-linux_x86_64.whl
└── ... (other dependency packages)
```

## Step 2: Transfer Package Files

Transfer the entire `wheels/` directory to the offline environment via USB drive, internal network, or other means.

## Step 3: Install in Offline Environment

### Method A: Direct Installation with pip (Recommended)

```bash
# Navigate to wheels directory
cd wheels/

# Install all packages
pip install *.whl

# Or install PETsARD and its dependencies
pip install --no-index --find-links=. petsard
```

### Method B: Using pip with Local Directory

```bash
# Install from wheels directory
pip install --no-index --find-links=./wheels petsard

# Install specific group packages
pip install --no-index --find-links=./wheels petsard[ds]
```

### Verify Installation

```bash
# Check if PETsARD is correctly installed
python -c "import petsard; print('✅ PETsARD installed, version:', petsard.__version__)"

# Check if Executor is available
python -c "from petsard.executor import Executor; print('✅ Executor available')"
```

## Troubleshooting

### No Matching Package Version Found

**Issue:** Installation prompts no matching package version found

**Solution:**
1. Ensure the Python version used for download matches the offline environment
2. Ensure the operating system used for download matches the offline environment
3. Re-download the correct version of packages

### Dependency Conflicts

**Issue:** Installation prompts package dependency conflicts

**Solution:**
```bash
# Force installation, ignoring dependency checks (use with caution)
pip install --no-deps --no-index --find-links=./wheels petsard

# Then manually install missing dependencies
pip install --no-index --find-links=./wheels <missing-package-name>
```

### Permission Issues

**Issue:** No permission to install to system Python

**Solution:**
```bash
# Install to user directory
pip install --user --no-index --find-links=./wheels petsard

# Or use virtual environment (recommended)
python -m venv petsard-env
source petsard-env/bin/activate  # Linux/macOS
# or
petsard-env\Scripts\activate  # Windows

pip install --no-index --find-links=./wheels petsard
```

## Advanced Usage

### Download Specific PETsARD Version

```bash
# Download packages from specific branch
python demo/petsard_wheel_downloader.py --branch v1.0.0 --python-version 3.11 --os linux

# Download development version
python demo/petsard_wheel_downloader.py --branch dev --python-version 3.11 --os linux
```

### Batch Download for Multiple Platforms

```bash
# Download packages for multiple platforms
for os in linux windows macos macos-arm; do
    python demo/petsard_wheel_downloader.py \
        --branch main \
        --python-version 3.11 \
        --os $os \
        --groups ds
done
```

## Next Steps

After installation, you can:

* Check the [Getting Started](../getting-started) guide for detailed examples
* Visit the PETsARD YAML documentation to learn about configuration
* Explore benchmark datasets for testing
* Review example configurations in the GitHub repository