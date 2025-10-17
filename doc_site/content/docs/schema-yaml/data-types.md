---
title: "Data Types"
weight: 202
---

Basic data types supported by Schema.

## Basic Types

| Type Name | YAML Syntax | Description | Example Values |
|---------|----------|------|--------|
| **Integer** | `type: int64` | 64-bit integer | `123`, `-456` |
| **Float** | `type: float64` | 64-bit floating point | `3.14`, `-0.5` |
| **String** | `type: string` | Text data | `"Hello"`, `"123"` |
| **Boolean** | `type: boolean` | True/false values | `true`, `false` |
| **Datetime** | `type: datetime64` | Date and time | `"2024-01-15"`, `"2024-01-15 14:30:00"` |

{{< callout type="info" >}}
**Categorical Data**: Use the `category: true` parameter to mark categorical data, not `type: category`.
{{< /callout >}}

## Type Mapping

| Pandas dtype | Schema type |
|-------------|-------------|
| int8, int16, int32, int64 | int64 |
| uint8, uint16, uint32, uint64 | int64 |
| float16, float32, float64 | float64 |
| object, string | string |
| bool | boolean |
| datetime64 | datetime64 |