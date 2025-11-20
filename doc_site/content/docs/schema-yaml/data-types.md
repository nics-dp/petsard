---
title: "Data Types"
type: docs
weight: 730
prev: docs/schema-yaml/attribute-parameters
next: docs/schema-yaml/precision
---

PETsARD uses a simplified type system.

## Basic Types

| Type | Description | Configuration |
|------|-------------|---------------|
| `int` | Integer | `type: int` or `type: integer` |
| `float` | Float | `type: float` |
| `str` | String | `type: str` or `type: string` |
| `date` | Date | `type: date` |
| `datetime` | Datetime | `type: datetime` |

{{< callout type="info" >}}
**Note**: PETsARD does not support `type: category`. Categorical information should be marked using the `category: true` parameter, as this is treated as field attribute information rather than a data type.
{{< /callout >}}

## Type Conversion Mapping

The system automatically converts various pandas dtypes to simplified types:

| Pandas dtype | PETsARD Type |
|--------------|--------------|
| int8, int16, int32, int64, Int64 | `int` |
| uint8, uint16, uint32, uint64 | `int` |
| float16, float32, float64 | `float` |
| object, string | `str` |
| bool, boolean | `str` |
| datetime64[ns] | `datetime` |

{{< callout type="info" >}}
**Why Unify Types**: To support null value handling (using nullable integer) and ensure synthetic data compatibility (handling float → int conversion).
{{< /callout >}}