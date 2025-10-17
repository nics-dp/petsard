---
title: "資料型別"
weight: 202
---

Schema 支援的基本資料型別。

## 基本型別

| 型別名稱 | YAML 語法 | 說明 | 範例值 |
|---------|----------|------|--------|
| **整數** | `type: int64` | 64 位元整數 | `123`, `-456` |
| **浮點數** | `type: float64` | 64 位元浮點數 | `3.14`, `-0.5` |
| **字串** | `type: string` | 文字資料 | `"Hello"`, `"123"` |
| **布林** | `type: boolean` | 真假值 | `true`, `false` |
| **日期時間** | `type: datetime64` | 日期與時間 | `"2024-01-15"`, `"2024-01-15 14:30:00"` |

{{< callout type="info" >}}
**分類資料**：使用 `category: true` 參數來標記分類資料，而不是 `type: category`。
{{< /callout >}}

## 型別對應

| Pandas dtype | Schema type |
|-------------|-------------|
| int8, int16, int32, int64 | int64 |
| uint8, uint16, uint32, uint64 | int64 |
| float16, float32, float64 | float64 |
| object, string | string |
| bool | boolean |
| datetime64 | datetime64 |