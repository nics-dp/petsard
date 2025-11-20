---
title: "Iterative Tuning: Data Property Adjustment"
type: docs
weight: 500
prev: docs/evaluation-purpose
next: docs/petsard-yaml
---

## Overview

Data property adjustment is a critical step in ensuring synthetic data quality, but **it is not a one-time configuration task, but rather an iterative tuning process**.

### Iterative Adjustment Workflow

In practical applications, data property adjustment follows this iterative cycle:

1. **Initial Synthesis**: Use default or basic data processing settings to generate the first version of synthetic data
2. **Evaluation Analysis**: Review synthesis quality through evaluation metrics (such as Column Shapes, Column Pair Trends, Synthesis)
3. **Problem Diagnosis**: When evaluation results are unsatisfactory, deeply analyze which columns or data characteristics cause problems
4. **Targeted Adjustments**: Based on data characteristics, adjust individual column processing methods or overall dataset settings
5. **Re-synthesis and Evaluation**: Apply new settings, generate synthetic data again and evaluate
6. **Continuous Optimization**: Repeat the above steps until satisfactory evaluation results are achieved

This process emphasizes **evaluation-driven optimization strategy**: rather than blindly applying all possible adjustment methods, selectively choose and adjust processing strategies based on specific problems revealed by evaluation results. For example:

- When **Column Shapes scores are low**, logarithmic transformation may be needed to handle long-tailed distributions
- When **categorical variable distributions differ significantly**, uniform encoding may need to be applied
- When **time logic shows contradictions**, time anchoring scaling may be needed
- When **synthesis quality of certain subgroups is poor**, split-synthesize-merge strategy may need to be considered

### Nature of Adjustment Methods

Different data characteristics require different processing strategies to ensure synthesizers can effectively learn data's statistical properties and business logic. Each adjustment method is a tool designed for specific types of data problems, and through appropriate combination and application, synthesis quality can be significantly improved.

This section introduces four common data property adjustment methods, covering important issues such as handling complex data structures, categorical variables, distribution skewness, and temporal relationships. The important thing is understanding **when** and **why** these methods are needed, rather than mechanically applying all techniques.

## Adjustment Methods Overview

### 1. High Heterogeneity Data: Split-Synthesize-Merge

For data containing multiple heterogeneous attributes, use the Split-Synthesize-Merge strategy to divide data into more homogeneous subsets, synthesize them separately, then integrate. This method originated from hardware limitations in processing large datasets, but practice has shown significant effectiveness in improving synthesis quality for heterogeneous and imbalanced data.

**Applicable Scenarios**:
- Data volume too large to load into memory at once (e.g., nationwide population data ~5GB)
- Obvious inherent heterogeneity exists (e.g., single-person households vs. multi-person households)
- Highly imbalanced data (e.g., fraud detection with 99% normal transactions vs. 1% fraud)
- Need to adopt different synthesis strategies or parameters for different subgroups

**Expected Effects**:
- Overcome hardware limitations to process large datasets
- Improve synthesis quality for each subgroup (more precisely capture subgroup characteristics)
- Improve synthesis effects for rare categories
- Flexibly adjust strategies for different subgroups

**Detailed Explanation**: [High Heterogeneity Data: Split-Synthesize-Merge](split-synthesize)

### 2. Categorical Data: Uniform Encoding

For categorical variables, use Uniform Encoding method to map discrete category values to the continuous [0,1] interval, where interval size is determined by category occurrence frequency, enabling synthesizers to more effectively learn category distribution and associations.

**Applicable Scenarios**:
- Data contains nominal or ordinal scale categorical variables
- Moderate number of categories (no more than 100 unique values per variable)
- Occurrence frequency differs between categories
- Using deep learning synthesizers (such as CTGAN, TVAE)

**Expected Effects**:
- Avoid introducing non-existent ordering relationships
- Preserve original category distribution information
- Improve synthetic data fidelity (average improvement of 15-40%)
- Reduce invalid or unreasonable synthetic samples

**Detailed Explanation**: [Categorical Data: Uniform Encoding](uniform-encoding)

### 3. Long-Tailed Distribution: Logarithmic Transformation

For numerical variables exhibiting long-tailed distribution (heavy-tailed distribution), use logarithmic transformation (log or log1p) to convert skewed distributions into more symmetric distributions, making it easier for synthesizers to capture data characteristics. Logarithmic transformation can compress value ranges, reduce extreme value impact, and improve model learning effectiveness.

**Applicable Scenarios**:
- Numerical variables show significant right or left skew (skewness absolute value > 1)
- Extreme values or outliers exist (ratio of maximum to median > 10)
- Variable's dynamic range is large (such as income, transaction amounts, website traffic)
- Variables show multiplicative rather than additive relationships

**Expected Effects**:
- Transform skewed distributions into approximately normal distributions
- Reduce dominant influence of extreme values
- Improve synthesizer's learning effectiveness and training stability
- Improve numerical distribution similarity (Column Shapes score average improvement of 10-30%)

**Detailed Explanation**: [Long-Tailed Distribution: Logarithmic Transformation](long-tail)

### 4. Multi-Timestamp Data: Time Anchoring Scaling

For data containing multiple time points, use Time Anchoring method to transform each time point into time differences relative to an anchor point, ensuring synthetic data maintains logical relationships and business constraints between time points.

**Applicable Scenarios**:
- Data contains 2 or more time or date columns
- Clear sequential relationships exist between time points
- Time points represent different lifecycle stages of the same entity
- Intervals between time points reflect important business patterns

**Expected Effects**:
- Greatly reduce synthetic records violating time logic
- Better preserve association patterns between time points
- Improve synthesizer's learning efficiency and stability
- Ensure business logic consistency

**Detailed Explanation**: [Multi-Timestamp Data: Time Anchoring Scaling](time-anchoring)

## Selecting Appropriate Adjustment Methods

Different data characteristics require different adjustment strategies. Here is a selection guide:

| Data Characteristic | Recommended Method | Priority |
|---------------------|-------------------|----------|
| Contains multiple categorical variables | Uniform Encoding | Required |
| Contains multiple time points | Time Anchoring Scaling | Strongly Recommended |
| Numerical distribution shows long tail | Logarithmic Transformation | Recommended |
| Data structure highly heterogeneous | Split-Synthesize-Merge | Case by Case |

## Combined Usage

In practical applications, multiple adjustment methods often need to be used in combination:

**Example 1: Enterprise Financing Data**
- Time Anchoring Scaling (handling multiple application, approval, tracking time points)
- Uniform Encoding (handling industry categories, financing types, etc.)
- Logarithmic Transformation (handling financing amounts and other long-tailed distributions)

**Example 2: Student Enrollment Data**
- Uniform Encoding (handling departments, admission methods, identity categories, etc.)
- Category as Time (handling birth year-month-day)
- High Cardinality Handling (handling department codes, etc.)

## Notes

1. **Assess Necessity**: Not all data needs all adjustment methods, should choose based on actual data characteristics
2. **Sequence Considerations**: Execution order of certain adjustment methods affects results, requires careful planning
3. **Business Logic**: Adjustment process should always consider business logic to avoid generating unreasonable data
4. **Effect Verification**: After adjustment, should confirm whether expected effects are achieved through evaluation metrics

## Related Documents

- [Best Practices](../best-practices)
- [Preprocessor Configuration Detailed Explanation](../petsard-yaml/preprocessor-yaml)
- [Data Fidelity Evaluation](../petsard-yaml/evaluator-yaml/#資料保真度)
- [Fidelity or Utility](../evaluation-purpose/fidelity-or-utility)