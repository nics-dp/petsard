---
title: "PETsARD YAML"
weight: 100
---

<!--
Documentation Writing Principles (for roo code reference):

### YAML-First Documentation
- Target **YAML users** as the primary audience
- Provide detailed explanations of all options configurable in YAML
- Include complete YAML configuration examples
- **Users should prioritize consulting YAML documentation**

### Documentation Standards

#### Avoid Cross-Links
- **Do not use internal links**: Avoid cross-page links as document structure may change
- **Self-contained**: Each page should contain complete information without depending on other pages

#### Use Bullet Points Instead of Multi-level Headings
- **Simplify hierarchy**: Use bullet format for parameter descriptions, avoid excessive heading levels
- **Improve readability**: Use bullets and indentation to express structure for cleaner, more readable documentation
- **Reduce whitespace**: Avoid large amounts of whitespace from individual parameter headings

#### Option Description Principles
- **YAML first**: All configuration options and detailed descriptions are in YAML documentation
- **Complete descriptions**: Each parameter should include type, default value, examples
- **Avoid duplication**: Maintain detailed descriptions only in YAML documentation, not in Python API

#### Structured Information
- **From simple to advanced**: Progress from basic usage to advanced options
- **Complete examples**: Provide multiple examples from simple to complex
- **Practice-oriented**: Start from actual use cases
-->

## What is YAML?

YAML (YAML Ain't Markup Language) is a human-readable data serialization format that PETsARD uses for experiment configuration. This document explains how to effectively organize your YAML configurations.

- **Easy to read and write**: Uses indentation and concise syntax, understandable without programming background
- **Clear structure**: Expresses hierarchical relationships through indentation, visually clear at a glance
- **Supports multiple data types**: Strings, numbers, booleans, lists, objects, etc.

## Why Does PETsARD Use YAML?

PETsARD adopts YAML as its primary configuration method, allowing you to accomplish most tasks without writing Python code.

1. **No programming required**: Execute complete synthesis and evaluation workflows just by writing configuration files
2. **Easy version control**: Plain text format, convenient for tracking changes and team collaboration
3. **Batch processing**: One configuration file can define multiple experiments and operations
4. **Reusable**: Configuration files can be easily shared and reused
<!-- 5. **Environment variable support**: Sensitive information (like API keys) can be protected using environment variables -->

## PETsARD YAML Basic Structure

PETsARD's YAML configuration adopts a three-layer architecture:

```yaml
Module_Name:             # Layer 1: Module
    Experiment_Name:     # Layer 2: Experiment
        parameter1: value   # Layer 3: Parameters
        parameter2: value
```

### Module Level

The top level defines processing modules arranged in execution order:

- **Executor**: Execution settings (logging, working directory, etc.)
- **Loader**: Data loading
- **Splitter**: Data splitting
- **Preprocessor**: Data preprocessing
- **Synthesizer**: Data synthesis
- **Postprocessor**: Data postprocessing
- **Constrainer**: Data constraints
- **Evaluator**: Result evaluation
- **Reporter**: Report generation

### Experiment Level

Each module can have multiple experiment configurations. Experiment names are custom and can be named according to purpose:

```yaml
Synthesizer:
    gaussian-copula:   # Using Gaussian Copula method
        method: 'sdv-single_table-gaussiancopula'
    ctgan:             # Using CTGAN method
        method: 'sdv-single_table-ctgan'
        epochs: 100
    tvae:              # Using TVAE method  
        method: 'sdv-single_table-tvae'
        epochs: 200
```

Multiple experiments within the same module execute sequentially, allowing you to:
- Compare effects of different methods
- Test different parameter settings
- Perform batch processing

### Parameter Level

Each experiment contains specific parameter settings. Different methods have different parameter requirements.

## Complete Example

```yaml
# A complete PETsARD configuration example
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'

Preprocessor:
  demo:
    method: 'default'

Synthesizer:
  gaussian-copula:
    method: 'sdv-single_table-gaussiancopula'
  ctgan:
    method: 'sdv-single_table-ctgan'
  tvae:
    method: 'sdv-single_table-tvae'

Postprocessor:
  demo:
    method: 'default'

Evaluator:
  quality-report:
    method: 'sdmetrics-qualityreport'

Reporter:
  save-data:
    method: 'save_data'
    source: 'Synthesizer'
```

This example demonstrates:
1. Loading data (Loader)
2. Data preprocessing (Preprocessor)
3. Synthesizing data using three different methods (Synthesizer)
4. Data postprocessing (Postprocessor)
5. Evaluating synthetic data quality (Evaluator)
6. Saving results (Reporter)