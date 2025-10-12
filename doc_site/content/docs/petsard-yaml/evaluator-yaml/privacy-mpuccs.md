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

### Key Features
1. Progressive tree-based search with entropy-based pruning
2. Automatic precision handling for numeric and datetime fields
3. Weighted risk calculation with field decay factor
4. Comprehensive progress tracking

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
    n_cols:        # Combination sizes to evaluate (default: null = all sizes from 1 to total columns)
      - 1
      - 2
    min_entropy_delta: 0.01     # Minimum entropy gain threshold (default: 0.0)
    field_decay_factor: 0.5     # Field combination weighting decay (default: 0.5)
    renyi_alpha: 2.0            # Rényi entropy parameter (default: 2.0)
    numeric_precision: null     # Auto-detect or specify decimal places (default: null)
    datetime_precision: null    # Auto-detect or specify time precision (default: null)
```

## Parameter Description

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **method** | `string` | Required | - | Fixed value: `mpuccs` |
| **n_cols** | `int`, `list`, `null` | Optional | null | Target combination sizes to evaluate<br>- `null` (default): All possible sizes from 1 to total number of columns<br>- `int`: Single specific size<br>- `list`: Multiple specific sizes |
| **min_entropy_delta** | `float` | Optional | 0.0 | Minimum entropy gain threshold for pruning<br>Higher values = more aggressive pruning |
| **field_decay_factor** | `float` | Optional | 0.5 | Decay factor for field combination weighting<br>Reduces weight for larger combinations |
| **renyi_alpha** | `float` | Optional | 2.0 | Alpha parameter for Rényi entropy calculation<br>- α=0: Hartley entropy (max-entropy)<br>- α=1: Shannon entropy<br>- α=2: Collision entropy (default)<br>- α→∞: Min-entropy<br>Higher α values give more weight to frequent values |
| **numeric_precision** | `int`, `null` | Optional | null | Precision for numeric field comparison<br>- `null`: Auto-detect<br>- `int`: Decimal places |
| **datetime_precision** | `string`, `null` | Optional | null | Precision for datetime field comparison<br>- `null`: Auto-detect<br>- Options: 'D', 'H', 'T', 's', 'ms', 'us', 'ns' |

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
Overall privacy risk metrics including:
- `total_syn_records`: Total synthetic records
- `total_ori_records`: Total original records
- `total_identified`: Number of records identified
- `identification_rate`: Proportion of identified records
- `weighted_identification_rate`: Weighted identification rate
- `total_combinations_checked`: Number of combinations evaluated
- `total_combinations_pruned`: Number of pruned combinations

### 2. Detailed Results (`details`)
Specific collision information for each identified record:
- `combo_size`: Size of the identifying combination
- `syn_idx`: Index in synthetic data
- `field_combo`: Field combination used
- `value_combo`: Actual values that caused identification
- `ori_idx`: Corresponding index in original data

### 3. Tree Search Results (`tree`)
Complete search tree showing:
- `check_order`: Evaluation sequence
- `combo_size`: Combination size
- `field_combo`: Field combination
- `combo_entropy`: Entropy of the combination
- `entropy_gain`: Entropy improvement over base
- `is_pruned`: Whether combination was pruned
- `mpuccs_cnt`: Number of unique combinations in synthetic data
- `mpuccs_collision_cnt`: Number of collisions found
- `weighted_mpuccs_collision_cnt`: Weighted collision count

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
4. **Interpret Results**: Focus on `weighted_identification_rate` for overall risk assessment

## Comparison with Traditional Methods

| Aspect | MPUCCs | Traditional Singling Out |
|--------|--------|-------------------------|
| **Combination Selection** | Maximal only | All combinations |
| **Risk Estimation** | More accurate | May overestimate |
| **Performance** | Optimized with pruning | Exhaustive search |
| **Weighting** | Field decay factor | Usually uniform |
| **Precision Handling** | Built-in | Manual preprocessing |

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