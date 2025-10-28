---
title: Multi-Table Relationships
type: docs
weight: 2
prev: docs/data-preparation/data-describing
next: docs/data-preparation/business-logic-constraints
---

Applicable when **data is scattered across multiple related tables**.

Before synthesis, use database denormalization techniques to integrate multiple tables. Avoid using immature multi-table synthesis techniques. Choose appropriate granularity and aggregation methods based on downstream tasks.

> If your data is **already integrated into a single table**, you can skip to [Business Logic Constraints](../business-logic-constraints).

## Case Background

A policy financial institution possesses rich data on corporate financing, including enterprise basic information, financing applications, and financial changes across multiple dimensions of historical records. The institution hopes to promote innovative cooperation with fintech companies through synthetic data technology, allowing third parties to develop risk prediction models using this data while ensuring data privacy, thereby helping the institution improve risk management effectiveness.

### Data Characteristics

- **Complex table structure**: Original data is scattered across multiple business system tables, involving enterprise basic data, application records, financial tracking, and other aspects
- **Time-series data**: Contains multiple key time points (such as application date, approval date, tracking time, etc.) with logical sequential relationships between these time points

### Table Relationships and Business Significance

The data structure in this case reflects the complete business process of corporate financing, mainly containing three core data tables:

**Enterprise Basic Information Table**
- Contains enterprise ID, industry category, sub-industry, geographical location, and capital information
- Each record represents an independent enterprise entity
- This table serves as the master table, forming one-to-many relationships with other tables

**Financing Application Record Table**
- Records details of each financing application submitted by enterprises to financial institutions
- Includes application type, application date, approval date, application status, and amount information
- An enterprise may have multiple financing applications spanning several years
- Application results are divided into three statuses: approved, rejected, and withdrawn

**Financial Tracking Record Table**
- Records financial performance tracking data of enterprises after obtaining financing
- Includes profit ratio indicators, tracking time range, revenue indicators, and risk level assessment
- Each financing application may generate multiple tracking records representing financial conditions at different time points

These three data tables form a hierarchical relationship structure: Enterprise Basic Data(1) → Financing Application Records(N) → Financial Tracking Records(N). In the actual business process, enterprises first establish basic files, then submit financing applications, and each application case triggers a financial tracking mechanism.

### Sample Data Demonstration

Considering data privacy, the following uses simulated data to demonstrate data structure and business logic. Although this data is simulated, it retains the key characteristics and business constraints of the original data:

#### Enterprise Basic Information

| company_id | industry | sub_industry | city | district | established_date | capital |
|------------|----------|--------------|------|----------|------------------|---------|
| C000001 | Construction | Environmental Engineering | New Taipei | Banqiao | 2019-11-03 | 19899000 |
| C000002 | Construction | Building Engineering | Taipei | Neihu | 2017-01-02 | 17359000 |
| C000003 | Manufacturing | Metal Processing | Taipei | Neihu | 2012-05-29 | 5452000 |

#### Financing Application Records

| application_id | company_id | loan_type | apply_date | approval_date | status | amount_requested | amount_approved |
|----------------|------------|-----------|------------|---------------|--------|------------------|-----------------|
| A00000001 | C000001 | Factory Expansion | 2022-01-21 | 2022-03-19 | approved | 12848000 | 12432000.0 |
| A00000002 | C000001 | Working Capital | 2025-01-05 | 2025-02-11 | approved | 2076000 | 1516000.0 |
| A00000004 | C000002 | Working Capital | 2020-12-12 | NaN | rejected | 5533000 | NaN |

#### Financial Tracking Records

| application_id | profit_ratio_avg | tracking_months | last_tracking_date | avg_revenue | risk_level |
|----------------|------------------|-----------------|--------------------|--------------|-----------------------|
| A00000001 | 0.033225 | 3.0 | 2024-09-04 | 1.840486e+07 | high_risk |
| A00000002 | -0.002636 | 3.0 | 2027-07-31 | 1.926350e+07 | normal |

### Why Choose Denormalization Over Multi-Table Synthesis?

