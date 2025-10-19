---
title: "Numeric Precision"
weight: 203
---

PETsARD provides automatic numeric precision tracking and preservation functionality, ensuring synthetic data maintains the precision characteristics of the original data throughout the processing pipeline.

## Overview

Numeric precision refers to the number of decimal places. PETsARD automatically:
1. **Infers Precision**: Automatically detects the precision of each numeric field from the original data
2. **Records Precision**: Stores precision information in the schema's `type_attr`
3. **Maintains Precision**: Automatically applies rounding in Loader, Preprocessor, and Postprocessor

{{< callout type="info" >}}
**Automated Processing**: Precision tracking is fully automated, requiring no manual configuration. The system infers precision during data loading and maintains it throughout the pipeline.
{{< /callout >}}

## Schema Configuration

### Automatic Inference

When no schema is provided, the system automatically infers the precision of each numeric field:

```yaml
# System automatically infers and records precision
fields:
  price:
    name: price
    type: float64
    type_attr:
      precision: 2  # Auto-inferred: 10.12, 20.68 → precision is 2
  
  amount:
    name: amount
    type: float64
    type_attr:
      precision: 3  # Auto-inferred: 100.123, 200.988 → precision is 3
```

### Manual Specification

You can also manually specify precision in the schema:

```yaml
fields:
  balance:
    name: balance
    type: float64
    enable_null: false
    type_attr:
      precision: 2  # Manually specify precision of 2 (two decimal places)
  
  rate:
    name: rate
    type: float64
    type_attr:
      precision: 4  # Manually specify precision of 4 (four decimal places)
```

{{< callout type="warning" >}}
**Manual Specification Priority**: When precision is already specified in the schema, the system will not re-infer but use the specified precision value.
{{< /callout >}}

## Precision Inference Rules

### Numeric Types

| Data Type | Inference Rule | Example |
|-----------|---------------|---------|
| **Integer** | precision = 0 | `1, 2, 3` → precision: 0 |
| **Float** | precision = max decimal places | `1.12, 2.345` → precision: 3 |
| **Integer-type Float** | precision = 0 | `1.0, 2.0` → precision: 0 |

### Special Cases

- **With null values**: Ignores null values, only infers from non-null values
- **Mixed precision**: Uses the maximum number of decimal places among all values
- **Non-numeric types**: Does not infer precision (e.g., strings, booleans)

### Examples

```python
import pandas as pd

# Example 1: Mixed precision
df = pd.DataFrame({
    'value': [1.1, 2.22, 3.333, 4.4444]
})
# Inference result: precision = 4 (maximum decimal places)

# Example 2: With null values
df = pd.DataFrame({
    'price': [10.12, None, 20.68, np.nan]
})
# Inference result: precision = 2 (ignore nulls)

# Example 3: Integer-type floats
df = pd.DataFrame({
    'count': [1.0, 2.0, 3.0]
})
# Inference result: precision = 0
```

## Precision Application Timing

Precision is automatically applied with rounding at the following stages:

### 1. Loader Stage

Precision is applied immediately after data loading:

```python
from petsard import Loader

# Load data (automatically applies precision)
loader = Loader(filepath="data.csv")
data, metadata = loader.load()

# Numeric fields in data are already rounded according to inferred precision
```

### 2. Preprocessor Stage

Precision is applied after preprocessing transformations:

```python
from petsard import Preprocessor

# Preprocess (automatically applies precision after transformation)
preprocessor = Preprocessor(metadata=metadata)
preprocessor.fit(data)
processed_data = preprocessor.transform(data)

# processed_data maintains original precision
```

### 3. Postprocessor Stage

Precision is applied after postprocessing restoration:

```python
from petsard import Postprocessor

# Postprocess (automatically applies precision after restoration)
postprocessor = Postprocessor(metadata=preprocessor_input_schema)
restored_data = postprocessor.transform(synthetic_data)

# restored_data recovers original precision
```

{{< callout type="info" >}}
**Precision Source**: Postprocessor uses precision from `preprocessor_input_schema`, ensuring restoration to the original precision before preprocessing.
{{< /callout >}}

## Implementation Details

### Precision Inference Mechanism

PETsARD uses Python's `Decimal` module for precise precision calculation:

```python
from decimal import Decimal

def _infer_precision(series: pd.Series) -> int:
    """Infer precision (decimal places) of numeric series"""
    max_precision = 0
    
    for value in series.dropna():
        if pd.notna(value):
            # Use Decimal for precise decimal place calculation
            decimal_value = Decimal(str(value))
            
            # Get decimal part
            exponent = decimal_value.as_tuple().exponent
            
            if exponent < 0:
                precision = abs(exponent)
                max_precision = max(max_precision, precision)
    
    return max_precision
```

### Precision Application Mechanism

At the end of each adapter, the `_apply_precision_rounding()` method is called:

