---
title: "Adapter API"
weight: 390
---

## 概述

Adapter 層是 PETsARD 架構中的關鍵組件，負責將各個模組包裝成統一的執行介面，供 [`Executor`](../executor-api) 調用。每個 Adapter 為其對應的模組提供標準化的生命週期方法和資料流管理。

## Adapter 整體架構

{{< mermaid-file file="content/docs/python-api/adapter-api/adapter-overview-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 灰色框：抽象基底類別
> - 淺紫框：具體 Adapter 實作類別
> - `<|--`：繼承關係 (inheritance)

## 架構

所有 Adapter 類別都繼承自 [`BaseAdapter`](petsard/adapter.py:20)，並實作以下核心介面：

### 核心方法

- **[`__init__(config: dict)`](petsard/adapter.py:25)** - 使用配置初始化 adapter
- **[`run(input: dict)`](petsard/adapter.py:328)** - 執行模組功能並計時
- **[`set_input(status)`](petsard/adapter.py:403)** - 從 Status 物件準備輸入資料
- **[`get_result()`](petsard/adapter.py:413)** - 取得執行結果
- **[`get_metadata()`](petsard/adapter.py:421)** - 取得詮釋資料（Schema）（如適用）

### 工具方法

[`BaseAdapter`](petsard/adapter.py:20) 提供多個工具方法用於常見操作：

- **[`_apply_precision_rounding()`](petsard/adapter.py:51)** - 根據 schema 對數值欄位套用精度四捨五入
- **[`_update_schema_stats()`](petsard/adapter.py:96)** - 重新計算統計資訊並更新 schema
- **[`_handle_benchmark_download()`](petsard/adapter.py:133)** - 處理 benchmark:// 協議下載
- **[`_resolve_data_source()`](petsard/adapter.py:208)** - 統一的資料來源解析，支援 "Module.key" 格式
- **[`_get_metadata_with_priority()`](petsard/adapter.py:282)** - 按優先順序取得 metadata
- **[`_safe_copy()`](petsard/adapter.py:306)** - 根據資料類型的統一拷貝策略

## Adapter 類別

| Adapter | 對應模組 | 主要特色 |
|---------|----------|----------|
| [`LoaderAdapter`](petsard/adapter.py:431) | [`Loader`](../loader-api) | 資料載入，支援 benchmark:// 協議 |
| [`SplitterAdapter`](petsard/adapter.py:588) | [`Splitter`](../splitter-api) | 資料分割，支援 custom_data 方法 |
| [`PreprocessorAdapter`](petsard/adapter.py:792) | [`Processor`](../processor-api) | 前處理，支援全域離群值配置展開 |
| [`SynthesizerAdapter`](petsard/adapter.py:1015) | [`Synthesizer`](../synthesizer-api) | 資料合成，支援 custom_data 方法 |
| [`PostprocessorAdapter`](petsard/adapter.py:1171) | [`Processor`](../processor-api) | 後處理，支援資料型別復原 |
| [`ConstrainerAdapter`](petsard/adapter.py:1312) | [`Constrainer`](../constrainer-api) | 約束應用，支援 resample/validate 模式 |
| [`EvaluatorAdapter`](petsard/adapter.py:1840) | [`Evaluator`](../evaluator-api) | 評估，支援自動資料型別對齊 |
| [`DescriberAdapter`](petsard/adapter.py:1996) | [`Describer`](../describer-api) | 描述統計，支援 describe/compare 模式 |
| [`ReporterAdapter`](petsard/adapter.py:2318) | [`Reporter`](../reporter-api) | 報告產生，支援計時和驗證結果 |

## 基本使用模式

```python
from petsard.adapter import LoaderAdapter

# 創建 adapter
adapter = LoaderAdapter(config)

# 從 Status 設定輸入
input_data = adapter.set_input(status)

# 執行並計時
adapter.run(input_data)

# 取得結果
result = adapter.get_result()
metadata = adapter.get_metadata()  # 如適用
```

## 錯誤處理

所有 Adapter 都使用裝飾器模式處理錯誤：

- [`@log_and_raise_config_error`](petsard/adapter.py:361) - 配置錯誤處理，包含詳細日誌記錄
- [`@log_and_raise_not_implemented`](petsard/adapter.py:374) - 未實作方法處理

## 資料流

Adapter 透過 Status 物件管理模組間的資料流：

1. **輸入階段**：[`set_input()`](petsard/adapter.py:403) 透過 Status 從前置模組取得資料
2. **執行階段**：[`run()`](petsard/adapter.py:328) 執行包裝的模組並計時
3. **輸出階段**：[`get_result()`](petsard/adapter.py:413) 和 [`get_metadata()`](petsard/adapter.py:421) 將結果提供給 Status

## 注意事項

- Adapter 層是內部架構 - 不建議直接使用
- 優先使用 YAML 配置檔搭配 [`Executor`](../executor-api)
- 所有資料修改都遵守 Schema 的精度和統計設定
- Benchmark 下載透過 benchmark:// 協議自動處理
- 各 Adapter 的詳細配置選項請參考個別頁面