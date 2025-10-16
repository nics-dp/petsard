---
title: "Adapter API"
weight: 390
---

## 概述

Adapter 層是 PETsARD 架構中的關鍵組件，負責將各個模組包裝成統一的執行介面，供 Executor 調用。

## Adapter 整體架構

{{< mermaid-file file="content/docs/python-api/adapter-api/adapter-overview-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 灰色框：抽象基底類別
> - 淺紫框：具體 Adapter 實作類別
> - `<|--`：繼承關係 (inheritance)

## 架構

所有 Adapter 類別都繼承自 `BaseAdapter`，並實作以下核心方法：

- `__init__(config: dict)` - 初始化配置
- `run(input: dict)` - 執行主要邏輯
- `set_input(status)` - 設定輸入參數
- `get_result()` - 取得執行結果
- `get_metadata()` - 取得 metadata（如適用）

## Adapter 類別

| Adapter | 對應模組 | 說明 |
|---------|----------|------|
| LoaderAdapter | Loader | 資料載入，支援 benchmark:// 協議 |
| SplitterAdapter | Splitter | 資料分割 |
| PreprocessorAdapter | Processor | 前處理 |
| SynthesizerAdapter | Synthesizer | 資料合成 |
| PostprocessorAdapter | Processor | 後處理 |
| ConstrainerAdapter | Constrainer | 約束處理 |
| EvaluatorAdapter | Evaluator | 評估 |
| DescriberAdapter | Describer | 描述統計 |
| ReporterAdapter | Reporter | 報告產生 |

## 基本使用模式

```python
from petsard.adapter import LoaderAdapter

# 創建 adapter
adapter = LoaderAdapter(config)

# 設定輸入
input_data = adapter.set_input(status)

# 執行
adapter.run(input_data)

# 取得結果
result = adapter.get_result()
```

## 錯誤處理

所有 Adapter 都使用裝飾器模式處理錯誤：

- `@log_and_raise_config_error` - 配置錯誤處理
- `@log_and_raise_not_implemented` - 未實作方法處理

## 注意事項

- Adapter 層是內部架構，不建議直接使用
- 優先使用 YAML 配置檔和 Executor 執行
- 各 Adapter 的具體參數請參考子頁面文檔