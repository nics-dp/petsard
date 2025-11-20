---
title: "Data Preparation: Data Governance Check"
type: docs
weight: 300
prev: docs/installation
next: docs/evaluation-purpose
---

Choose appropriate preparation methods based on data structure and business requirements. We recommend starting with data profiling to understand data quality and characteristics before deciding on multi-table integration or constraint definitions.

{{< mermaid-file file="content/docs/data-preparation/data-preparation-flow.mmd" >}}

**Legend:**

- Light blue box: Starting point
- Light purple box: Decision node
- Light green box: Action node

## Data Preparation Workflow

Follow these preparation steps based on your data characteristics:

### Step 1: Data Profiling

- **[Data Profiling](data-profiling)** - Starting point for all data preparation (Required)
  - Generate statistical reports using Describer module
  - Review basic statistical information
  - Identify data quality issues
  - Understand data distribution characteristics

### Step 2: Multi-table Data Processing

- **[Multi-table Relationships](multi-table-relationships)** - When data is scattered across related tables
  - Use database denormalization to integrate multiple tables
  - Choose appropriate granularity based on downstream tasks
  - Provides Python pandas and SQL integration examples
  - Avoids immature multi-table synthesis techniques

### Step 3: Constraint Definition

- **[Business Logic Constraints](business-logic-constraints)** - When business rules need to be enforced
  - Define logical relationships between fields
  - Maintain category distributions and missing value ratios
  - Use Constrainer for validation and filtering
  - Provides complete YAML configuration examples

### Next Steps

After completing data preparation, you can:

1. Refer to [Getting Started](../getting-started) to begin data synthesis
2. Check [Best Practices](../best-practices) for handling special data types
3. Learn more about [PETsARD YAML](../petsard-yaml) configuration details