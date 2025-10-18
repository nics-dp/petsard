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
| [Adapter]({{< ref "docs/api/adapter" >}}) | `*Adapter` | `*Adapter(config)` | `run()`, `set_input()`, `get_result()` |
| [Utils]({{< ref "docs/api/utils" >}}) | Functions | Direct import | `load_external_module()` |

## System Components
- [Adapter]({{< ref "docs/api/adapter" >}}) - Standardized execution wrappers for all modules
- [Utils]({{< ref "docs/api/utils" >}}) - Core utility functions and external module loading