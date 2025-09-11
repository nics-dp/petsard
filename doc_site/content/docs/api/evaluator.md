---
title: Evaluator
type: docs
weight: 58
prev: docs/api/constrainer
next: docs/api/describer
---


```python
Evaluator(method, **kwargs)
```

Synthetic data quality evaluator providing privacy risk metrics, data quality assessment, and machine learning utility analysis.

## Parameters

- `method` (`str`): Evaluation method (case-insensitive):

  - Privacy Risk Assessment (Anonymeter):
    - 'anonymeter-singlingout': Singling out risk
    - 'anonymeter-linkability': Linkability risk
    - 'anonymeter-inference': Inference risk

  - Data Quality Assessment (SDMetrics):
    - 'sdmetrics-diagnosticreport': Data validity report
    - 'sdmetrics-qualityreport': Data quality report

  - Machine Learning Utility Assessment (MLUtility - Legacy):
    - 'mlutility-classification': Classification utility (using multiple models)
    - 'mlutility-regression': Regression utility (using multiple models)
    - 'mlutility-cluster': Clustering utility (K-means)

  - Machine Learning Utility Assessment (MLUtility - New, Recommended):
    - 'mlutility' with `task_type` parameter:
      - `task_type='classification'`: Classification utility (using XGBoost)
      - `task_type='regression'`: Regression utility (using XGBoost)
      - `task_type='clustering'`: Clustering utility (K-means)

  - 'default': Uses 'sdmetrics-qualityreport'
  - 'stats': Statistical evaluation, comparing the statistical differences before and after synthesis
  - 'custom_method': Custom evaluation method. To be used with:
    - `module_path` (str): Evaluation method file path
    - `class_name` (str): Evaluation method name

## Examples

```python
from petsard import Evaluator


eval_result: dict[str, pd.DataFrame] = None

# Privacy risk assessment
eval = Evaluator('anonymeter-singlingout')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
privacy_risk: pd.DataFrame = eval_result['global']

# Data quality assessment
eval = Evaluator('sdmetrics-qualityreport')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data
})
quality_score: pd.DataFrame = eval_result['global']
```

## Methods

### `create()`

Initial evaluator

**Parameters**

None

**Returns**

None

### `eval()`

```python
eval.eval(data)
```

Perform evaluation.

**Parameters**

- `data` (dict): Evaluation data
  - For Anonymeter and MLUtility:
    - 'ori': Original data used for synthesis (pd.DataFrame)
    - 'syn': Synthetic data (pd.DataFrame)
    - 'control': Control data not used for synthesis (pd.DataFrame)
  - For SDMetrics:
    - 'ori': Original data (pd.DataFrame)
    - 'syn': Synthetic data (pd.DataFrame)

**Returns**

`(dict[str, pd.DataFrame])`, varies by module:
  - 'global': Single row dataframe representing overall dataset evaluation results
  - 'columnwise': Column-level evaluation results, each row representing evaluation results for one column
  - 'pairwise': Column pair evaluation results, each row representing evaluation results for a pair of columns
  - 'details': Other detailed information

## Attributes

- `config` (`EvaluatorConfig`): Evaluator configuration containing `method` and `method_code`

## Appendix: Supported Evaluation Methods

### Supported Evaluation Methods

The evaluator supports three major categories of evaluation methods:

- **Privacy Risk Assessment** used to evaluate the privacy protection level of synthetic data. Including:
  - **Singling Out Risk**: Evaluates whether specific individuals can be identified from the data
  - **Linkability Risk**: Evaluates whether the same individual can be linked across different datasets
  - **Inference Risk**: Evaluates whether other attributes can be inferred from known information

- **Data Fidelity Assessment** used to evaluate the fidelity of synthetic data. Including:
  - **Diagnostic Report**: Examines data structure and basic characteristics
  - **Quality Report**: Evaluates the similarity of statistical distributions

