---
title: "Save Timing Information"
weight: 5
---

Use the `save_timing` method to record the execution time of each module for performance analysis and optimization.

## Usage Example

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-validation.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: default

Synthesizer:
  default:
    method: default

  petsard-gaussian-copula:
    method: petsard-gaussian-copula

Postprocessor:
  default:
    method: default

Reporter:
  save_all_timing:
    method: save_timing  # Required: Fixed as save_timing
    # time_unit: seconds # Optional: Time unit (default: seconds)
    # module:            # Optional: Specify modules to record
    #   - Synthesizer
    #   - Evaluator
    # output: petsard    # Optional: Output filename prefix (default: petsard)
```

## Main Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `method` | `string` | Fixed as `save_timing` | `save_timing` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `time_unit` | `string` | `seconds` | Time unit: `seconds`, `minutes`, `hours`, `days` | `minutes` |
| `module` | `string` or `list` | All modules | Specify modules to record | `["Synthesizer", "Evaluator"]` |
| `output` | `string` | `petsard` | Output filename prefix | `timing_analysis` |

#### time_unit Parameter Details

The `time_unit` parameter specifies the time display unit and supports the following options: `seconds`, `minutes`, `hours`, `days`.

#### module Parameter Details

The `module` parameter filters which modules to record and can specify a single module or a list of modules.

## Output Format

Timing information is saved in CSV format with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `record_id` | Unique record identifier | `timing_000001_20251017_112722` |
| `module_name` | Module name | `SynthesizerAdapter` |
| `experiment_name` | Experiment name | `default` |
| `step_name` | Execution step | `run` |
| `start_time` | Start time (ISO 8601) | `2025-10-17T11:27:22.182237` |
| `end_time` | End time (ISO 8601) | `2025-10-17T11:27:22.328833` |
| `duration_seconds` | Execution time (seconds) | `0.15` |
| `source` | Data source | `logging` |
| `status` | Execution status | `completed` |

**Example Output:**
```csv
record_id,module_name,experiment_name,step_name,start_time,end_time,duration_seconds,source,status
timing_000001_20251017_112722,LoaderAdapter,default,run,2025-10-17T11:27:22.182237,2025-10-17T11:27:22.328833,0.15,logging,completed
timing_000004_20251017_112722,SynthesizerAdapter,default,run,2025-10-17T11:27:22.630578,2025-10-17T11:27:24.672193,2.04,logging,completed
timing_000010_20251017_112725,EvaluatorAdapter,default,run,2025-10-17T11:27:25.623084,2025-10-17T11:27:30.833015,5.21,logging,completed
```

## Key Field Descriptions

- **duration_seconds**: Execution time in seconds; use `time_unit` parameter to change display unit
- **module_name**: Actual adapter name executed (e.g., `LoaderAdapter`, `SynthesizerAdapter`)
- **start_time / end_time**: Precise timestamps of start and end times

## Notes

- CSV output retains 2 decimal places
- Files with the same name will be overwritten
- System load and data size affect execution time