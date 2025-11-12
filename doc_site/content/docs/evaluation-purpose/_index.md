---
title: "Evaluation Interpretation: Purpose-Driven Assessment"
weight: 4
---

After completing data preparation, evaluating the quality of synthetic data is a critical step to ensure it meets application requirements. Evaluation strategies should be determined based on the intended use of synthetic data, as different application scenarios require different evaluation focuses and standards. This chapter will help you select appropriate evaluation methods and parameter settings based on data usage.

Quality assessment of synthetic data encompasses three core aspects:

- **Privacy Protection**: Ensuring synthetic data does not leak personally identifiable information from the original data
- **Data Fidelity**: Measuring the similarity of synthetic data to original data in statistical properties
- **Data Utility**: Verifying the performance of synthetic data in specific machine learning tasks

For these three aspects, our team recommends always prioritizing privacy protection, then determining the importance of the other two based on different application scenarios:

- **Data Release Scenarios**: When synthetic data will be publicly released or shared with third parties, pursue high fidelity to maintain data versatility
- **Specific Task Modeling**: When synthetic data is used for specific machine learning tasks (such as data augmentation, model training), pursue high utility to meet task requirements

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-overview.zh-tw.mmd" >}}

## Chapter Navigation

### [1. Privacy Risk Estimation: Protection Parameter Configuration](privacy-risk-estimation)

Privacy protection is the primary key to synthetic data quality assessment. This section explains how to use the Anonymeter tool to evaluate three privacy attack modes (singling out, linkability, inference), and provides parameter configuration recommendations and risk interpretation standards.

### [2. Release or Modeling: Fidelity or Utility](fidelity-or-utility)

Select fidelity or utility as the primary evaluation aspect based on the intended use of synthetic data. This section explains that data release scenarios should pursue high fidelity, specific task modeling should pursue high utility, and how to conduct evaluation and interpretation.

### [3. Synthetic Data Modeling Use: Experiment Design Selection](experiment-design-selection)

When synthetic data is used for specific machine learning tasks, experiment design determines how to train and evaluate models. This section explains the differences between domain transfer and dual model control group designs, selection criteria, and application scenarios.