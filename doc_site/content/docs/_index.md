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

## Colab Execution Guide

Colab's default Python version is now 3.12.12 (2025.10), but PETsARD currently only supports Python 3.10 and 3.11. If you want to run PETsARD on Colab, please change the Runtime type to Python 3.11.13 (2025.07) as shown below:

![How to Change Colab Runtime Version](/images/colab-change-runtime.png)

For detailed Colab runtime version information, please refer to: https://github.com/googlecolab/backend-info#202507

## Release History

- [Milestone](https://github.com/nics-dp/PETsARD/releases/latest)
  - The Milestone document provide detailed information about the latest version of `PETsARD`.
- [Release Note](https://github.com/nics-dp/petsard/releases)
  - Release note provides information of each version of `PETsARD`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. And please make sure to update tests as appropriate.