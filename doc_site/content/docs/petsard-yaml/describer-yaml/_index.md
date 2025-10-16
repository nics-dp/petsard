---
title: "Describer YAML"
weight: 150
---

YAML configuration file format for the Describer module. Provides statistical description and comparison functionality for datasets.

## Main Parameters

- **method** (`string`, optional)
  - Evaluation method
  - `default`: Automatically determine based on source count (1→describe, 2→compare)
  - `describe`: Single dataset statistical description
  - `compare`: Dataset comparison (integrating Stats functionality)
  - Default: `default`

- **source** (`string | dict`, required)
  - Specify data source(s)
  - Single source: For describe method
  - Two sources: For compare method (must use dictionary format)
  - Available values: `Loader`, `Splitter`, `Preprocessor`, `Synthesizer`, `Postprocessor`, `Constrainer`

## Supported Methods

| Method | Description | Data Requirements | Output Content |
|--------|-------------|-------------------|----------------|
| **default** | Auto-detect mode | Based on source count | Based on detection result |
| **describe** | Single dataset statistics | One data source | global, columnwise, pairwise |
| **compare** | Dataset comparison analysis | Two data sources | global (with Score), columnwise |

## Parameter Details

### Common Parameters

| Parameter | Type | Required/Optional | Default | Description | Example |
|-----------|------|-------------------|---------|-------------|---------|
| `method` | `string` | Optional | `default` | Evaluation method | `describe`, `compare` |
| `source` | `string\|dict` | **Required** | None | Data source module(s) | See below |

### Source Parameter Formats

#### 1. Single source (describe method)
```yaml
source: Loader
```

#### 2. Dictionary format (compare method - required)
```yaml
source:
  base: Splitter.train    # Explicitly specify base data
  target: Synthesizer      # Explicitly specify target for comparison
```

Note: Backward compatibility supports `ori`/`syn` key names, but `base`/`target` is recommended.

### Compare Method Specific Parameters

| Parameter | Type | Default | Description | Available Values |
|-----------|------|---------|-------------|------------------|
| `stats_method` | `list` | All methods | Statistical methods list | `mean`, `std`, `median`, `min`, `max`, `nunique`, `jsdivergence` |
| `compare_method` | `string` | `pct_change` | Comparison method | `pct_change`, `diff` |
| `aggregated_method` | `string` | `mean` | Aggregation method | `mean` |
| `summary_method` | `string` | `mean` | Summary method | `mean` |

### Statistical Methods Explanation

| Method | Applicable Data Type | Description | Execution Level |
|--------|---------------------|-------------|-----------------|
| `mean` | Numeric | Mean value | columnwise |
| `std` | Numeric | Standard deviation | columnwise |
| `median` | Numeric | Median value | columnwise |
| `min` | Numeric | Minimum value | columnwise |
| `max` | Numeric | Maximum value | columnwise |
| `nunique` | Categorical | Number of unique values | columnwise |
| `jsdivergence` | Categorical | JS divergence | percolumn |

### Comparison Methods Explanation

| Method | Formula | Use Case |
|--------|---------|----------|
| `pct_change` | `(target - base) / abs(base)` | View relative change magnitude |
| `diff` | `target - base` | View absolute change amount |

## Usage Examples

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/describer-yaml/describer.ipynb)

### Single Dataset Description (describe mode)

```yaml
---
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Describer:
  describer-describe:
    method: default    # Auto-detects as describe (single source)
    source: Synthesizer
...
```

### Dataset Comparison (compare mode)

```yaml
---
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Describer:
  describer-compare:
    method: default         # Auto-detects as compare (two sources)
    source:
      base: Splitter.train  # Use Splitter's train output as base
      target: Synthesizer   # Compare with Synthesizer's output
...
```

### Custom Comparison Method

```yaml
---
Loader:
  load_original:
    filepath: benchmark://adult-income_ori
    schema: benchmark://adult-income_schema
Synthesizer:
  generate_synthetic:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Describer:
  custom_comparison:
    method: compare           # Explicitly specify compare method
    source:
      base: Loader
      target: Synthesizer
    stats_method:             # Custom statistical methods
      - mean
      - std
      - nunique
      - jsdivergence
    compare_method: diff      # Use difference instead of percentage change
    aggregated_method: mean
    summary_method: mean
...
```

## Auto-detection Logic (default method)

- **1 source**: Automatically uses `describe` method
- **2 sources**: Automatically uses `compare` method (must use dictionary format)
  - Must explicitly specify `base` and `target` keys
- **Other counts**: Error

## Execution Notes

- Experiment names (second level) can be freely named, descriptive names recommended
- source parameter is required, must explicitly specify data source(s)
- method parameter can be omitted, defaults to `default` (auto-detection)
- Statistical methods automatically filtered based on data types

## Important Notes

- **source is a required parameter**: Must explicitly specify data source(s) to analyze
- **compare mode requires dictionary format**: Must explicitly specify `base` and `target` keys
- **Backward compatibility**: Still supports `ori`/`syn` parameter names, but `base`/`target` recommended
- compare method integrates the original Stats evaluator functionality
- Inapplicable statistical methods will return NaN
- Recommended for numeric data: `mean`, `std`, `median`, `min`, `max`
- Recommended for categorical data: `nunique`, `jsdivergence`

## Related Documentation

- **Data Sources**: Any data-producing module can be used as source, such as Loader, Splitter, Synthesizer, etc.
- **Module.key Format**: Use dot notation to precisely specify when modules have multiple outputs, e.g., `Splitter.train`
- **Statistical Methods**: Automatically determines applicable statistical methods based on data types