---
title: "Benchmarker API"
weight: 330
---

## 概述

Benchmarker 模組提供基準測試資料集的下載與管理功能。透過 `benchmark://` 協議，可以方便地存取預定義的基準資料集。

## 架構

{{< mermaid-file file="content/docs/python-api/benchmarker-api/benchmarker-class-diagram.mmd" >}}

> **圖例說明：**
> - 紫色框：配置類別 (BenchmarkerConfig)
> - 淺藍框：請求處理類別 (BenchmarkerRequests)
> - 淺紅框：例外類別 (BenchmarkDatasetsError)
> - 黃色框：類別註釋說明
> - `-->`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 主要類別

### BenchmarkerConfig

處理基準資料集的配置管理。

```python
from petsard.loader.benchmarker import BenchmarkerConfig

config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)
```

#### 屬性

- `benchmark_name`: 基準資料集名稱
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
2. **配置建立**：根據資料集名稱建立配置
3. **資料下載**：從遠端下載資料集
4. **本地儲存**：儲存到 `benchmark/` 目錄

## 錯誤處理

- **BenchmarkDatasetsError**
  - 下載失敗時拋出
  - 資料集不存在時拋出
  - 網路連線問題時拋出

## 注意事項

- 資料集下載後會快取在本地 `benchmark/` 目錄
- 首次使用需要網路連線
- 建議透過 LoaderAdapter 使用，而非直接呼叫
- 使用 YAML 配置檔是推薦做法