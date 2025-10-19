---
title: "Constrainer YAML"
weight: 160
---

Data constraints are a sophisticated mechanism for fine-grained control of synthetic data quality and consistency, enabling users to define acceptable data ranges through multi-layered rules. `PETsARD` provides four primary constraint types: NaN group constraints, field constraints, field combination constraints, and field proportion constraints. These constraints work together to ensure that generated synthetic data not only faithfully preserves statistical properties of the original data, but also conforms to specific domain logic and business requirements.

The Constrainer module supports two operational modes: **Resample mode** and **Validate mode**, which can be automatically selected or manually specified based on different use cases.

## Usage Examples

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
#### Constraints File Example

Below is the complete content of [`adult-income_constraints.yaml`](demo/petsard-yaml/constrainer-yaml/adult-income_constraints.yaml:1), demonstrating practical applications of all four constraint types:

```yaml
nan_groups:             # NaN handling rules, default none
                        # Delete entire row when workclass is NA
  workclass: 'delete'
                        # Set income to NA when occupation is NA
  occupation:
    'erase':
      - 'income'
                        # Copy value from educational-num to age when age is NA and educational-num has value
  age:
    'copy':
      'educational-num'
field_constraints:      # Field constraint conditions, default none
                        # Age between 18 and 65
  - "age >= 18 & age <= 65"
                        # Hours per week between 20 and 60
  - "hours-per-week >= 20 & hours-per-week <= 60"
field_combinations:     # Field value pairing relationships, default none
                        # Doctorate education can only have >50K income
                        # Masters education can have >50K or <=50K income
  -
    - education: income
    - Doctorate:
        - '>50K'
      Masters:
        - '>50K'
        - '<=50K'
field_proportions:      # Field proportion maintenance, default none
                        # Maintain education distribution, 10% tolerance
  - fields: 'education'
    mode: 'all'
    tolerance: 0.1
                        # Maintain income distribution, 5% tolerance
  - fields: 'income'
    mode: 'all'
    tolerance: 0.05
                        # Maintain workclass missing value proportion, 3% tolerance
  - fields: 'workclass'
    mode: 'missing'
    tolerance: 0.03
```

#### Constraint Explanations

##### 1. NaN Group Constraints (nan_groups)

**NaN handling rules, default none**

- **`workclass: 'delete'`**
  - 🌐 **English**: Delete entire row when workclass is NA
  - 🇹🇼 **繁體中文**: 當 `workclass` 欄位為空值時，刪除整筆資料
  - 💡 **Explanation**: This rule ensures all retained records have complete workclass information

- **`occupation` with `erase` rule**
  - 🌐 **English**: Set income to NA when occupation is NA
  - 🇹🇼 **繁體中文**: 當 `occupation` 欄位為空值時，將 `income` 欄位設為空值
  - 💡 **Explanation**: Establishes correlation between occupation and income; income data is unreliable without occupation information

- **`age` with `copy` rule**
  - 🌐 **English**: Copy value from educational-num to age when age is NA and educational-num has value
  - 🇹🇼 **繁體中文**: 當 `age` 欄位為空值且 `educational-num` 有值時，將 `educational-num` 的值複製到 `age`
  - 💡 **Explanation**: An imputation strategy using years of education to estimate age (demonstration only; practical use requires feasibility assessment)

##### 2. Field Constraints (field_constraints)

**Field constraint conditions, default none**

- **`"age >= 18 & age <= 65"`**
  - 🌐 **English**: Age between 18 and 65
  - 🇹🇼 **繁體中文**: 年齡必須介於 18 到 65 歲之間
  - 💡 **Explanation**: Limits dataset to working-age population, aligning with common labor force statistics ranges

- **`"hours-per-week >= 20 & hours-per-week <= 60"`**
  - 🌐 **English**: Hours per week between 20 and 60
  - 🇹🇼 **繁體中文**: 每週工作時數必須介於 20 到 60 小時之間
  - 💡 **Explanation**: Excludes part-time (<20 hours) and extreme overwork (>60 hours) cases, focusing on standard employment patterns

##### 3. Field Combination Constraints (field_combinations)

**Field value pairing relationships, default none**

- **Education-Income Pairing Rules**
  - 🌐 **English**: 
    - Doctorate education can only have >50K income
    - Masters education can have >50K or <=50K income
  - 🇹🇼 **繁體中文**:
    - 博士學歷（`Doctorate`）只能配對高收入（`>50K`）
    - 碩士學歷（`Masters`）可以配對高收入（`>50K`）或低收入（`<=50K`）
  - 💡 **Explanation**:
    - Reflects real-world education returns: Doctorate degrees typically correspond to higher income
    - Master's degrees may have varying income levels depending on field, experience, and other factors
    - **Positive listing**: Unlisted education levels will be treated as invalid combinations

##### 4. Field Proportion Constraints (field_proportions)

**Field proportion maintenance, default none**

- **Education Distribution Maintenance**
  - 🌐 **English**: Maintain education distribution, 10% tolerance
  - 🇹🇼 **繁體中文**: 維護 `education` 欄位的整體分布，容許 10% 的誤差
  - 💡 **Explanation**:
    - `mode: 'all'`: Maintains proportions for all categories
    - `tolerance: 0.1`: Allows synthetic data proportions to differ from original by ±10%

- **Income Distribution Maintenance**
  - 🌐 **English**: Maintain income distribution, 5% tolerance
  - 🇹🇼 **繁體中文**: 維護 `income` 欄位的整體分布，容許 5% 的誤差
  - 💡 **Explanation**: Stricter tolerance (5%) ensures income class distribution closely matches original data

- **Workclass Missing Value Proportion Maintenance**
  - 🌐 **English**: Maintain workclass missing value proportion, 3% tolerance
  - 🇹🇼 **繁體中文**: 維護 `workclass` 欄位的遺失值比例，容許 3% 的誤差
  - 💡 **Explanation**:
    - `mode: 'missing'`: Only maintains proportion of missing values (NA)
    - `tolerance: 0.03`: Strictly controls missing value proportion to preserve data quality characteristics

#### Referencing Constraints File in Main Configuration

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  default:
    method: default
Constrainer:
  external_constraints:
    method: auto
    constraints_yaml: adult-income_constraints.yaml  # Reference external constraints file
    target_rows: None
    sampling_ratio: 10.0
    max_trials: 300
```

{{< /callout >}}

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