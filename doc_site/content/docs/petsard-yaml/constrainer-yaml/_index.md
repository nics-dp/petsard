---
title: "Constrainer YAML"
weight: 140
---

The Constrainer module is used to define constraints for synthetic data, supporting two operational modes.

## Main Parameters

- **method** (`string`, optional)
  - Operating mode
  - `auto`: Automatically determines mode (has Synthesizer and not custom_data → resample, otherwise → validate)
  - `resample`: Resampling mode
  - `validate`: Validation mode
  - Default: `auto`

- **constraints_yaml** (`string`, optional)
  - Path to external constraints file
  - Use exclusively with individual constraint parameters

- **Constraint Parameters** (optional)
  - `nan_groups`: NaN handling rules
  - `field_constraints`: Field constraint conditions
  - `field_combinations`: Field combination rules
  - `field_proportions`: Field proportion maintenance
  - Use exclusively with `constraints_yaml`

- **Sampling Parameters** (optional, resample mode only)
  - `target_rows`: Target number of output rows
  - `sampling_ratio`: Sampling multiplier per attempt (default 10.0)
  - `max_trials`: Maximum number of attempts (default 300)
  - `verbose_step`: Progress output interval (default 10)

## Operating Modes

The Constrainer controls operating mode through the `method` parameter (default is `auto` for automatic determination):

### Mode Selection Decision Tree

 When method='auto':

{{< mermaid-file file="content/docs/petsard-yaml/constrainer-yaml/mode-decision-tree.mmd" >}}

**Legend**:
- 🟢 **Start**: Flow begins
- 🟠 **Decision**: Conditional judgment (diamond)
- 🔵 **Mode**: Selected operating mode
- 🟣 **Result**: Final output

### Resample Mode

Iterative Sampling Until Constraints Met

**When to use**: Synthetic data generation pipeline (has Synthesizer and not custom_data)

**Workflow**:

{{< mermaid-file file="content/docs/petsard-yaml/constrainer-yaml/resample-flow.mmd" >}}

**Legend**:
- 🔵 **Process**: Generate data, apply constraints
- 🟠 **Decision**: Check if sufficient rows
- 🟢 **Result**: Final output

**Features**:
- ✅ Automatic resampling until sufficient compliant data obtained
- ✅ Filters non-compliant data
- ✅ Records sampling attempts
- 💡 Optional `target_rows`, `sampling_ratio` parameters to optimize performance

### Validate Mode

Check Data Compliance

**When to use**:
- Using Synthesizer's `custom_data` method (external data files)
- Pipeline without Synthesizer
- Need to check existing data compliance
- Manually specify `method='validate'`

**Workflow**:

{{< mermaid-file file="content/docs/petsard-yaml/constrainer-yaml/validate-flow.mmd" >}}

**Legend**:
- 🔵 **Input**: Read data
- 🟠 **Process**: Check constraints, record violations
- 🟢 **Result**: Output data and report

**Features**:
- ✅ Retains all data (does not delete violations)
- ✅ Provides detailed violation statistics and records
- ✅ Outputs pass rate, violation ratios and analysis
- ✅ Reporter can output validation reports
- ⚠️ Does not use `target_rows`, `sampling_ratio` sampling parameters (ignored even if set)

**Validation Report Format**:

Use the `Reporter`'s `SAVE_VALIDATION` method to export validation results as CSV reports includes:

1. **`{output}_summary.csv`** - Overall statistics summary

| Metric | Value |
|--------|-------|
| total_rows | 1000 |
| passed_rows | 850 |
| failed_rows | 150 |
| pass_rate | 0.850000 |
| is_fully_compliant | False |

2. **`{output}_violations.csv`** - Constraint violation statistics

| Constraint Type | Rule | Failed Count | Fail Rate | Violation Examples | Error Message |
|-----------------|------|--------------|-----------|-------------------|---------------|
| field_constraints | age >= 18 & age <= 65 | 80 | 0.080000 | 5, 12, 23 | |
| field_constraints | salary > 30000 | 40 | 0.040000 | 8, 15, 31 | |
| field_combinations | education-income | 30 | 0.030000 | 2, 9, 17 | |

3. **`{output}_details.csv`** - Detailed violation records (optional, maximum 10 records per rule)

| Constraint Type | Rule | Violation Index | age | salary | education | income |
|-----------------|------|-----------------|-----|--------|-----------|--------|
| field_constraints | age >= 18 & age <= 65 | 1 | 15 | 35000 | HS-grad | <=50K |
| field_constraints | age >= 18 & age <= 65 | 2 | 16 | 42000 | Bachelors | <=50K |
| field_constraints | salary > 30000 | 1 | 25 | 28000 | Masters | <=50K |

## Constraint Types

Constrainer supports four constraint types with fixed execution order:

```
nan_groups (NaN handling)
  ↓
field_constraints (Field constraints)
  ↓
field_combinations (Field combinations)
  ↓
field_proportions (Field proportions)
```

For detailed explanations, see respective pages.

## Usage Examples and Configuration

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer.ipynb)

### Resample Mode: Inline Constraints Configuration

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  default:
    method: default
