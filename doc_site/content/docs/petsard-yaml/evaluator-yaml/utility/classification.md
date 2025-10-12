---
title: "Classification Task"
weight: 1
---

Evaluate synthetic data utility for classification problems.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-classification.ipynb)

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
  classification_utility:
    method: mlutility
    task_type: classification
    target: income                       # Target column (required)
    experiment_design: domain_transfer   # Experiment design (default: domain_transfer)
    resampling: None                     # Imbalance handling (default none, omit if not needed)
    metrics:                             # Evaluation metrics
      - mcc
      - f1_score
      - roc_auc
      - accuracy
    random_state: 42                     # Random seed (default: 42)
    xgb_params:                          # XGBoost parameters (omit if not needed)
      scale_pos_weight: 3                # Positive class weight ratio (default: 1)
      max_depth: 5                       # Maximum tree depth (default: 6)
      min_child_weight: 3                # Minimum sum of instance weight in a child (default: 1)
      subsample: 0.8                     # Sample ratio per tree (default: 1.0)
      colsample_bytree: 0.8              # Feature ratio per tree (default: 1.0)
```

## Task-Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **target** | `string` | Required | Target variable column name for classification |
| **resampling** | `string` | None | Imbalanced data handling: omit for none, or use `smote-enn`, `smote-tomek` |
| **metrics** | `array` | See below | Evaluation metrics to calculate |
| **xgb_params** | `dict` | None | XGBoost hyperparameters (omit for defaults) |

### Default Metrics
- `f1_score`, `roc_auc`, `accuracy`
- `precision`, `recall`, `specificity`
- `mcc`, `pr_auc`
- `tp`, `tn`, `fp`, `fn`

### XGBoost Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_estimators` | 100 | Number of boosting rounds (trees) |
| `max_depth` | 6 | Maximum tree depth |
| `learning_rate` | 0.3 | Learning rate (eta) |
| `subsample` | 1.0 | Sample ratio per tree |
| `colsample_bytree` | 1.0 | Feature ratio per tree |
| `scale_pos_weight` | 1 | Weight ratio for positive class (for imbalanced data) |
| `min_child_weight` | 1 | Minimum sum of instance weight in a child |

{{< callout type="info" >}}
If you don't need to adjust XGBoost parameters, you can omit the entire `xgb_params` block and the system will use default values.
{{< /callout >}}

For detailed parameter descriptions and tuning guidance, please refer to the [XGBoost documentation](https://xgboost.readthedocs.io/en/stable/parameter.html).

## Supported Metrics

| Metric | Description | Range | Default |
|--------|-------------|-------|---------|
| `f1_score` | Harmonic mean of precision and recall | 0-1 | ✓ |
| `roc_auc` | Area under ROC curve | 0-1 | ✓ |
| `accuracy` | Overall correct predictions | 0-1 | ✓ |
| `precision` | True positives / (True positives + False positives) | 0-1 | ✓ |
| `recall` | True positives / (True positives + False negatives) | 0-1 | ✓ |
| `specificity` | True negatives / (True negatives + False positives) | 0-1 | ✓ |
| `mcc` | Matthews Correlation Coefficient | -1 to 1 | ✓ |
| `pr_auc` | Area under Precision-Recall curve | 0-1 | ✓ |
| `tp` | True positives (count) | ≥0 | ✓ |
| `tn` | True negatives (count) | ≥0 | ✓ |
| `fp` | False positives (count) | ≥0 | ✓ |
| `fn` | False negatives (count) | ≥0 | ✓ |
| `sensitivity` | Same as recall | 0-1 | ✗ |

## Key Metrics Recommendations

### Standard Classification

| Metric | Description | Recommended Standard |
|--------|-------------|---------------------|
| **F1 Score** | Balance between precision and recall | ≥ 0.7 |
| **ROC AUC** | Comprehensive performance across all thresholds | ≥ 0.8 |

### Imbalanced Classification

| Metric | Description | Recommended Standard |
|--------|-------------|---------------------|
| **PR AUC** | Performance on minority class (not diluted by negatives) | ≥ 0.3* |
| **MCC** | Balanced measure considering all confusion matrix elements | ≥ 0.5 |

*PR AUC standard varies with imbalance ratio:
- Mild imbalance (10-20% minority): ≥ 0.5
- Moderate imbalance (5-10% minority): ≥ 0.3
- Severe imbalance (<5% minority): ≥ 0.2

## Handling Imbalanced Data

### When to Use Resampling

- **Class imbalance > 10:1**: Consider resampling
- **Minority class < 10%**: Strongly recommended
- **Minority class < 1%**: Essential

### Resampling Methods

**SMOTE-ENN**: Synthesizes minority class samples and aggressively removes noise, suitable for noisy data with unclear boundaries.

**SMOTE-Tomek**: Synthesizes minority class samples and conservatively removes boundary conflicts, suitable for cleaner data with overlapping classes.

{{< callout type="info" >}}
Resampling is only applied to training data (ori and syn), never to test data (control).
{{< /callout >}}