---
title: "DescriberAdapter"
weight: 5
---

DescriberAdapter 處理資料描述和比較，支援單一資料集描述和多資料集比較分析。

## 類別架構

{{< mermaid-file file="content/docs/python-api/adapter-api/describeradapter-usage-diagram.zh-tw.mmd" >}}

> **圖例：**
> - 淺紫色框：DescriberAdapter 主類別
> - 藍色框：核心描述模組
> - 紫色框：資料對齊模組
> - 淺粉色框：配置類別
> - `..>`：依賴關係
> - `-->`：擁有關係

## 主要功能

- 統一的資料描述介面
- 靈活的資料源選擇（透過 `source` 參數）
- 支援兩種模式：describe（單一資料集）、compare（資料集比較）
- 自動資料類型對齊（使用 Schema）
- 支援多種統計方法和 JS Divergence 計算

## 方法參考

### `__init__(config: dict)`

初始化 DescriberAdapter 實例。

**參數：**
- `config`：dict，必要
  - 配置參數字典
  - 必須包含 `source` 鍵（資料來源）
  - 可選 `method` 鍵：default、describe、compare
  - 可選 `mode` 鍵：自動根據 source 數量決定

### `run(input: dict)`

執行資料描述或比較，包括自動資料類型對齊。

**參數：**
- `input`：dict，必要
  - 輸入參數字典
  - 包含 `data` 字典（資料集）
  - 可選 `metadata` 用於資料類型對齊

**回傳：**
無直接回傳值。使用 `get_result()` 取得結果。

### `set_input(status)`

設定描述器的輸入資料。

**參數：**
- `status`：Status，必要
  - 系統狀態物件
  - 根據 source 配置提取資料

**回傳：**
- `dict`：包含描述所需的資料字典

### `get_result()`

取得描述結果。

**回傳：**
- `dict[str, pd.DataFrame]`：描述結果字典

## 使用範例

### 單一資料集描述

```python
from petsard.adapter import DescriberAdapter

# 描述單一資料集
adapter = DescriberAdapter({
    "source": "Loader",  # 或 ["Loader"]
    "method": "describe",
    "describe_method": ["mean", "median", "std", "corr"]
})

# 執行描述
adapter.run({})

# 取得結果
results = adapter.get_result()
```

### 資料集比較

```python
# 比較兩個資料集
adapter = DescriberAdapter({
    "source": {
        "base": "Splitter.train",
        "target": "Synthesizer"
    },
    "method": "compare",
    "stats_method": ["mean", "std", "jsdivergence"],
    "compare_method": "pct_change"
})

# 執行比較
adapter.run({})

# 取得結果
comparison_results = adapter.get_result()
```

## 工作流程

1. **Source 解析**：解析 source 參數決定資料來源
2. **Mode 決定**：
   - 1 個 source：describe 模式
   - 2 個 source：compare 模式
3. **資料收集**：從 Status 收集指定的資料
4. **Schema 取得**：嘗試取得 metadata 用於資料對齊
5. **資料類型對齊**（有 Schema 時）
6. **執行描述或比較**

## Source 參數格式

### 描述模式（單一資料源）

```yaml
# 字串格式
source: "Loader"

# 列表格式
source: ["Synthesizer"]
```

### 比較模式（兩個資料源）

```yaml
# 字典格式（推薦）
source:
  base: "Splitter.train"
  target: "Synthesizer"

# 向後相容格式
source:
  ori: "Splitter.train"
  syn: "Synthesizer"
```

## 資料源語法

- **簡單格式**：`"ModuleName"` - 取該模組的第一個可用資料
- **精確格式**：`"ModuleName.key"` - 取該模組的特定鍵值資料
  - 例如：`"Splitter.train"`、`"Splitter.validation"`

## 注意事項

- 這是內部 API，不建議直接使用
- 建議使用 YAML 配置檔和 Executor
- compare 模式會重用 DescriberDescribe 的統計功能
- 參數命名建議使用 `base`/`target` 取代舊的 `ori`/`syn`
- 結果會快取直到下次 run() 呼叫