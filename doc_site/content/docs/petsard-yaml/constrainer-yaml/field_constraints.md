---
title: "Field Constraints"
weight: 2
---

Define value domain constraints for individual fields using string expressions.

## Usage Examples

Click the button below to run examples in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_field_constraints.ipynb)

```yaml
field_constraints:
  - "age >= 18 & age <= 65"                        # Age range: 18-65 years
  - "hours-per-week >= 20 & hours-per-week <= 60"  # Working hours: 20-60 hours per week
  - "income == '>50K' | income == '<=50K'"         # Income must be either '>50K' or '<=50K'
```

## Syntax Format

### Comparison Operators

```yaml
- "field_name > value"   # Greater than (numeric)
- "field_name >= value"  # Greater than or equal to (numeric)
- "field_name == value"  # Equal to (numeric, text)
- "field_name != value"  # Not equal to (numeric, text)
- "field_name < value"   # Less than (numeric)
- "field_name <= value"  # Less than or equal to (numeric)
```

---

### Logical Operators

```yaml
- "field_name > value1 & field_name < value2"        # AND
- "field_name == 'value1' | field_name == 'value2'"  # OR
- "(condition1 & condition2) | condition3"           # Parentheses for precedence
```

---

### Null Value Checking

```yaml
- "field_name IS pd.NA"      # Field is null
- "field_name IS NOT pd.NA"  # Field is not null
```

---

### Date Comparison

```yaml
- "date_field >= DATE('2020-01-01')"  # Date greater than or equal to 2020-01-01
```

---

### Operator Precedence

| Priority | Operator | Description |
|----------|----------|-------------|
| 1 (Highest) | `()` | Parentheses |
| 2 | `>`, `>=`, `==`, `!=`, `<`, `<=`, `IS`, `IS NOT` | Comparison operators |
| 3 | `&` | Logical AND |
| 4 (Lowest) | `\|` | Logical OR |

**Note**: Comparison operators have higher precedence than logical operators (AND, OR). This means `age >= 20 & age <= 60` is correctly parsed as `(age >= 20) & (age <= 60)`.

**Recommendation**: Use parentheses to explicitly specify precedence and avoid ambiguity.

## Important Notes

- Each constraint must be wrapped as a string with quotes
- String values must be single-quoted: `"field == 'value'"`
- Use `IS` or `IS NOT` for null checking, not `==` or `!=`
- Does not support cross-field operations (e.g., `field1 + field2 > 100`)