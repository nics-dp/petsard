---
title: "LoaderAdapter"
weight: 341
---

LoaderAdapter 負責資料載入，並自動處理 `benchmark://` 協議的基準資料集和 schema 檔案下載。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/loaderadapter-usage-diagram.mmd" >}}

> **圖例說明：**
> - 淺紫框：LoaderAdapter 主類別  
> - 藍色框：核心載入模組
> - 紫色框：基準資料集處理模組
> - 淺粉框：配置類別
> - `..>`：依賴關係 (dependency)
> - `-->`：包含關係 (has)

## 主要功能

- 資料載入的統一介面
- 自動偵測並處理 `benchmark://` 協議（同時支援資料和 schema）
- 整合 Loader 與 Benchmarker 功能
- 返回資料與 Schema metadata
- 支援 CSV 資料檔案和 YAML schema 檔案

## 方法說明

### `__init__(config: dict)`

初始化 LoaderAdapter 實例，自動處理 benchmark:// 協議。

**參數：**
- `config`: dict, required
  - 配置參數字典
  - 必須包含 `filepath` 鍵
  - 支援 `benchmark://` 協議

**內部處理：**
1. **協議檢測**：檢查 filepath 或 schema 是否使用 `benchmark://` 協議
2. **Benchmarker 配置**：若為 benchmark 協議，建立 BenchmarkerConfig
3. **路徑轉換**：將 benchmark:// 路徑轉換為本地路徑
4. **Schema 處理**：若 schema 使用 benchmark:// 協議，單獨處理
5. **Loader 初始化**：使用處理後的配置建立 Loader 實例

### `run(input: dict)`

執行資料載入，包含 benchmark 資料集的自動下載。

**參數：**
- `input`: dict, required
  - 輸入參數字典
  - LoaderAdapter 通常接收空字典 `{}`

**執行流程：**
1. **Benchmark 處理**（若使用 benchmark:// 協議）
   - 下載基準資料集（CSV）
   - 下載基準 schema（YAML）若有指定
   - 驗證 SHA-256 完整性（不匹配時記錄警告）
   - 儲存至本地 `benchmark/` 目錄
   
2. **資料載入**
   - 呼叫內部 Loader 實例的 load() 方法
   - 載入資料並取得 Schema metadata

**返回值：**

無直接返回值。資料儲存在內部屬性中：
- 使用 `get_result()` 取得資料
- 使用 `get_metadata()` 取得 metadata

### `get_result()`

取得載入的資料。

**返回：**
- `pd.DataFrame`: 載入的資料

### `get_metadata()` 

取得資料的 Schema metadata。

**返回：**
- `Schema`: 資料的 metadata

## 使用範例

### 基本載入

```python
from petsard.adapter import LoaderAdapter

# 一般檔案載入
adapter = LoaderAdapter({
    "filepath": "data/users.csv",
    "schema": "schemas/user.yaml"
})

# 執行載入
adapter.run({})

# 取得結果
data = adapter.get_result()
metadata = adapter.get_metadata()
```

### Benchmark 資料集載入

```python
# 僅資料使用 benchmark:// 協議
adapter = LoaderAdapter({
    "filepath": "benchmark://adult-income",
    "schema": "schemas/adult-income.yaml"
})

# 資料和 schema 都使用 benchmark:// 協議
adapter = LoaderAdapter({
    "filepath": "benchmark://adult-income",
    "schema": "benchmark://adult-income_schema"
})

# 自動下載並載入
adapter.run({})
data = adapter.get_result()
metadata = adapter.get_metadata()
```

### 錯誤處理

```python
try:
    adapter = LoaderAdapter(config)
    adapter.run({})
except BenchmarkDatasetsError as e:
    print(f"下載基準資料集失敗: {e}")
except Exception as e:
    print(f"載入失敗: {e}")
```

## 支援的 Benchmark 資料集

目前支援以下基準資料集：

- `benchmark://adult-income` - UCI Adult Income 資料集（CSV）
- `benchmark://adult-income_schema` - Adult Income schema（YAML）

## 工作流程

1. **協議偵測**：檢查 filepath/schema 是否使用 `benchmark://` 協議
2. **Benchmarker 處理**（若為 benchmark 協議）
   - 為資料/schema 建立 BenchmarkerConfig
   - 下載檔案到本地
   - 驗證 SHA-256（不匹配時警告）
   - 轉換路徑為本地路徑
3. **Loader 初始化**：使用處理後的配置建立 Loader
4. **資料載入**：呼叫 Loader.load() 載入資料

## 注意事項

- 此為內部 API，不建議直接使用
- 優先使用 YAML 配置檔和 Executor
- benchmark:// 協議不區分大小寫
- 資料集和 schema 檔案會下載到 `benchmark/` 目錄
- 首次使用需要網路連線
- Benchmark 檔案首次下載後會快取
- 大型資料集下載可能需要較長時間
- `method` 參數已棄用，會自動移除
- SHA-256 驗證失敗會記錄警告但不會阻擋執行（v2.0.0+）
- 支援 CSV 資料檔案和 YAML schema 檔案