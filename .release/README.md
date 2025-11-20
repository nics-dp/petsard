# Release Configuration 發布配置

This directory contains all release and packaging related configurations.

本目錄包含所有發布和打包相關的配置檔案。

## Configuration 配置

The semantic release configuration is defined in [`pyproject.toml`](../pyproject.toml):

語意化版本發布配置定義在 [`pyproject.toml`](../pyproject.toml) 中：

```toml
[tool.semantic_release]
tag_format = "v{version}"
commit_parser = "conventional"
# ... other configurations
```

## Usage 使用方式

The release process is automatically triggered when:

發布流程會在以下情況自動觸發：

1. Pushing commits to `main` or `dev` branches 推送提交到 `main` 或 `dev` 分支
2. Running `semantic-release version` command 執行 `semantic-release version` 命令
3. The GitHub Actions workflow triggers semantic release GitHub Actions 工作流程觸發語意化發布

Version information will be automatically updated in [`pyproject.toml`](../pyproject.toml) based on conventional commits.

版本資訊會根據符合規範的提交訊息自動更新到 [`pyproject.toml`](../pyproject.toml) 中。

## Directory Structure 目錄結構

```
.release/
├── README.md          # This documentation file 此說明檔案
├── v*.md             # Release notes for specific versions 特定版本的發布說明
└── docker/           # Docker related files Docker 相關檔案
```

## Related Files 相關檔案

- [`../pyproject.toml`](../pyproject.toml) - Main project configuration with semantic-release settings 主要專案配置，包含語意化發布設定
- [`../.github/workflows/`](../.github/workflows/) - GitHub Actions workflows for CI/CD CI/CD 的 GitHub Actions 工作流程

## Maintenance Notes 維護注意事項

- Version numbers follow [Semantic Versioning 2.0.0](https://semver.org/) 版本號遵循[語意化版本 2.0.0](https://semver.org/)
- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) specification 提交訊息必須遵循[約定式提交](https://www.conventionalcommits.org/)規範
- Release notes are automatically generated from commit messages 發布說明會自動從提交訊息生成