- **Data Utility Assessment** used to evaluate the practical value of synthetic data. Including:
  - **Classification Utility**: Compares classification model performance
  - **Regression Utility**: Compares regression model performance
  - **Clustering Utility**: Compares clustering results

- **Statistical Assessment** used to compare statistical differences before and after synthesis. Including:
  - **Statistical Comparison**: Compares statistical measures such as mean, standard deviation, median, etc.
  - **Distribution Comparison**: Compares distribution differences such as Jensen-Shannon divergence

- **Custom Assessment** used to integrate user-defined evaluation methods.

| Evaluation Type | Evaluation Method | Method Name |
| :---: | :---: | :---: |
| Privacy Risk Assessment | Singling Out Risk | anonymeter-singlingout |
| Privacy Risk Assessment | Linkability Risk | anonymeter-linkability |
| Privacy Risk Assessment | Inference Risk | anonymeter-inference |
| Data Fidelity Assessment | Diagnostic Report | sdmetrics-diagnosticreport |
| Data Fidelity Assessment | Quality Report | sdmetrics-qualityreport |
| Data Utility Assessment (Legacy) | Classification Utility | mlutility-classification |
| Data Utility Assessment (Legacy) | Regression Utility | mlutility-regression |
| Data Utility Assessment (Legacy) | Clustering Utility | mlutility-cluster |
| Data Utility Assessment (New) | Classification/Regression/Clustering Utility | mlutility |
| Statistical Assessment | Statistical Comparison | stats |
| Custom Assessment | Custom Method | custom_method |

### Privacy Risk Assessment

#### Singling Out Risk Assessment

Evaluates whether specific individual records can be identified from the data. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts (unique queries)
- 'n_cols' (`int`, default=3): Number of columns used in each query
- 'max_attempts' (`int`, default=500000): Maximum number of attempts to find successful attacks

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'risk': Privacy risk score (0-1)
  - 'risk_CI_btm': Lower bound of privacy risk confidence interval
  - 'risk_CI_top': Upper bound of privacy risk confidence interval
  - 'attack_rate': Main privacy attack success rate
  - 'attack_rate_err': Error of main privacy attack success rate
  - 'baseline_rate': Baseline privacy attack success rate
  - 'baseline_rate_err': Error of baseline privacy attack success rate
  - 'control_rate': Control group privacy attack success rate
  - 'control_rate_err': Error of control group privacy attack success rate

#### Linkability Risk Assessment

Evaluates whether records belonging to the same individual can be linked across different datasets. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts
- 'max_n_attacks' (`bool`, default=False): Whether to force using the maximum number of attacks
- 'aux_cols' (`Tuple[List[str], List[str]]`): Auxiliary information columns, for example:
    ```python
    aux_cols = [
        ['gender', 'zip_code'],  # Public data
        ['age', 'medical_history']    # Private data
    ]
    ```
- 'n_neighbors' (`int`, default=10): Number of nearest neighbors to consider

**Returns**

- `pd.DataFrame`: Evaluation result dataframe in the same format as the singling out risk assessment

#### Inference Risk Assessment

Evaluates whether other attributes can be inferred from known information. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts
- 'max_n_attacks' (`bool`, default=False): Whether to force using the maximum number of attacks
- 'secret' (`str`): The attribute to be inferred
- 'aux_cols' (`List[str]`, optional): Columns used for inference, defaults to all columns except the 'secret'

**Returns**

- `pd.DataFrame`: Evaluation result dataframe in the same format as the singling out risk assessment

### Data Fidelity Assessment

#### Diagnostic Report

Validates the structure and basic characteristics of synthetic data.

**Parameters**

None

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'Score': Overall diagnostic score
  - 'Data Validity': Data validity score
    - 'KeyUniqueness': Primary key uniqueness
    - 'BoundaryAdherence': Numerical range compliance
    - 'CategoryAdherence': Category compliance
  - 'Data Structure': Data structure score
    - 'Column Existence': Column existence
    - 'Column Type': Column type compliance

#### Quality Report

Evaluates the statistical similarity between original and synthetic data.

