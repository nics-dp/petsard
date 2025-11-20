# Release Configuration

This directory contains all release and packaging related configurations.

## Configuration

The semantic release configuration is defined in `pyproject.toml`:

```toml
[tool.semantic_release]
tag_format = "v{version}"
commit_parser = "conventional"
# ... other configurations
```

## Usage

The release process is automatically triggered when:
1. Pushing commits to `main` or `dev` branches
2. Running `semantic-release version` command
3. The GitHub Actions workflow triggers semantic release

Version information will be automatically updated in `pyproject.toml` based on conventional commits.