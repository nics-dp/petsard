---
title: "Custom Data"
weight: 122
---

To use pre-split data from external sources, use the `custom_data` method.

The `custom_data` method allows you to provide pre-split training and validation datasets.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/splitter-yaml/custom-data.ipynb)

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori         # Training set
      control: benchmark://adult-income_control # Validation set
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
```

This example demonstrates `custom_data` usage with other modules:
- **Splitter**: Uses `custom_data` to load pre-split datasets
- **Other modules**: Loader, Synthesizer, and Evaluator are used together for complete evaluation workflow

{{< callout type="info" >}}
The `filepath` parameter supports all Loader formats, including `benchmark://` protocol and regular file paths.
{{< /callout >}}