**Parameters**

None

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'Score': Overall validity score
  - 'Column Shapes': Column distribution similarity
    - 'KSComplement': Continuous variable distribution similarity
    - 'TVComplement': Categorical variable distribution similarity
  - 'Column Pair Trends': Column relationship preservation
    - 'Correlation Similarity': Correlation preservation
    - 'Contingency Similarity': Contingency table similarity

### Data Utility Assessment - Legacy (MLUtility V1)

Uses multiple models to evaluate machine learning utility of synthetic data.

#### Classification Utility Assessment (Legacy)

**Models Used**
- Logistic Regression
- Support Vector Classifier (SVC)
- Random Forest Classifier
- Gradient Boosting Classifier

**Parameters**
- 'eval_method' (`str`): `'mlutility-classification'`
- 'target' (`str`): Classification target column

#### Regression Utility Assessment (Legacy)

**Models Used**
- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

**Parameters**
- 'eval_method' (`str`): `'mlutility-regression'`
- 'target' (`str`): Regression target column

#### Clustering Utility Assessment (Legacy)

**Models Used**
- K-means (iterating over multiple cluster numbers)

**Parameters**
- 'eval_method' (`str`): `'mlutility-cluster'`
- 'n_clusters' (`list`, default=[4, 5, 6]): List of cluster numbers

### Data Utility Assessment - New (MLUtility, Recommended)

Uses simplified single-model architecture (XGBoost) to evaluate machine learning utility of synthetic data.

**Preprocessing Pipeline**:
  1. **Missing Value Handling**: Remove rows with missing values
  2. **Feature Separation**: Distinguish numerical and categorical features
  3. **Categorical Encoding**: Use OneHotEncoder (sparse_output=False, handle_unknown='ignore')
     - Train encoders using only ori and syn data to avoid data leakage
     - Unseen categories in control are encoded as zero vectors
  4. **Feature Standardization**: Use StandardScaler to standardize combined feature matrix
     - Use only ori and syn data to calculate mean and standard deviation
  5. **Target Variable Processing**:
     - Classification: Automatically detect target column type
       - If already numerical: Use directly without encoding
       - If categorical: Use LabelEncoder (trained on ori + syn only)
     - Regression: Use StandardScaler to standardize (parameters from ori + syn only)
     - Clustering: No target variable
  6. **Imbalanced Data Handling** (classification only, training data only):
     - If `resampling` enabled, apply imbalanced handling on training data
     - `'smote-enn'` (recommended): SMOTE + ENN
       - SMOTE: Synthesize minority class samples
       - ENN (Edited Nearest Neighbors): Remove noisy samples, more aggressive cleaning strategy
     - `'smote-tomek'`: SMOTE + Tomek Links
       - SMOTE: Synthesize minority class samples
       - Tomek Links: Clean boundary samples, more conservative cleaning strategy
     - Note: No resampling on test data (control) to maintain real distribution
  7. **Constant Target Check**: Abort evaluation if target column is constant

**Experimental Design Options**:
MLUtility supports two experimental design modes for different evaluation needs:

  1. **Dual Model Control** (**dual_model_control**)
     - **Purpose**: Evaluate if synthetic data can directly replace original data for model development
     - **Process**:
       1. Train model with ori → Test on control
       2. Train model with syn → Test on control
       3. Compare performance on control
     - **Required Data**: ori, syn, control
     - **Use Case**: When you want to know if models trained on synthetic data can achieve similar performance as those trained on original data

  2. **Domain Transfer** (**domain_transfer**)
     - **Purpose**: Evaluate deployment performance of models trained on synthetic data in real environments
     - **Process**:
       1. Train model with syn → Test on ori
       2. Evaluate domain transfer capability
     - **Required Data**: ori, syn
     - **Use Case**: When you want to know if models trained on synthetic data can work well on real data

#### Classification Utility Assessment

Evaluates synthetic data utility in classification tasks using XGBoost classifier.

**Model Used**
- XGBoost Classifier (XGBClassifier)

