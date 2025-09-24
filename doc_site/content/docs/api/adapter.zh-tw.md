---
title: Adapter
type: docs
weight: 61
prev: docs/api/reporter
next: docs/api/config
---

```python
petsard.adapter
```

Adapter 模組提供包裝類別，為所有 PETsARD 管線組件標準化執行介面。每個適配器封裝特定模組（Loader、Synthesizer 等），並提供一致的配置、執行和結果檢索方法。

## 設計概覽

Adapter 系統遵循裝飾器模式，以標準化介面包裝核心模組進行管線執行。此設計確保所有管線組件的一致行為，同時保持模組特定功能的靈活性。

### 核心原則

1. **標準化**：所有適配器實作相同的基礎介面，確保管線執行的一致性
2. **封裝**：每個適配器包裝對應的模組，處理配置和執行細節
3. **錯誤處理**：跨所有適配器的全面錯誤記錄和例外處理
4. **詮釋資料管理**：使用 Metadater 系統進行一致的詮釋資料處理

## 基礎類別

### `BaseAdapter`

```python
BaseAdapter(config)
```

定義所有適配器標準介面的抽象基礎類別。

**參數**
- `config` (dict)：適配器的配置參數

**方法**
- `run(input)`：執行適配器的功能
- `set_input(status)`：從管線狀態配置輸入資料
- `get_result()`：檢索適配器的輸出資料
- `get_metadata()`：檢索與輸出相關的詮釋資料

## 適配器類別

### `LoaderAdapter`

```python
LoaderAdapter(config)
```

包裝 Loader 模組進行資料載入操作，並自動處理基準資料集協議。

**配置參數**
- `filepath` (str)：資料檔案路徑，支援兩種格式：
  - **本地檔案**：一般檔案路徑（如 'data.csv'）
  - **基準資料集**：使用 `benchmark://` 協議（如 'benchmark://adult-income'）
- `column_types` (dict, optional)：**已棄用** - 欄位類型規格（請改用 schema）
- `header_names` (list, optional)：無標頭檔案的自訂標題名稱
- `na_values` (str/list/dict, optional)：**已棄用** - 自訂 NA 值定義（請改用 schema）
- `schema` (Schema/dict/str, optional)：完整資料類型和詮釋資料的 Schema 設定：
  - Schema 物件：直接提供 schema 設定
  - dict：將轉換為 Schema 的字典
  - str：包含 schema 設定的 YAML 檔案路徑

**基準資料集處理**
LoaderAdapter 會自動偵測 `benchmark://` 協議並處理：
1. 解析協議並提取資料集名稱
2. 建立 BenchmarkerConfig 實例
3. 使用 BenchmarkerRequests 下載資料集（如需要）
4. 將路徑轉換為本地檔案路徑
5. 使用 Loader 載入本地檔案

此設計實現了 Loader 與 Benchmarker 的完全解耦，讓 Loader 專注於純檔案載入功能。

**主要方法**
- `get_result()`：回傳載入的 DataFrame
- `get_metadata()`：回傳載入資料的 SchemaMetadata

### `SplitterAdapter`

```python
SplitterAdapter(config)
```

包裝 Splitter 模組進行資料分割操作。當配置中指定 `method='custom_data'` 時，適配器會直接使用 LoaderAdapter 處理預分割資料的載入，而不使用 Splitter 模組。

**配置參數**
- `train_split_ratio` (float)：訓練資料比例（預設：0.8）
- `num_samples` (int)：分割樣本數量（預設：1）
- `random_state` (int/float/str, optional)：隨機種子

自訂資料模式：
- `method` (str)：設為 'custom_data' 以載入預分割資料
- `filepath` (dict)：'ori'（訓練）和 'control'（驗證）資料的路徑
- 支援每個檔案的所有 LoaderAdapter 參數，包括：
  - `header_names` (list)：無標頭檔案的自訂欄位標頭
  - `schema` (Schema/dict/str)：資料類型和詮釋資料的 Schema 設定
  - 其他資料載入所需的參數

**主要方法**
- `get_result()`：回傳包含 'train' 和 'validation' DataFrame 的字典
- `get_metadata()`：回傳包含分割資訊的更新 SchemaMetadata

### `PreprocessorAdapter`

```python
PreprocessorAdapter(config)
```

包裝 Processor 模組進行資料前處理操作。

**配置參數**
- `method` (str)：處理方法（'default' 或 'custom'）
- `sequence` (list, optional)：自訂處理序列
- `config` (dict, optional)：處理器特定配置

