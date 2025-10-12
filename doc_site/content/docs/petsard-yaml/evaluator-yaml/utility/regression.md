---
title: "Regression Task"
weight: 2
---

Evaluate synthetic data utility for regression problems.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-regression.ipynb)

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
  regression_utility:
    method: mlutility
    task_type: regression
    target: capital-gain                 # Target column (required)
    experiment_design: domain_transfer   # Experiment design (default: domain_transfer)
    metrics:                             # Evaluation metrics
      - r2_score
      - rmse
    random_state: 42                     # Random seed (default: 42)
    xgb_params:                          # XGBoost parameters (omit if not needed)
      n_estimators: 200                  # Number of trees (default: 100)
      max_depth: 8                       # Maximum tree depth (default: 6)
```

## Task-Specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **target** | `string` | Required | Target variable column name for regression |
| **metrics** | `array` | See below | Evaluation metrics to calculate |
| **xgb_params** | `dict` | None | XGBoost hyperparameters (omit for defaults) |

### Default Metrics
- `r2_score`, `rmse`

### XGBoost Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_estimators` | 100 | Number of boosting rounds (trees) |
| `max_depth` | 6 | Maximum tree depth |
| `learning_rate` | 0.3 | Learning rate (eta) |
| `subsample` | 1.0 | Sample ratio per tree |
| `colsample_bytree` | 1.0 | Feature ratio per tree |
| `min_child_weight` | 1 | Minimum sum of instance weight in a child |

{{< callout type="info" >}}
If you don't need to adjust XGBoost parameters, you can omit the entire `xgb_params` block and the system will use default values.
{{< /callout >}}

For detailed parameter descriptions and tuning guidance, please refer to the [XGBoost documentation](https://xgboost.readthedocs.io/en/stable/parameter.html).

## Supported Metrics

| Metric | Description | Range | Default | Use Case |
|--------|-------------|-------|---------|----------|
| `r2_score` | Coefficient of determination | -∞ to 1 | ✓ | Primary metric for cross-dataset comparison |
| `rmse` | Root Mean Squared Error | 0-∞ | ✓ | Understand prediction errors, penalizes large errors |
| `mse` | Mean Squared Error | 0-∞ | ✗ | Convenient for optimization, but units are squared |
| `mae` | Mean Absolute Error | 0-∞ | ✗ | More robust when data has outliers |
| `mape` | Mean Absolute Percentage Error | 0-∞ | ✗ | For relative errors, avoid when data contains zeros |

## Key Metrics Recommendations

### Primary Evaluation Criteria

| Metric | Excellent | Good | Acceptable | Needs Improvement |
|--------|-----------|------|------------|-------------------|
| **R²** | ≥ 0.9 | ≥ 0.7 | ≥ 0.5 | < 0.5 |
| **RMSE** | < Y_StdDev×0.3 | < Y_StdDev×0.5 | < Y_StdDev×0.7 | ≥ Y_StdDev×0.7 |

*Y_StdDev: Standard deviation of the target variable (target column)

### Synthetic Data Utility Assessment

For dual_model_control design, compare ori vs syn differences:

| Grade | R² Difference | RMSE Increase |
|-------|---------------|---------------|
| Excellent | < 0.05 | < 10% |
| Good | < 0.10 | < 20% |
| Acceptable | < 0.20 | < 30% |
| Needs Improvement | ≥ 0.20 | ≥ 30% |

{{< callout type="info" >}}
**RMSE Interpretation**:
- RMSE absolute values must be interpreted in context of data range
- RMSE/Y_StdDev ratio (Normalized RMSE) provides a unitless performance metric
- Example: House price prediction (unit: $10k) RMSE = 10 might be good; Temperature prediction (unit: °C) RMSE = 10 might be poor
{{< /callout >}}

## Usage Considerations

### When to Use Regression

- **Continuous target variable**: Price, temperature, score, etc.
- **Numerical predictions needed**: Forecasting, estimation
- **All features are numerical**: Often indicates regression suitability

### Data Preprocessing

The evaluator automatically:
1. Removes missing values
2. Encodes categorical variables (OneHotEncoder)
3. Standardizes numerical features
4. Standardizes target variable

### Model Details

- **Algorithm**: XGBoost Regressor
- **Objective**: Minimize squared error
- **Feature importance**: Available through XGBoost

{{< callout type="info" >}}
For highly skewed target distributions, consider log transformation before evaluation.
{{< /callout >}}

## References

1. Despotovic, M., Nedic, V., Despotovic, D., & Cvetanovic, S. (2016). Evaluation of empirical models for predicting monthly mean horizontal diffuse solar radiation. *Renewable and Sustainable Energy Reviews*, 56, 246-260.

2. Chai, T., & Draxler, R. R. (2014). Root mean square error (RMSE) or mean absolute error (MAE)?–Arguments against avoiding RMSE in the literature. *Geoscientific model development*, 7(3), 1247-1250.