---
title: "Privacy Protection Assessment"
type: docs
weight: 692
prev: docs/petsard-yaml/evaluator-yaml/diagnostic
next: docs/petsard-yaml/evaluator-yaml/fidelity
---

Evaluate the privacy protection level of processed data by simulating three privacy attack scenarios. The evaluation uses Anonymeter, a Python library developed by [Statice](https://www.statice.ai/) that implements the anonymization evaluation standards proposed by the Article 29 Working Party (WP29) of EU Data Protection Directive in 2014 and received endorsement from the French Data Protection Authority (CNIL) in 2023.

## Usage Examples

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/privacy.ipynb)
> **Note**: If using Colab, please see the [runtime setup guide](/petsard/docs/#colab-execution-guide).

### Singling Out Risk

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
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400          # Number of attacks (default: 2,000)
    n_cols: 3               # Columns per query (default: 3)
    max_attempts: 4000      # Maximum attempts (default: 500,000)
```

### Linkability Risk

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
  linkability_risk:
    method: anonymeter-linkability
    max_n_attacks: true      # Use control dataset size (default: true)
    n_neighbors: 1           # Nearest neighbors (default: 1)
    aux_cols:                # Auxiliary columns (default: None)
      -                      # First list: Public data columns
        - workclass
        - education
        - occupation
        - race
        - gender
      -                      # Second list: Private data columns
        - age
        - marital-status
        - relationship
        - native-country
        - income
```

### Inference Risk

```yaml
Evaluator:
  inference_risk:
    method: anonymeter-inference
    max_n_attacks: true      # Use control dataset size (default: true)
    secret: income           # Sensitive column to infer (required)
```

## Main Parameters

### Singling Out Risk Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **method** | `string` | Required | - | Fixed value: `anonymeter-singlingout` |
| **n_attacks** | `integer` | Optional | 2,000 | Number of attack executions<br>Recommendation: Standardize to 2,000 |
| **n_cols** | `integer` | Optional | 3 | Number of columns used per query<br>Recommendation: Use 3-column multivariate mode |
| **max_attempts** | `integer` | Optional | 500,000 | Maximum attempts to find successful attacks<br>Recommendation: Reduce only when execution time is too long |

{{< callout type="info" >}}
**Note on Computational Efficiency**: Since anonymeter's singling out performs sampling with replacement for attack attempts, if the data cannot achieve the expected number of attacks and there's no check mechanism, it will still try to exhaust the maximum attempts, causing significant computational burden.

**NICS Recommended Guidelines**:
- **n_attacks**: Between 100 and n_rows/100
- **max_attempts**: Between 1,000 and n_rows/10
{{< /callout >}}

### Linkability Risk Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **method** | `string` | Required | - | Fixed value: `anonymeter-linkability` |
| **n_attacks** | `integer` | Optional | None | Number of attack executions<br>Can be omitted when max_n_attacks=true<br>**Note**: Ignored when max_n_attacks is true |
| **max_n_attacks** | `boolean` | Optional | true | Whether to automatically adjust n_attacks to match control dataset size<br>**When false**: Uses the configured n_attacks value (n_attacks must be specified)<br>**When true (default)**: Ignores n_attacks setting and uses control dataset size instead |
| **aux_cols** | `array` | Optional | None | Auxiliary information columns<br>Format: Two non-overlapping lists, simulating data held by different entities<br>**Selection guideline**: Divide column names into two lists based on understanding of systems, functions, and business logic. This simulates scenarios where data is held or released by different entities. Not all variables need to be included, but key variables should be covered. The division is relatively subjective and aims to assess linkability attack risks in realistic scenarios. |
| **n_neighbors** | `integer` | Optional | 1 | Number of nearest neighbors to consider<br>**Recommendation**: Set to 1 for strictest evaluation. Since linkability is a difficult attack mode, after failing to find the closest match, other less similar records pose no immediate risk. |

### Inference Risk Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **method** | `string` | Required | - | Fixed value: `anonymeter-inference` |
| **n_attacks** | `integer` | Optional | None | Number of attack executions<br>Can be omitted when max_n_attacks=true<br>**Note**: Ignored when max_n_attacks is true |
| **max_n_attacks** | `boolean` | Optional | true | Whether to automatically adjust n_attacks to match control dataset size<br>**When false**: Uses the configured n_attacks value (n_attacks must be specified)<br>**When true (default)**: Ignores n_attacks setting and uses control dataset size instead |
| **secret** | `string` | Required | - | Name of sensitive column to infer<br>Recommendation: Use target modeling column (Y) or most sensitive column |
| **aux_cols** | `array` | Optional | All columns except secret | List of columns used for inference |

### Others

{{< callout type="info" >}}
**Missing Value Handling**

For Linkability and Inference attacks, PETsARD automatically handles missing values:
- **Categorical columns**: Missing values are filled with the string "missing"
- **Numerical columns**: Columns are converted to float64 and missing values are filled with -999999

This ensures compatibility with anonymeter's evaluation functions, which require consistent data types for numba JIT compilation.
{{< /callout >}}

{{< callout type="warning" >}}
**Common Warning and Solutions**

If you encounter warnings like:
```
Reached maximum number of attempts 4000 when generating singling out queries.
Returning 1 instead of the requested 400.
Attack `multivariate` could generate only 1 singling out queries out of the requested 400.
```

**What this means**: The data has too few unique combinations to generate enough distinct attack queries. This typically occurs when:
- The dataset is too small
- Columns have low cardinality (few unique values)
- High correlation between columns limits unique combinations

**Solutions**:
1. **Reduce n_attacks**: Set to a smaller value (e.g., 100-500) for small datasets
2. **Increase max_attempts**: Allow more attempts to find unique queries (but this increases computation time)
3. **Adjust n_cols**: Try using fewer columns per query (e.g., 2 instead of 3)
4. **Accept the limitation**: If the warning persists, it indicates the data inherently has limited attack surface, which may actually suggest better privacy protection
{{< /callout >}}

## Assessment Framework

Anonymeter evaluates privacy risks from three perspectives:

### Singling Out Risk
Assesses the possibility of identifying specific individuals within the data. For example: "finding an individual with unique characteristics X, Y, and Z."

### Linkability Risk
Evaluates the possibility of linking records belonging to the same individual across different datasets. For example: "determining that records A and B belong to the same person."

For handling mixed data types, this assessment uses Gower's Distance:
- Numerical variables: Normalized absolute difference
- Categorical variables: Distance of 1 if unequal

### Inference Risk
Measures the possibility of inferring attributes from known characteristics. For example: "determining characteristic Z for individuals with characteristics X and Y."

## Evaluation Metrics

| Metric | Description | Range | Recommended Standard |
|--------|-------------|-------|---------------------|
| **risk** | Privacy risk score<br>Calculation: `(main attack rate - control attack rate) / (1 - control attack rate)` | 0-1 | < 0.09¹ |
| **attack_rate** | Main privacy attack rate (success rate of inferring training data using synthetic data) | 0-1 | - |
| **baseline_rate** | Baseline privacy attack rate (success rate baseline for random guessing) | 0-1 | - |
| **control_rate** | Control privacy attack rate (success rate of inferring control data using synthetic data) | 0-1 | - |

## Risk Calculation Details

### Privacy Risk Score Formula

The privacy risk score quantifies the additional risk introduced by synthetic data:

$$
\text{Privacy Risk} = \frac{\text{Attack Rate}_{\text{Main}} - \text{Attack Rate}_{\text{Control}}}{1 - \text{Attack Rate}_{\text{Control}}}
$$

This formula measures:
- **Numerator**: Additional risk introduced by synthetic data (relative to control group)
- **Denominator**: Maximum effect of ideal attack (relative to control group)

Scores range from 0-1, with higher values indicating greater privacy risk.

### Attack Success Rate Calculation

Attack success rate is calculated using Wilson score for better statistical accuracy:

$$
\text{Attack Rate} = \frac{N_{\text{Success}} + \frac{Z^2}{2}}{N_{\text{Total}} + Z^2}
$$

Where:
- N_Success: Number of successful attacks
- N_Total: Total number of attacks
- Z: Z-score for 95% confidence level (1.96)

### Three Types of Attack Rates

1. **Main Attack Rate**: Success rate of using synthetic data to infer original training data

2. **Baseline Attack Rate**: Success rate of random guessing
   - If main attack rate ≤ baseline, the assessment is invalid for reference
   - Possible causes: insufficient attack attempts, limited auxiliary information, data characteristic issues

3. **Control Attack Rate**: Success rate of using synthetic data to infer control group data (holdout set)

## References

1. Personal Data Protection Commission Singapore. (2023). *Proposed guide on synthetic data generation*. https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/proposed-guide-on-synthetic-data-generation.pdf

2. Article 29 Working Party. (2014). *Opinion 05/2014 on Anonymisation Techniques* (WP216). https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf

3. Anonymeter GitHub Repository. https://github.com/statice/anonymeter

4. French Data Protection Authority (CNIL). https://www.cnil.fr/en/home

## Notes

{{< callout type="warning" >}}
The risk calculated by Anonymeter is only one evaluation approach for each attack mode. A score of 0.0 does not mean zero risk. To avoid potential "Harvest Now, Decrypt Later" (HNDL) risks, users should interpret results with caution.
{{< /callout >}}

- If main attack rate ≤ baseline attack rate, the evaluation is not suitable for reference
- Possible causes: Insufficient attacks, inadequate auxiliary information, data characteristic issues
- Recommend combining with other protection measures to protect synthetic data