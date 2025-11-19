---
title: Test Coverage
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide/docker-development
---

## Test Statistics

**Current Test Status** (November 2025):
- **Total Tests**: 607 tests
- **Passing**: 100%
- **Execution Time**: ~55 seconds

## Test Organization

### Test Classification

PETsARD test suite is organized by functional modules, using pytest markers for classification:

- **`unit`**: Unit tests for isolated component functionality
- **`integration`**: Integration tests for module interactions
- **`stress`**: Stress tests for large datasets and extreme scenarios
- **`excel`**: Excel file tests requiring openpyxl package

### Test Directory Structure

```
tests/
├── test_petsard.py          # End-to-end workflow tests
├── test_executor.py          # Executor configuration & logging
├── test_adapter.py           # Configuration adapter tests
├── loader/                   # Data loading module
├── processor/                # Data processing module
├── metadater/               # Metadata management module
├── synthesizer/             # Synthesizer module
├── constrainer/             # Constrainer module
├── evaluator/               # Evaluator module
├── describer/               # Describer module
└── reporter/                # Reporter module
```

## Core Functionality Tests

### End-to-End Tests (`test_petsard.py`)

Tests complete PETsARD workflows:

- **Basic Workflow**: Load → Preprocess → Synthesize → Postprocess
- **Data Preprocessing**: Missing value handling, encoding, standardization
- **Constraint Application**: Numeric ranges, field proportion control
- **Evaluation Metrics**: Quality reports, statistical comparison
- **Minimal Pipeline**: Load and report only
- **Error Handling**: Invalid configuration detection

### Executor (`test_executor.py`)

Tests Executor configuration and execution management:

- Configuration validation (log level, output type)
- Logger system initialization and reconfiguration
- YAML configuration loading
- Default value handling

## Data Loading Tests

### Loader (`loader/test_loader.py`)

**Core Functionality**:
- CSV/Excel file loading
- Custom NA values and header handling
- Data-Schema auto-reconciliation (field alignment, type inference)

**Logical Type System**:
- Text types: email, url, uuid, categorical, ip_address
- Numeric types: percentage, currency, latitude, longitude
- Identifier types: primary_key
- Type compatibility validation and conflict resolution

**Schema Parameter System**:
- Global parameters: compute_stats, optimize_dtypes, sample_size
- Field parameters: logical_type, leading_zeros
- Parameter conflict detection

**Stress Tests** (marked `stress`):
- 100MB - 5GB file processing
- Memory usage monitoring
- Type inference edge cases

### Benchmarker (`loader/test_benchmarker.py`)

Tests benchmark dataset management:

- Dataset download and caching
- SHA-256 integrity verification (warns on mismatch)
- benchmark:// protocol handling
- LoaderAdapter integration

### Splitter (`loader/test_splitter.py`)

Tests data splitting functionality:

- Train/test splitting
- Multiple sample generation
- Stratified sampling
- Random seed control

## Data Processing Tests

### Processor (`processor/`)

**Missing Value Handlers** (`test_missing.py`):
- MissingMean, MissingMedian, MissingSimple, MissingDrop
- Pandas nullable integer type support
- Banker's rounding for integer types

**Outlier Handlers**:
- IQR, Z-score, Isolation Forest methods
- Outlier clipping or removal
- Pandas array compatibility

**Encoders**:
- Label, OneHot, Target encoding
- Automatic type inference

**Scalers**:
- Standard, MinMax, Robust scaling
- Numeric feature processing

### Metadater (`metadater/`)

Tests three-layer metadata architecture:

**Three-Layer Architecture**:
- Metadata layer: Multi-table management
- Schema layer: Field definitions
- Attribute layer: Field properties

**Core Functionality**:
- Create metadata from data/configuration
- Difference comparison (diff)
- Data alignment (align)
- Statistics calculation
- YAML roundtrip compatibility

## Evaluation & Reporting Tests

### Describer (`describer/`)

**DescriberDescribe** (`test_describer_describe.py`):
- Statistical methods: basic, percentile, na, cardinality
- Granularity: global, columnwise
- Data types: numeric, categorical, mixed
- Edge cases: empty data, extreme values, high cardinality

**DescriberCompare** (`test_describer_compare.py`):
- JS Divergence calculation
- Code reuse architecture (reuses DescriberDescribe)
- NA value handling
- base/target parameter naming

### Evaluator (`evaluator/`)

**SDMetrics Integration** (`test_sdmetrics.py`):
- Quality report evaluation
- Diagnostic report generation
- Single/multi-table scenarios
- Granularity control (global/columnwise/pairwise)

**MPUCCS Privacy** (`test_mpuccs.py`):
- Membership inference attack evaluation
- Privacy risk indicators
- Multi-class classification support

**Custom Evaluator** (`test_custom_evaluator.py`):
- Evaluator registration mechanism
- Custom evaluation logic
- Factory pattern integration

### Constrainer (`constrainer/`)

**Constraint Types**:
- **NaN Group Constraints** (`test_nan_group_constrainer.py`):
  - Delete, Erase, Copy actions
  - Multi-field processing
- **Field Constraints** (`test_field_constrainer.py`):
  - Numeric ranges, conditional expressions
  - Complex logic combinations
  - String literal handling (with operators)
- **Field Proportions** (`test_constrainer.py`):
  - Category distribution maintenance
  - Missing value proportion control
  - Resampling mechanism

### Reporter (`reporter/`)

**ReporterSaveData**:
- CSV/Excel/Pickle output
- Multi-format simultaneous saving
- Custom output paths

**ReporterSaveSchema** (`test_reporter_save_schema.py`):
- Schema CSV summary generation
- YAML detailed output
- Multi-source module support
- Schema flattening and structuring

## Configuration Adapter Tests

### Adapter (`test_adapter.py`)

Tests YAML configuration processing:

**Three-Layer YAML Architecture**:
- Module layer: Module type and name
- Experiment layer: Experiment configuration
- Parameters layer: Parameter details

**Functionality Tests**:
- benchmark:// protocol handling
- Postprocessor precision and rounding
- Multi-postprocessor sequences
- Pipeline data flow validation