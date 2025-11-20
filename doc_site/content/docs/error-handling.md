---
title: Error Handling
type: docs
weight: 800
prev: docs/schema-yaml
next: docs/glossary
---

PETsARD uses a structured error code system. All errors provide error codes, context, and resolution suggestions.

## Error Message Structure

Each error provides:
- **Error Code**: Structured identifier (e.g., `CONFIG_001`)
- **Error Message**: Clear problem description
- **Context**: Relevant information (file paths, field names, etc.)
- **Suggestions**: Resolution guidance

## Error Code Hierarchy

```
Configuration Errors (CONFIG_*)
├── CONFIG_001 (NoConfigError)
└── CONFIG_002 (ConfigError)

Data Processing Errors (DATA_*)
├── DATA_001 (UnableToLoadError)
├── DATA_002 (MetadataError)
├── DATA_003 (UnableToFollowMetadataError)
└── DATA_004 (BenchmarkDatasetsError)

Operation State Errors (STATE_*)
├── STATE_001 (UncreatedError)
├── STATE_002 (UnfittedError)
└── STATE_003 (UnexecutedError)

Execution Errors (EXEC_*)
├── EXEC_001 (UnableToSynthesizeError)
├── EXEC_002 (UnableToEvaluateError)
├── EXEC_003 (UnsupportedMethodError)
├── EXEC_004 (CustomMethodEvaluatorError)
└── EXEC_005 (MissingDependencyError)

Status Management Errors (STATUS_*)
├── STATUS_001 (SnapshotError)
└── STATUS_002 (TimingError)
```

## Configuration Errors (CONFIG_*)

### CONFIG_001
**Name**: NoConfigError

**Common Causes**: No configuration file provided or empty configuration string

**Resolution**: Provide a valid configuration file path or YAML string

### CONFIG_002
**Name**: ConfigError

**Common Causes**: YAML syntax errors or field values out of valid range

**Resolution**: Validate YAML syntax and confirm field values are correct

## Data Processing Errors (DATA_*)

### DATA_001
**Name**: UnableToLoadError

**Common Causes**: File does not exist or unsupported format

**Resolution**: Confirm file path is correct and format is supported (CSV, Excel, Parquet)

### DATA_002
**Name**: MetadataError

**Common Causes**: Incorrect metadata format or mismatch with actual data

**Resolution**: Ensure metadata format matches data structure

### DATA_003
**Name**: UnableToFollowMetadataError

**Common Causes**: Metadata schema does not match data structure

**Resolution**: Ensure metadata field names match data columns

### DATA_004
**Name**: BenchmarkDatasetsError

**Common Causes**: Network connection issues or incorrect benchmark name

**Resolution**: Check network connection and verify benchmark name is correct

## Operation State Errors (STATE_*)

### STATE_001
**Name**: UncreatedError

**Common Causes**: Using object before calling create() method

**Resolution**: Call create() method before using the object

### STATE_002
**Name**: UnfittedError

**Common Causes**: Using model before calling fit() method

**Resolution**: Call fit() method to train the model first

### STATE_003
**Name**: UnexecutedError

**Common Causes**: Accessing results before workflow execution

**Resolution**: Execute workflow before accessing results

## Execution Errors (EXEC_*)

### EXEC_001
**Name**: UnableToSynthesizeError

**Common Causes**: Incomplete metadata or data quality issues

**Resolution**: Confirm metadata completeness and check data quality

### EXEC_002
**Name**: UnableToEvaluateError

**Common Causes**: Missing required datasets or inconsistent data formats

**Resolution**: Ensure all required datasets exist and formats are consistent

### EXEC_003
**Name**: UnsupportedMethodError

**Common Causes**: Incorrect method name or missing required dependencies

**Resolution**: Confirm method name spelling and install required dependencies

### EXEC_004
**Name**: CustomMethodEvaluatorError

**Common Causes**: Implementation error in custom evaluator

**Resolution**: Check custom evaluator implementation and confirm correct base class inheritance

### EXEC_005
**Name**: MissingDependencyError

**Common Causes**: Method requires optional dependency package that is not installed

**Resolution**: Install the required package (e.g., `pip install sdv`)

