---
title: "Custom Evaluation Method"
type: docs
weight: 695
prev: docs/petsard-yaml/evaluator-yaml/utility
next: docs/petsard-yaml/evaluator-yaml/privacy-mpuccs
---

To create your own evaluator, you need to implement a Python class with required attributes and methods, and configure a YAML file to use it.

## Usage Example

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/custom-evaluation.ipynb)

```yaml
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
Evaluator:
  your-custom-evaluator:
    method: custom_method
    module_path: custom-evaluation.py  # Python file name
    class_name: MyEvaluator_Pushover   # Class name in the file
```

## Required Implementation

Your Python class must include:

```python
class YourEvaluator:
    # Required attributes
    REQUIRED_INPUT_KEYS = ['ori', 'syn']  # or ['ori', 'syn', 'control']
    AVAILABLE_SCORES_GRANULARITY = ['global', 'columnwise', 'pairwise', 'details']

    def __init__(self, config):
        """Initialize evaluator"""
        self.config = config

    def eval(self, data: dict) -> dict:
        """Execute evaluation and return results"""
        # data contains 'ori', 'syn', optionally 'control'
        # returns dict[str, pd.DataFrame]
        return results
```

## Example Implementation: Pushover Evaluator

Our example `custom-evaluation.py` implements a demonstration evaluator that:
1. **Receives data**: Accepts original, synthetic, and control data in `eval()`
2. **Calculates scores**: Returns fixed scores for all granularities (for testing)
3. **Returns results**: Provides global, columnwise, pairwise, and details results

## Key Concepts

### REQUIRED_INPUT_KEYS
- `['ori', 'syn']`: Basic configuration, requires original and synthetic data
- `['ori', 'syn', 'control']`: Advanced configuration, additionally requires control group data

### AVAILABLE_SCORES_GRANULARITY
Defines the result granularities returned by the evaluator:
- `global`: Overall score (single-row DataFrame)
- `columnwise`: Per-column scores (indexed by column names)
- `pairwise`: Column-pair scores (MultiIndex)
- `details`: Custom detailed information

### Return Format Requirements
- Each granularity must return a `pd.DataFrame`
- `columnwise` must include all columns
- `pairwise` must include all column pairs
- Indexes must match expected formats

## Parameter Description

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **method** | `string` | Required | Fixed value: `custom_method` |
| **module_path** | `string` | Required | Python file path (relative to project root) |
| **class_name** | `string` | Required | Class name (must exist in specified file) |
| **Other parameters** | `any` | Optional | Custom parameters passed to evaluator's `__init__` |

## Applicable Scenarios

- **Domain-specific evaluation**: Healthcare, finance, and other domain-specific evaluation requirements
- **External tool integration**: Using existing evaluation libraries
- **New algorithm implementation**: Implementing new evaluation methods from research
- **Customized workflows**: Meeting organization-specific evaluation requirements

## Notes

{{< callout type="warning" >}}
**Important Path Configuration Notes**
- If Python file is in the same directory as YAML file: use filename only (e.g., `custom-evaluation.py`)
- If executing from another directory: use relative path (e.g., `petsard-yaml/evaluator-yaml/custom-evaluation.py`)
- Path is relative to the working directory where PETsARD is executed
{{< /callout >}}

{{< callout type="info" >}}
Evaluators may optionally inherit from `BaseEvaluator`, but this is not required. The key is implementing the necessary attributes and methods.
{{< /callout >}}