Current open-source multi-table synthesis techniques (such as SDV's HMA) can directly handle multi-table data but have obvious limitations:

1. **Scale and complexity limitations**: Best suited for structures with no more than 5 tables and only one level of parent-child relationships
2. **Field type limitations**: Primarily supports numerical fields; categorical fields require preprocessing
3. **Constraint handling limitations**: Insufficient support for complex business logic constraints
4. **Quality issues**: Actual testing shows low cross-table correlation and insufficient association between categorical variables

In contrast, after adopting a denormalization strategy to integrate into a single wide table:
- Can use mature and stable single-table synthesis techniques
- Can fully define business logic constraints
- Synthesis quality is more controllable and predictable
- Clearly preserves business logic relationships

## Step 1: Data Exploration and Analysis

### Analyze Table Relationship Structure

Draw an ER diagram (Entity-Relationship Diagram) to understand the relationships between tables:

- Identify relationships between parent and child tables (one-to-many, many-to-many)
- Confirm primary key/foreign key correspondences
- Observe temporal dependencies in the data

### Confirm Downstream Requirements

Discuss analysis objectives with data users (such as data scientists, business analysts):

- **Enterprise-level analysis**: One row per enterprise (one record represents one company)
- **Application-level analysis**: One row per application (one record represents one application)
- **Time-point analysis**: One row per specific time point (one record represents a temporal cross-section)

## Step 2: Design Integration Strategy

### Choose Appropriate Granularity

Continuing with the enterprise financing case above, if the downstream task focuses on overall risk assessment for each enterprise, the appropriate granularity is "one record per enterprise". We will integrate the following information:

**Enterprise Basic Information** (directly included)
- Company ID (`company_id`)
- Industry category (`industry`), sub-industry (`sub_industry`)
- City (`city`), district (`district`)
- Capital (`capital`)
- Establishment date (`established_date`)

**First Application Record** (preserve temporal starting point)
- Application date (`first_apply_date`)
- Loan type (`first_apply_loan_type`)
- Requested amount (`first_apply_amount_requested`)
- Approved amount (`first_apply_amount_approved`)
- Application status (`first_apply_status`)

**Latest Application Record** (reflect current status)
- Application date (`latest_apply_date`)
- Loan type (`latest_apply_loan_type`)
- Requested amount (`latest_apply_amount_requested`)
- Approved amount (`latest_apply_amount_approved`)
- Application status (`latest_apply_status`)

**Latest Financial Tracking** (current financial health)
- Tracking date (`latest_track_date`)
- Average profit ratio (`latest_track_profit_ratio_avg`)
- Tracking months (`latest_track_tracking_months`)
- Average revenue (`latest_track_avg_revenue`)
- Risk level (`latest_track_risk_level`)

### Handle One-to-Many Relationships

For one-to-many relationships, choose appropriate handling methods:

- **Select specific records**: such as latest, earliest, maximum, minimum values
- **Statistical aggregation**: such as calculating average, sum, count
- **Expand fields**: create independent fields for different time points or states
- **Keep multiple records**: if downstream tasks require it, mark with sequence numbers

## Step 3: Execute Denormalization

### Method A: Using Python pandas

Suitable for moderate data volumes requiring flexible handling:

```python
import pandas as pd

# Read original data tables
companies = pd.read_csv('companies.csv')
applications = pd.read_csv('applications.csv')
tracking = pd.read_csv('tracking.csv')

# Mark first and latest applications for each company
applications['sort_tuple'] = list(zip(applications['apply_date'], applications['application_id']))

# Find earliest application for each company
min_tuples = applications.groupby('company_id')['sort_tuple'].transform('min')
applications['is_first_application'] = (applications['sort_tuple'] == min_tuples)

# Find latest application for each company
max_tuples = applications.groupby('company_id')['sort_tuple'].transform('max')
applications['is_latest_application'] = (applications['sort_tuple'] == max_tuples)

applications.drop(columns=['sort_tuple'], inplace=True, errors='ignore')

# Join tracking data with application data to get company_id
tracking_w_company = tracking.merge(
    applications[['company_id', 'application_id']],
    how='left',
    left_on='application_id',
    right_on='application_id'
)

# Mark latest financial tracking for each company
tracking_w_company['sort_tuple'] = list(zip(
    tracking_w_company['tracking_date_last_tracking_date'],
    tracking_w_company['application_id']
))

max_tuples = tracking_w_company.groupby('company_id')['sort_tuple'].transform('max')
tracking_w_company['is_latest_tracking'] = (tracking_w_company['sort_tuple'] == max_tuples)

tracking_w_company.drop(columns=['sort_tuple'], inplace=True, errors='ignore')

# Merge enterprise data with application data
denorm_data = companies.merge(
    applications[applications['is_first_application']].add_prefix('first_apply_'),
    how='left',
    left_on='company_id',
    right_on='first_apply_company_id'
).drop(columns=['first_apply_company_id', 'first_apply_is_first_application', 'first_apply_is_latest_application']).merge(
    applications[applications['is_latest_application']].add_prefix('latest_apply_'),
    how='left',
    left_on='company_id',
    right_on='latest_apply_company_id'
).drop(columns=['latest_apply_company_id', 'latest_apply_is_first_application', 'latest_apply_is_latest_application'])

# Add aggregated tracking data
denorm_data = denorm_data.merge(
    tracking_w_company[tracking_w_company['is_latest_tracking']].drop(columns=['sort_tuple'], errors='ignore').add_prefix('latest_track_'),
    how='left',
    left_on='company_id',
    right_on='latest_track_company_id'
).drop(columns=['latest_track_company_id', 'latest_track_is_latest_tracking'])

# Save integrated wide table
denorm_data.to_csv('denormalized_data.csv', index=False)
```

### Method B: Using SQL

Suitable for large data volumes already in databases:

```sql
-- Execute denormalization directly in database
WITH first_applications AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY apply_date) as rn
    FROM applications
),
latest_applications AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY apply_date DESC) as rn
    FROM applications
),
latest_tracking AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY application_id ORDER BY tracking_date DESC) as rn
    FROM tracking
)
SELECT 
    c.*,
    fa.* AS first_apply_,
    la.* AS latest_apply_,
    lt.* AS latest_track_
FROM companies c
LEFT JOIN first_applications fa ON c.company_id = fa.company_id AND fa.rn = 1
LEFT JOIN latest_applications la ON c.company_id = la.company_id AND la.rn = 1
LEFT JOIN latest_tracking lt ON la.application_id = lt.application_id AND lt.rn = 1;
```

## Using PETsARD After Integration

After integration is complete, use the standard PETsARD workflow:

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
Postprocessor:
  default:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
```

## Important Notes

When performing data integration, pay special attention to:

- **Confirm primary key relationships**: avoid duplicates or omissions
- **Handle time series information properly**: for example, use summary statistics to preserve important features
- **Table merge order**: affects final results, suggest processing strongly related tables first
- **Downstream task requirements**: to reduce synthesis complexity, keep only necessary fields

Through pre-denormalization processing, you can clearly preserve business logic relationships, reduce data distortion during synthesis, and improve the usability and quality of final synthesized data.