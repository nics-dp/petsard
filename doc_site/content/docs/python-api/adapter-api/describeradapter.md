---
title: "DescriberAdapter"
weight: 396
---

DescriberAdapter handles data description and comparison, supporting single dataset description and multi-dataset comparative analysis.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/describeradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: DescriberAdapter main class
> - Blue box: Core description modules
> - Purple box: Data alignment modules
> - Light pink box: Configuration classes
> - `..>`: Dependency relationship
> - `-->`: Ownership relationship

## Main Features

- Unified data description interface
- Flexible data source selection (via `source` parameter)
- Two modes support: describe (single dataset), compare (dataset comparison)
- Automatic data type alignment (using Schema)
- Support for various statistical methods and JS Divergence calculation

## Method Reference

### `__init__(config: dict)`

Initialize a DescriberAdapter instance.

**Parameters:**
- `config`: dict, required
  - Configuration parameters dictionary
  - Must include `source` key (data source)
  - Optional `method` key: default, describe, compare
  - Optional `mode` key: automatically determined by source count

### `run(input: dict)`

Execute data description or comparison, including automatic data type alignment.

**Parameters:**
- `input`: dict, required
  - Input parameters dictionary
  - Contains `data` dictionary (datasets)
  - Optional `metadata` for data type alignment

**Returns:**
No direct return value. Use `get_result()` to retrieve results.

### `set_input(status)`

Set input data for the describer.

**Parameters:**
- `status`: Status, required
  - System status object
  - Extracts data based on source configuration

**Returns:**
- `dict`: Dictionary containing data required for description

### `get_result()`

Retrieve description results.

**Returns:**
- `dict[str, pd.DataFrame]`: Dictionary of description results

## Usage Examples

### Single Dataset Description

```python
from petsard.adapter import DescriberAdapter

# Describe single dataset
adapter = DescriberAdapter({
    "source": "Loader",  # or ["Loader"]
    "method": "describe",
    "describe_method": ["mean", "median", "std", "corr"]
})

# Execute description
adapter.run({})

# Get results
results = adapter.get_result()
```

### Dataset Comparison

```python
# Compare two datasets
adapter = DescriberAdapter({
    "source": {
        "base": "Splitter.train",
        "target": "Synthesizer"
    },
    "method": "compare",
    "stats_method": ["mean", "std", "jsdivergence"],
    "compare_method": "pct_change"
})

# Execute comparison
adapter.run({})

# Get results
comparison_results = adapter.get_result()
```

## Workflow

1. **Source Parsing**: Parse source parameter to determine data sources
2. **Mode Determination**:
   - 1 source: describe mode
   - 2 sources: compare mode
3. **Data Collection**: Collect specified data from Status
4. **Schema Retrieval**: Attempt to get metadata for data alignment
5. **Data Type Alignment** (when Schema is available)
6. **Execute Description or Comparison**

## Source Parameter Format

### Describe Mode (Single Data Source)

```yaml
# String format
source: "Loader"

# List format
source: ["Synthesizer"]
```

### Compare Mode (Two Data Sources)

```yaml
# Dictionary format (recommended)
source:
  base: "Splitter.train"
  target: "Synthesizer"

# Backward compatibility format
source:
  ori: "Splitter.train"
  syn: "Synthesizer"
```

## Data Source Syntax

- **Simple format**: `"ModuleName"` - Takes first available data from module
- **Precise format**: `"ModuleName.key"` - Takes specific keyed data from module
  - Examples: `"Splitter.train"`, `"Splitter.validation"`

## Notes

- This is an internal API, direct usage is not recommended
- Use YAML configuration files and Executor instead
- Compare mode reuses DescriberDescribe's statistical functionality
- Parameter naming recommends using `base`/`target` instead of legacy `ori`/`syn`
- Results are cached until next run() call