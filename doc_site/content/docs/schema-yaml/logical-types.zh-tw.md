---
title: "邏輯型別"
weight: 203
---

邏輯型別用於語義標註和驗證，不改變底層儲存型別。

## 支援的邏輯型別

| 邏輯型別 | YAML 語法 | 說明 | 範例值 |
|---------|----------|------|--------|
| **電子郵件** | `logical_type: email` | 電子郵件地址格式 | `user@example.com` |
| **網址** | `logical_type: url` | 網址連結 | `https://example.com` |
| **IP 位址** | `logical_type: ip_address` | IP 地址 | `192.168.1.1` |
| **電話** | `logical_type: phone` | 電話號碼 | `+886-2-1234-5678` |
| **郵遞區號** | `logical_type: postal_code` | 郵遞區號 | `10045` |

## 注意事項

- 邏輯型別僅用於驗證，不改變儲存格式
- 底層資料型別通常為 `string`
- 可搭配基本型別一起使用以提供額外的語義資訊