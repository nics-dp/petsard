---
title: API Documentation
type: docs
weight: 1050
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## API Reference Overview

| Module | Object Name | Creation Method | Main Methods |
|--------|-------------|-----------------|--------------|
| [Executor]({{< ref "docs/api/executor" >}}) | `Executor` | `Executor(config)` | `run()`, `get_result()`, `get_timing()` |
| [Adapter]({{< ref "docs/api/adapter" >}}) | `*Adapter` | `*Adapter(config)` | `run()`, `set_input()`, `get_result()` |
| [Config]({{< ref "docs/api/config" >}}) | `Config` | `Config(config_dict)` | Auto-processing during init |
| [Status]({{< ref "docs/api/status" >}}) | `Status` | `Status(config)` | `put()`, `get_result()`, `create_snapshot()` |
| [Utils]({{< ref "docs/api/utils" >}}) | Functions | Direct import | `load_external_module()` |

## Configuration & Execution
- [Executor]({{< ref "docs/api/executor" >}}) - The main interface for experiment pipeline

## System Components
- [Adapter]({{< ref "docs/api/adapter" >}}) - Standardized execution wrappers for all modules
- [Config]({{< ref "docs/api/config" >}}) - Experiment configuration management
- [Status]({{< ref "docs/api/status" >}}) - Pipeline state and progress tracking
- [Utils]({{< ref "docs/api/utils" >}}) - Core utility functions and external module loading