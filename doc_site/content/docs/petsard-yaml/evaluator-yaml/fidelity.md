---
title: "Data Fidelity Assessment"
weight: 143
---

Measure the similarity between synthetic and original data, evaluating the preservation of data distributions and variable relationships.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/fidelity.ipynb)

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
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Evaluator:
  fidelity_check:
    method: sdmetrics-qualityreport
```

## Parameter Description

- **method** (`string`, required)
  - Fixed value: `sdmetrics-qualityreport`

## Evaluation Metrics

| Metric | Description | Recommended Standard |
|--------|-------------|---------------------|
| **Score** | Overall fidelity score (arithmetic mean of Column Shapes and Column Pair Trends) | ≥ 0.75 |
| **Column Shapes** | Column shapes | ≥ 0.75 |
| - KSComplement | K-S complement (numerical columns) | |
| - TVComplement | Total variation distance complement (categorical columns) | |
| **Column Pair Trends** | Column pair trends | ≥ 0.75 |
| - Correlation Similarity | Correlation similarity (numerical pairs) | |
| - Contingency Similarity | Contingency similarity (categorical pairs) | |

## Metric Calculation Details

### Column Shapes
Arithmetic mean of shape fidelity for each column, calculated based on column characteristics:

- **KSComplement**: Numerical or date columns
  - Uses K-S test (Kolmogorov-Smirnov test)
  - Checks difference between two empirical distributions using cumulative distribution function (CDF)
  - Calculates 1 - K-S value as metric
  - Ranges from 0 to 1, higher values indicate more similar shapes

- **TVComplement**: Categorical or boolean columns
  - Calculates Total Variation Distance (TVD)
  - Measures probability differences across all categories
  - Calculates 1 - TVD as metric
  - Ranges from 0 to 1, higher values indicate more similar shapes

### Column Pair Trends
Arithmetic mean of pairwise correlation fidelity between columns:

- **CorrelationSimilarity**: Both columns are numerical or date
  - Calculates Pearson correlation coefficients for original and synthetic data
  - Formula: `1 - |r_synthetic - r_original| / 2`
  - Ranges from 0 to 1, higher values indicate more similar trends

- **ContingencySimilarity**: Both columns are categorical or boolean
  - Calculates total variation distance of normalized contingency tables
  - Formula: `1 - 1/2 * ΣΣ |r_synthetic - r_original|`
  - Ranges from 0 to 1, higher values indicate more similar trends

- **Mixed Column Pairs**: One numerical/date, one categorical/boolean
  - First discretizes numerical/date column into bins
  - Number of bins follows numpy defaults (Sturges' rule or FD rule)
  - Then calculates contingency similarity

## Applicable Scenarios

- Evaluating effectiveness of synthesis process
- Comparing quality between different synthesis methods
- Confirming preservation of important features and patterns

## Recommended Standards

- Above 0.75 is acceptable¹
- Score, Column Shapes, and Column Pair Trends should all be ≥ 0.75
- If scores are low, may need to adjust synthesis method or parameters

## Technical Reference

- Sturges' rule: Optimal number of bins = log₂(n) + 1
- FD rule: Optimal bin width = 2 × IQR / n^(1/3)
- Transition point approximately at 1,000 samples

## References

¹ Tao, Y., McKenna, R., Hay, M., Machanavajjhala, A., & Miklau, G. (2021). Benchmarking differentially private synthetic data generation algorithms. *arXiv preprint arXiv:2112.09238*. https://doi.org/10.48550/arXiv.2112.09238