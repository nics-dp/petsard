---
title: "Logical Types"
weight: 5
---

Logical Type is a declarative attribute for annotating field semantics without changing the underlying data type.

## Usage

```yaml
fields:
  email:
    name: email
    type: str
    logical_type: email  # Annotate this as an email field
```

## Common Logical Types

- `email`: Email address
- `url`: URL link
- `phone`: Phone number

## Auto-Inference

When no schema is provided, the system checks string field data content:

- If field values match email format (contains `@`), it automatically sets `logical_type: email`
- Other logical types (`url`, `phone`) are not auto-inferred and must be manually specified in schema

## Notes

- No data validation functionality; used only for semantic annotation
- Underlying data type is determined by `type`; `logical_type` doesn't affect storage format