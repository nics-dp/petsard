---
title: "safe_round()"
weight: 90
---

**模組**：`petsard.utils`

安全四捨五入函數，保持輸入/輸出型別一致性。

## 語法

```python
safe_round(value, decimals=2)
```

## 參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|------|------|--------|--------|------|
| `value` | `int | float | Decimal | None` | 必要 | - | 要四捨五入的值 |
| `decimals` | `int` | 選填 | `2` | 小數位數 |

## 返回值

回傳保持原始型別的四捨五入值：
- `int` 輸入 → 回傳原值（不進行四捨五入）
- `float` 輸入 → 回傳 `float`
- `Decimal` 輸入 → 回傳 `Decimal`
- `None` 輸入 → 回傳 `None`

## 使用範例

```python
from petsard.utils import safe_round

# 整數 - 不進行四捨五入
result = safe_round(10)
print(result)  # 10 (int)

# 浮點數 - 預設四捨五入到 2 位小數
result = safe_round(3.14159)
print(result)  # 3.14 (float)

# Decimal - 保持 Decimal 型別
from decimal import Decimal
result = safe_round(Decimal('3.14159'), decimals=3)
print(result)  # Decimal('3.142')

# None - 回傳 None
result = safe_round(None)
print(result)  # None

# 自訂小數位數
result = safe_round(3.14159, decimals=4)
print(result)  # 3.1416 (float)
```

## 注意事項

- **型別保持**：總是在輸出中保持輸入型別
- **整數行為**：整數會原樣回傳（不套用四捨五入）
- **None 處理**：安全處理 `None` 值
- **Decimal 支援**：適當處理 `Decimal` 型別與精度控制