---
title: "Glossary"
weight: 999
---

Technical terms and definitions used in PETsARD documentation (alphabetically ordered).

## A

- **Adapter**: In PETsARD, refers to standardized execution wrappers that provide consistent execution interfaces for all modules, a core design pattern of the PETsARD architecture.
- **Adult Income Dataset**: UCI Machine Learning Repository census income dataset containing 48,842 records and 15 fields, one of PETsARD's standard benchmark datasets.
- **Anonymeter**: Privacy risk assessment tool whose developer Statice is recognized by the French Data Protection Authority (CNIL) as compliant with EU regulations, evaluating singling out, linkability, and inference risks.

## B

- **Balanced Accuracy**: Classification accuracy metric that accounts for class imbalance.
- **Benchmark Dataset**: Standard datasets used for testing and validation, such as Adult Income Dataset.
- **Bimodal Distribution**: Probability distribution with two peaks, indicating data has two main concentration areas, presenting challenges for statistical modeling.
- **Boundary Adherence**: Whether numeric or date fields remain within the upper and lower bounds of the original data.
- **Brier Score**: Metric evaluating the accuracy of probabilistic predictions, lower is better.

## C

- **Cardinality**: The number of distinct values in a categorical field. High cardinality indicates many category values, low cardinality indicates fewer.
- **Classification**: Machine learning task type for predicting category labels.
- **Clustering**: Unsupervised learning task in machine learning for grouping data.
- **CNIL**: Commission Nationale de l'Informatique et des Libertés. French National Commission on Informatics and Liberty, the French data protection authority that recognized Anonymeter as compliant with EU anonymization standards in 2023.
- **Cohen's Kappa**: Metric measuring classification agreement, accounting for chance agreement.
- **Confidence Interval**: In statistics, the range within which the true value of a parameter is estimated to lie, representing the degree of uncertainty in the estimation.
- **Config**: In PETsARD, refers to the system component managing experiment settings, responsible for processing YAML configuration files and coordinating module execution.
- **Constrainer**: In PETsARD, refers to the system module that performs constraint checking and enforcement.
- **Constraints**: In PETsARD, refers to the rule system ensuring synthetic data complies with business specifications, including column constraints, column combination constraints, and missing value group constraints.
- **Contingency Table**: Cross-tabulation showing relationships between two categorical variables.
- **Control Data**: In PETsARD evaluation, refers to data not used for synthesis, retained as an independent test set.
- **Control Group**: Baseline dataset used for comparison in privacy risk assessment.
- **Copula Function**: Used to describe the dependence structure among variables in a multivariate distribution. Gaussian Copula uses Gaussian distribution as the copula function.
- **CopulaGAN**: Hybrid synthesis method provided by SDV, combining Copula statistical methods with GAN deep learning technology, balancing quality and efficiency.
- **Correlation Coefficient**: Statistic measuring the strength of linear relationship between two variables.
- **Cross-Validation**: Technique for assessing model generalization ability by splitting data into multiple folds for training and validation.
- **CSV**: Comma-Separated Values. File format for comma-delimited data, one of the primary data input/output formats supported by PETsARD.
- **CTGAN**: Conditional Tabular GAN. Tabular data synthesis method using generative adversarial networks, specialized for mixed-type data.

## D

- **Datacebo**: Development company of SDV (Synthetic Data Vault), proposing innovative technologies such as Uniform Encoding.
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

- **Eigenvalue Decomposition**: Mathematical operation decomposing a matrix into eigenvectors and eigenvalues. Ledoit-Wolf regularization avoids this operation to improve efficiency.
- **Evaluator**: In PETsARD, refers to the system module executing privacy, fidelity, and utility evaluations, integrating third-party tools like Anonymeter and SDMetrics.
- **Excel**: Microsoft Excel spreadsheet format (.xlsx, .xls), one of the data input formats supported by PETsARD, requires openpyxl package installation.
- **Executor**: In PETsARD, refers to the main execution interface of the pipeline, the core control component coordinating execution flow of all modules.
- **Experiment Repetition**: Mechanism in PETsARD for executing the same experiment multiple times to ensure result reliability.
- **Experiment Tuple**: In PETsARD, an identification pair composed of module name and experiment name, formatted as (module_name, experiment_name).
- **External Synthesis**: Synthetic data generated using tools or methods outside of PETsARD. PETsARD can load these externally generated synthetic data and evaluate quality using built-in assessment framework to help compare different synthesis methods.

