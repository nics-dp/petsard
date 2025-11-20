---
title: Business Logic Constraints
type: docs
weight: 330
prev: docs/data-preparation/multi-table-relationships
next: docs/data-preparation
---

Applicable when **business rules need to be ensured**.

Define logical relationships between fields, range restrictions, and proportion maintenance through Constraints YAML to ensure synthesized data complies with business specifications. Supports four constraint types: missing value groups, field constraints, field combinations, and field proportions.

> If your data **has no special constraint requirements**, you can directly use default synthesis methods, refer to [Getting Started](../../getting-started).

## Constraints YAML Example

Save the following content as `business_constraints.yaml`:

```yaml
# Missing value handling rules
nan_groups:
  # Delete entire record when capital is missing (incomplete enterprise basic information)
  capital: 'delete'

# Field constraint conditions
field_constraints:
  # Time logic constraints: established_date < first_apply_date <= latest_apply_date < latest_track_date
  - "established_date < first_apply_date"
  - "first_apply_date <= latest_apply_date"
  - "latest_apply_date < latest_track_date"

  # Numerical relationship constraints: approved amount cannot exceed requested amount
  - "latest_apply_amount_approved <= latest_apply_amount_requested"

  # Range constraints
  - "capital > 0"  # Capital must be positive
  - "latest_track_profit_ratio >= -1.0 & latest_track_profit_ratio <= 1.0"  # Profit ratio range
  - "latest_apply_amount_requested > 0"  # Application amount must be positive

# Field combination constraints (allowlist)
field_combinations:
  # Application status and approved amount pairing relationship
  -
    - latest_apply_status: latest_apply_amount_approved
    - approved:  # Must have amount when approved
        - 1000000
        - 5000000
        - 10000000
        - 20000000
      rejected:  # Amount is null when rejected
        - "pd.NA"
      withdrawn:  # Amount is null when withdrawn
        - "pd.NA"

# Field proportion maintenance
field_proportions:
  # Maintain industry distribution with 10% tolerance
  - fields: 'industry'
    mode: 'all'
    tolerance: 0.1

  # Maintain risk level distribution with 5% tolerance
  - fields: 'latest_track_risk_level'
    mode: 'all'
    tolerance: 0.05
```

## Detailed Constraint Type Descriptions

### nan_groups (Missing Value Group Constraints)

Define handling rules when specific fields have null values.

**`capital: 'delete'`**
- Description: When `capital` field is null, delete entire record
- Applicable scenario: When a field is null, entire record is meaningless (e.g., company has no capital information)
- Handling methods: `delete` (delete entire record), `erase` (clear related fields), `copy` (copy other field values)

### field_constraints (Field Constraints)

Define numerical ranges and logical relationships for single or multiple fields.

**Time Logic Constraints**
- `"established_date < first_apply_date"`
  - Description: Company establishment date must be earlier than first application date
  - Applicable scenario: Time sequence business logic

- `"first_apply_date <= latest_apply_date"`
  - Description: First application date must be earlier than or equal to latest application date
  - Applicable scenario: Equality allowed because there may be only one application

**Numerical Relationship Constraints**
- `"latest_apply_amount_approved <= latest_apply_amount_requested"`
  - Description: Approved amount cannot exceed requested amount
  - Applicable scenario: Basic review principles of financial institutions

**Range Constraints**
- `"capital > 0"`
  - Description: Capital must be positive
  - Applicable scenario: Fields that logically cannot be zero or negative

- `"latest_track_profit_ratio >= -1.0 & latest_track_profit_ratio <= 1.0"`
  - Description: Profit ratio ranges from -100% to 100%
  - Applicable scenario: Reasonable range for ratio-type fields
  - Syntax: Use `&` (AND) to combine multiple conditions

### field_combinations (Field Combination Constraints)

Define valid pairings between field values (allowlist).

