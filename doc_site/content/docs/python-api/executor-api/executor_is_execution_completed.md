---
title: "is_execution_completed()"
weight: 314
---

Check if workflow execution is complete.

## Syntax

```python
executor.is_execution_completed()
```

## Parameters

This method takes no parameters.

## Return Value

- **Type**: `bool`
- **Description**: `True` if execution completed; `False` otherwise

## Description

The `is_execution_completed()` method checks the execution status of the workflow. It returns:

- `True`: All experiments executed successfully
- `False`: Execution not started or incomplete

This method is useful for:
- Validating execution status before retrieving results
- Implementing error handling logic
- Creating conditional workflows
- Building monitoring systems

## Basic Example

### Example 1: Basic Status Check

```python
from petsard import Executor

config = {
    'Loader': {
        'load_data': {'filepath': 'data.csv'}
    },
    'Synthesizer': {
        'generate': {'method': 'sdv', 'model': 'GaussianCopula'}
    }
}

executor = Executor(config=config)

# Before execution
print(f"Before run: {executor.is_execution_completed()}")  # False

# Execute workflow
executor.run()

# After execution
print(f"After run: {executor.is_execution_completed()}")   # True
```

### Example 2: Conditional Result Retrieval

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Check before getting results
if executor.is_execution_completed():
    results = executor.get_result()
    print(f"Retrieved {len(results)} results")
else:
    print("Execution incomplete; cannot retrieve results")
```

### Example 3: Error Handling

```python
from petsard import Executor

try:
    executor = Executor(config='config.yaml')
    executor.run()
    
    if not executor.is_execution_completed():
        raise RuntimeError("Execution failed to complete")
    
    results = executor.get_result()
    print("Execution successful")
    
except Exception as e:
    print(f"Error: {e}")
```

## Advanced Usage

### Example 4: Execution Monitoring

```python
from petsard import Executor
import time

def monitor_execution(executor, check_interval=5):
    """Monitor execution progress"""
    start_time = time.time()
    
    while not executor.is_execution_completed():
        elapsed = time.time() - start_time
        print(f"Execution in progress... ({elapsed:.1f}s)")
        time.sleep(check_interval)
    
    total_time = time.time() - start_time
    print(f"Execution completed in {total_time:.1f}s")

# Note: This pattern requires async execution
# Currently Executor.run() is blocking, so this is for illustration
```

### Example 5: Batch Processing with Status Checks

```python
from petsard import Executor
from pathlib import Path

data_files = ['data1.csv', 'data2.csv', 'data3.csv']
successful = []
failed = []

for data_file in data_files:
    config = {
        'Loader': {
            'load': {'filepath': data_file}
        },
        'Synthesizer': {
            'generate': {'method': 'sdv'}
        }
    }
    
    try:
        executor = Executor(config=config, verbose=False)
        executor.run()
        
        if executor.is_execution_completed():
            successful.append(data_file)
            print(f"✓ {data_file}")
        else:
            failed.append(data_file)
            print(f"✗ {data_file}")
            
    except Exception as e:
        failed.append(data_file)
        print(f"✗ {data_file}: {e}")

print(f"\nSuccessful: {len(successful)}/{len(data_files)}")
print(f"Failed: {len(failed)}/{len(data_files)}")
```

### Example 6: Conditional Workflow

```python
from petsard import Executor

# First workflow
executor1 = Executor(config='preprocessing_config.yaml')
executor1.run()

# Only proceed if first workflow completed
if executor1.is_execution_completed():
    # Use results from first workflow in second workflow
    results1 = executor1.get_result()
    
    # Second workflow
    executor2 = Executor(config='synthesis_config.yaml')
    executor2.run()
    
    if executor2.is_execution_completed():
        results2 = executor2.get_result()
        print("Both workflows completed successfully")
    else:
        print("Second workflow failed")
else:
    print("First workflow failed; skipping second workflow")
```

### Example 7: Result Validation

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Comprehensive validation
validation_passed = True

# Check execution status
if not executor.is_execution_completed():
    print("❌ Execution incomplete")
    validation_passed = False
else:
    print("✓ Execution completed")
    
    # Check results
    results = executor.get_result()
    
    if len(results) == 0:
        print("❌ No results generated")
        validation_passed = False
    else:
        print(f"✓ Generated {len(results)} results")
    
    # Validate each result
    for exp_key, exp_result in results.items():
        if 'data' not in exp_result:
            print(f"❌ Missing data in {exp_key}")
            validation_passed = False
        elif exp_result['data'].empty:
            print(f"❌ Empty data in {exp_key}")
            validation_passed = False
        else:
            print(f"✓ {exp_key}: {len(exp_result['data'])} records")

if validation_passed:
    print("\n✓ All validations passed")
else:
    print("\n❌ Validation failed")
```

## Status Check Patterns

### Pattern 1: Safe Result Access

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Safe pattern
if executor.is_execution_completed():
    results = executor.get_result()
    # Process results