## F

- **F1 Score**: Harmonic mean of precision and recall, comprehensive evaluation metric for classification tasks.
- **FD Rule**: Freedman-Diaconis Rule. Histogram bin width selection rule with formula 2 × IQR / n^(1/3), suitable for large sample data.
- **Fidelity**: Degree of similarity in statistical distribution between synthetic and original data.
- **FNR**: False Negative Rate. Proportion of actual positives predicted as negative.
- **FPR**: False Positive Rate. Proportion of actual negatives predicted as positive.

## G

- **GAN**: Generative Adversarial Network. A deep learning architecture composed of a generator and discriminator, used for generating high-quality synthetic data.
- **Gaussian Copula**: Default synthesis method used by PETsARD, preserving correlation structure between data using Gaussian distribution and Copula functions.
- **GHCR**: GitHub Container Registry. Container image storage service provided by GitHub, hosting PETsARD Docker images.
- **Granularity**: In PETsARD reports, refers to levels of evaluation results, including global, columnwise, pairwise, details, tree, etc.

## H

- **HDF5**: Hierarchical Data Format 5. Hierarchical data format for storing large-scale numerical datasets.
- **Histogram**: Chart grouping numerical data into intervals and displaying frequency, used for distribution comparison in fidelity assessment.
- **HMA**: Hierarchical Modeling Algorithm. Hierarchical modeling algorithm provided by SDV, using recursive techniques to model parent-child relationships in multi-table datasets, but with scale and complexity limitations.
- **Hyperparameters**: External settings controlling the model training process, such as learning rate, batch size.

## I

- **Inference Risk**: Degree of risk that sensitive information can be inferred, assessing whether other attributes can be deduced from known information.
- **Isolation Forest**: Decision tree-based anomaly detection algorithm for identifying outliers in data, one of the outlier handling methods supported by PETsARD.

## J

- **Jaccard Score**: Metric measuring set similarity, used for classification task evaluation.
- **Jensen-Shannon Divergence**: Symmetric metric measuring differences between two probability distributions.
- **JIT**: Just-In-Time Compilation. Compilation technique where Numba uses JIT to compile Python code into machine code for improved execution performance.
- **JSON**: JavaScript Object Notation. Lightweight data interchange format, one of the configuration and data formats supported by PETsARD.
- **Jupyter Lab**: Interactive development environment supporting Notebook, code editing, and data visualization, optionally included in PETsARD Docker images.

## K

- **K-S Test**: Kolmogorov-Smirnov Test. Statistical test comparing differences between two empirical distributions.

## L

- **Label Encoding**: Encoding method converting category values to continuous integers, suitable for ordinal categorical variables.
- **Ledoit-Wolf Regularization**: Shrinkage estimation method for covariance matrix with formula Σ_reg = (1-λ)Σ + λI, used to improve correlation estimation for small sample or high-dimensional data.
- **Linkability Risk**: Degree of risk that records from different data sources can be linked, assessing whether the same individual can be linked across different datasets.
- **Loader**: In PETsARD, refers to the system module responsible for reading and loading data, supporting various file formats and benchmark datasets.
- **Log Loss**: Logarithmic loss, metric measuring accuracy of classification model probability predictions.
- **Log Transformation**: Preprocessing technique using logarithmic functions to transform skewed distribution data.

## M