**Application Status and Approved Amount Pairing**
```yaml
-
  - latest_apply_status: latest_apply_amount_approved
  - approved: [1000000, 5000000, 10000000, 20000000]
    rejected: ["pd.NA"]
    withdrawn: ["pd.NA"]
```

- Description: Define allowed approved amounts for different application statuses
- `approved`: Approved status can have specific amounts (list common amounts)
- `rejected`, `withdrawn`: Rejected or withdrawn status amount must be null
- **Note**: This is an allowlist; unlisted combinations are considered invalid

**Syntax Rules**
- Null values must use `"pd.NA"` (case-sensitive)
- String values must be quoted like `"approved"`
- Numerical values do not need quotes

### field_proportions (Field Proportion Constraints)

Maintain category distributions or null value proportions close to original data.

**Maintain Industry Distribution**
```yaml
- fields: 'industry'
  mode: 'all'
  tolerance: 0.1
```
- `fields`: Field name to maintain proportion
- `mode: 'all'`: Maintain all category distributions
- `tolerance: 0.1`: Allowable error range (±10%)

**Maintain Risk Level Distribution**
```yaml
- fields: 'latest_track_risk_level'
  mode: 'all'
  tolerance: 0.05
```
- `tolerance: 0.05`: Stricter tolerance (±5%) ensures risk distribution is close to original data

**Maintain Null Value Proportion**
```yaml
- fields: 'workclass'
  mode: 'missing'
  tolerance: 0.03
```
- `mode: 'missing'`: Only maintain missing value (NA) proportion
- Applicable scenario: Preserve data quality characteristics

**Note**: This constraint achieves proportions by removing excess data, which may reduce total number of synthesized records.

## Usage Methods

### Iterative Sampling Mode (Synthesized Data Generation)

Synthesis process automatically filters data that does not meet constraints:

```yaml
Loader:
  data:
    filepath: 'denormalized_data.csv'
    schema: 'denormalized_schema.yaml'

Preprocessor:
  default:
    method: 'default'

Synthesizer:
  default:
    method: 'default'

Constrainer:
  apply_constraints:
    method: resample  # or auto (automatically determines)
    constraints_yaml: 'business_constraints.yaml'
    target_rows: None  # If not specified, uses original data row count
    sampling_ratio: 10.0  # Each sampling is 10 times the target row count
    max_trials: 300  # Maximum 300 attempts

Postprocessor:
  default:
    method: 'default'

Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
```

### Validation Check Mode (Check Existing Data)

To check if original or synthesized data meets constraints:

```yaml
Loader:
  original_data:
    filepath: 'denormalized_data.csv'
    schema: 'denormalized_schema.yaml'

Constrainer:
  check_constraints:
    method: validate
    source: Loader  # Specify data source to check
    constraints_yaml: 'business_constraints.yaml'

Reporter:
  validation_report:
    method: save_validation
    output: 'data_validation'  # Output filename prefix
    include_details: true  # Include detailed violation records
```

This will generate three CSV files:
- `data_validation_summary.csv`: Overall statistics (pass rate, violation rate, etc.)
- `data_validation_violations.csv`: Violation statistics for each constraint
- `data_validation_details.csv`: Detailed violation records (up to 10 examples per rule)

## Constraint Definition Principles

In practice, it is recommended to first discuss with domain experts to confirm hard constraints and data quality requirements in business rules. Then identify constraint patterns through exploratory data analysis and write identified constraints into YAML files. After definition is complete, use Constrainer in validate mode to check if original data meets constraints. If violation rate is too high (>5%), reassess reasonableness of constraint definitions and gradually refine constraint definitions based on validation results.

Important principles when defining constraints:

- All constraint conditions must be satisfied simultaneously (AND logic)
- Execution order of four constraint types is fixed and cannot be adjusted
- field_combinations uses allowlist approach, only allowing explicitly listed combinations
- Null values must use `"pd.NA"` (case-sensitive)
- String values must be quoted like `"approved"`
- field_constraints supports pandas query syntax, can use `&` (AND), `|` (OR) and other operators to combine conditions