else:
    # Handle incomplete execution
    print("Cannot proceed without complete results")
```

### Pattern 2: Logging Integration

```python
from petsard import Executor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = Executor(config='config.yaml')

try:
    executor.run()
    
    if executor.is_execution_completed():
        logger.info("Execution completed successfully")
        results = executor.get_result()
        logger.info(f"Retrieved {len(results)} results")
    else:
        logger.warning("Execution completed but status is incomplete")
        
except Exception as e:
    logger.error(f"Execution failed: {e}")
```

### Pattern 3: Retry Logic

```python
from petsard import Executor
import time

def execute_with_retry(config, max_retries=3, retry_delay=5):
    """Execute with retry logic"""
    for attempt in range(max_retries):
        try:
            executor = Executor(config=config)
            executor.run()
            
            if executor.is_execution_completed():
                return executor.get_result()
            else:
                print(f"Attempt {attempt + 1} incomplete")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    raise RuntimeError(f"Failed after {max_retries} attempts")

# Use retry logic
results = execute_with_retry('config.yaml')
```

## Execution States

### Before Execution

```python
executor = Executor(config='config.yaml')
print(executor.is_execution_completed())  # False
```

State characteristics:
- No results available
- No timing information
- Status object empty

### During Execution

```python
executor = Executor(config='config.yaml')
# executor.run() is blocking, so cannot check during execution
# This is for illustration of the concept
```

Note: Since `run()` is blocking, you cannot check status during execution in the same thread.

### After Successful Execution

```python
executor = Executor(config='config.yaml')
executor.run()
print(executor.is_execution_completed())  # True
```

State characteristics:
- Results available via `get_result()`
- Timing information available via `get_timing()`
- Status object populated

### After Failed Execution

```python
try:
    executor = Executor(config='config.yaml')
    executor.run()
except Exception as e:
    print(f"Execution failed: {e}")
    print(executor.is_execution_completed())  # False
```

State characteristics:
- Partial results may exist
- Some timing information may be available
- Status object partially populated

## Integration with Other Methods

### With run()

```python
from petsard import Executor

executor = Executor(config='config.yaml')

# Before run()
assert not executor.is_execution_completed()

# Execute
executor.run()

# After run()
assert executor.is_execution_completed()
```

### With get_result()

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Safe result retrieval
if executor.is_execution_completed():
    results = executor.get_result()
else:
    raise RuntimeError("Cannot get results: execution incomplete")
```

### With get_timing()

```python
from petsard import Executor

executor = Executor(config='config.yaml')
executor.run()

# Get timing only if execution completed
if executor.is_execution_completed():
    timing = executor.get_timing()
    print(f"Total time: {timing['duration_seconds'].sum():.2f}s")
else:
    print("Cannot get timing: execution incomplete")
```

## Error Scenarios

### Example 8: Handle Execution Errors

```python
from petsard import Executor

executor = Executor(config='config.yaml')

try:
    executor.run()
except Exception as e:
    print(f"Execution error: {e}")

# Check status even after error
if executor.is_execution_completed():
    print("Execution recovered and completed")
    results = executor.get_result()
else:
    print("Execution did not complete")
    # Investigate partial results
    try:
        partial_results = executor.get_result()
        print(f"Partial results available: {len(partial_results)}")
    except:
        print("No results available")
```

## Best Practices

### 1. Always Check Before Result Access

```python
# Good practice
if executor.is_execution_completed():
    results = executor.get_result()
else:
    raise RuntimeError("Execution incomplete")

# Avoid this
results = executor.get_result()  # May fail if execution incomplete
```

### 2. Use in Validation Workflows

```python
def validate_and_process(config):
    executor = Executor(config=config)
    executor.run()
    
    # Validate
    if not executor.is_execution_completed():
        return None, "Execution failed"
    
    results = executor.get_result()
    
    if len(results) == 0:
        return None, "No results generated"
    
    return results, "Success"

results, message = validate_and_process('config.yaml')
print(message)
```

### 3. Logging and Monitoring

```python
import logging

logger = logging.getLogger(__name__)

executor = Executor(config='config.yaml')

logger.info("Starting execution")
executor.run()

if executor.is_execution_completed():
    logger.info("Execution completed successfully")
    results = executor.get_result()
    logger.info(f"Generated {len(results)} results")
else:
    logger.error("Execution did not complete")
```

## Notes

- **State Indicator**: Returns current execution state; does not provide detailed status
- **Single Check**: Checking multiple times returns same result; no state changes after execution
- **Thread Safety**: Not thread-safe; use separate executor instances in multi-threaded environments
- **Blocking Execution**: Since `run()` is blocking, status changes only after `run()` completes
- **Partial Results**: Method does not indicate whether partial results are available
- **No Details**: Does not provide information about which experiments failed or succeeded
- **Post-Execution Only**: Useful only after `run()` method called

## Related Methods

- `run()`: Execute workflow
- `get_result()`: Get execution results
- `get_timing()`: Get execution time report