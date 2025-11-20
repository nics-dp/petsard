---
title: "Postprocessor YAML"
type: docs
weight: 660
prev: docs/petsard-yaml/synthesizer-yaml
next: docs/petsard-yaml/constrainer-yaml
---

YAML configuration file format for the Postprocessor module, used for data postprocessing (inverse transformation).

## Usage Example

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/postprocessor-yaml/postprocessor.ipynb)
> **Note**: If using Colab, please see the [runtime setup guide](/petsard/docs/#colab-execution-guide).

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Preprocessor:
  default:
    method: default
Synthesizer:
  default:
    method: default
Postprocessor:
  default:
    method: default  # Postprocessing: automatically restore preprocessing transformations
Reporter:
  save_all_step:
    method: save_data
    source:
      - Preprocessor
      - Synthesizer
      - Postprocessor
```

## Main Parameters

- **method** (`string`, required)
  - Currently only the `'default'` method is available, which automatically detects the corresponding Preprocessor configuration and performs inverse restoration operations

## How It Works

The Postprocessor automatically performs inverse operations of the Preprocessor, restoring synthetic data to its original format:

1. **Auto-detection**: Reads the corresponding Preprocessor configuration
2. **Reverse execution**: Executes restoration operations in reverse order
3. **Data restoration**:
   - Inverse scaling (scaler → inverse scaler)
   - Inverse encoding (encoder → inverse encoder)
   - Inverse discretization (discretizing → inverse discretizing)
   - Restore missing values (missing → restore NA)

## Mapping with Preprocessor

| Preprocessor Step | Postprocessor Mapping | Description |
|------------------|-------------------|------|
| `missing` | `restore_missing` | Re-insert missing values proportionally |
| `outlier` | ❌ Not restored | Outlier handling cannot be reversed |
| `encoder` | `inverse_encoder` | Decode categorical variables |
| `scaler` | `inverse_scaler` | Inverse scale numerical values |
| `discretizing` | `inverse_discretizing` | Continualization |

## Restoration Sequence

Assuming the Preprocessor sequence is `['missing', 'outlier', 'encoder', 'scaler']`,
the Postprocessor restoration sequence will be `['scaler', 'encoder', 'missing']`

**Note**:
- `outlier` will not be restored (outlier handling cannot be reversed)
- Sequence is automatically reversed
- Missing values are re-inserted according to the original data proportions

## Restoration Flowchart

```
Synthetic Data (encoded)
  ↓
Inverse Scaling (Scaler inverse)
  ↓
Inverse Encoding (Encoder inverse)
  ↓
Insert Missing Values (Missing restore)
  ↓
Original Format Data
```

## Precision Restoration

Postprocessor automatically restores numeric fields to their original precision:

- **Precision Source**: Uses the schema from Preprocessor input (preprocessor_input_schema)
- **Auto-Application**: Data is rounded according to original precision after restoration
- **Precision Consistency**: Ensures restored data matches original data precision

## Execution Instructions

- Postprocessor must be executed after Preprocessor
- The system will automatically read the previous Preprocessor configuration
- The system will automatically retrieve original data precision information
- If there is no corresponding Preprocessor, the Postprocessor will not perform any operations

## Notes

- Postprocessor automatically detects and uses the corresponding Preprocessor configuration
- Outlier handling cannot be restored, so data ranges may differ slightly from the original data
- Missing values are randomly inserted according to the original proportions (positions may differ)
- Data types are automatically aligned with the original schema definition
- Precision is automatically restored to match original data precision
- **Multiple Preprocessor/Postprocessor Configuration Recommendations**:
  - Even with multiple Preprocessors configured, typically only a single Postprocessor is needed to automatically handle all restoration operations
  - Testing for multiple Preprocessor combinations and multiple Postprocessor configurations is currently not comprehensive
  - **Recommendation**: Avoid trying multiple complex combinations of Preprocessors simultaneously to ensure postprocessing stability
- For detailed restoration mechanisms, please refer to the Postprocessor API documentation