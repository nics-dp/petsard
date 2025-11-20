---
title: "Adapter API"
type: docs
weight: 1140
---

## Overview

The Adapter layer is a key component in the PETsARD architecture, responsible for wrapping each module into a unified execution interface for [`Executor`](../executor-api) invocation. Each Adapter provides standardized lifecycle methods and data flow management for its corresponding module.

## Adapter Overall Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/adapter-overview-diagram.mmd" >}}

> **Legend:**
> - Gray box: Abstract base class
> - Light purple box: Concrete Adapter implementation classes
> - `<|--`: Inheritance relationship

## Architecture

All Adapter classes inherit from [`BaseAdapter`](petsard/adapter.py:20) and implement the following core interface:

### Core Methods

- **[`__init__(config: dict)`](petsard/adapter.py:25)** - Initialize adapter with configuration
- **[`run(input: dict)`](petsard/adapter.py:328)** - Execute the module's functionality with timing
- **[`set_input(status)`](petsard/adapter.py:403)** - Prepare input data from Status object
- **[`get_result()`](petsard/adapter.py:413)** - Retrieve execution results
- **[`get_metadata()`](petsard/adapter.py:421)** - Retrieve metadata (Schema) if applicable

### Utility Methods

[`BaseAdapter`](petsard/adapter.py:20) provides several utility methods for common operations:

- **[`_apply_precision_rounding()`](petsard/adapter.py:51)** - Apply precision rounding to numerical columns based on schema
- **[`_update_schema_stats()`](petsard/adapter.py:96)** - Recalculate statistics and update schema
- **[`_handle_benchmark_download()`](petsard/adapter.py:133)** - Handle benchmark:// protocol downloads
- **[`_resolve_data_source()`](petsard/adapter.py:208)** - Unified data source resolution supporting "Module.key" format
- **[`_get_metadata_with_priority()`](petsard/adapter.py:282)** - Retrieve metadata with priority order
- **[`_safe_copy()`](petsard/adapter.py:306)** - Unified copy strategy based on data type

## Adapter Classes

| Adapter | Corresponding Module | Key Features |
|---------|---------------------|--------------|
| [`LoaderAdapter`](petsard/adapter.py:431) | [`Loader`](../loader-api) | Data loading with benchmark:// protocol support |
| [`SplitterAdapter`](petsard/adapter.py:588) | [`Splitter`](../splitter-api) | Data splitting with custom_data method support |
| [`PreprocessorAdapter`](petsard/adapter.py:792) | [`Processor`](../processor-api) | Preprocessing with global outlier config expansion |
| [`SynthesizerAdapter`](petsard/adapter.py:1015) | [`Synthesizer`](../synthesizer-api) | Data synthesis with custom_data method support |
| [`PostprocessorAdapter`](petsard/adapter.py:1171) | [`Processor`](../processor-api) | Postprocessing with dtype restoration |
| [`ConstrainerAdapter`](petsard/adapter.py:1312) | [`Constrainer`](../constrainer-api) | Constraint application with resample/validate modes |
| [`EvaluatorAdapter`](petsard/adapter.py:1840) | [`Evaluator`](../evaluator-api) | Evaluation with auto dtype alignment |
| [`DescriberAdapter`](petsard/adapter.py:1996) | [`Describer`](../describer-api) | Descriptive statistics with describe/compare modes |
| [`ReporterAdapter`](petsard/adapter.py:2318) | [`Reporter`](../reporter-api) | Report generation with timing and validation support |

## Basic Usage Pattern

```python
from petsard.adapter import LoaderAdapter

# Create adapter
adapter = LoaderAdapter(config)

# Set input from Status
input_data = adapter.set_input(status)

# Execute with timing
adapter.run(input_data)

# Get results
result = adapter.get_result()
metadata = adapter.get_metadata()  # If applicable
```

## Error Handling

All Adapters use decorator pattern for error handling:

- [`@log_and_raise_config_error`](petsard/adapter.py:361) - Configuration error handling with detailed logging
- [`@log_and_raise_not_implemented`](petsard/adapter.py:374) - Not implemented method handling

## Data Flow

Adapters manage data flow between modules through the Status object:

1. **Input Phase**: [`set_input()`](petsard/adapter.py:403) retrieves data from previous modules via Status
2. **Execution Phase**: [`run()`](petsard/adapter.py:328) executes the wrapped module with timing
3. **Output Phase**: [`get_result()`](petsard/adapter.py:413) and [`get_metadata()`](petsard/adapter.py:421) provide results to Status

## Important Notes

- Adapter layer is internal architecture - direct use is not recommended
- Prefer using YAML configuration files with [`Executor`](../executor-api)
- All data modifications respect Schema precision and statistics settings
- Benchmark downloads are handled transparently via benchmark:// protocol
- See individual Adapter pages for detailed configuration options