- **MAE**: Mean Absolute Error. Mean absolute error, evaluation metric for regression tasks.
- **MCC**: Matthews Correlation Coefficient. Classification evaluation metric comprehensively considering all elements of the confusion matrix.
- **Metadata**: Information describing data characteristics, including field types, distributions, constraints, etc.
- **Metadater**: In PETsARD, refers to the core system component responsible for managing and maintaining data schema information, uniformly handling metadata requirements for all modules.
- **Missing Value Handling**: Techniques for handling missing data, including deletion, mean imputation, mode imputation, median imputation, etc.
- **MLUtility**: Module in PETsARD evaluating machine learning utility of synthetic data. V1 version evaluated multiple models simultaneously (deprecated), V2 version uses XGBoost (classification/regression) and K-means (clustering).
- **Model Parameters**: Internal configuration of machine learning models, such as neural network weights.
- **mpUCCs**: Maximal Partial Unique Column Combinations. Theoretical foundation for advanced singling out risk assessment.
- **MSE**: Mean Squared Error. Mean squared error, evaluation metric for regression tasks.

## N

- **NaN Groups**: Not a Number Groups. Constraint rules for handling missing values, including operations like deletion, filling, or copying.
- **Naming Strategy**: Setting in PETsARD Reporter controlling output filename format, including traditional and compact modes.
- **Non-parametric Estimation**: Statistical method that does not assume data follows a specific probability distribution, more flexible but with higher computational cost.
- **NPV**: Negative Predictive Value. Proportion of actual negatives among predicted negatives.
- **Numba**: Python JIT compiler that compiles numerical computation code into machine code for significantly improved execution speed. PETsARD's Gaussian Copula implementation uses Numba for acceleration.
- **NumPy**: Python's core numerical computation library providing high-performance multi-dimensional array operations, one of PETsARD's fundamental dependencies.

## O

- **One-Hot Encoding**: Encoding method converting each category value to independent binary features, suitable for unordered categorical variables.
- **OpenDocument**: Open document format (.ods, .odf, .odt), data input format supported by PETsARD, requires openpyxl package installation.
- **openpyxl**: Python library for reading and writing Excel and OpenDocument format files, a necessary dependency for PETsARD to support these formats.
- **Original Data**: In PETsARD, refers to the dataset used for training synthetic models, which may be real data or processed data.
- **Outlier**: Extreme values deviating from normal data distribution.
- **Outlier Handling**: Techniques for identifying and handling anomalous values in data, including Z-score, IQR, LOF methods, etc.

## P

- **Pandas**: Python data analysis library providing data structures like DataFrame, one of PETsARD's core dependencies.
- **Parametric Statistics**: Statistical method assuming data follows a specific probability distribution (such as normal distribution), as opposed to non-parametric statistics.
- **Parquet**: Columnar binary file format suitable for efficient access of large datasets.
- **PETsARD**: Privacy-Enhanced Technology for Synthetic Assessment Reporting and Decision. Open-source synthetic data evaluation framework developed by the National Institute of Cyber Security.
- **Postprocessing**: In PETsARD, refers to restoration processing steps after synthetic data generation, converting preprocessed data back to original format.
- **PPV**: Positive Predictive Value. Also known as precision, proportion of actual positives among predicted positives.
- **PR AUC**: Precision-Recall Area Under the Curve. Area under Precision-Recall curve, evaluation metric suitable for imbalanced datasets.
- **Precision**: Proportion of actual positives among predicted positives.
- **Preprocessing**: In PETsARD, refers to preparation processing steps before data synthesis, including missing value handling, outlier handling, encoding, scaling, etc.
- **Primary Key**: Field uniquely identifying each record in a data table.
- **Privacy Protection**: Degree of preventing individual information leakage after data processing.
- **Python**: Programming language used by PETsARD, providing rich data science and machine learning ecosystem.
- **PyTorch**: Deep learning framework used by PETsARD for GPU-accelerated large-scale matrix operations and deep learning model training.

## Q

- **Quasi-identifier**: QID. Fields that are not direct identifiers but may identify individuals when combined.

## R

- **R² Score**: Coefficient of determination, metric measuring variance explained by regression models.
- **Recall**: Proportion correctly predicted among actual positives, also known as sensitivity.
- **Regression**: Machine learning task type for predicting continuous values.
- **Regularization**: Technique in statistics and machine learning for reducing model complexity and improving generalization ability. Ledoit-Wolf regularization is used for covariance matrix estimation.
- **Reporter**: In PETsARD, refers to the system module generating and storing experiment result reports, supporting multiple output formats.
- **RMSE**: Root Mean Squared Error. Root mean squared error, evaluation metric for regression tasks.
- **ROC AUC**: Receiver Operating Characteristic Area Under the Curve. Area under Receiver Operating Characteristic curve, comprehensive performance metric for classification models.

