---
title: Getting Started
type: docs
weight: 50
---


PETsARD's target audience is any data user, meaning we do not expect users to have engineering knowledge, particularly Python programming skills. Users only need to use the following three lines of Python code and can focus on writing configuration files:

```python
from petsard import Executor

exec = Executor(config=yaml_path)
exec.run()
```

Our only public class is `Executor`, and users interact with PETsARD through YAML configuration files. The required configuration files include:

1. **PETsARD YAML**: One synthesis execution corresponds to one configuration file
2. **Schema YAML**: One data table corresponds to one Schema configuration
3. **Constraints YAML** (optional): One data table corresponds to one constraint configuration

## What is YAML?

YAML (YAML Ain't Markup Language) is a human-readable data serialization format that PETsARD uses for experiment configuration.

- **Easy to read and write**: Uses indentation and concise syntax, understandable without programming background
- **Clear structure**: Expresses hierarchical relationships through indentation, visually clear at a glance
- **Supports multiple data types**: Strings, numbers, booleans, lists, objects, etc.

The following scenarios guide you in choosing the right YAML configuration:

1. **[Basic Usage: Default Synthesis](default-synthesis)**

  - When you only need basic data synthesis
  - For simple privacy-enhanced synthetic data generation

2. **[Basic Usage with Evaluation: Default Synthesis and Evaluation](default-synthesis-default-evaluation)**

  - When you need both synthesis and comprehensive evaluation
  - Includes protection, fidelity, and utility assessments

3. **[Evaluation of External Solutions: External Synthesis with Default Evaluation](external-synthesis-default-evaluation)**

  - When you have pre-synthesized data
  - For evaluating existing privacy-enhanced solutions

Simply choose the scenario that matches your needs, prepare the corresponding YAML configuration, and run the code above.