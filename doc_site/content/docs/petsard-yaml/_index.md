---
title: "PETsARD YAML"
type: docs
weight: 600
prev: docs/data-property-adjustment
next: docs/schema-yaml
---

## Why Does PETsARD Use YAML?

PETsARD adopts YAML as its primary configuration method, allowing you to accomplish most tasks without writing Python code.

1. **No programming required**: Execute complete synthesis and evaluation workflows just by writing configuration files
2. **Easy version control**: Plain text format, convenient for tracking changes and team collaboration
3. **Batch processing**: One configuration file can define multiple experiments and operations
4. **Reusable**: Configuration files can be easily shared and reused

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

{{< callout type="info" >}}
**Strongly Recommended Execution Order**

We strongly recommend configuring modules in the following order. We are not responsible for execution results caused by changing the order.
{{< /callout >}}

- **Executor**: Execution settings (logging, working directory, etc.)
- **Loader**: Data loading
- **Splitter**: Data splitting
- **Preprocessor**: Data preprocessing
- **Synthesizer**: Data synthesis
- **Postprocessor**: Data postprocessing
- **Constrainer**: Data constraints
- **Describer**: Data description
- **Evaluator**: Result evaluation
- **Reporter**: Report generation

{{< callout type="warning" >}}
**Module Execution Limitation**

Currently, each module can only be executed once.
{{< /callout >}}

### Experiment Level

Each module can have multiple experiment configurations. Experiment names are custom and can be named according to purpose:

```yaml
Synthesizer:
    gaussian-copula:   # Using Gaussian Copula method
        method: 'sdv-single_table-gaussiancopula'
    ctgan:             # Using CTGAN method
        method: 'sdv-single_table-ctgan'
    tvae:              # Using TVAE method
        method: 'sdv-single_table-tvae'
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

## Execution Flow

When multiple experiments are defined, PETsARD executes all module combinations in a **depth-first** manner:

```
Loader → Splitter → Preprocessor → Synthesizer → Postprocessor → Constrainer → Describer → Evaluator → Reporter
```

{{< callout type="info" >}}
**Depth-First Execution Order**

Depth-first means PETsARD will complete all modules for the first experiment combination before starting the second one. It's like walking one path to the end before returning to walk another path.

**Example**:
```
Combination 1: Loader(A) → Synthesizer(method_a) → Evaluator → Reporter
Combination 2: Loader(A) → Synthesizer(method_b) → Evaluator → Reporter
Combination 3: Loader(B) → Synthesizer(method_a) → Evaluator → Reporter
Combination 4: Loader(B) → Synthesizer(method_b) → Evaluator → Reporter
```

**Execution Tree**:

{{< mermaid-file file="content/docs/petsard-yaml/depth-first-execution.mermaid" >}}

> **Legend:**
> - ① ② ③ ④: Execution order numbers
> - Green boxes: Complete experiment combinations (will execute all subsequent modules)
> - Arrows: Data flow direction

Execution order: Complete all modules for combination ① → then combination ② → and so on

Not breadth-first: executing Loader for all combinations first, then Preprocessor for all combinations...
{{< /callout >}}

### Experiment Combinations

If multiple experiments are defined in different modules, PETsARD generates all possible combinations. For example:

```yaml
Loader:
  load_a:
    filepath: 'data1.csv'
  load_b:
    filepath: 'data2.csv'
Synthesizer:
  method_a:
    method: 'method-a'
  method_b:
    method: 'method-b'
```

This generates four experiment combinations:
1. load_a + method_a
2. load_a + method_b
3. load_b + method_a
4. load_b + method_b

Each combination executes the complete workflow once, allowing you to systematically compare the effects of different configurations.

## Output Results

Output results require the use of the Reporter module. Please refer to the Reporter module documentation for detailed configuration methods.

## Best Practices

Following these recommendations will make your YAML configurations more readable and maintainable:

1. **Use meaningful experiment names**
   - Good: `ctgan_epochs100`, `preprocessing_with_scaling`
   - Avoid: `exp1`, `test`, `a`

2. **Organize parameters by module**
   - Keep related parameters together
   - Maintain consistent indentation (usually 2 or 4 spaces)

3. **Add comments to experiment configurations**
   ```yaml
   Synthesizer:
     ctgan:  # Using CTGAN for tabular data synthesis
       method: 'sdv-single_table-ctgan'
       epochs: 300  # Increase training epochs to improve quality
   ```

4. **Validate YAML syntax before execution**
   - Ensure correct indentation (YAML is indentation-sensitive)
   - Check for spaces after colons
   - Verify quote pairing

5. **Leverage multi-experiment comparisons**
   - Define multiple experiments in the same configuration file for comparison
   - Use consistent naming conventions for easy identification

6. **Keep configuration files concise**
   - Only set parameters that need to be changed
   - Use default values for other parameters