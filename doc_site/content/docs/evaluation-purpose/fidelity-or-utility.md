---
title: Fidelity or Utility
type: docs
weight: 420
prev: docs/evaluation-purpose/privacy-risk-estimation
next: docs/evaluation-purpose/experiment-design-selection
---

After confirming that privacy protection meets standards, the next step is to determine the evaluation focus based on the intended use of synthetic data. Different application scenarios have different quality requirements for synthetic data: when synthetic data will be publicly released or shared with multiple unspecified recipients, high fidelity should be pursued to maintain data versatility; while when synthetic data is used for specific machine learning tasks (such as classification, regression, clustering), high utility should be pursued to ensure task performance.

## Differences Between Fidelity and Utility

Fidelity and Utility are two complementary aspects of evaluating synthetic data quality. Fidelity measures the similarity of synthetic data to original data in statistical properties, evaluated through statistical distribution comparison (such as SDMetrics Quality Report), suitable for data release or general-purpose scenarios. Utility measures the actual performance of synthetic data in specific tasks, evaluated through machine learning model effectiveness (ML Utility), suitable for specific task modeling scenarios.

Fidelity focuses on "what the data looks like," concerning whether statistical distributions and variable relationships are similar to original data; Utility focuses on "what the data can do," concerning whether it can achieve performance comparable to original data in specific tasks. It's worth noting that high fidelity does not necessarily guarantee high utility, and vice versa, so the choice of evaluation focus should be based on the actual use of the data.

### Evaluation Workflow Diagram

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-overview.zh-tw.mmd" >}}

## Considerations for Selecting Evaluation Focus

### Data Release Scenarios: Pursuing High Fidelity

When the use of synthetic data is undefined or needs to support multiple uses, fidelity should be the primary evaluation aspect. In public data release scenarios, since all possible uses cannot be foreseen, it is necessary to ensure that synthetic data is highly similar to original data in statistical properties, maintaining data versatility.

In this case, use SDMetrics Quality Report for evaluation, focusing on three aspects: distribution shape similarity of individual columns (Column Shapes), correlation preservation between columns (Column Pair Trends), and overall quality comprehensive score (Overall Score). According to differential privacy synthetic data evaluation benchmark research, the overall score should reach 0.75 or above as a quality standard.

Academic research sharing scenarios are similar to public release, but may require additional utility verification for specific domains, such as in biomedical fields where preservation of associations between specific biomarkers may need confirmation. Algorithm development scenarios similarly focus on fidelity, as algorithm design requires similar statistical properties of data to support testing and verification.

### Specific Task Modeling: Pursuing High Utility

When synthetic data has a clear downstream task, utility should be the primary evaluation aspect, with fidelity only needing to meet a basic threshold (≥ 0.75). Task type selection depends on data characteristics and domain knowledge: if data consists entirely of numerical features with no clear target variable, clustering tasks are most suitable; if there is a target variable, choose classification (categorical target) or regression (numerical target) tasks; if data mixes categorical and numerical features, any task type can be chosen based on actual use.

When evaluating, consider the expected use of data:
- **Predictive Modeling Scenarios**: Should choose classification or regression tasks
- **Pattern Discovery Scenarios**: Suitable for exploratory analysis using clustering
- **Risk Assessment Scenarios**: Classification tasks best provide clear insights

The key to utility evaluation lies in selecting appropriate evaluation metrics and experimental design.

#### Main Metrics for Classification Tasks

- **F1 Score**: Harmonic mean of precision and recall, general standard ≥ 0.7
- **ROC AUC**: Overall classification capability, general standard ≥ 0.8
- **MCC**: Matthews Correlation Coefficient, particularly important for imbalanced datasets, general standard ≥ 0.5

#### Main Metrics for Regression Tasks

- **R²**: Degree of variance explained by model, general standard ≥ 0.7

#### Main Metrics for Clustering Tasks

- **Silhouette Score**: Clustering quality, general standard ≥ 0.5

Regarding experimental design, the default uses domain transfer design (train on synthetic data, test on original data) to assess whether synthetic data captures basic patterns that can generalize to real data. It's particularly important to note that when data has high imbalance (e.g., fraud detection with positive class rate of only 1-2%), ROC AUC may produce misleadingly optimistic results. In this case, MCC should be prioritized as the main metric (as it considers all confusion matrix elements and is robust to imbalanced data), supplemented by PR AUC (Precision-Recall AUC, focusing on positive class quality).

## Practical Application Cases

### Case 1: Government Data Public Release

A government agency wishes to release synthetic census data for academic research use, with many recipients and unclear purposes. This scenario should prioritize ensuring data is highly similar to original data in statistical properties:

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
    n_attacks: 100
    max_attempts: 1000

  # Focus: Pursue high fidelity (higher score is better)
  fidelity_assessment:
    method: sdmetrics-qualityreport