**Example**:
```python
try:
    synthesizer = Synthesizer(method="sdv-single_table-gaussiancopula")
except MissingDependencyError as e:
    print(f"Missing dependency: {e}")
    print(f"Install command: {e.context.get('install_command')}")
```

## Status Management Errors (STATUS_*)

### STATUS_001
**Name**: SnapshotError

**Common Causes**: Attempting to access non-existent snapshot or corrupted snapshot data

**Resolution**: Confirm snapshot ID is correct and check data integrity

### STATUS_002
**Name**: TimingError

**Common Causes**: Invalid timing data format or missing paired records

**Resolution**: Check timing record format and ensure START/END records are complete

## Best Practices

### Developer Guidelines

When developing PETsARD or extensions, follow these principles:

#### 1. Use Appropriate Custom Errors

**❌ Wrong Approach**:
```python
except Exception as e:
    print(f"Error: {e}")
    return None
```

**✅ Correct Approach**:
```python
from petsard.exceptions import DataProcessingError
import logging

logger = logging.getLogger(__name__)

try:
    # Process data
    data = process_data()
except ValueError as e:
    logger.error(f"Value conversion failed: {e}")
    raise DataProcessingError(
        message="Unable to process data",
        error_code="DATA_002",
        field_name=field_name,
        suggestion="Please check if data format is correct"
    ) from e
```

#### 2. Use Logging Instead of Print

**❌ Wrong Approach**:
```python
print(f"Processing column: {col}")
print(f"Error occurred: {e}")
```

**✅ Correct Approach**:
```python
import logging

logger = logging.getLogger(__name__)

logger.debug(f"Processing column: {col}")
logger.error(f"Error occurred: {e}")
logger.warning(f"Skipping invalid column: {col}")
```

#### 3. Catch Specific Exception Types

**❌ Wrong Approach**:
```python
try:
    result = risky_operation()
except Exception as e:  # Too broad
    handle_error(e)
```

**✅ Correct Approach**:
```python
try:
    result = risky_operation()
except (ValueError, KeyError, TypeError) as e:  # Specific types
    logger.warning(f"Operation failed: {e}")
    handle_error(e)
except FileNotFoundError as e:  # File-related
    raise UnableToLoadError(
        message="Unable to load file",
        filepath=filepath
    ) from e
```

#### 4. Provide Useful Error Context

**❌ Wrong Approach**:
```python
raise ConfigError("Invalid config")
```

**✅ Correct Approach**:
```python
raise ConfigError(
    message="Invalid field value in configuration",
    config_section="synthesizer",
    invalid_field="sample_size",
    provided_value=-100,
    valid_values=["positive integer"],
    suggestion="sample_size must be a positive integer"
)
```

#### 5. Chain from Original Exception

Use `from e` to preserve original error stack:

```python
try:
    data = pd.read_csv(filepath)
except FileNotFoundError as e:
    raise UnableToLoadError(
        message=f"File not found: {filepath}",
        filepath=filepath
    ) from e  # Preserve original error information
```

### Logging Level Guidelines

- **DEBUG**: Detailed diagnostic information (variable values, execution flow)
- **INFO**: General informational messages (operation completion, stage progress)
- **WARNING**: Warning messages (recoverable errors, degraded processing)
- **ERROR**: Error messages (operation failure but doesn't affect overall system)
- **CRITICAL**: Critical errors (system cannot continue)

### Error Message Writing Principles

1. **Clearly describe the problem**: Explain what error occurred
2. **Provide context**: Include relevant values, file paths, field names
3. **Suggest solutions**: Tell users how to fix the issue
4. **Use error codes**: Make it easy to find documentation and track issues

## Debugging and Help

If encountering errors:
1. **Check error code**: Review this guide for common causes and resolutions
2. **Examine logs**: Enable DEBUG logging to inspect execution flow and TIMING records
3. **Seek help**: If issue persists, open an issue on [GitHub](https://github.com/nics-tw/PETsARD/issues) with:
   - Error code and full error message
   - Relevant configuration files or code snippets
   - Log excerpts (DEBUG level)
   - Python version and PETsARD version