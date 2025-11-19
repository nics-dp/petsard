---
title: "資料型別"
weight: 3
---

PETsARD 使用簡化的型別系統。

## 基本型別

| 型別 | 說明 | 設定方式 |
|------|------|----------|
| `int` | 整數 | `type: int` 或 `type: integer` |
| `float` | 浮點數 | `type: float` |
| `str` | 字串 | `type: str` 或 `type: string` |
| `date` | 日期 | `type: date` |
| `datetime` | 日期時間 | `type: datetime` |

{{< callout type="info" >}}
**注意**：PETsARD 不支援 `type: category`。類別資訊應使用 `category: true` 參數標記，因為這被視為欄位屬性資訊而非資料型別。
{{< /callout >}}

## 型別轉換對應

系統會自動將各種 pandas dtype 轉換為簡化型別：

| Pandas dtype | PETsARD 型別 |
|--------------|--------------|
| int8, int16, int32, int64, Int64 | `int` |
| uint8, uint16, uint32, uint64 | `int` |
| float16, float32, float64 | `float` |
| object, string | `str` |
| bool, boolean | `str` |
| datetime64[ns] | `datetime` |

{{< callout type="info" >}}
**型別統一原因**：為了支援空值處理（使用 nullable integer）以及確保合成資料的相容性（處理 float → int 轉換）。
{{< /callout >}}