---
title: Data Synthesis and Evaluation with Default Parameters
type: docs
weight: 120
prev: docs/getting-started/default-synthesis
next: docs/getting-started/external-synthesis-default-evaluation
---

Default synthesis with default evaluation.
Current default evaluation uses SDMetrics Quality Report.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/getting-started/default-synthesis-default-evaluation.ipynb)

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
Splitter:
  basic_split:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: 'default'
Synthesizer:
  default:
    method: 'default'
Postprocessor:
  default:
    method: 'default'
Evaluator:
  validity_check:
    method: sdmetrics-diagnosticreport
  fidelity_check:
    method: sdmetrics-qualityreport
  singling_out_risk:
    method: anonymeter-singlingout
  linkability_risk:
    method: anonymeter-linkability
    aux_cols:
      -
        - workclass
        - education
        - occupation
        - race
        - gender
      -
        - age
        - marital-status
        - relationship
        - native-country
        - income
  inference_risk:
    method: 'anonymeter-inference'
    secret: 'income'
  classification_utility:
    method: mlutility
    task_type: classification
    target: income
Reporter:
  data:
    method: 'save_data'
    source: 'Postprocessor'
  rpt:
    method: 'save_report'
    granularity:
      - 'global'
      - 'columnwise'
      - 'pairwise'
      - 'details'
```

## YAML Parameters Detailed Explanation

### Loader, Preprocessor, Synthesizer, Postprocessor

For parameter descriptions of these modules, please refer to the [Default Synthesis Tutorial](../default-synthesis).

### Splitter (Data Splitting Module)

- **`basic_split`**: Experiment name, can be freely named
- **`num_samples`**: Number of repeated sampling
  - Value: `1`
  - Description: At least one validation group is needed to evaluate privacy protection
  - This split is essential for Anonymeter evaluation, as it needs to compare training and testing data to assess privacy risks
  - Default value: 1
- **`train_split_ratio`**: Proportion of data for training set
  - Value: `0.8`
  - Description: Uses 80% of data for training set and 20% for testing set
  - This is a common practice for cross-validation
  - Range: 0.0 to 1.0
  - Default value: 0.8

### Evaluator (Data Evaluation Module)

This example includes multiple evaluation methods covering data validity, privacy protection, fidelity, and utility:

#### validity_check (Data Validity Diagnosis)
- **`method`**: `sdmetrics-diagnosticreport`
- **Description**: Checks data structure and basic properties
- **Standard**: Diagnosis score should approach 1.0

#### fidelity_check (Data Fidelity Evaluation)
- **`method`**: `sdmetrics-qualityreport`
- **Description**: Evaluates statistical distribution similarity between synthetic and original data
- **Standard**: Fidelity score should be above 0.75

#### singling_out_risk (Singling Out Risk Evaluation)
- **`method`**: `anonymeter-singlingout`
- **Description**: Evaluates whether attackers can identify specific individuals from synthetic data
- **Standard**: Risk score should be below 0.09

#### linkability_risk (Linkability Risk Evaluation)
- **`method`**: `anonymeter-linkability`
- **`aux_cols`**: Auxiliary column combinations
  - Description: Groups variables based on domain knowledge for linkability attack evaluation
  - First group: Employment and demographic data (workclass, education, occupation, race, gender)
  - Second group: Personal status and income data (age, marital-status, relationship, native-country, income)

#### inference_risk (Inference Risk Evaluation)
- **`method`**: `anonymeter-inference`
- **`secret`**: Sensitive column
  - Value: `income`
  - Description: Sets the most sensitive column as secret to evaluate whether attackers can infer its value

#### classification_utility (Classification Utility Evaluation)
- **`method`**: `mlutility`
- **`task_type`**: Task type
  - Value: `classification`
  - Description: Specifies the machine learning task as classification
- **`target`**: Target variable
  - Value: `income`
  - Description: Evaluates the performance of classification models trained on synthetic data
  - This should align with actual analysis objectives

### Reporter (Output Module)

For the description of the `save_data` method, please refer to the [Default Synthesis Tutorial](../default-synthesis/#reporter-output-module).

This example additionally uses the `save_report` method to save evaluation reports:

#### rpt (Save Evaluation Report)
- **`method`**: `save_report`
- **`granularity`**: Report granularity levels
  - Value: `[global, columnwise, pairwise, details]`
  - Description: Outputs evaluation results at different granularity levels
    - **global**: Overall scores at the global level
    - **columnwise**: Individual scores for each column
    - **pairwise**: Scores for inter-column correlations
    - **details**: Detailed evaluation data

## Execution Flow

1. **Loader** loads the [`adult-income.csv`](benchmark/adult-income.csv) data
2. **Splitter** splits data into training set (80%) and testing set (20%)
3. **Preprocessor** performs preprocessing on training set (impute missing values, handle outliers, encode, scale)
4. **Synthesizer** generates synthetic data on training set using Gaussian Copula method
5. **Postprocessor** restores synthetic data to original format (reverse scaling, reverse encoding, insert missing values)
6. **Evaluator** performs multiple evaluations:
   - Data validity diagnosis
   - Privacy risk assessment (singling out, linkability, inference)
   - Data fidelity assessment
   - Machine learning utility assessment
7. **Reporter** saves synthetic data and multi-level evaluation reports

## Evaluation Overview

The evaluation of synthetic data requires balancing three key aspects:
1. Protection - assessing security level
2. Fidelity - measuring similarity with original data
3. Utility - evaluating practical performance

> Note: These three aspects often involve trade-offs. Higher protection might lead to lower fidelity, and high fidelity might result in lower protection.

## Evaluation Parameters

1. `Splitter`:
  - `num_samples: 1`: At least one validation group for evaluating privacy protection. This split is essential for Anonymeter to assess privacy risks by comparing training and testing data
  - `train_split_ratio: 0.8`: Split the dataset with 80% for training and 20% for testing, which is a common practice for cross-validation

2. `Evaluator`:
  - For linkability risk, `aux_cols` groups variables based on domain knowledge, such as personal demographic information and employment-related data
  - For inference risk, choose the most sensitive field (income) as the `secret` column
  - For classification utility, use the main `target` variable (income) that aligns with the actual analysis goal

## Evaluation Process

Follow these steps to evaluate your synthetic data:

1. **Data Validity Diagnosis** (using SDMetrics)
  - Goal: Ensure schema consistency
  - Standard: Diagnosis score should reach 1.0
  - Why: Valid data is the foundation for all subsequent analysis

2. **Privacy Protection Assessment** (using Anonymeter)
  - Goal: Verify privacy protection level
  - Standard: Risk score should be below 0.09
  - Evaluates: Singling out, linkability, and inference risks
  > Note: A risk score of 0.0 does NOT mean zero risk. Always implement additional protection measures.

3. **Application-Specific Assessment**

  Based on your use case, focus on either:

  A. No Specific Task (Data Release Scenario):
  - Focus on Data Fidelity (using SDMetrics)
  - Standard: Fidelity score above 0.75
  - Measures: Distribution similarity and correlation preservation

  B. Specific Task (Model Training Scenario):
  - Focus on Data Utility
  - Standards vary by task type:
    * Classification: ROC AUC > 0.8
    * Clustering: Silhouette > 0.5
    * Regression: Adjusted R² > 0.7
  > Note: ROC AUC (Receiver Operating Characteristic Area Under Curve) measures the model's ability to distinguish between classes

