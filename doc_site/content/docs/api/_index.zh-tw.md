---
title: API 文件
type: docs
weight: 1050
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## API 參考概覽

| 模組 | 物件名稱 | 建立方法 | 主要方法 |
|------|----------|----------|----------|
| [Adapter]({{< ref "docs/api/adapter" >}}) | `*Adapter` | `*Adapter(config)` | `run()`, `set_input()`, `get_result()` |
| [Utils]({{< ref "docs/api/utils" >}}) | 函式 | 直接匯入 | `load_external_module()` |

## 系統組件
- [Adapter]({{< ref "docs/api/adapter" >}}) - 所有模組的標準化執行包裝器
- [Utils]({{< ref "docs/api/utils" >}}) - 核心工具函式和外部模組載入