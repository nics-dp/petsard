---
title: Error Handling
type: docs
weight: 10
---

# PETsARD Error Handling Guide

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
└── EXEC_004 (CustomMethodEvaluatorError)

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

## Status Management Errors (STATUS_*)

### STATUS_001
**Name**: SnapshotError

**Common Causes**: Attempting to access non-existent snapshot or corrupted snapshot data

**Resolution**: Confirm snapshot ID is correct and check data integrity

### STATUS_002
**Name**: TimingError

**Common Causes**: Invalid timing data format or missing paired records

**Resolution**: Check timing record format and ensure START/END records are complete

## Debugging and Help

If encountering errors:
1. Check error code against this guide for common causes and resolutions
2. Refer to configuration guide to enable DEBUG logging, examine execution flow and TIMING records
3. If issue persists, open a GitHub issue with error code, message, and log excerpts