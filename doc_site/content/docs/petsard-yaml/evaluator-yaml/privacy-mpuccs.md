---
title: "mpUCCs Privacy Risk Assessment (Experimental)"
weight: 147
---

{{< callout type="warning" >}}
**Experimental Feature**: MPUCCs is an experimental privacy risk assessment method that is still under development. The API and behavior may change in future versions.
{{< /callout >}}

Evaluate privacy risks using Maximal Partial Unique Column Combinations (mpUCCs), an advanced singling-out risk assessment algorithm that identifies field combinations capable of uniquely identifying records.

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

## Usage Example

```yaml
Evaluator:
  mpuccs_assessment:
    method: mpuccs
    max_baseline_cols: null     # Maximum columns to evaluate (default: null = all columns)
    min_entropy_delta: 0.01     # Minimum entropy gain threshold (default: 0.0)
    field_decay_factor: 0.5     # Field combination weighting decay (default: 0.5)
    renyi_alpha: 2.0            # Rényi entropy parameter (default: 2.0)
    numeric_precision: null     # Auto-detect or specify decimal places (default: null)
    datetime_precision: null    # Auto-detect or specify time precision (default: null)
    calculate_baseline: true    # Calculate baseline protection metrics (default: true)
```

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

## Algorithm Details

### Progressive Field Search
1. Fields are processed in descending order of cardinality
2. For each field, combinations are built progressively
3. Entropy-based pruning eliminates ineffective combinations
4. Only maximal combinations are retained

### Entropy Calculation
Uses Rényi entropy (α=2, Collision Entropy):
```
H₂(X) = -log₂(∑ pᵢ²)
```
Normalized to [0, 1] range for comparison

### Weighting Scheme
- Single field: weight = 1.0
- Multiple fields: weight = decay_factor^(size-1)
- Penalizes larger combinations to avoid overestimation

## Best Practices

1. **Start with Small Combinations**: Begin with `n_cols: [1, 2, 3]` to assess basic risks
2. **Adjust Entropy Threshold**: Increase `min_entropy_delta` for faster evaluation with more pruning
3. **Precision Settings**: Let auto-detection handle precision unless specific requirements exist
4. **Interpret Results**:
   - Use `overall_protection` for standardized risk assessment (0-1 scale)
   - Compare `main_protection` vs `baseline_protection` to understand risk sources
   - Focus on `privacy_risk_score` for executive summaries

## Comparison with Traditional Methods

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