**主要方法**
- `get_result()`：回傳前處理的 DataFrame
- `get_metadata()`：回傳更新的 SchemaMetadata

### `SynthesizerAdapter`

```python
SynthesizerAdapter(config)
```

包裝 Synthesizer 模組進行合成資料生成。當配置中指定 `syn_method='custom_data'` 時，適配器會直接使用 LoaderAdapter 處理外部合成資料的載入，而不使用 Synthesizer 模組。

**配置參數**
- `method` (str)：合成方法（例如：'sdv'）
- `model` (str)：模型類型（例如：'GaussianCopula'）
- 選定方法的額外特定參數

自訂資料模式：
- `method` (str)：設為 'custom_data' 以載入外部合成資料
- `filepath` (str)：預合成資料檔案的路徑
- 支援所有 LoaderAdapter 參數，包括：
  - `header_names` (list)：無標頭檔案的自訂欄位標頭
  - `schema` (Schema/dict/str)：資料類型和詮釋資料的 Schema 設定
  - 其他資料載入所需的參數

**主要方法**
- `get_result()`：回傳合成的 DataFrame

### `PostprocessorAdapter`

```python
PostprocessorAdapter(config)
```

包裝 Processor 模組進行資料後處理操作。

**配置參數**
- `method` (str)：處理方法（'default' 或自訂）

**主要方法**
- `get_result()`：回傳後處理的 DataFrame

### `ConstrainerAdapter`

```python
ConstrainerAdapter(config)
```

包裝 Constrainer 模組應用資料約束。

**配置參數**
- `field_combinations` (list)：欄位組合約束
- `target_rows` (int, optional)：目標行數
- `sampling_ratio` (float, optional)：重新採樣的採樣比例
- `max_trials` (int, optional)：最大重新採樣嘗試次數

**主要方法**
- `get_result()`：回傳約束後的 DataFrame

### `EvaluatorAdapter`

```python
EvaluatorAdapter(config)
```

包裝 Evaluator 模組進行資料品質評估。

**配置參數**
- `method` (str)：評估方法（例如：'sdmetrics'）
- 選定方法的額外特定參數

**主要方法**
- `get_result()`：回傳按指標類型分類的評估結果字典

### `DescriberAdapter`

```python
DescriberAdapter(config)
```

包裝 Describer 模組進行描述性資料分析。

**配置參數**
- `method` (str)：描述方法
- 選定方法的額外特定參數

**主要方法**
- `get_result()`：回傳描述性分析結果字典

### `ReporterAdapter`

```python
ReporterAdapter(config)
```

包裝 Reporter 模組進行結果匯出和報告。

**配置參數**
- `method` (str)：報告方法（'save_data' 或 'save_report'）
- `source` (str/list)：資料匯出的來源模組
- `granularity` (str)：報告粒度（'global'、'columnwise'、'pairwise'）
- `output` (str, optional)：輸出檔名前綴

**主要方法**
- `get_result()`：回傳生成的報告資料

## 使用範例

### 基本適配器使用

```python
from petsard.adapter import LoaderAdapter

# 建立和配置適配器
config = {"filepath": "data.csv"}
loader_adapter = LoaderAdapter(config)

# 設定輸入（通常由 Executor 完成）
input_data = loader_adapter.set_input(status)

# 執行操作
loader_adapter.run(input_data)

# 檢索結果
data = loader_adapter.get_result()
metadata = loader_adapter.get_metadata()
```

### 管線整合

```python
from petsard.config import Config
from petsard.executor import Executor

# 適配器通常透過 Config 和 Executor 使用
config_dict = {
    "Loader": {"load_data": {"filepath": "data.csv"}},
    "Synthesizer": {"synth": {"method": "sdv", "model": "GaussianCopula"}},
    "Evaluator": {"eval": {"method": "sdmetrics"}}
}

config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## 架構優勢

### 1. 一致介面
- **標準化方法**：所有適配器實作相同的基礎介面
- **可預測行為**：跨所有模組的一致執行模式

### 2. 錯誤處理
- **全面記錄**：詳細的除錯和監控記錄
- **例外管理**：一致的錯誤處理和報告

### 3. 管線整合
- **狀態管理**：與 Status 系統的無縫整合
- **資料流**：管線階段間的標準化資料傳遞

### 4. 模組化
- **關注點分離**：每個適配器處理一個特定功能
- **可擴展性**：容易為新模組添加新適配器

Adapter 系統為 PETsARD 的模組化管線架構提供基礎，確保所有資料處理階段的一致和可靠執行。