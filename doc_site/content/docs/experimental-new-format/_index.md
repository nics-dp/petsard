---
title: "Experimental New Format"
weight: 100
prev: docs/developer-guide
next: docs/glossary
---

{{< callout type="warning" >}}
This is an experimental documentation format showcase page for testing new documentation writing approaches. Content is subject to change.
{{< /callout >}}

## Description

This page demonstrates the new documentation writing format for the PETsARD project, following these principles:

### 1. YAML-First Documentation

- Primarily targeting **YAML users**
- Detailed explanation of all options configurable in YAML
- Complete YAML configuration examples

### 2. Concise Python API Documentation

- Only documents **top-level public methods**
- Provides method **parameter names and types**
- **For developer reference only**
- For specific configuration options, refer to YAML documentation
- **Users should primarily consult YAML documentation**

## Documentation Writing Standards

### Avoid Cross-Linking
- **No internal links**: Avoid inter-page linking as document structure may change
- **Self-contained**: Each page should contain complete information without depending on other pages

### Parameter Description Format
- **No tables**: Use bullet points for parameters and return values, following mainstream Python package style
- **Type annotations**: Clearly indicate parameter types
- **Concise descriptions**: One-line description per parameter

### Use Bullet Points Instead of Multiple Headings
- **Simplify hierarchy**: Use bullet format for parameter descriptions, avoiding excessive heading levels
- **Improve readability**: Use bullet points and indentation to express structure, making documentation more concise and understandable
- **Reduce whitespace**: Avoid excessive whitespace caused by making each parameter an individual heading
- **Example**:
  ```markdown
  ### Main Parameters

  - **filepath** (`string`)
    - Data file path
    - Example: `data/users.csv`

  - **method** (`string`)
    - Loading method
    - Default: 'default'
  ```

### Option Description Principles
- **YAML-first**: All configuration options and detailed descriptions are in YAML documentation
- **Minimalist Python API**: Only provides method signatures and basic parameter types
- **User-oriented**: General users only need to consult YAML documentation to complete configuration
- **Developer reference**: Python API documentation serves only as technical reference for developers
- **Avoid duplication**: Detailed descriptions maintained only in YAML documentation, not repeated in Python API

### Structured Information
- **Three-tier architecture explanation**: For complex modules (e.g., Schema), first explain conceptual architecture
- **Progressive depth**: Explain from basic usage to advanced options step by step
- **Complete examples**: Provide multiple examples from simple to complex

{{< callout type="info" >}}
Currently available in Traditional Chinese only for internal development testing.
{{< /callout >}}