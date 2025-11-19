---
title: "邏輯型別"
weight: 5
---

邏輯型別（Logical Type）是用於標註欄位語義的宣告性屬性，不改變底層資料型別。

## 使用方式

```yaml
fields:
  email:
    name: email
    type: str
    logical_type: email  # 標註這是電子郵件欄位
```

## 常見的邏輯型別

- `email`：電子郵件地址
- `url`：網址連結
- `phone`：電話號碼

## 自動推斷

當不提供 schema 時，系統會檢查字串欄位的資料內容：

- 如果欄位值符合 email 格式（包含 `@`），會自動設定 `logical_type: email`
- 其他邏輯型別（`url`、`phone`）不會自動推斷，需在 schema 中手動指定

## 注意事項

- 不具備資料驗證功能，僅作為語義標註
- 底層資料型別由 `type` 決定，`logical_type` 不影響儲存格式