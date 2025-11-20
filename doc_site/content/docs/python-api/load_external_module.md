---
title: "load_external_module()"
type: docs
weight: 1150
---

**Module**: `petsard.utils`

Load external Python module and return the module instance and class.

## Syntax

```python
load_external_module(module_path, class_name, logger, required_methods=None, search_paths=None)
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module_path` | `str` | Yes | - | Path to the external module (relative or absolute) |
| `class_name` | `str` | Yes | - | Name of the class to load from the module |
| `logger` | `logging.Logger` | Yes | - | Logger for recording messages |
| `required_methods` | `dict[str, list[str]]` | No | `None` | Dictionary mapping method names to required parameter names |
| `search_paths` | `list[str]` | No | `None` | Additional search paths to try when resolving the module path |

## Return Value

Returns a tuple `(module, class)`:
- `module`: The loaded module instance
- `class`: The class from the module

## Raises

- `FileNotFoundError`: If the module file does not exist
- `ConfigError`: If the module cannot be loaded or doesn't contain the specified class

## Usage Examples

**Example 1: Load a custom synthesizer**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# Load external synthesizer module
module, CustomSynthesizer = load_external_module(
    module_path='./custom_synthesizer.py',
    class_name='CustomSynthesizer',
    logger=logger,
    required_methods={
        'fit': ['data'],
        'sample': ['num_samples']
    }
)

# Use the loaded class
synthesizer = CustomSynthesizer()
```

**Example 2: Load module with search paths**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# Load module from multiple possible locations
module, MyClass = load_external_module(
    module_path='my_module.py',
    class_name='MyClass',
    logger=logger,
    search_paths=[
        './modules',
        './custom_modules',
        '/path/to/shared/modules'
    ]
)
```

**Example 3: Load without method validation**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# Load module without checking methods
module, SimpleClass = load_external_module(
    module_path='./simple_class.py',
    class_name='SimpleClass',
    logger=logger
)
```

## Module Resolution

The function searches for the module in the following order:

1. If `module_path` is an absolute path and exists, use it directly
2. Try `module_path` as provided
3. Try current working directory + `module_path`
4. Try each directory in `search_paths` + `module_path`

## Method Validation

When `required_methods` is provided, the function validates:

1. **Method Existence**: Each specified method must exist in the class
2. **Callable Check**: Each method must be callable
3. **Parameter Check**: Each method must accept the required parameters

Example of `required_methods`:

```python
required_methods = {
    'fit': ['data', 'metadata'],  # fit() must accept 'data' and 'metadata' parameters
    'sample': ['num_samples'],     # sample() must accept 'num_samples' parameter
    'save': []                     # save() must exist but no parameters required
}
```

## Notes

- **Path Flexibility**: Supports both absolute and relative paths
- **Search Strategy**: Tries multiple locations to find the module
- **Validation**: Optional method signature validation
- **Error Handling**: Provides detailed error messages for troubleshooting
- **Logger Integration**: Uses provided logger for all messages