## S

- **Scaling**: Preprocessing techniques adjusting numerical ranges, including standardization, min-max scaling, time-anchored scaling, etc.
- **Schema**: Metadata defining data structure, including field names, data types, constraints, and relationships. In PETsARD, used to track structural changes of data throughout the processing pipeline.
- **Scikit-learn**: Abbreviated as sklearn. Python machine learning library providing classification, regression, clustering algorithms, used by PETsARD for machine learning utility evaluation.
- **SDMetrics**: Evaluation tool in the SDV ecosystem for assessing synthetic data quality, fidelity, and diagnostic reports.
- **SDV**: Synthetic Data Vault. Open-source synthetic data generation framework providing various synthesis algorithms.
- **Sensitivity**: Also known as recall, proportion correctly predicted among actual positives.
- **Silhouette Coefficient**: Metric evaluating clustering quality, ranging from -1 to 1.
- **Singling Out Risk**: Degree of risk that individual records can be uniquely identified, assessing whether specific individuals can be identified from data.
- **SMOTE**: Synthetic Minority Over-sampling Technique for handling imbalanced data.
- **SMOTE-ENN**: Imbalanced data processing method combining SMOTE with Edited Nearest Neighbors, oversampling followed by boundary sample cleaning.
- **SMOTE-Tomek**: Imbalanced data processing method combining SMOTE with Tomek Links, oversampling followed by Tomek link removal.
- **Specificity**: Proportion correctly predicted as negative among actual negatives.
- **Splitter**: In PETsARD, refers to the system module splitting data into training and validation sets, supporting multiple splits required for privacy assessment.
- **SQL**: Structured Query Language. Language for database operations and data processing.
- **Statice**: Development company of Anonymeter, focusing on privacy protection and synthetic data technology.
- **Sturges' Rule**: Histogram bin number selection rule with formula log₂(n) + 1, suitable for small sample data.
- **Synthetic Data**: Artificial data generated through machine learning models, preserving statistical properties of original data without containing real individual information.
- **Synthesizer**: In PETsARD, refers to the core system module generating synthetic data, integrating various synthesis algorithms from SDV, custom implementations, etc.

## T

- **Threshold**: Decision boundary value used to convert continuous predictions to category labels.
- **Time Anchoring**: Method for handling multi-timepoint data, setting the most important time field as anchor and converting other timepoints to relative time differences.
- **Total Variation Distance**: TVD. Statistic measuring differences between two probability distributions.
- **TSV**: Tab-Separated Values. Tab-delimited file format, one of the data input formats supported by PETsARD.
- **TVAE**: Tabular Variational Autoencoder. Tabular data synthesis method using variational autoencoders, focusing on data distribution characteristics.

## U

- **UCI**: University of California, Irvine. Its machine learning repository provides multiple standard datasets, including Adult Income Dataset.
- **Uniform Encoding**: Categorical variable processing method proposed by Datacebo, mapping discrete category values to continuous [0,1] interval while preserving statistical properties of category distribution.
- **UTF-8**: Unicode Transformation Format - 8-bit. Default character encoding used by PETsARD, supporting multilingual text processing.
- **Utility**: Performance capability of synthetic data in machine learning tasks.

## V

- **VAE**: Variational Autoencoder. A generative model that learns latent representations of data through an encoder and decoder. TVAE is based on this architecture.
- **Validity**: Degree to which data accurately reflects fundamental characteristics and structure.

## X

- **XGBoost**: eXtreme Gradient Boosting. Gradient boosting decision tree algorithm used for classification and regression tasks in PETsARD MLUtility V2.

## Y

- **YAML**: YAML Ain't Markup Language. Human-readable data serialization format used by PETsARD as the primary configuration file format.