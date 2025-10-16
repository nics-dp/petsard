---
title: "mpUCCs Privacy Risk Assessment (Experimental)"
weight: 6
---

{{< callout type="warning" >}}
**Experimental Feature**: MPUCCs is an experimental privacy risk assessment method that is still under development. The API and behavior may change in future versions.
{{< /callout >}}

Evaluate privacy risks using Maximal Partial Unique Column Combinations (mpUCCs), an advanced singling-out risk assessment algorithm that identifies field combinations capable of uniquely identifying records.

## Usage Example

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/privacy-mpuccs.ipynb)

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
  mpuccs_assessment:
    method: mpuccs
    max_baseline_cols: 2        # Maximum columns to evaluate (default: null = all columns)
    min_entropy_delta: 0.01     # Minimum entropy gain threshold (default: 0.0)
    field_decay_factor: 0.5     # Field combination weighting decay (default: 0.5)
    renyi_alpha: 2.0            # Rényi entropy parameter (default: 2.0)
    numeric_precision: null     # Auto-detect or specify decimal places (default: null)
    datetime_precision: null    # Auto-detect or specify time precision (default: null)
    calculate_baseline: true    # Calculate baseline protection metrics (default: true)
```

## Overview

MPUCCs (Maximal Partial Unique Column Combinations) implements an advanced privacy risk assessment based on:
- **Theory**: mpUCCs = QIDs (Quasi-identifiers)
- **Core Concept**: Singling-out attacks find unique field combinations in synthetic data that correspond to unique records in original data
- **Advantage**: Avoids overestimation by focusing on maximal combinations only
- **Framework**: Implements three-layer protection metrics based on SAFE framework

### Key Features
1. Progressive tree-based search with entropy-based pruning
2. Automatic precision handling for numeric and datetime fields
3. Weighted risk calculation with field decay factor
4. Comprehensive progress tracking
5. **Three-layer Protection Metrics**:
   - Main Protection: Direct protection against identification
   - Baseline Protection: Theoretical protection based on attribute distributions
   - Overall Protection: Normalized protection score (0-1)

## Theoretical Foundation

### Core Concepts

#### UCC (Unique Column Combinations)
A UCC is a field combination where all values are unique across all records in the dataset, with no duplicates.

**Example:**
For address data, the complete address is a unique value. An address can also be viewed as a unique combination of city, district, street, and house number.

#### pUCC (Partial Unique Column Combinations)
A pUCC is only unique under specific conditions or for specific values, rather than being unique across the entire dataset.

**Example:**
In most cases, street names and house numbers are not unique because many towns have streets with the same name. Only (1) special street names or (2) special house numbers are unique values.

#### mpUCCs (Maximal Partial Unique Column Combinations)
mpUCCs are pUCCs in maximal form, meaning there is no smaller subset that can achieve the same identification effect.

**Example:**
For "Zhongxiao East Road" "Section 1" "No. 1", since other cities also have Zhongxiao East Road, removing any field attribute would prevent unique identification, making this an mpUCC.

### Key Theoretical Insights

#### mpUCCs = QIDs (Quasi-identifiers)
The essence of singling-out attacks is:
1. Identifying a unique field combination in synthetic data
2. That combination also corresponds to only one unique record in the original data

This is essentially finding pUCCs and then checking if they are also pUCCs in the original data.

#### Self-contained Anonymity
A dataset is considered anonymized when no feature combination (IDs + QIDs) can uniquely identify an original entity.

**Finding QIDs (Find-QIDs problem) is equivalent to discovering mpUCCs!**

Repeatedly counting non-maximal field combinations overestimates risk - this is the inverse statement of singling-out risk having set-theoretic meaning!

## Algorithm Implementation

### Difficulty of the Find-QIDs Problem

1. For k attributes, there are 2^k - 1 potential QIDs
2. Proven to be W[2]-complete (Bläsius et al., 2017)
3. The problem lacks optimal substructure, so dynamic programming doesn't work

**Example:** Knowing that {A, B} and {B, C} have no pUCCs does not mean {A, B, C} has none.

### Our Solution: Heuristic Greedy Cardinality-First Algorithm

#### 1. High Cardinality Fields First
- Calculate cardinality for all fields
- For numeric fields, round to lowest precision
- Field combination breadth-first: from few to many, high cardinality first

#### 2. Set Operations on Field and Value Domain Combinations
- Use `collections.Counter` to capture synthetic data value combinations with only one occurrence
- Match original data with the same value combination and only one occurrence
- Record corresponding original and synthetic data indices

#### 3. Pruning Strategy
If all value combinations for a field combination are unique and collide, skip its supersets.

#### 4. Masking Mechanism
For synthetic data already identified by high-cardinality few-field combinations, that row no longer collides.

#### 5. Conditional Entropy-Based Early Stopping
Based on past research on information entropy for Functional Dependencies (Mandros et al., 2020), we propose:

**For field combinations with k ≥ 2:**

1. **Combination Entropy** H(XY) = entropy(Counter(syn_data[XY]) / syn_n_rows)
2. **Conditional Entropy** H(Y|X) = Σ p(X = x)*H(Y | X = x), where x ∈ {pUCC, ¬pUCC}
3. **Mutual Information** I(X; Y) = H(Y) - H(Y|X)

**Early Stopping:** If mutual information is negative, subsequent inherited field combinations are no longer checked.

#### 6. Rényi Entropy (α=2, Collision Entropy)
We use Rényi entropy instead of Shannon entropy for better collision probability analysis:

- **Theoretical Maximum Entropy** = log(n_rows)
- **Synthetic Data Maximum Entropy** = scipy.stats.entropy(Counter(syn_data))
- **Field Combination Entropy** = scipy.stats.entropy(Counter(syn_data[column_combos]))
- **Normalization** = Synthetic Data Maximum Entropy - Field Combination Entropy

## Data Preprocessing Details

MPUCCs performs several preprocessing steps to ensure accurate privacy risk assessment:

### Missing Value Handling
- **NA Comparison**: When comparing values, `pd.NA` (pandas missing value) is handled separately
- **Safe Comparison**: Uses `fillna(False)` to convert NA comparisons to False in boolean masks
- **Fallback Logic**: For edge cases, iterates through values with explicit NA checking

### Precision Processing

#### Numeric Precision
- **Auto-detection**: Automatically detects decimal places in floating-point numbers
- **Rounding**: Applies consistent rounding to specified decimal places using `round()`
- **Integer Preservation**: Integer columns remain unchanged

#### Datetime Precision
- **Auto-detection**: Detects minimum time precision (day, hour, minute, second, millisecond, microsecond, nanosecond)
- **Floor Operation**: Uses `dt.floor()` to round down to specified precision
- **Case-insensitive**: Supports various precision format inputs (e.g., 'D', 'd', 'H', 'h')

### Deduplication
- **Complete Duplicates**: Removes exact duplicate rows before analysis
- **Index Reset**: Resets DataFrame index after deduplication
- **Logging**: Reports number of removed duplicates

### Column Processing Order
- **Cardinality-based**: Sorts columns by number of unique values (descending)
- **High Cardinality First**: Processes columns with more unique values first
- **Efficiency**: This order typically leads to faster identification and better pruning

## Parameter Description

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **method** | `string` | Required | - | Fixed value: `mpuccs` |
| **max_baseline_cols** | `int`, `null` | Optional | null | Maximum number of columns to evaluate and calculate baseline<br>- `null` (default): Evaluate all possible combinations (1 to total columns)<br>- `int`: Evaluate combinations from 1 to n columns<br>Example: 5 = evaluate only 1, 2, 3, 4, 5 column combinations<br>**Controls both evaluation scope and baseline calculation**<br>Useful for limiting computation on datasets with many columns |
| **min_entropy_delta** | `float` | Optional | 0.0 | Minimum entropy gain threshold for pruning<br>Higher values = more aggressive pruning |
| **field_decay_factor** | `float` | Optional | 0.5 | Decay factor for field combination weighting<br>Reduces weight for larger combinations |
| **renyi_alpha** | `float` | Optional | 2.0 | Alpha parameter for Rényi entropy calculation<br>- α=0: Hartley entropy (max-entropy)<br>- α=1: Shannon entropy<br>- α=2: Collision entropy (default)<br>- α→∞: Min-entropy<br>Higher α values give more weight to frequent values |
| **numeric_precision** | `int`, `null` | Optional | null | Precision for numeric field comparison<br>- `null`: Auto-detect<br>- `int`: Decimal places |
| **datetime_precision** | `string`, `null` | Optional | null | Precision for datetime field comparison<br>- `null`: Auto-detect<br>- Options: 'D', 'H', 'T', 's', 'ms', 'us', 'ns' |
| **calculate_baseline** | `boolean` | Optional | true | Enable calculation of baseline protection metrics<br>Based on attribute value distributions |

### Datetime Precision Options
- `D`: Day
- `H`: Hour
- `T`: Minute
- `s`: Second
- `ms`: Millisecond
- `us`: Microsecond
- `ns`: Nanosecond

## Evaluation Results

MPUCCs returns three types of results:

### 1. Global Statistics (`global`)
Simplified privacy risk metrics following Plan B (Three-layer Protection):

#### Core Metrics (Ordered by Importance)
When `calculate_baseline=true`:
1. **`privacy_risk_score`** ⭐ - Overall privacy risk (0=safe, 1=risky)
   - Formula: `1 - overall_protection`
   - **Most important metric for decision making**

2. **`overall_protection`** - Normalized protection score (0-1)
   - Formula: `min(main_protection / baseline_protection, 1.0)`
   - Compares actual protection to theoretical best

3. **`main_protection`** - Direct protection against identification
   - Formula: `1 - identification_rate`
   - Raw protection provided by synthetic data

4. **`baseline_protection`** - Theoretical protection from data structure
   - Based on attribute cardinalities
   - Represents protection of perfectly random data

5. **`identification_rate`** - Proportion of records identified
   - Formula: `identified_records / total_records`

6. **`total_identified`** - Number of records identified
7. **`total_syn_records`** - Total synthetic records

When `calculate_baseline=false`:
- `identification_rate` - Primary risk metric
- `main_protection` - Simple protection (1 - identification_rate)
- `total_identified` - Number of records identified
- `total_syn_records` - Total synthetic records

### 2. Detailed Results (`details`)
Simplified collision information with risk-first ordering:

#### Field Order (by importance)
1. **`risk_level`** ⭐ - Risk classification (high/medium/low)
   - Placed first for quick risk assessment
2. **`syn_idx`** - Index in synthetic data
3. **`ori_idx`** - Corresponding index in original data
4. **`combo_size`** - Size of the identifying combination
5. **`field_combo`** - Field combination used
6. **`value_combo`** - Actual values that caused identification
7. **`baseline_protection`** - Baseline protection for this combination (if enabled)

#### Risk Level Classification
- **high**: Protection ratio < 0.3 or combo_size ≤ 2
- **medium**: Protection ratio 0.3-0.7 or combo_size 3-4
- **low**: Protection ratio > 0.7 or combo_size ≥ 5

### 3. Tree Search Results (`tree`)
Simplified search tree with essential fields first:

#### Core Fields (always present)
1. **`check_order`** - Evaluation sequence number
2. **`field_combo`** - Field combination being tested
3. **`combo_size`** - Number of fields in combination
4. **`is_pruned`** - Whether combination was pruned (true/false)
5. **`mpuccs_cnt`** - Unique combinations found in synthetic data
6. **`mpuccs_collision_cnt`** - Successfully identified records

#### Protection Metrics (if baseline enabled)
7. **`baseline_protection`** - Theoretical protection for this combination
8. **`overall_protection`** - Normalized protection score (if collisions found)

#### Technical Details (only with non-default settings)
These fields appear only when using non-default entropy or decay settings:
- **`entropy`** - Combination entropy value
- **`entropy_gain`** - Entropy improvement over base combination
- **`field_weight`** - Weight factor for this combination
- **`weighted_collision`** - Weighted collision count

{{< callout type="info" >}}
**Simplified Output**: Tree results now prioritize essential information. Technical details are hidden when using default settings to reduce clutter.
{{< /callout >}}

## Best Practices

1. **Start with Small Combinations**: Begin with `n_cols: [1, 2, 3]` to assess basic risks
2. **Adjust Entropy Threshold**: Increase `min_entropy_delta` for faster evaluation with more pruning
3. **Precision Settings**: Let auto-detection handle precision unless specific requirements exist
4. **Interpret Results**:
   - Use `overall_protection` for standardized risk assessment (0-1 scale)
   - Compare `main_protection` vs `baseline_protection` to understand risk sources
   - Focus on `privacy_risk_score` for executive summaries

## Comparison with Traditional Methods
## Key Improvements over Anonymeter

### 1. Theoretical Foundation
- **Clear Theoretical Basis**: mpUCCs = QIDs provides solid mathematical foundation
- **Avoids Risk Overestimation**: Focuses on maximal form combinations
- **Set-Theoretic Meaning**: Correctly understands the nature of singling-out risk

### 2. Algorithm Optimization
- **Progressive Tree-based Search**: Efficient field combination exploration
- **Entropy-based Pruning**: Intelligent early stopping mechanism
- **Cardinality-first Processing**: High cardinality fields processed first
- **Collision-oriented Analysis**: Directly focuses on actual privacy risk

### 3. Precision Handling
- **Automatic Numeric Precision Detection**: Handles floating-point comparison issues
- **Datetime Precision Support**: Appropriate handling of time data
- **Manual Precision Override**: Allows custom precision settings

### 4. Performance Improvements
- **Faster Execution**: 44 seconds vs 12+ minutes on adult-income dataset
- **Better Scalability**: Efficiently handles high-dimensional data
- **Memory Optimization**: Counter-based uniqueness detection

### 5. Comprehensive Progress Tracking
- **Dual-layer Progress Bars**: Field-level and combination-level progress
- **Detailed Execution Tree**: Complete audit trail of algorithm decisions
- **Pruning Statistics**: Transparency of optimization decisions

### Performance Comparison with Anonymeter
| Metric | Anonymeter | mpUCCs | Improvement |
|--------|------------|--------|-------------|
| Execution Time (adult-income, n_cols=3) | 12+ minutes | 44 seconds | 16x faster |
| Singling-out Attack Detection | ~1,000-2,000 (random sampling) | 7,999 (complete evaluation) | Full coverage |
| Theoretical Foundation | Heuristic | Mathematical theory | Solid theory |
| Risk Overestimation | High | Low | Accurate assessment |
| Progress Visibility | Not supported | Comprehensive | Full transparency |
| Precision Handling | Not supported | Automatic | Better usability |

## Performance Characteristics

### Computational Complexity
- **Time Complexity**: Worst case O(2^k), but with significant pruning
- **Space Complexity**: O(n*k) where n is number of records, k is number of fields
- **Actual Performance**: Linear to sub-quadratic on real datasets due to pruning

### Scalability
- **Field Scalability**: Highly scalable through pruning - efficiently handles datasets with many fields
- **Record Scalability**: Tested on datasets with 100K+ records
- **Memory Efficiency**: Counter-based operations minimize memory usage


| Aspect | MPUCCs | Traditional Singling Out |
|--------|--------|-------------------------|
| **Combination Selection** | Maximal only | All combinations |
| **Risk Estimation** | More accurate | May overestimate |
| **Performance** | Optimized with pruning | Exhaustive search |
| **Weighting** | Field decay factor | Usually uniform |
| **Precision Handling** | Built-in | Manual preprocessing |
| **Baseline Comparison** | Three-layer protection | Simple identification rate |
| **Risk Normalization** | 0-1 scale with baseline | Raw percentages |

## Notes

{{< callout type="info" >}}
**Performance Considerations**
- Large datasets with many columns may require significant computation time
- Use `n_cols` parameter to limit combination sizes
- Increase `min_entropy_delta` for more aggressive pruning
{{< /callout >}}

{{< callout type="warning" >}}
**Interpretation Guidelines**
- A score of 0.0 does not mean zero risk
- Consider results alongside other privacy metrics
- Account for "Harvest Now, Decrypt Later" (HNDL) risks
{{< /callout >}}

## Risk Threshold Recommendations 🎯

### Executive Summary
For most use cases, we recommend targeting a **privacy_risk_score < 0.1** (equivalent to overall_protection > 0.9).

### Detailed Risk Thresholds by Use Case

| Use Case | Privacy Risk Score | Overall Protection | Recommendation |
|----------|-------------------|-------------------|----------------|
| **Public Release** | < 0.05 | > 0.95 | Very low risk, suitable for public datasets |
| **Research Sharing** | < 0.10 | > 0.90 | Low risk, suitable for research collaborations |
| **Internal Analytics** | < 0.20 | > 0.80 | Acceptable for internal use with access controls |
| **Development/Testing** | < 0.30 | > 0.70 | OK for development with synthetic data |
| **High-Risk Data** | < 0.01 | > 0.99 | Medical/financial data requiring maximum protection |

### Additional Metrics Guidelines

#### Identification Rate Thresholds
- **Excellent**: < 1% records identified
- **Good**: 1-5% records identified
- **Acceptable**: 5-10% records identified
- **Poor**: > 10% records identified

#### Baseline Protection Considerations
- If `baseline_protection > 0.95`: Data structure inherently provides good protection
- If `baseline_protection < 0.90`: Consider adding noise or generalizing attributes
- If `baseline_protection < 0.80`: High-risk data structure, needs significant protection measures

### Mitigation Strategies by Risk Level

{{< callout type="info" >}}
**High Risk (privacy_risk_score > 0.3)**
- Add differential privacy noise
- Generalize or suppress high-risk attributes
- Increase k-anonymity parameter
- Consider using fully synthetic data
{{< /callout >}}

{{< callout type="warning" >}}
**Medium Risk (0.1 < privacy_risk_score ≤ 0.3)**
- Review and generalize quasi-identifiers
- Apply targeted suppression on rare values
- Implement access controls
- Monitor usage patterns
{{< /callout >}}

{{< callout type="success" >}}
**Low Risk (privacy_risk_score ≤ 0.1)**
- Standard release procedures apply
- Document privacy measures taken
- Regular re-evaluation recommended
- Suitable for most use cases
{{< /callout >}}

### Continuous Monitoring Recommendations
1. **Quarterly Reviews**: Re-evaluate privacy metrics every 3 months
2. **Data Drift Monitoring**: Check if data distributions change significantly
3. **Attack Evolution**: Update thresholds based on new attack techniques
4. **Regulatory Updates**: Adjust thresholds for new privacy regulations

## Understanding the Simplified Metrics

### Why Privacy Risk Score First?
The **privacy_risk_score** is placed first because it's the single most important metric for decision-making:
- **0.0 - 0.1**: Very low risk, safe to release
- **0.1 - 0.3**: Acceptable risk for internal use
- **0.3 - 0.5**: Medium risk, needs additional protection
- **0.5 - 1.0**: High risk, not recommended for release

### Three-layer Protection Model Explained

1. **Privacy Risk Score** (Top Level - Decision Metric)
   - What executives need to know
   - Single number for risk assessment
   - Formula: `1 - overall_protection`

2. **Overall Protection** (Normalized Comparison)
   - Compares synthetic data quality to theoretical best
   - Accounts for data structure limitations
   - Value of 1.0 means "as good as random data"

3. **Main vs Baseline Protection** (Detailed Analysis)
   - **Main**: Actual protection achieved
   - **Baseline**: Maximum possible protection given data structure
   - Ratio reveals synthesis quality

### Example Interpretation
```
privacy_risk_score: 0.15     # Low risk (good!)
overall_protection: 0.85      # 85% of theoretical maximum
main_protection: 0.90         # 90% records protected
baseline_protection: 0.95     # Could achieve 95% with random data
identification_rate: 0.10     # 10% records identified
total_identified: 100         # 100 records at risk
total_syn_records: 1000       # Out of 1000 total
```
**Conclusion**: The synthetic data performs well (85% of theoretical best), with acceptable risk level (0.15).

## Limitations and Future Work

### Current Limitations
1. **Experimental Status**: Still under active development and validation
2. **Memory Usage**: May be memory-intensive for very high-dimensional data
3. **Risk Weighting**: Theoretically sound risk weighting methods are under research, currently set to field_decay_factor = 0.5

### Future Enhancements
1. **Distributed Computing**: Support for parallel processing of large datasets (nice-to-have)

## References

1. Abedjan, Z., & Naumann, F. (2011). Advancing the discovery of unique column combinations. In Proceedings of the 20th ACM international conference on Information and knowledge management (pp. 1565-1570).

2. Mandros, P., Kaltenpoth, D., Boley, M., & Vreeken, J. (2020). Discovering Functional Dependencies from Mixed-Type Data. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 1404-1414).

3. Bläsius, T., Friedrich, T., Lischeid, J., Meeks, K., & Schirneck, M. (2017). Efficiently enumerating hitting sets of hypergraphs arising in data profiling. In Proceedings of the 16th International Symposium on Experimental Algorithms (pp. 130-145).

## Support and Feedback

As an experimental feature, mpUCCs is under active development and improvement. We welcome feedback, bug reports, and suggestions for improvement. Please refer to the project's issue tracker to report issues or request features.