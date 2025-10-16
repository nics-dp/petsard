---
title: "LoaderAdapter"
weight: 1
---

LoaderAdapter 處理資料載入，並自動處理 `benchmark://` 協定以下載基準資料集和模式檔案。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/loaderadapter-usage-diagram.mmd" >}}

> **圖例：**
> - 淺紫色框：LoaderAdapter 主類別
> - 藍色框：核心載入模組
> - 紫色框：基準資料集處理模組
> - 淺粉色框：配置類別
> - `..>`：依賴關係
> - `-->`：擁有關係

## 主要功能

- 統一的資料載入介面
- 自動偵測並處理資料和模式的 `benchmark://` 協定
- 整合 Loader 與 Benchmarker 功能
- 回傳資料和 Schema 詮釋資料
- 支援 CSV 資料檔和 YAML 模式檔

## 方法參考

### `__init__(config: dict)`

初始化 LoaderAdapter 實例，自動處理 benchmark:// 協定。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 必須包含 `filepath` 鍵
  - 支援 `benchmark://` 協定
  - 可選參數包括：
    - `schema`：Schema 檔案路徑
    - `nrows`：僅載入指定數量的資料列（用於快速測試）
    - `delimiter`、`encoding`、`header` 等 pandas 讀取參數

### `run(input: dict)`

執行資料載入，包括自動下載基準資料集。

**參數：**
- `input`：dict，必要
  - 輸入參數字典
  - LoaderAdapter 通常接收空字典 `{}`

**回傳：**
無直接回傳值。使用 `get_result()` 和 `get_metadata()` 取得結果。

### `get_result()`

取得載入的資料。

**回傳：**
- `pd.DataFrame`：載入的資料

### `get_metadata()`

取得資料的 Schema 詮釋資料。

**回傳：**
- `Schema`：資料詮釋資料

## 使用範例

```python
from petsard.adapter import LoaderAdapter

# 一般檔案載入
adapter = LoaderAdapter({
    "filepath": "data/users.csv",
    "schema": "schemas/user.yaml"
})

# 使用 nrows 參數進行快速測試
adapter = LoaderAdapter({
    "filepath": "data/large_dataset.csv",
    "schema": "schemas/data.yaml",
    "nrows": 1000  # 僅載入前 1000 列
})

# 或使用 benchmark:// 協定
# adapter = LoaderAdapter({
#     "filepath": "benchmark://adult-income",
#     "schema": "benchmark://adult-income_schema"
# })

# 執行載入
adapter.run({})

# 取得結果
data = adapter.get_result()
metadata = adapter.get_metadata()
```

## 工作流程

1. **協定偵測**：檢查 filepath/schema 是否使用 `benchmark://` 協定
2. **Benchmarker 處理**（基準協定時）
   - 下載檔案到本地
   - 驗證 SHA-256（不符時發出警告）
   - 轉換路徑為本地路徑
3. **資料載入**：載入資料和詮釋資料

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- 基準檔案在首次下載後會快取
- 結果會快取直到下次 run() 呼叫