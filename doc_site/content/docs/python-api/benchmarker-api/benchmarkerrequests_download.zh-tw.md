---
title: "download()"
weight: 331
---

下載指定的基準資料集到本地。

## 語法

```python
def download() -> None
```

## 說明

`download()` 方法負責從 AWS S3 儲存區下載指定的基準資料集，並儲存到本地 `benchmark/` 目錄。下載過程包含完整性驗證。

## 返回值

無返回值。資料集下載後會儲存在 `benchmark/` 目錄。

## 基本範例

```python
from petsard.loader.benchmarker import BenchmarkerConfig, BenchmarkerRequests

# 建立配置
config = BenchmarkerConfig(
    benchmark_name="adult-income",
    filepath_raw="benchmark://adult-income"
)

# 建立下載器並執行下載
downloader = BenchmarkerRequests(config.get_benchmarker_config())
downloader.download()
```

## 下載流程

1. **檢查本地快取**：檢查 `benchmark/` 目錄是否已存在該資料集
2. **建立目錄**：若不存在，建立 `benchmark/` 目錄
3. **下載資料**：從 AWS S3 下載資料集
4. **驗證完整性**：使用 SHA256 驗證下載的資料
5. **儲存檔案**：將資料儲存到本地

## 錯誤處理

```python
from petsard.exceptions import BenchmarkDatasetsError

try:
    downloader.download()
except BenchmarkDatasetsError as e:
    print(f"下載失敗: {e}")
```

可能的錯誤原因：
- 網路連線失敗
- 資料集不存在
- SHA256 驗證失敗
- 磁碟空間不足

## 注意事項

- 首次下載需要網路連線
- 資料集會快取在本地，重複下載會跳過
- 大型資料集下載可能需要較長時間
- 建議透過 LoaderAdapter 間接使用，而非直接呼叫