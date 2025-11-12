---
title: Uniform Encoding
weight: 2
---

Categorical variables are variables that can be divided into different categories or groups, where values represent some classification rather than measured numbers. These values are typically discrete, non-numerical labels, such as gender (male, female), blood type (A, B, AB, O), city names, or education level. Categorical variables can be nominal scale (unordered categories, such as colors) or ordinal scale (with natural ordering, such as education level).

Since most synthetic data models, and even statistical and machine learning algorithms, can only accept numerical column inputs, encoding is needed to process nominal or ordinal scale categorical variables, making the data understandable and operable for models.

## Principles and Advantages of Uniform Encoding

Uniform encoding is a categorical variable processing method proposed by Datacebo, specifically designed to improve generative model effectiveness. Its core concept is to map discrete category values to the continuous [0,1] interval, where the interval size corresponding to each category is determined by its frequency in the original data. This method can effectively convert categorical information into continuous values while preserving the statistical properties of category distribution.

In practical operation, if a categorical variable contains three categories 'a', 'b', 'c' with occurrence ratios of 1:3:1, then during encoding 'a' is mapped to the [0.0, 0.2) interval, 'b' is mapped to the [0.2, 0.8) interval, 'c' is mapped to the [0.8, 1.0] interval, and random values are taken within their respective intervals. During restoration, the original category is determined based on which interval the value falls into. This bidirectional transformation mechanism ensures data integrity throughout the modeling and restoration process.

Uniform encoding simultaneously solves multiple data processing challenges. According to Datacebo's research, first, it converts discrete distributions into continuous distributions for easier modeling, and provides a fixed value range [0,1] for convenient restoration. More importantly, this method preserves original distribution information, giving common categories higher sampling probability while not introducing non-existent ordering relationships like label encoding. Compared to one-hot encoding, uniform encoding also doesn't cause dimension explosion problems, significantly improving processing efficiency. This encoding method is particularly suitable for features with moderate category counts and imbalanced category distribution scenarios, can be flexibly combined with other preprocessing methods, and demonstrates excellent performance in synthetic model applications.

## Determining Whether Uniform Encoding Is Suitable

When data exhibits the following characteristics, uniform encoding should be considered. If categorical variables exist, containing nominal or ordinal scale categorical columns that need to convert discrete values into continuous values for synthesizer learning, uniform encoding is an ideal choice. When category counts are moderate, with average samples per category ≥ 10 (i.e., total samples / category count ≥ 10), encoding stability can be ensured; for example, 10,000 data records with 100 categories, or 100,000 data records with 1,000 categories both fall within the moderate range. If distribution among categories is imbalanced, with significant differences in occurrence frequency, uniform encoding can preserve original distribution information through interval sizes.

When using deep learning synthesizers (such as CTGAN, TVAE), uniform encoding is more efficient than one-hot encoding and can avoid dimension explosion problems. When data contains multiple categorical variables, if using one-hot encoding would lead to sharp increases in feature count, significantly raising computational costs and memory requirements, uniform encoding is a better choice.

In some cases, other encoding methods may need to be considered, or columns may need to be removed or categories merged beforehand. When encountering high cardinality categories with average samples per category < 10 (such as personal ID, detailed addresses), too few samples make it difficult for each interval to learn stable patterns. In this case, it's recommended to use constraints, feature hashing, or consider whether split-synthesize-merge is needed.

## Practical Application Examples

The following example demonstrates how to use uniform encoding to process multiple categorical variables in university student data:

```yaml
Preprocessor:
  encoding_uniform:
    sequence:
      - 'encoder' # Use positive declaration to disable other default preprocessing
    encoder:
      zodiac: 'encoding_uniform'           # Zodiac sign
      department_name: 'encoding_uniform'  # Department name
      admission_type: 'encoding_uniform'   # Admission type
      disabled_type: 'encoding_uniform'    # Disability status
      nationality: 'encoding_uniform'      # Nationality
      identity: 'encoding_uniform'         # Identity category
      sex: 'encoding_uniform'              # Gender
```

This configuration applies uniform encoding to seven categorical variables in student data. These variables include zodiac sign (zodiac), department name (department_name), admission type (admission_type), disability status (disabled_type), nationality (nationality), identity category (identity), and gender (sex). By declaring only encoder in the sequence, other default preprocessing steps can be disabled, ensuring only encoding processing is performed. This configuration is particularly suitable when these categorical variables have moderate category counts and potentially imbalanced distributions.

## Notes and Common Questions

### What's the Difference Between Uniform Encoding and Label Encoding?

Label Encoding simply maps categories to integer sequences (0, 1, 2, ...), with the main problem being it introduces non-existent ordering relationships—the model may mistakenly think category 2 is "greater" than category 1, and the "distance" between categories has no actual meaning.

Uniform encoding maps categories to continuous intervals, avoiding implied ordering relationships, and interval sizes reflect category frequencies, preserving statistical distribution information, making it more suitable for synthetic model learning.

### Why Not Use One-Hot Encoding?

The advantage of One-Hot Encoding is that encoded results are completely interpretable and don't introduce ordering relationships, suitable for traditional machine learning models.

However, the disadvantage is that high cardinality causes dimension explosion (such as 100 categories generating 100 new columns), increasing memory requirements and computational costs, and may also lead to sparsity problems. Both high-dimensional data and sparse data reduce the performance of tabular synthetic models.

### What If Categories Contain Missing Values?

PETsARD's default preprocessing process automatically deletes rows with missing values in categorical columns during missing value handling, so there are no missing values when encoding begins.

However, if missing values have specific meaning, users can disable missing value handling as in the example (by not declaring missing), and then PETsARD has special handling—missing values are treated as an independent category before uniform encoding. Therefore, missing values also get their own interval and will be restored in post-processing after synthesis.

### Should Time Data Be Treated as Categories or Numerical Values?

Regardless of whether time columns are single columns or stored separately, and regardless of their original data type, our team recommends properly declaring time data as time columns, and PETsARD will treat them as continuous columns to preserve time continuity.

The only exception is when you have clear domain knowledge confirming that separated time components (such as month, week) have known associations with data trend periodicity, then it's suitable to treat these time components as categorical variables and appropriate to use them as uniform encoding targets.