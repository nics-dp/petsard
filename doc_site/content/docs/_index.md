---
title: Docs
type: docs
weight: 0
prev: docs/developer-guide
next: docs/get-started
---

`PETsARD` (Privacy Enhancing Technologies Analysis, Research, and Development, /pəˈtɑrd/) is a Python library for facilitating data generation algorithm and their evaluation processes.

The main functionalities include dataset description, various dataset generation algorithms, and the measurements on privacy protection and utility.

## Design Structure

The following outlines the module design and execution workflow of `PETsARD`:

<p align="center"><img src="/petsard/images/PETsARD_design_en.png"></p>

### System Design

PETsARD adopts a modular design with YAML-based configuration for data processing workflows. The system integrates multiple synthesis algorithms, built-in privacy assessment and quality evaluation, automatically generating visualization reports.

### Ready to Use

The system provides CLI interface and default configuration templates, supporting batch processing and detailed logging. Even users with basic data knowledge can quickly get started and effectively apply privacy-enhancing technologies.

## User Guide

For quick start, we provide comprehensive [Installation](installation) and [Best Practices](best-practices) guides, covering environment check, data governance, evaluation design, and attribute adjustment. Follow this workflow: verify environment compatibility before installation, apply governance standards during data preparation, select evaluation strategies based on use cases when configuring experiments, and optimize performance through attribute adjustment after execution.

<p align="center"><img src="/petsard/images/best-practice.zh-tw.png"></p>

## Release History

- [Milestone](https://github.com/nics-dp/PETsARD/releases/latest)
  - The Milestone document provide detailed information about the latest version of `PETsARD`.
- [Release Note](https://github.com/nics-dp/petsard/releases)
  - Release note provides information of each version of `PETsARD`.
- [CHANGELOG.md](https://github.com/nics-dp/petsard/blob/main/CHANGELOG.md)
  - Changelog provides evolution of the `PETsARD` over time.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. And please make sure to update tests as appropriate.