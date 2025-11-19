---
title: "數值精度"
weight: 4
---

PETsARD 會自動追蹤並保持數值欄位的精度（小數位數），在 Loader、Preprocessor、Postprocessor 階段自動套用四捨五入，確保合成資料與原始資料的精度一致。精度僅在輸出時套用，不影響模型訓練。

## 使用方式

### 自動推斷（預設）

不提供 schema，或在 schema 中不指定 `precision`，系統會自動推斷：

```yaml
fields:
  price:
    name: price
    type: float
    # 不設定 precision，系統會自動推斷
    # 例如資料為 10.12, 20.68 → 自動推斷為 precision: 2
```

### 手動指定

需要明確控制精度時，在 schema 中設定 `precision`。每個欄位可獨立設定不同精度：

```yaml
fields:
  balance:
    name: balance
    type: float
    type_attr:
      precision: 2  # 強制使用 2 位小數
```

{{< callout type="warning" >}}
手動指定的 `precision` 會覆蓋自動推斷的結果。
{{< /callout >}}

## 推斷規則

| 資料類型 | 精度推斷 | 範例 |
|---------|---------|------|
| **整數** | 0 | `1, 2, 3` → precision: 0 |
| **浮點數** | 最大小數位數 | `1.12, 2.345` → precision: 3 |
| **整數型浮點數** | 0 | `1.0, 2.0` → precision: 0 |

**特殊情況**：
- 含 null 值：僅從非 null 值推斷
- 混合精度：取最大小數位數