---
title: "Glossary"
weight: 999
prev: docs/experimental-new-format
next: docs
---

Technical terms and definitions used in PETsARD documentation (alphabetically ordered).

## A

- **Adapter**: In PETsARD, refers to standardized execution wrappers that provide consistent execution interfaces for all modules, a core design pattern of the PETsARD architecture.
- **Anonymeter**: Privacy risk assessment tool whose developer Statice is recognized by the French Data Protection Authority (CNIL) as compliant with EU regulations, evaluating singling out, linkability, and inference risks.

## B

- **Balanced Accuracy**: Classification accuracy metric that accounts for class imbalance.
- **Benchmark Dataset**: Standard datasets used for testing and validation, such as Adult Income Dataset.
- **Boundary Adherence**: Whether numeric or date fields remain within the upper and lower bounds of the original data.
- **Brier Score**: Metric evaluating the accuracy of probabilistic predictions, lower is better.

## C

- **Cardinality**: The number of distinct values in a categorical field. High cardinality indicates many category values, low cardinality indicates fewer.
- **Classification**: Machine learning task type for predicting category labels.
- **Clustering**: Unsupervised learning task in machine learning for grouping data.
- **Cohen's Kappa**: Metric measuring classification agreement, accounting for chance agreement.
- **Config**: In PETsARD, refers to the system component managing experiment settings, responsible for processing YAML configuration files and coordinating module execution.
- **Constrainer**: In PETsARD, refers to the system module that performs constraint checking and enforcement.
- **Constraints**: In PETsARD, refers to the rule system ensuring synthetic data complies with business specifications, including column constraints, column combination constraints, and missing value group constraints.
- **Contingency Table**: Cross-tabulation showing relationships between two categorical variables.
- **Control Data**: In PETsARD evaluation, refers to data not used for synthesis, retained as an independent test set.
- **Control Group**: Baseline dataset used for comparison in privacy risk assessment.
- **Correlation Coefficient**: Statistic measuring the strength of linear relationship between two variables.
- **Cross-Validation**: Technique for assessing model generalization ability by splitting data into multiple folds for training and validation.
- **CTGAN (Conditional Tabular GAN)**: Tabular data synthesis method using generative adversarial networks, specialized for mixed-type data.

## D

- **Default Evaluation**: Default evaluation methods provided by the PETsARD system, including basic metrics for privacy, fidelity, and utility dimensions.
- **Default Synthesis**: Default synthetic data generation method provided by the PETsARD system, using SDV's Gaussian Copula model.
- **Denormalization**: Database processing technique merging multiple related tables into a single wide table, used to simplify multi-table data synthesis.
- **Describer**: In PETsARD, refers to the system module that analyzes and describes statistical properties of data, generating data overview reports.
- **Differential Privacy**: Mathematically defined privacy protection method ensuring individual information is not leaked.
- **Direct Identifier**: Fields that can directly identify individual identity, such as ID numbers, names, etc.
- **Discretization**: Preprocessing technique converting continuous values to categorical data, such as K-bins discretization.
- **Docker**: Containerization technology, PETsARD provides Docker images for rapid deployment.
- **Docker Compose**: Tool for defining and running multi-container Docker applications, used to coordinate PETsARD services.
- **Domain Transfer**: In PETsARD MLUtility, evaluating deployment performance of models trained on synthetic data when applied to real data.
- **Dual Model Control**: Experimental design training models using both original and synthetic data, comparing performance on control data.

## E

- **Evaluator**: In PETsARD, refers to the system module executing privacy, fidelity, and utility evaluations, integrating third-party tools like Anonymeter and SDMetrics.
- **Executor**: In PETsARD, refers to the main execution interface of the pipeline, the core control component coordinating execution flow of all modules.
- **Experiment Repetition**: Mechanism in PETsARD for executing the same experiment multiple times to ensure result reliability.
- **Experiment Tuple**: In PETsARD, an identification pair composed of module name and experiment name, formatted as (module_name, experiment_name).
- **External Synthesis**: Synthetic data generated using tools or methods outside of PETsARD. PETsARD can load these externally generated synthetic data and evaluate quality using built-in assessment framework to help compare different synthesis methods.

