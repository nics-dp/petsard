---
title: "Numeric Precision"
weight: 4
---

PETsARD automatically tracks and maintains the precision (decimal places) of numeric fields, applying rounding in Loader, Preprocessor, and Postprocessor stages to ensure synthetic data matches the original data's precision. Precision is only applied at output and doesn't affect model training.

## Usage

### Automatic Inference (Default)

Without providing a schema, or without specifying `precision` in the schema, the system automatically infers precision:

```yaml
fields:
  price:
    name: price
    type: float
    # Don't set precision, system will auto-infer
    # e.g., data: 10.12, 20.68 → auto-inferred as precision: 2
```

### Manual Specification

When you need explicit control over precision, set `precision` in the schema. Each field can have independent precision settings:

```yaml
fields:
  balance:
    name: balance
    type: float
    type_attr:
      precision: 2  # Force 2 decimal places
```

{{< callout type="warning" >}}
Manually specified `precision` overrides auto-inferred values.
{{< /callout >}}

## Inference Rules

| Data Type | Inference | Example |
|-----------|-----------|---------|
| **Integer** | 0 | `1, 2, 3` → precision: 0 |
| **Float** | Max decimal places | `1.12, 2.345` → precision: 3 |
| **Integer-type Float** | 0 | `1.0, 2.0` → precision: 0 |

**Special Cases**:
- With null values: Only infer from non-null values
- Mixed precision: Use maximum decimal places