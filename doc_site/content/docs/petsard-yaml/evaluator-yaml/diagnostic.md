---
title: "Data Validity Diagnosis"
weight: 1
---

Check whether synthetic data accurately reflects the basic characteristics and structure of the original data.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/diagnostic.ipynb)

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
  validity_check:
    method: sdmetrics-diagnosticreport
```

## Main Parameters

- **method** (`string`, required)
  - Fixed value: `sdmetrics-diagnosticreport`

## Evaluation Metrics

| Metric | Description | Recommended Standard |
|--------|-------------|---------------------|
| **Score** | Overall diagnostic score (arithmetic mean of Data Validity and Data Structure) | Close to 1.0 |
| **Data Validity** | Data validity | Close to 1.0 |
| - KeyUniqueness | Primary key uniqueness (0-1, proportion of unique values) | |
| - BoundaryAdherence | Numerical boundary consistency (0-1, proportion within range) | |
| - CategoryAdherence | Category cardinality consistency (0-1, proportion belonging to cardinality) | |
| **Data Structure** | Data structure | 1.0 |
| - Column Existence | Column existence | |
| - Column Type | Column type consistency | |

## Metric Calculation Details

### Data Validity
Arithmetic mean of validity scores for each column, calculated based on column characteristics:

- **KeyUniqueness**: Whether each record in primary key columns is unique
- **BoundaryAdherence**: Whether numerical or date columns are within the bounds of original data
- **CategoryAdherence**: Whether the cardinality of categorical or boolean columns belongs to the original data's cardinality set

### Data Structure
Checks whether column names in synthetic data match those in original data.

## Applicable Scenarios

- Primary check after completing data synthesis
- Confirming synthesis process hasn't damaged data structure
- Validating basic data validity

## Score Interpretation and Actions

### Ideal Situation
- Diagnostic score should be close to 100%
- High score indicates synthetic data successfully preserves key characteristics of original data

### Possible Reasons for Score Below 1.0

#### Data Validity Below 1.0

**Common Issues**:
- Problems typically occur with numerical columns
- Post-synthesis column values exceed original range

**Recommended Actions**:
- Evaluate based on specific data context
- Example: Date columns
  - Original data may be truncated to report date
  - If synthetic data predicts future events, assess reasonableness
  - Not all out-of-range situations require rejection

#### Data Structure Below 1.0

**Common Issues**:
- Reduced number of columns after synthesis
- Usually indicates preprocessing workflow errors

**Recommended Actions**:
- Check preprocessing steps
- Pay special attention to direct identifier handling:
  - If direct identifiers were removed before training synthetic data
  - Should compare "direct identifier removed version" of original data
  - Not the database version of original data
- For external synthetic data, provide uniform table ㄋchema