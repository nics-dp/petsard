---
title: "Python API"
weight: 300
---

<!--
Documentation Writing Principles (for roo code reference):

### Python API Documentation
- Target **Python developers** as the primary audience  
- Provide complete class and method references
- Include practical code examples
- **YAML users should prioritize YAML documentation**

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

Documentation of PETsARD's Python API interface.

## Module Overview

PETsARD provides the following main modules:

- **Loader**: Data loading and management
- **Preprocessor**: Data preprocessing
- **Synthesizer**: Synthetic data generation
- **Postprocessor**: Data postprocessing
- **Constrainer**: Data constraint application
- **Evaluator**: Data quality evaluation
- **Reporter**: Report generation
- **Metadater**: Metadata and schema management

## Documentation Format

- **YAML users**: Please refer to the [YAML documentation](../petsard-yaml) for configuration instructions
- **Python developers**: This section provides API reference and programmatic usage
- **Examples**: Each module provides complete usage examples

## Quick Start

```python
from petsard import Loader, Synthesizer, Evaluator

# Load data
loader = Loader()
data = loader.load("path/to/data.csv")

# Synthesize
synthesizer = Synthesizer(method="ctgan")
synthetic_data = synthesizer.fit_transform(data)

# Evaluate
evaluator = Evaluator()
report = evaluator.evaluate(data, synthetic_data)