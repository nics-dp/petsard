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
| [Executor]({{< ref "docs/api/executor" >}}) | `Executor` | `Executor(config)` | `run()`, `get_result()`, `get_timing()` |
| [Adapter]({{< ref "docs/api/adapter" >}}) | `*Adapter` | `*Adapter(config)` | `run()`, `set_input()`, `get_result()` |
| [Config]({{< ref "docs/api/config" >}}) | `Config` | `Config(config_dict)` | 初始化時自動處理 |
| [Status]({{< ref "docs/api/status" >}}) | `Status` | `Status(config)` | `put()`, `get_result()`, `create_snapshot()` |
| [Utils]({{< ref "docs/api/utils" >}}) | 函式 | 直接匯入 | `load_external_module()` |

## 配置與執行
- [Executor]({{< ref "docs/api/executor" >}}) - 實驗管線的主要介面

## 系統組件
- [Adapter]({{< ref "docs/api/adapter" >}}) - 所有模組的標準化執行包裝器
- [Config]({{< ref "docs/api/config" >}}) - 實驗配置管理
- [Status]({{< ref "docs/api/status" >}}) - 管線狀態和進度追蹤
- [Utils]({{< ref "docs/api/utils" >}}) - 核心工具函式和外部模組載入