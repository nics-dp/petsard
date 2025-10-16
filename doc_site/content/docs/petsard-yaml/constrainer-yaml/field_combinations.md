---
title: "Field Combinations"
weight: 3
---

Define value pairing relationships between different fields using **allowlist** approach (only affects explicitly specified value combinations).

## Usage Examples

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_combinations.ipynb)

```yaml
field_combinations:
  -
    - education: income        # Define field mapping: education (source) -> income (target)
    -
        Doctorate:             # When education is Doctorate
          - '>50K'             # income can only be '>50K'
        Masters:               # When education is Masters
          - '>50K'             # income can be '>50K'
          - '<=50K'            # or '<=50K'
```

**Allowlist Effect Example**:

Given rule:
```yaml
field_combinations:
  -
    - education: income
    - Doctorate:
        - '>50K'
```

| education | income | Result |
|-----------|--------|--------|
| Doctorate | >50K | ✅ Keep (matches rule) |
| Doctorate | <=50K | ❌ Filter (violates rule) |
| Masters | >50K | ➖ Unaffected (rule not applicable) |
| Masters | <=50K | ➖ Unaffected (rule not applicable) |
| Bachelor | >50K | ➖ Unaffected (rule not applicable) |
| Bachelor | <=50K | ➖ Unaffected (rule not applicable) |

**Important**: Only affects explicitly specified value combinations (Doctorate), all other combinations are retained.

## Syntax Format

### Single Field Mapping

```yaml
-
  - source_field_name: target_field_name
  -
      source_value1:
        - target_value1
        - target_value2
      source_value2:
        - target_value3
```

---

### Multi-Field Mapping

```yaml
-
  -
    - source_field_name1
    - source_field_name2
  : target_field_name
  -
    - source_value1
    - source_value2
  :
    - target_value1
    - target_value2
```

## Important Notes

- Uses **allowlist** approach: only checks explicitly listed value combinations
- Null values (NA) are not affected by rules
- String values require exact matching (case-sensitive)
- Target values must use list format: `[value]` or `[value1, value2]`