**Parameters**
- 'eval_method' (`str`): Evaluation method name `'mlutility'`
- 'task_type' (`str`): Task type `'classification'`
- 'experiment_design' (`str`, default='dual_model_control'): Experimental design
  - `'dual_model_control'`: Dual model control - ori and syn train separately, test on control
  - `'domain_transfer'`: Domain transfer - train with syn, test on ori (evaluate synthetic data domain transfer capability)
- 'resampling' (`str`, optional): Imbalanced data handling method (classification only)
  - `None` (default): No imbalanced handling
  - `'smote-enn'`: Use SMOTE-ENN for imbalanced handling (recommended)
    - SMOTE (Synthetic Minority Over-sampling Technique): Synthesize new samples for minority class
    - ENN (Edited Nearest Neighbors): Use k-NN to remove noisy samples, more aggressive cleaning
    - Supports binary and multi-class classification
    - Suitable for datasets with more noise
  - `'smote-tomek'`: Use SMOTE-Tomek for imbalanced handling
    - SMOTE: Synthesize new samples for minority class
    - Tomek Links: Remove boundary sample pairs, more conservative cleaning
    - Supports binary and multi-class classification
    - Suitable for datasets with unclear boundaries
  - Only applied to training data (ori/syn), not test data (control)
- 'target' (`str`): Classification target column (supports numerical or categorical types, automatically detected)
- 'metrics' (`list[str]`, optional): List of evaluation metrics, default:
  - `['mcc', 'f1_score', 'roc_auc', 'pr_auc', 'accuracy', 'balanced_accuracy', 'precision', 'recall', 'specificity', 'tp', 'tn', 'fp', 'fn']`
- 'xgb_params' (`dict`, optional): Additional XGBoost parameters
- 'random_state' (`int`, default=42): Random seed

**Supported Evaluation Metrics**

Basic Classification Metrics:
- `accuracy`: Accuracy
- `balanced_accuracy`: Balanced accuracy (sklearn.metrics.balanced_accuracy_score)
- `f1_score`: F1 score (binary for binary, weighted average for multi-class)
- `f2_score`: F2 score (beta=2)
- `f0.5_score`: F0.5 score (beta=0.5)
- `precision`: Precision (zero_division=0)
- `recall`: Recall
- `mcc`: Matthews correlation coefficient (sklearn.metrics.matthews_corrcoef)
- `cohen_kappa`: Cohen's Kappa coefficient (sklearn.metrics.cohen_kappa_score)
- `jaccard`: Jaccard similarity (sklearn.metrics.jaccard_score)

Probability Metrics:
- `roc_auc`: Area under ROC curve (direct for binary, OvR + weighted for multi-class)
- `pr_auc`: Area under Precision-Recall curve (using sklearn.metrics.auc)
- `log_loss`: Log loss (sklearn.metrics.log_loss)
- `brier_score`: Brier score (binary classification only, sklearn.metrics.brier_score_loss)

Confusion Matrix Derived Metrics:
- `tp`, `tn`, `fp`, `fn`: True/False Positive/Negative counts
- `sensitivity` (=TPR=recall): Sensitivity
- `specificity` (=TNR): Specificity
- `ppv` (=precision): Positive predictive value
- `npv`: Negative predictive value
- `fpr`: False positive rate
- `fnr`: False negative rate
- `fdr`: False discovery rate
- `for`: False omission rate
- `informedness`: Youden's J statistic (TPR + TNR - 1)
- `markedness`: Markedness (PPV + NPV - 1)
- `prevalence`: Prevalence
- `dor`: Diagnostic odds ratio

**Returns**
- `dict[str, pd.DataFrame]`:
  - 'global': Overall evaluation results
    - **Dual Model Control mode** includes:
      - 'metric': Metric name
      - 'ori': Original data model score on control
      - 'syn': Synthetic data model score on control
      - 'diff': syn - ori
    - **Domain Transfer mode** includes:
      - 'metric': Metric name
      - 'syn_to_ori': Synthetic data model score on original data
  - 'details': Detailed metric values for each dataset

