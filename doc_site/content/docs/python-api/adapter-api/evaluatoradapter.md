---
title: "EvaluatorAdapter"
weight: 395
---

EvaluatorAdapter handles data evaluation, supporting comparative assessment of original, synthetic, and control datasets.

## Class Architecture

{{< mermaid-file file="content/docs/python-api/adapter-api/evaluatoradapter-usage-diagram.mmd" >}}

> **Legend:**
> - Light purple box: EvaluatorAdapter main class
> - Blue box: Core evaluation modules
> - Purple box: Data alignment modules
> - Light pink box: Configuration classes
> - `..>`: Dependency relationship
> - `-->`: Ownership relationship

## Main Features

- Unified data evaluation interface
- Automatic data type alignment (using Schema)
- Multi-dataset evaluation support (ori, syn, control)
- Integration of various evaluation methods (Privacy, Utility, Diagnostic)
- Fixed data source naming logic

## Method Reference

### `__init__(config: dict)`

Initialize an EvaluatorAdapter instance.

**Parameters:**
- `config`: dict, required
  - Configuration parameters dictionary
  - Must include `method` key (evaluation method)
  - Supported evaluation methods: privacy, utility, diagnostic, etc.

### `run(input: dict)`

Execute data evaluation, including automatic data type alignment.

**Parameters:**
- `input`: dict, required
  - Input parameters dictionary
  - Contains `data` dictionary (ori, syn, control data)
  - Optional `schema` for data type alignment

**Returns:**
No direct return value. Use `get_result()` to retrieve results.

### `set_input(status)`

Set input data for the evaluator.

**Parameters:**
- `status`: Status, required
  - System status object
  - Automatically extracts ori, syn, control data

**Returns:**
- `dict`: Dictionary containing data required for evaluation

### `get_result()`

Retrieve evaluation results.

**Returns:**
- `dict[str, pd.DataFrame]`: Dictionary of evaluation results

## Usage Example

```python
from petsard.adapter import EvaluatorAdapter

# Initialize evaluator
adapter = EvaluatorAdapter({
    "method": "privacy",
    "privacy_method": ["membership_inference", "attribute_inference"]
})

# Set input data (usually handled automatically by Executor)
input_data = {
    "data": {
        "ori": original_df,
        "syn": synthetic_df,
        "control": control_df  # Optional
    },
    "schema": schema  # Optional, for data type alignment
}

# Execute evaluation
adapter.run(input_data)

# Get results
results = adapter.get_result()
```

## Workflow

1. **Data Collection**: Collect ori, syn, control data from Status
2. **Schema Retrieval**: Priority order: Loader > Splitter > Preprocessor
3. **Data Type Alignment** (when Schema is available)
   - Use SchemaMetadater.align() to align data types
   - Ensure consistent data types during evaluation
4. **Evaluation Execution**: Call underlying Evaluator to perform evaluation

## Data Source Logic

EvaluatorAdapter uses fixed data source naming:

- **ori (original data)**:
  - With Splitter: Takes Splitter's train
  - Without Splitter: Takes Loader's result
  
- **syn (synthetic data)**:
  - Takes previous module's result (usually Synthesizer or Postprocessor)
  
- **control (control data)**:
  - Only exists when Splitter is present
  - Takes Splitter's validation

## Notes

- This is an internal API, direct usage is not recommended
- Use YAML configuration files and Executor instead
- Data source naming is fixed, customization not supported
- Automatically handles data type alignment for evaluation accuracy
- Results are cached until next run() call