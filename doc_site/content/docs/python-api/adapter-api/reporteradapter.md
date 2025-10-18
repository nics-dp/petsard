---
title: "ReporterAdapter"
weight: 7
---

ReporterAdapter handles result output and report generation, wrapping the Reporter module to provide a unified pipeline interface.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/reporteradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: ReporterAdapter main class
> - Blue box: Reporter factory class
> - Green boxes: Concrete reporter implementations
> - Light pink box: Configuration class
> - `-->`: Ownership relationship
> - `..>`: Dependency relationship

## Main Features

- Unified report generation interface
- Support for multiple report methods (data saving, evaluation reports, timing information)
- Automatic filename generation with naming strategies
- Pipeline state integration for automatic report data collection
- Multi-granularity report generation support

## Method Reference

### `__init__(config: dict)`

Initialize ReporterAdapter instance.

**Parameters:**
- `config`: dict, required
  - Configuration parameter dictionary
  - Must include `method` key
  - Different methods require different additional parameters:
    - **save_data**: Requires `source` parameter
    - **save_report**: Requires `granularity` parameter
    - **save_timing**: Optional `time_unit` and `module` parameters
    - **save_validation**: No additional required parameters
  - Optional parameters:
    - `output`: Output filename prefix (default: 'petsard')
    - `naming_strategy`: Naming strategy ('traditional' or 'compact')

### `run(input: dict)`

Execute report generation operation.

**Parameters:**
- `input`: dict, required
  - Data collected from pipeline state
  - Usually set automatically by `set_input()` method
  - Contains experiment results to report

**Returns:**
No direct return value. Report files are saved directly to disk.

### `set_input(status)`

Automatically collect data to report from pipeline state.

**Parameters:**
- `status`: Status object
  - Pipeline execution state
  - Contains execution results from all modules

**Returns:**
- `dict`: Data dictionary prepared for reporting

### `get_result()`

Get result data from report generation.

**Returns:**
- `dict | pd.DataFrame | None`: Processed report data
  - save_data: DataFrame dictionary
  - save_report: Granularity result dictionary
  - save_timing: Timing information DataFrame
  - save_validation: Validation result dictionary

## Usage Examples

### Save Synthetic Data

```python
from petsard.adapter import ReporterAdapter

# Save synthetic data
adapter = ReporterAdapter({
    "method": "save_data",
    "source": "Synthesizer",
    "output": "my_experiment"
})

# Set input from state
input_data = adapter.set_input(status)

# Execute report generation
adapter.run(input_data)
# Output: my_experiment_Synthesizer[exp1].csv
```

### Generate Evaluation Report (Single Granularity)

```python
from petsard.adapter import ReporterAdapter

# Generate global evaluation report
adapter = ReporterAdapter({
    "method": "save_report",
    "granularity": "global",
    "output": "evaluation_results"
})

# Execute
input_data = adapter.set_input(status)
adapter.run(input_data)
# Output: evaluation_results[Report]_eval1_[global].csv
```

### Generate Evaluation Report (Multiple Granularities)

```python
from petsard.adapter import ReporterAdapter

# Generate multi-granularity evaluation report
adapter = ReporterAdapter({
    "method": "save_report",
    "granularity": ["global", "columnwise", "details"],
    "naming_strategy": "compact"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# Output:
# - petsard_eval1_global.csv
# - petsard_eval1_columnwise.csv
# - petsard_eval1_details.csv
```

### Save Timing Information

```python
from petsard.adapter import ReporterAdapter

# Save timing information for specific modules
adapter = ReporterAdapter({
    "method": "save_timing",
    "time_unit": "minutes",
    "module": ["Loader", "Synthesizer"],
    "output": "timing_analysis"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# Output: timing_analysis_timing_report.csv
```

### Use Compact Naming Strategy

```python
from petsard.adapter import ReporterAdapter

# Use compact naming
adapter = ReporterAdapter({
    "method": "save_data",
    "source": ["Synthesizer"],
    "naming_strategy": "compact",
    "output": "results"
})

input_data = adapter.set_input(status)
adapter.run(input_data)
# Output: results_Synthesizer_exp1.csv (more concise filename)
```

## Configuration Parameter Details

### Common Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `method` | `string` | Yes | - | Report method: 'save_data', 'save_report', 'save_timing', 'save_validation' |
| `output` | `string` | No | `'petsard'` | Output filename prefix |
| `naming_strategy` | `string` | No | `'traditional'` | Naming strategy: 'traditional' or 'compact' |

### save_data Method Specific

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | `string\|list` | Yes | Target module name (e.g., 'Synthesizer') |

### save_report Method Specific

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `granularity` | `string\|list` | Yes | Report granularity: 'global', 'columnwise', 'pairwise', 'details', 'tree' |
| `eval` | `string\|list` | No | Filter specific evaluation experiments |

### save_timing Method Specific

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time_unit` | `string` | No | Time unit: 'seconds', 'minutes', 'hours', 'days' |
| `module` | `string\|list` | No | Filter specific modules |

## Workflow

1. **Initialize**: Create ReporterAdapter and configure settings
2. **Collect Data**: `set_input()` collects relevant data from pipeline state
3. **Process Data**: Reporter internally processes and formats data
4. **Generate Report**: Write data to CSV files
5. **Return Result**: Provide processed data via `get_result()`

## Naming Strategies

### Traditional Strategy (Default)

Maintains backward compatibility with detailed naming format:
- `petsard_Synthesizer[exp1].csv`
- `petsard[Report]_eval1_[global].csv`

### Compact Strategy

Uses simplified naming for better readability:
- `petsard_Synthesizer_exp1.csv`
- `petsard_eval1_global.csv`

## Pipeline Integration

ReporterAdapter typically serves as the final stage of the pipeline, collecting and outputting results:

```python
from petsard.config import Config
from petsard.executor import Executor

config_dict = {
    "Loader": {
        "load_data": {"filepath": "data.csv"}
    },
    "Synthesizer": {
        "synth": {"method": "default"}
    },
    "Evaluator": {
        "eval": {"method": "default"}
    },
    "Reporter": {
        # Save synthetic data
        "save_synthetic": {
            "method": "save_data",
            "source": "Synthesizer"
        },
        # Generate evaluation report
        "save_evaluation": {
            "method": "save_report",
            "granularity": ["global", "columnwise"]
        },
        # Save timing information
        "save_timing": {
            "method": "save_timing",
            "time_unit": "minutes"
        }
    }
}

config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## Notes

- This is an internal API; direct usage is not recommended
- Use YAML configuration files and Executor instead
- Report files are saved in the current working directory
- Files with the same name will be overwritten
- Multi-granularity reports generate multiple files
- `set_input()` automatically collects data from pipeline state
- CSV files use UTF-8 encoding

## Related Documentation

- Reporter Python API: Detailed Reporter module description
- Reporter YAML: YAML configuration explanation
- Adapter Overview: Overview of all Adapters