```

When evaluating, confirm:
- Data validity score is close to 1.0
- All privacy risk indicators are below 0.09 (recommend below 0.07 for external release)
- Fidelity score reaches 0.75 or above as the main goal (higher score is better)

Fidelity evaluation focuses on three aspects:
- **Column Shapes**: Distribution shape similarity of individual columns, target ≥ 0.75
- **Column Pair Trends**: Correlation preservation between columns, target ≥ 0.75
- **Overall Score**: Overall quality comprehensive score, target ≥ 0.75

In this scenario, utility evaluation is not necessary unless there are specific domain requirements requiring additional verification.

### Case 2: Financial Institution Risk Model Development

A financial institution wishes to use synthetic data to train a credit risk prediction model, with the clear downstream task being binary classification (default vs. normal). This scenario should prioritize ensuring synthetic data can support effective model training:

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
    n_attacks: 100
    max_attempts: 1000

  # Fidelity reaching threshold is sufficient (≥ 0.75)
  quality_assessment:
    method: sdmetrics-qualityreport

  # Focus: Pursue high utility (evaluate based on task type)
  ml_utility_assessment:
    method: mlutility
    task_type: classification
    target: income
    experiment_design: domain_transfer  # Default: domain transfer
    random_state: 42
```

When evaluating, confirm:
- Data validity score is close to 1.0
- All privacy risk indicators are below 0.09
- Fidelity score reaches the threshold of 0.75

Utility metrics meeting standards is the main goal, with key metrics for classification tasks including:
- **F1 Score**: Harmonic mean of precision and recall, target ≥ 0.7
- **ROC AUC**: Area under receiver operating characteristic curve, target ≥ 0.8
- **Precision**: Proportion of predicted positive class that is actually positive, target ≥ 0.7
- **Recall**: Proportion of actual positive class that is correctly predicted, target ≥ 0.7
- **Accuracy**: Overall prediction accuracy, target ≥ 0.75

## Notes and Common Questions

### Can Fidelity and Utility Be Pursued Simultaneously?

Yes, but you need to understand the priorities and trade-offs between the two:
- **Release Scenarios**: Take fidelity as the main goal (≥ 0.75), with utility as additional verification
- **Modeling Scenarios**: Ensure fidelity reaches basic threshold (≥ 0.75), focus on pursuing utility
- **Mixed Scenarios**: Need to set clear priorities to avoid over-optimization sacrificing other aspects

It should be noted that over-pursuing fidelity may affect utility for certain specific tasks, over-optimizing for specific tasks may reduce versatility for other uses, so a balance needs to be found between privacy protection and quality.

### What If Fidelity Is High But Utility Is Poor?

This situation may have several reasons:
- **Task Mismatch**: Synthetic data preserves statistical properties but fails to capture task-critical patterns
- **Class Imbalance**: Features of rare classes are not sufficiently learned
- **Complex Relationships Lost**: High-order interactions or nonlinear relationships are not preserved
- **Too Much Noise**: Synthesis process introduces noise that affects task performance

Solutions include:

**Adjust Synthesis Parameters**
- Increase training epochs to 500
- Adjust batch_size to 500
- Increase discriminator training steps (discriminator_steps) to 5

**Optimize for Tasks**
- Assess whether additional post-processing steps are needed
- Consider using data augmentation rather than complete replacement

**Re-evaluate Requirements**
- Check if utility standards are too strict
- Assess if more original data is needed to train the synthesizer
- Consider if the task itself is reasonably difficult

### What If Utility Is High But Fidelity Is Poor?

This situation may have several reasons:
- **Overfitting to Task**: Synthesizer optimizes for specific task at the expense of overall statistical similarity
- **Simplified Features**: Simplifies certain complex features to improve task performance
- **Selective Preservation**: Only preserves feature relationships useful for the task

Solutions include:

**Assess Actual Needs**
- If data is only used for that specific task, high utility may be sufficient
- If multi-purpose use is needed, fidelity needs improvement

**Adjust Synthesis Strategy**
- Use CTGAN without conditional synthesis to let model learn all relationships
- Set epochs to 300
- Adjust discriminator_loss_weight to 1.0 to balance generator and discriminator

**Adopt Mixed Approach**
- Use high-fidelity base synthetic data
- Fine-tune or augment for specific tasks
- Maintain different versions of synthetic data for different purposes

## References

1. Tao, Y., McKenna, R., Hay, M., Machanavajjhala, A., & Miklau, G. (2021). Benchmarking differentially private synthetic data generation algorithms. *arXiv preprint arXiv:2112.09238*.

2. NIST SP 800-188. (2023). *De-Identifying Government Data Sets*. Section 4.4.5 "Synthetic Data with Validation"

3. Jordon, J., Yoon, J., & van der Schaar, M. (2019). Measuring the quality of synthetic data for use in competitions. *arXiv preprint arXiv:1806.11345*.

4. Dankar, F. K., & Ibrahim, M. (2021). Fake it till you make it: Guidelines for effective synthetic data generation. *Applied Sciences*, 11(5), 2158.

5. Hernandez, M., Epelde, G., Alberdi, A., Cilla, R., & Rankin, D. (2022). Synthetic data generation for tabular health records: A systematic review. *Neurocomputing*, 493, 28-45.

## Related Documents

- [Privacy Risk Estimation](privacy-risk-estimation)
- [Experiment Design Selection](experiment-design-selection)
- [Data Fidelity Evaluation Detailed Description](../petsard-yaml/evaluator-yaml/#資料保真度)
- [Data Utility Evaluation Detailed Description](../petsard-yaml/evaluator-yaml/utility)