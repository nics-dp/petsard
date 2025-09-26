---
title: "Adapter API"
weight: 390
---

## Overview

The Adapter layer is a key component in the PETsARD architecture, responsible for wrapping each module into a unified execution interface for Executor invocation.

## Adapter Overall Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/adapter-overview-diagram.mmd" >}}

> **Legend:**
> - Gray box: Abstract base class
> - Light purple box: Concrete Adapter implementation classes
> - `<|--`: Inheritance relationship

## Architecture

All Adapter classes inherit from `BaseAdapter` and implement the following core methods:

- `__init__(config: dict)` - Initialize configuration
- `run(input: dict)` - Execute main logic
- `set_input(status)` - Set input parameters
- `get_result()` - Get execution results
- `get_metadata()` - Get metadata (if applicable)

## Adapter Classes

| Adapter | Corresponding Module | Description |
|---------|---------------------|-------------|
| LoaderAdapter | Loader | Data loading, supports benchmark:// protocol |
| SplitterAdapter | Splitter | Data splitting |
| PreprocessorAdapter | Processor | Preprocessing |
| SynthesizerAdapter | Synthesizer | Data synthesis |
| PostprocessorAdapter | Processor | Postprocessing |
| ConstrainerAdapter | Constrainer | Constraint processing |
| EvaluatorAdapter | Evaluator | Evaluation |
| DescriberAdapter | Describer | Descriptive statistics |
| ReporterAdapter | Reporter | Report generation |

## Basic Usage Pattern

```python
from petsard.adapter import LoaderAdapter

# Create adapter
adapter = LoaderAdapter(config)

# Set input
input_data = adapter.set_input(status)

# Execute
adapter.run(input_data)

# Get results
result = adapter.get_result()
```

## Error Handling

All Adapters use decorator pattern for error handling:

- `@log_and_raise_config_error` - Configuration error handling
- `@log_and_raise_not_implemented` - Not implemented method handling

## Important Notes

- Adapter layer is internal architecture, direct use is not recommended
- Prefer using YAML configuration files and Executor execution
- See sub-page documentation for specific parameters of each Adapter