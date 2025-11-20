---
title: "Evaluator YAML"
type: docs
weight: 690
prev: docs/petsard-yaml/describer-yaml
next: docs/petsard-yaml/reporter-yaml
---

YAML configuration file format for the Evaluator module.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/evaluator.ipynb)
> **Note**: If using Colab, please see the [runtime setup guide](/petsard/docs/#colab-execution-guide).

### Recommended Evaluation Workflow

We recommend the following evaluation workflow to ensure synthetic data meets requirements:

#### 1. Evaluation Workflow Overview

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-overview.en.mmd" >}}

#### 2. Data Diagnostics Standard

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-diagnostic.en.mmd" >}}

#### 3. Privacy Protection Standard

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-privacy.en.mmd" >}}

#### 4. Data Fidelity Standard

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-fidelity.en.mmd" >}}

#### 5. Data Utility Standard

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-utility.en.mmd" >}}

> **Legend:**
> - Light blue boxes: Start/End points
> - White boxes: Evaluation steps
> - Diamond shapes: Decision points
> - Green boxes: Success outcomes
> - Red boxes: Failure states requiring action
> - Yellow boxes: Improvement needed
> - Orange boxes: Assessment methods

### 1. Foundation Evaluation (Required)

First, confirm data **validity** and **privacy protection**:

### 2. Goal-Oriented Evaluation

After passing foundation evaluation, choose evaluation focus based on the **intended use** of synthetic data:

#### Scenario A: Data Release (No Specific Downstream Task)

If synthetic data will be released publicly, pursue **highest fidelity**:

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
  # Step 1: Data validity diagnosis (should be close to 1.0)
  validity_check:
    method: sdmetrics-diagnosticreport
  # Step 2: Privacy protection assessment (risk should be < 0.09)
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    max_attempts: 4000
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
    method: anonymeter-inference
    secret: income
  # Focus: Pursue high fidelity (higher score is better)
  fidelity_assessment:
    method: sdmetrics-qualityreport
  # Utility evaluation is optional (not necessary)
```

#### Scenario B: Specific Task Application (Data Augmentation, Model Training, etc.)

If synthetic data is for specific machine learning tasks, pursue **high utility**:

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
  # Step 1: Data validity diagnosis (should be close to 1.0)
  validity_check:
    method: sdmetrics-diagnosticreport
  # Step 2: Privacy protection assessment (risk should be < 0.09)
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    max_attempts: 4000
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
    method: anonymeter-inference
    secret: income
  # Fidelity just needs to meet threshold (≥ 0.75)
  fidelity_assessment:
    method: sdmetrics-qualityreport
  # Focus: Pursue high utility (evaluate by task type)
  ml_utility_assessment:
    method: mlutility
    task_type: classification  # or regression/clustering
    target: income
```

## Main Parameters

- **method** (`string`, required)
  - Evaluation method name
  - See supported methods in the table below

## Supported Evaluation Methods

| Type | Method Name | Description | Recommended Standard |
|------|-------------|-------------|---------------------|
| **Default Method** | `default` | Default evaluation (equivalent to `sdmetrics-qualityreport`) | Score ≥ 0.75¹ |
| **Data Validity** | `sdmetrics-diagnosticreport` | Check data structure and basic characteristics | Score ≈ 1.0² |
| **Privacy Protection** | `anonymeter-singlingout` | Singling out risk assessment | Risk < 0.09³ |
| | `anonymeter-linkability` | Linkability risk assessment | Risk < 0.09³ |
| | `anonymeter-inference` | Inference risk assessment | Risk < 0.09³ |
| **Data Fidelity** | `sdmetrics-qualityreport` | Statistical distribution similarity assessment | Score ≥ 0.75¹ |
| **Data Utility** | `mlutility` | Machine learning model utility | Task-dependent⁴ |
| **Custom Assessment** | `custom_method` | Custom evaluation method | - |

### Recommended Standards Notes

¹ **Fidelity Standard** (Score ≥ 0.75): Based on statistical distribution similarity

² **Validity Standard** (Score ≈ 1.0): Data structure integrity check

³ **Privacy Risk Standard** (Risk < 0.09): Based on PDPC Singapore guidelines

⁴ **Utility Standard** (Task-dependent):
- Classification tasks (XGBoost): F1 ≥ 0.7
- Regression tasks (XGBoost): R² ≥ 0.7
- Clustering tasks (K-means): Silhouette coefficient ≥ 0.5

> **Default Method**: When `method: default` is used, the system automatically executes `sdmetrics-qualityreport` to evaluate data fidelity.

> **Threshold Adjustment**: The above recommended standards are general reference values. Please adjust appropriate thresholds based on your specific use case and risk tolerance. For detailed theoretical foundations and references for each metric, please refer to the corresponding subdocumentation.

## Execution Notes

- Evaluation of large datasets may require significant time, especially for Anonymeter methods
- Recommend executing evaluations sequentially, ensuring prerequisites are met before proceeding