Constrainer:
  inline_field_constraints:
    # Operating mode setting
    method: auto  # Operating mode, default 'auto' (auto-detect: has Synthesizer and not custom_data → resample)
    # Constraint conditions (use exclusively with constraints_yaml)
    field_constraints:      # Field constraint conditions, default none
                            # Age between 18 and 65
      - "age >= 18 & age <= 65"
    # Sampling parameters (resample mode only)
    target_rows: None        # Target number of output rows, optional (defaults to input data row count if not specified or set to None)
    sampling_ratio: 10.0     # Sampling multiplier per attempt, default 10.0
    max_trials: 300          # Maximum number of attempts, default 300
    verbose_step: 10         # Progress output interval, default 10
```

### Resample Mode: External Constraints File (Recommended)

**Advantages of External Files**:
- ✅ Better maintainability: Complex constraints independently managed
- ✅ Reusability: Same constraints can be reused across experiments
- ✅ Version control: Constraint files can be versioned independently
- ✅ Clear separation of concerns: Main YAML focuses on pipeline configuration, constraint files focus on data rules

{{< callout type="warning" >}}
**Important**: Cannot use both `constraints_yaml` and individual constraint parameters simultaneously.
{{< /callout >}}

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  default:
    method: default
Constrainer:
  inline_field_constraints:
    # Operating mode setting
    method: auto  # Operating mode, default 'auto' (auto-detect: has Synthesizer and not custom_data → resample)
    # Constraint conditions (use exclusively with setting)
    constraints_yaml: adult-income_constraints.yaml
    # Sampling parameters (resample mode only)
    target_rows: None        # Target number of output rows, defaults None to input data row count
    sampling_ratio: 10.0     # Sampling multiplier per attempt, default 10.0
    max_trials: 300          # Maximum number of attempts, default 300
    verbose_step: 10         # Progress output interval, default 10
```

### Validate Mode: Single Data Source

Validate constraint compliance for a single data source.

#### Source Parameter Specification

The `source` parameter specifies the data source to validate, supporting the following formats:

**Basic Formats**:
- **Single Module**: `source: Loader` (uses module's default output)
- **Module.Key**: `source: Splitter.ori` (specifies module's specific output)

**Splitter Special Notes**:
- Splitter has two outputs: `ori` (training set) and `control` (validation set)
- Internally stored as `train` and `validation`, but users can use familiar names
- Supported aliases:
  - `Splitter.ori` → `Splitter.train`
  - `Splitter.control` → `Splitter.validation`

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
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Constrainer:
  inline_field_constraints:
    method: auto          # Automatically selects validate mode
    source: Splitter.ori  # Specify single data source (optional if only one source exists)
    constraints_yaml: adult-income_constraints.yaml
```

### Validate Mode: Multiple Data Sources

Validate constraint compliance for multiple data sources simultaneously (using list format):

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
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
Constrainer:
  inline_field_constraints:
    method: auto  # Automatically selects validate mode
    source:       # Use list format for multiple sources
      - Loader
      - Splitter.ori
      - Splitter.control
      - Synthesizer
    constraints_yaml: adult-income_constraints.yaml
```

### Force Specific Mode

Force validate mode even with Synthesizer-generated data (no resampling):

```yaml
---
Synthesizer:
  demo:
    method: GaussianCopula

Constrainer:
  demo:
    method: validate  # Force validate mode (no resampling)
    source: Synthesizer
    field_constraints:
      - "age >= 18"
...
```

### External Constraints File Example

For complex constraint configurations, use external YAML files.

**File Example** ([`adult-income_constraints.yaml`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/adult-income_constraints.yaml)):

```yaml
nan_groups:
  workclass: 'delete'
  occupation:
    'erase': ['income']
  age:
    'copy': 'educational-num'

field_constraints:
  - "age >= 18 & age <= 65"
  - "hours-per-week >= 20 & hours-per-week <= 60"

field_combinations:
  -
    - education: income
    - Doctorate: ['>50K']
      Masters: ['>50K', '<=50K']

field_proportions:
  - education:
      mode: 'all'
      tolerance: 0.1
  - income:
      mode: 'all'
      tolerance: 0.05
```

## Important Notes

{{< callout type="warning" >}}
**Constraint Logic and Configuration Rules**

- **AND Logic Combination**: All constraint conditions must be satisfied simultaneously; a record is retained only if it passes all checks
- **Fixed Execution Order**: `nan_groups` → `field_constraints` → `field_combinations` → `field_proportions`, cannot be adjusted
- **Positive Listing Approach**: `field_combinations` only affects explicitly listed values; unlisted combinations are considered invalid
- **Field Proportion Maintenance**: `field_proportions` maintains distribution by iteratively removing excess records while protecting underrepresented groups
- **NaN Representation**: Must use string `"pd.NA"` (case-sensitive); avoid using `None`, `null`, or `np.nan`
- **YAML String Format**: String values must be quoted, e.g., `"HS-grad"` not `HS-grad`
- **Exclusive Configuration**: `constraints_yaml` and individual constraint parameters (`field_constraints`, etc.) cannot be used simultaneously
- **Mode Restrictions**: Validate mode ignores sampling parameters (`target_rows`, `sampling_ratio`, etc.)
{{< /callout >}}