#### Regression Utility Assessment

Evaluates synthetic data utility in regression tasks using XGBoost regressor.

**Model Used**
- XGBoost Regressor (XGBRegressor)

**Parameters**
- 'eval_method' (`str`): Evaluation method name `'mlutility'`
- 'task_type' (`str`): Task type `'regression'`
- 'experiment_design' (`str`, default='dual_model_control'): Experimental design (same as classification)
- 'target' (`str`): Regression target column (must be numerical)
- 'metrics' (`list[str]`, optional): List of evaluation metrics, default: `['r2_score', 'mse', 'mae', 'rmse']`
- 'xgb_params' (`dict`, optional): Additional XGBoost parameters
- 'random_state' (`int`, default=42): Random seed

**Supported Evaluation Metrics**
- `r2_score`: Coefficient of determination (sklearn.metrics.r2_score)
- `mse`: Mean squared error (sklearn.metrics.mean_squared_error)
- `mae`: Mean absolute error (sklearn.metrics.mean_absolute_error)
- `rmse`: Root mean squared error (sqrt(MSE))
- `mape`: Mean absolute percentage error

**Returns**
- Format same as classification task

#### Clustering Utility Assessment

Evaluates synthetic data clustering performance using K-means algorithm.

**Model Used**
- K-means clustering (sklearn.cluster.KMeans, n_init='auto')

**Parameters**
- 'eval_method' (`str`): Evaluation method name `'mlutility'`
- 'task_type' (`str`): Task type `'clustering'`
- 'experiment_design' (`str`, default='dual_model_control'): Experimental design (same as classification)
- 'n_clusters' (`int`, default=5): Number of clusters (fixed value, no iteration)
- 'metrics' (`list[str]`, optional): List of evaluation metrics, default: `['silhouette_score']`
- 'random_state' (`int`, default=42): Random seed

**Supported Evaluation Metrics**
- `silhouette_score`: Silhouette coefficient (sklearn.metrics.silhouette_score)
  - Values range from -1 to 1
  - Returns -1 when sample or cluster count is insufficient

**Returns**
- Format same as classification task

### Statistical Evaluation

Statistical evaluation compares statistical differences before and after data synthesis, supporting various statistical methods such as mean, standard deviation, median, minimum, maximum, number of unique values, and Jensen-Shannon divergence. It provides appropriate evaluation methods for both numerical and categorical data.

**Parameters**

- 'stats_method' (`list[str]`, default=["mean", "std", "median", "min", "max", "nunique", "jsdivergence"]): List of statistical methods
- 'compare_method' (`str`, default="pct_change"): Comparison method, options include "diff" (difference) or "pct_change" (percentage change)
- 'aggregated_method' (`str`, default="mean"): Aggregation method
- 'summary_method' (`str`, default="mean"): Summary method

**Return Value**

- `pd.DataFrame`: Dataframe containing statistical comparison results, including:
  - Statistical measures for each column (original and synthetic)
  - Differences or percentage changes between them
  - Overall score

### Custom Evaluation

Allows users to implement and integrate custom evaluation methods by specifying external module paths and class names to load custom evaluation logic.

**Parameters**

- 'module_path' (`str`): File path to the custom evaluation module
- 'class_name' (`str`): Name of the custom evaluation class
- Other parameters depending on the requirements of the custom evaluator

**Return Value**

- Depends on the implementation of the custom evaluator, but must follow the standard evaluator interface, returning a format of `dict[str, pd.DataFrame]`

**Required Methods for Custom Evaluators**

- `__init__(config)`: Initialization method
- `eval(data)`: Evaluation method that receives a data dictionary and returns evaluation results

**Required Attributes for Custom Evaluators**

- `REQUIRED_INPUT_KEYS`: List of required input data keys
- `AVAILABLE_SCORES_GRANULARITY`: List of supported evaluation granularities (such as "global", "columnwise")