## F

- **F1 Score**: Harmonic mean of precision and recall, comprehensive evaluation metric for classification tasks.
- **Fidelity**: Degree of similarity in statistical distribution between synthetic and original data.
- **FNR (False Negative Rate)**: Proportion of actual positives predicted as negative.
- **FPR (False Positive Rate)**: Proportion of actual negatives predicted as positive.

## G

- **Gaussian Copula**: Default synthesis method used by PETsARD, preserving correlation structure between data using Gaussian distribution and Copula functions.
- **GitHub Container Registry (GHCR)**: Container image storage service provided by GitHub, hosting PETsARD Docker images.
- **Granularity**: In PETsARD reports, refers to levels of evaluation results, including global, columnwise, pairwise, details, tree, etc.

## H

- **Hyperparameters**: External settings controlling the model training process, such as learning rate, batch size.

## I

- **Inference Risk**: Degree of risk that sensitive information can be inferred, assessing whether other attributes can be deduced from known information.

## J

- **Jaccard Score**: Metric measuring set similarity, used for classification task evaluation.
- **Jensen-Shannon Divergence**: Symmetric metric measuring differences between two probability distributions.

## K

- **Kolmogorov-Smirnov Test (K-S Test)**: Statistical test comparing differences between two empirical distributions.

## L

- **Label Encoding**: Encoding method converting category values to continuous integers, suitable for ordinal categorical variables.
- **Linkability Risk**: Degree of risk that records from different data sources can be linked, assessing whether the same individual can be linked across different datasets.
- **Loader**: In PETsARD, refers to the system module responsible for reading and loading data, supporting various file formats and benchmark datasets.
- **Log Loss**: Logarithmic loss, metric measuring accuracy of classification model probability predictions.
- **Log Transformation**: Preprocessing technique using logarithmic functions to transform skewed distribution data.

## M

- **MAE (Mean Absolute Error)**: Mean absolute error, evaluation metric for regression tasks.
- **Matthews Correlation Coefficient (MCC)**: Classification evaluation metric comprehensively considering all elements of the confusion matrix.
- **Metadata**: Information describing data characteristics, including field types, distributions, constraints, etc.
- **Metadater**: In PETsARD, refers to the core system component responsible for managing and maintaining data schema information, uniformly handling metadata requirements for all modules.
- **Missing Value Handling**: Techniques for handling missing data, including deletion, mean imputation, mode imputation, median imputation, etc.
- **MLUtility**: Module in PETsARD evaluating machine learning utility of synthetic data, divided into V1 (using decision trees) and V2 (using XGBoost) versions.
- **Model Parameters**: Internal configuration of machine learning models, such as neural network weights.
- **mpUCCs (Maximal Partial Unique Column Combinations)**: Theoretical foundation for advanced singling out risk assessment.
- **MSE (Mean Squared Error)**: Mean squared error, evaluation metric for regression tasks.

## N

- **Naming Strategy**: Setting in PETsARD Reporter controlling output filename format, including traditional and compact modes.
- **NaN Groups**: Constraint rules for handling missing values, including operations like deletion, filling, or copying.
- **NPV (Negative Predictive Value)**: Proportion of actual negatives among predicted negatives.

## O

- **One-Hot Encoding**: Encoding method converting each category value to independent binary features, suitable for unordered categorical variables.
- **Original Data**: In PETsARD, refers to the dataset used for training synthetic models, which may be real data or processed data.
- **Outlier**: Extreme values deviating from normal data distribution.
- **Outlier Handling**: Techniques for identifying and handling anomalous values in data, including Z-score, IQR, LOF methods, etc.

## P

