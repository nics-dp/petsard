---
title: API 文件
type: docs
weight: 50
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## API 參考概覽

| 模組 | 物件名稱 | 建立方法 | 主要方法 |
|------|----------|----------|----------|
| [Executor]({{< ref "docs/api/executor" >}}) | `Executor` | `Executor(config)` | `run()`, `get_result()`, `get_timing()` |
| Loader | `Loader` | `Loader(filepath, **kwargs)` | `load()` |
| [Metadater]({{< ref "docs/api/metadater" >}}) | `Metadater` | `Metadater.create_schema()` | `create_schema()`, `validate_schema()` |
| [Splitter]({{< ref "docs/api/splitter" >}}) | `Splitter` | `Splitter(**kwargs)` | `split()` |
| [Processor]({{< ref "docs/api/processor" >}}) | `Processor` | `Processor(metadata, config)` | `fit()`, `transform()`, `inverse_transform()` |
| [Synthesizer]({{< ref "docs/api/synthesizer" >}}) | `Synthesizer` | `Synthesizer(**kwargs)` | `create()`, `fit_sample()` |
| [Constrainer]({{< ref "docs/api/constrainer" >}}) | `Constrainer` | `Constrainer(config)` | `apply()`, `resample_until_satisfy()` |
| [Evaluator]({{< ref "docs/api/evaluator" >}}) | `Evaluator` | `Evaluator(**kwargs)` | `create()`, `eval()` |
| [Describer]({{< ref "docs/api/describer" >}}) | `Describer` | `Describer(**kwargs)` | `create()`, `eval()` |
| [Reporter]({{< ref "docs/api/reporter" >}}) | `Reporter` | `Reporter(method, **kwargs)` | `create()`, `report()` |
| [Adapter]({{< ref "docs/api/adapter" >}}) | `*Adapter` | `*Adapter(config)` | `run()`, `set_input()`, `get_result()` |
| [Config]({{< ref "docs/api/config" >}}) | `Config` | `Config(config_dict)` | 初始化時自動處理 |
| [Status]({{< ref "docs/api/status" >}}) | `Status` | `Status(config)` | `put()`, `get_result()`, `create_snapshot()` |
| [Utils]({{< ref "docs/api/utils" >}}) | 函式 | 直接匯入 | `load_external_module()` |

## 配置與執行
- [Executor]({{< ref "docs/api/executor" >}}) - 實驗管線的主要介面

## 資料管理
- [Metadater]({{< ref "docs/api/metadater" >}}) - 資料集架構和詮釋資料管理

## 管線組件
- Loader - 資料載入和處理
- [Splitter]({{< ref "docs/api/splitter" >}}) - 實驗資料分割
- [Processor]({{< ref "docs/api/processor" >}}) - 資料前處理和後處理
- [Synthesizer]({{< ref "docs/api/synthesizer" >}}) - 合成資料生成
- [Constrainer]({{< ref "docs/api/constrainer" >}}) - 合成資料的資料約束處理器
- [Evaluator]({{< ref "docs/api/evaluator" >}}) - 隱私、保真度和效用評估
- [Describer]({{< ref "docs/api/describer" >}}) - 描述性資料摘要
- [Reporter]({{< ref "docs/api/reporter" >}}) - 結果匯出和報告

## 系統組件
- [Adapter]({{< ref "docs/api/adapter" >}}) - 所有模組的標準化執行包裝器
- [Config]({{< ref "docs/api/config" >}}) - 實驗配置管理
- [Status]({{< ref "docs/api/status" >}}) - 管線狀態和進度追蹤
- [Utils]({{< ref "docs/api/utils" >}}) - 核心工具函式和外部模組載入