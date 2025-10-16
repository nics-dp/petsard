---
title: "NaN Handling"
weight: 1
---

Define how to handle missing values when specific fields contain NaN.

## Usage Examples

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_nan_groups.ipynb)

```yaml
nan_groups:
  # Required field: delete row if missing
  workclass: 'delete'

  # Related fields: if occupation is NA, income should also be NA
  occupation:
    erase: 'income'

  # Supplementary field: if age is NA, use educational-num to fill
  age:
    copy: 'educational-num'

  # Conditional NaN: if workclass is Never-worked, capital-gain should be NA
  capital-gain:
    nan_if_condition:
      workclass: 'Never-worked'
```

## Supported Actions

### delete - Delete Entire Row

Delete the entire row when the specified field is NA.

**Syntax:**
```yaml
main_field_name: 'delete'
```

---

### erase - Clear Other Fields

When the main field is NA, set other specified fields to NA. Supports single or multiple target fields.

**Syntax:**
```yaml
main_field_name:
  erase: 'target_field_name'
```
or
```yaml
main_field_name:
  erase:
    - 'target_field_name1'
    - 'target_field_name2'
```

---

### copy - Copy Values

When the main field has a value and the target field is NA, copy the main field's value to the target field.

**Syntax:**
```yaml
main_field_name:
  copy: 'target_field_name'
```

---

### nan_if_condition - Conditional NaN Setting

Set the main field to NA when the condition field meets specific conditions.

**Syntax:**
```yaml
main_field_name:
  nan_if_condition:
    condition_field_name: 'value'
```
or
```yaml
main_field_name:
  nan_if_condition:
    condition_field_name:
      - 'value1'
      - 'value2'
```

## Important Notes

- **Irreversible**: delete operation permanently removes data rows
- **Use copy carefully**: Ensure both fields have compatible value domains
- **Condition checking**: nan_if_condition checks if target field values meet conditions
- **Case sensitive**: Condition value matching is case-sensitive
