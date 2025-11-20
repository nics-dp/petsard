---
title: "Python API"
type: docs
weight: 1000
prev: docs/glossary
next: docs/developer-guide
---

Documentation of PETsARD's Python API.

{{< callout type="warning" >}}
**Important Note**: This package expects users to control execution using Executor with YAML. Users are not expected to directly use internal modules. This documentation is for internal development team reference only. Any changes to these module functions will not be considered BREAKING CHANGES and backward compatibility is not guaranteed.
{{< /callout >}}

## Design Principles

### Adapter Pattern
Uses the adapter design pattern to unify module interfaces through the Adapter layer, allowing Executor to execute all components consistently:
- `create()` - Create instance
- `fit_sample()` / `eval()` / `report()` - Execute methods (train and generate / execute evaluation / output report)

Each module is wrapped by an Adapter to ensure standardized external interfaces.

### Immutable Objects
All configuration classes are frozen dataclasses to ensure data safety.

### Type Hints
Complete type annotations for better development experience.

## Configuration and Execution

| Module | Function |
|--------|----------|
| Executor | Main interface for experiment pipeline, coordinates entire data synthesis and evaluation workflow |

## Data Management

| Module | Function |
|--------|----------|
| Metadater | Dataset structure and metadata management, handles data type definitions and validation |

## Pipeline Components

| Module | Function |
|--------|----------|
| Benchmarker | Benchmark dataset management, automatic downloading and processing of benchmark data |
| Loader | Data loading and processing, supports multiple file formats |
| Splitter | Experiment data splitting, supports train/test set splitting |
| Processor | Data preprocessing and postprocessing, includes encoding and normalization |
| Synthesizer | Synthetic data generation, supports multiple synthesis algorithms |
| Constrainer | Data constraint processor for synthetic data, ensures data meets business rules |
| Evaluator | Privacy, fidelity and utility evaluation, provides multi-dimensional quality assessment |
| Describer | Descriptive data summary, provides statistical analysis |
| Reporter | Result export and reporting, supports multiple output formats |

## System Components

| Module | Function |
|--------|----------|
| Adapter | Standardized execution wrapper for all modules |
| Config | Experiment configuration management, handles YAML configuration files |
| Status | Pipeline state and progress tracking, provides execution monitoring |
| Utils | Core utility functions and external module loading |