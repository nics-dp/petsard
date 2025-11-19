---
title: "safe_round()"
weight: 90
---

**Module**: `petsard.utils`

Safe rounding function that maintains input/output type consistency.

## Syntax

```python
safe_round(value, decimals=2)
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `value` | `int | float | Decimal | None` | Yes | - | Value to round |
| `decimals` | `int` | No | `2` | Number of decimal places |

## Return Value

Returns the rounded value maintaining the original type:
- `int` input → returns original value (no rounding)
- `float` input → returns `float`
- `Decimal` input → returns `Decimal`
- `None` input → returns `None`

## Usage Examples

```python
from petsard.utils import safe_round

# Integer - no rounding
result = safe_round(10)
print(result)  # 10 (int)

# Float - rounds to 2 decimal places by default
result = safe_round(3.14159)
print(result)  # 3.14 (float)

# Decimal - maintains Decimal type
from decimal import Decimal
result = safe_round(Decimal('3.14159'), decimals=3)
print(result)  # Decimal('3.142')

# None - returns None
result = safe_round(None)
print(result)  # None

# Custom decimal places
result = safe_round(3.14159, decimals=4)
print(result)  # 3.1416 (float)
```

## Notes

- **Type Preservation**: Always maintains the input type in the output
- **Integer Behavior**: Integers are returned unchanged (no rounding applied)
- **None Handling**: Safely handles `None` values
- **Decimal Support**: Properly handles `Decimal` type with precision control