- **PETsARD (Privacy-Enhanced Technology for Synthetic Assessment Reporting and Decision)**: Open-source synthetic data evaluation framework developed by the National Institute of Cyber Security.
- **Postprocessing**: In PETsARD, refers to restoration processing steps after synthetic data generation, converting preprocessed data back to original format.
- **PPV (Positive Predictive Value)**: Also known as precision, proportion of actual positives among predicted positives.
- **PR AUC**: Area under Precision-Recall curve, evaluation metric suitable for imbalanced datasets.
- **Precision**: Proportion of actual positives among predicted positives.
- **Preprocessing**: In PETsARD, refers to preparation processing steps before data synthesis, including missing value handling, outlier handling, encoding, scaling, etc.
- **Primary Key**: Field uniquely identifying each record in a data table.
- **Privacy Protection**: Degree of preventing individual information leakage after data processing.

## Q

- **Quasi-identifier (QID)**: Fields that are not direct identifiers but may identify individuals when combined.

## R

- **R² Score**: Coefficient of determination, metric measuring variance explained by regression models.
- **Recall**: Proportion correctly predicted among actual positives, also known as sensitivity.
- **Regression**: Machine learning task type for predicting continuous values.
- **Reporter**: In PETsARD, refers to the system module generating and storing experiment result reports, supporting multiple output formats.
- **RMSE (Root Mean Squared Error)**: Root mean squared error, evaluation metric for regression tasks.
- **ROC AUC**: Area under Receiver Operating Characteristic curve, comprehensive performance metric for classification models.

## S

- **Scaling**: Preprocessing techniques adjusting numerical ranges, including standardization, min-max scaling, time-anchored scaling, etc.
- **Schema**: In PETsARD, refers to metadata defining data structure, including field types, constraints, and relationships.
- **SDMetrics**: Evaluation tool in the SDV ecosystem for assessing synthetic data quality, fidelity, and diagnostic reports.
- **SDV (Synthetic Data Vault)**: Open-source synthetic data generation framework providing various synthesis algorithms.
- **Sensitivity**: Also known as recall, proportion correctly predicted among actual positives.
- **Silhouette Coefficient**: Metric evaluating clustering quality, ranging from -1 to 1.
- **Singling Out Risk**: Degree of risk that individual records can be uniquely identified, assessing whether specific individuals can be identified from data.
- **SMOTE**: Synthetic Minority Over-sampling Technique for handling imbalanced data.
- **SMOTE-ENN**: Imbalanced data processing method combining SMOTE with Edited Nearest Neighbors, oversampling followed by boundary sample cleaning.
- **SMOTE-Tomek**: Imbalanced data processing method combining SMOTE with Tomek Links, oversampling followed by Tomek link removal.
- **Specificity**: Proportion correctly predicted as negative among actual negatives.
- **Splitter**: In PETsARD, refers to the system module splitting data into training and validation sets, supporting multiple splits required for privacy assessment.
- **Synthetic Data**: Artificial data generated through machine learning models, preserving statistical properties of original data without containing real individual information.
- **Synthesizer**: In PETsARD, refers to the core system module generating synthetic data, integrating various synthesis algorithms from SDV, custom implementations, etc.

## T

- **Threshold**: Decision boundary value used to convert continuous predictions to category labels.
- **Time Anchoring**: Method for handling multi-timepoint data, setting the most important time field as anchor and converting other timepoints to relative time differences.
- **Total Variation Distance (TVD)**: Statistic measuring differences between two probability distributions.
- **TVAE (Tabular Variational Autoencoder)**: Tabular data synthesis method using variational autoencoders, focusing on data distribution characteristics.

## U

- **Uniform Encoding**: Categorical variable processing method proposed by Datacebo, mapping discrete category values to continuous [0,1] interval while preserving statistical properties of category distribution.
- **Utility**: Performance capability of synthetic data in machine learning tasks.

## V

- **Validity**: Degree to which data accurately reflects fundamental characteristics and structure.

## X

- **XGBoost**: Gradient boosting decision tree algorithm used for classification and regression tasks in PETsARD MLUtility V2.