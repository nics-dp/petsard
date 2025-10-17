---
title: "Logical Types"
weight: 203
---

Logical types are used for semantic annotation and validation without changing the underlying storage type.

## Supported Logical Types

| Logical Type | YAML Syntax | Description | Example Values |
|---------|----------|------|--------|
| **Email** | `logical_type: email` | Email address format | `user@example.com` |
| **URL** | `logical_type: url` | Web URL | `https://example.com` |
| **IP Address** | `logical_type: ip_address` | IP address | `192.168.1.1` |
| **Phone** | `logical_type: phone` | Phone number | `+886-2-1234-5678` |
| **Postal Code** | `logical_type: postal_code` | Postal code | `10045` |

## Notes

- Logical types are only used for validation and do not change storage format
- Underlying data type is typically `string`
- Can be used together with basic types to provide additional semantic information