```python
def _apply_precision_rounding(
    self, 
    data: pd.DataFrame, 
    schema: Schema, 
    context: str
) -> pd.DataFrame:
    """Apply precision rounding to numeric fields"""
    
    for col_name, attribute in schema.attributes.items():
        # Check if precision information exists
        if (attribute.type_attr and 
            'precision' in attribute.type_attr and
            col_name in data.columns):
            
            precision = attribute.type_attr['precision']
            
            # Apply rounding
            data[col_name] = data[col_name].apply(
                lambda x: safe_round(x, precision) if pd.notna(x) else x
            )
    
    return data
```

### Precision Preservation During Schema Transformation

In `SchemaInferencer`, transformation rules preserve `type_attr` (including precision):

```python
class ProcessorTransformRules:
    @staticmethod
    def apply_rule(...):
        # Preserve original type_attr (including precision information)
        if base_attribute and base_attribute.type_attr:
            target_attribute.type_attr = base_attribute.type_attr.copy()
```

### Precision Memory Mechanism

The `Status` class remembers the preprocessor's input schema:

```python
# Remember in PreprocessorAdapter
status.put(
    module='Preprocessor',
    preprocessor_input_schema=input_metadata
)

# Retrieve in PostprocessorAdapter
preprocessor_input_schema = status.get_preprocessor_input_schema()
```

## Practical Application Examples

### Complete Pipeline

```python
from petsard import Loader, Preprocessor, Synthesizer, Postprocessor

# 1. Load data (automatically infer and apply precision)
loader = Loader(filepath="financial_data.csv")
data, schema = loader.load()
# Assume 'amount' field is inferred as precision: 2

# 2. Preprocess (maintain precision)
preprocessor = Preprocessor(metadata=schema)
preprocessor.fit(data)
processed = preprocessor.transform(data)
# Transformed data maintains precision: 2

# 3. Synthesize
synthesizer = Synthesizer(metadata=preprocessor.metadata)
synthesizer.fit(processed)
synthetic = synthesizer.sample(n=1000)

# 4. Postprocess (recover original precision)
postprocessor = Postprocessor(metadata=preprocessor.metadata)
restored = postprocessor.transform(synthetic)
# restored 'amount' recovers to precision: 2

# Result: Synthetic data precision matches original data
```

### Custom Schema

```python
from petsard import Loader
from petsard.metadater import Schema, Attribute

# Define schema with precision
custom_schema = Schema(
    id="financial_schema",
    attributes={
        "balance": Attribute(
            name="balance",
            type="float64",
            enable_null=False,
            type_attr={"precision": 2}  # Specify precision
        ),
        "interest_rate": Attribute(
            name="interest_rate",
            type="float64",
            enable_null=False,
            type_attr={"precision": 4}  # Higher precision
        )
    }
)

# Load with custom schema
loader = Loader(filepath="data.csv", schema=custom_schema)
data, schema = loader.load()
# Data will be rounded according to specified precision
```

## Best Practices

### 1. Let System Auto-Infer

For most cases, recommend letting the system automatically infer precision:

```python
# ✅ Recommended: Auto-inference
loader = Loader(filepath="data.csv")
data, schema = loader.load()
```

### 2. Manual Specification for Special Requirements

Only manually specify when there are special requirements:

```python
# Example: Financial data requires uniform 2 decimal places
schema = Schema(
    attributes={
        "amount": Attribute(
            type="float64",
            type_attr={"precision": 2}
        )
    }
)
```

### 3. Check Inference Results

You can check the system-inferred precision:

```python
# View inferred precision
for name, attr in schema.attributes.items():
    if attr.type_attr and 'precision' in attr.type_attr:
        print(f"{name}: precision = {attr.type_attr['precision']}")
```

## Frequently Asked Questions

### Q: How to disable precision tracking?

A: Precision tracking is optional. If there is no `type_attr.precision` in the schema, rounding will not be applied.

### Q: Does precision affect synthetic data quality?

A: No. Precision is only applied in final output, does not affect model training and data synthesis processes.

### Q: Can different fields have different precisions?

A: Yes. Each field independently records and applies precision.

### Q: Will precision be lost after Preprocessor transformation?

A: No. `SchemaInferencer` preserves `type_attr` during transformation, ensuring precision information is not lost.

## Technical Details

### Rounding Function

PETsARD uses the `safe_round()` function for safe rounding:

```python
from petsard.utils import safe_round

# Handle various cases
safe_round(10.12345, 2)  # → 10.12
safe_round(None, 2)      # → None
safe_round(np.nan, 2)    # → np.nan
```

### Precision Storage Location

```yaml
fields:
  price:
    name: price
    type: float64
    type_attr:
      precision: 2  # Stored here
```

### Related Classes and Methods

- **AttributeMetadater.from_data()**: Infer precision
- **AttributeMetadater._infer_precision()**: Precision inference logic
- **SchemaInferencer**: Preserve type_attr
- **BaseAdapter._apply_precision_rounding()**: Apply precision
- **Status.get_preprocessor_input_schema()**: Get original schema

## Related Documentation

- Data Types - Learn about supported data types
- Schema Architecture - Learn about overall Schema architecture