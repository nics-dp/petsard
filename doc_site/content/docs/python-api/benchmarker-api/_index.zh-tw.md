---
title: "Benchmarker API"
weight: 315
---

## 概述

Benchmarker 模組提供基準測試資料集及其 schema 檔案的下載與管理功能。透過 `benchmark://` 協議，可以方便地存取預定義的基準資料集和 YAML schema 檔案。

## 架構

{{< mermaid-file file="content/docs/python-api/benchmarker-api/benchmarker-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 紫色框：配置類別 (BenchmarkerConfig)
> - 淺藍框：請求處理類別 (BenchmarkerRequests)
> - 淺紅框：例外類別 (BenchmarkDatasetsError)
> - 黃色框：類別註釋說明
> - `-->`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 主要類別

### BenchmarkerConfig

處理基準資料集和 schema 檔案的配置管理。

```python
from petsard.loader.benchmarker import BenchmarkerConfig

# 資料檔案
config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)

# Schema 檔案
schema_config = BenchmarkerConfig(
    benchmark_name="adult-income_schema",
    filepath_raw="benchmark://adult-income_schema"
)
```

#### 屬性

- `benchmark_name`: 基準資料集或 schema 名稱
- `filepath_raw`: 原始檔案路徑（benchmark:// 協議）
- `benchmark_filename`: 本地檔案名稱

### BenchmarkerRequests

負責從遠端來源下載基準資料集。

```python
from petsard.loader.benchmarker import BenchmarkerRequests

downloader = BenchmarkerRequests(config.get_benchmarker_config())
downloader.download()
```

## 工作流程

1. **協議解析**：解析 `benchmark://` 協議
2. **配置建立**：根據資料集/schema 名稱建立配置
3. **資料下載**：從遠端下載資料集或 schema
4. **SHA-256 驗證**：驗證檔案完整性（不匹配時記錄警告，不阻擋執行）
5. **本地儲存**：儲存到 `benchmark/` 目錄

## 錯誤處理

- **BenchmarkDatasetsError**
  - 下載失敗時拋出
  - 資料集不存在時拋出
  - 網路連線問題時拋出
- **SHA-256 驗證**
  - 不匹配時記錄警告（不阻擋執行）
  - 允許使用修改過的本地檔案進行開發

## 注意事項

- 資料集和 schema 檔案下載後會快取在本地 `benchmark/` 目錄
- 首次使用需要網路連線
- 建議透過 LoaderAdapter 使用，而非直接呼叫
- 使用 YAML 配置檔是推薦做法
- 支援 CSV 資料檔案和 YAML schema 檔案
- SHA-256 驗證失敗會記錄警告但不會阻擋執行（v2.0.0 起）