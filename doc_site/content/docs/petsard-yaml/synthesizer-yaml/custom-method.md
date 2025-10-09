---
title: "Custom Synthesis Method"
weight: 131
---

To create your own synthesizer, you need to implement a Python class with three required methods and configure the YAML file to use it.

## Required Implementation

Your Python class must have:

```python
class YourSynthesizer:
    def __init__(self, config: dict, metadata):
        """Initialize your synthesizer"""
        pass

    def fit(self, data: pd.DataFrame):
        """Learn from the input data"""
        pass

    def sample(self) -> pd.DataFrame:
        """Generate and return synthetic data"""
        pass
```

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/custom-method.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  your-custom-method:
    method: custom_method
    module_path: custom-synthesis.py  # Python file name
    class_name: MySynthesizer_Shuffle # Class name in the file
```

### Example: Shuffle Synthesizer

Our example `custom-synthesis.py` implements a simple synthesizer that:
1. **Stores** each column's values during `fit()`
2. **Shuffles** each column independently to break correlations
3. **Returns** the shuffled data in `sample()`

This preserves the distribution of each column while removing relationships between columns - useful for simple anonymization or as a baseline.

{{< callout type="info" >}}
The Python file should be in the same directory as your notebook or YAML file.
{{< /callout >}}