---
title: "Executor API"
weight: 50
---

Executor 是 PETsARD 的核心編排模組，負責解析配置、依序執行工作流程模組，並提供結果存取介面。

## 類別架構

{{< mermaid-file file="content/docs/python-api/executor-api/executor-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 淺紫框：配置與狀態類別
> - `*--`：組合關係 (composition)

## 基本使用

```python
from petsard import Executor

# 載入配置並執行
exec = Executor(config='config.yaml')
exec.run()

# 取得結果
results = exec.get_result()
timing = exec.get_timing()
```

## 建構函式

### 語法

```python
Executor(config: str)
```

### 參數

| 參數 | 類型 | 必要性 | 說明 |
|------|------|--------|------|
| `config` | `str` | 必要 | 配置輸入：YAML 檔案路徑或 YAML 字串 |

### 返回值

返回已初始化 Config 和 Status 的 Executor 實例。

### 使用範例

**範例 1：從 YAML 檔案載入**

```python
from petsard import Executor

# 從檔案建立 Executor
exec = Executor(config='workflow_config.yaml')
print("配置載入成功")
```

**範例 2：使用 YAML 字串**

```python
from petsard import Executor

# 定義 YAML 字串配置
config_yaml = """
Loader:
  load_csv:
    filepath: data/input.csv

Synthesizer:
  generate:
    method: sdv
    model: GaussianCopula
    num_samples: 1000
"""

# 從 YAML 字串建立 Executor
exec = Executor(config=config_yaml)
exec.run()
```

**範例 3：動態生成 YAML 字串**

```python
from petsard import Executor

# 動態生成 YAML 字串
def create_config_yaml(filepath, model_name):
    return f"""
Loader:
  load_data:
    filepath: {filepath}

Synthesizer:
  generate:
    method: sdv
    model: {model_name}
"""

# 使用動態配置
config = create_config_yaml('data/input.csv', 'CTGAN')
exec = Executor(config=config)
exec.run()
```

## 配置選項

Executor 支援在 YAML 檔案中設定執行相關的配置選項：

```yaml
Executor:
  log_output_type: "both"    # 日誌輸出位置："stdout", "file", "both"
  log_level: "INFO"          # 日誌等級
  log_dir: "./logs"          # 日誌檔案目錄
  log_filename: "PETsARD_{timestamp}.log"  # 日誌檔案名稱模板

# 其他模組配置
Loader:
  load_data:
    filepath: data.csv
```

### 配置參數說明

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `log_output_type` | `str` | `"file"` | 日誌輸出位置：`"stdout"`, `"file"`, `"both"` |
| `log_level` | `str` | `"INFO"` | 日誌等級：`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `log_dir` | `str` | `"."` | 日誌檔案儲存目錄 |
| `log_filename` | `str` | `"PETsARD_{timestamp}.log"` | 日誌檔案名稱模板（支援 `{timestamp}` 佔位符） |

## 方法

### run()

根據配置執行工作流程。

```python
exec = Executor(config='config.yaml')
exec.run()
```

**注意**：在 v2.0.0 中，此方法將回傳執行狀態（success/failed）而非 None。

### get_result()

取得執行結果，包含所有實驗的 DataFrames 和 Schemas。

```python
results = exec.get_result()

# 結果結構
# {
#   'Loader[experiment_1]_Synthesizer[method_a]': {
#     'data': DataFrame,
#     'schema': Schema
#   },
#   ...
# }
```

### get_timing()

取得執行時間報告，顯示各模組和步驟的耗時。

```python
timing_df = exec.get_timing()
print(timing_df)
```

回傳包含時間資訊的 pandas DataFrame。

### is_execution_completed()

檢查工作流程執行是否完成。

```python
if exec.is_execution_completed():
    print("執行完成")
    results = exec.get_result()
```

**注意**：此方法將在 v2.0.0 中廢棄。請改用 `run()` 的回傳值。

### get_inferred_schema(module)

取得指定模組的推論 Schema。

```python
# 取得推論的 Preprocessor Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    print(f"推論的 Schema：{inferred_schema.id}")
```

**參數**：
- `module` (str)：模組名稱（例如 'Preprocessor'）

**返回值**：推論的 Schema，如果不存在則回傳 None

## 執行流程

Executor 會按照以下順序執行各模組：

1. **Loader** - 資料載入
2. **Preprocessor** - 資料前處理（選填）
3. **Splitter** - 資料分割（選填）
4. **Synthesizer** - 資料合成
5. **Postprocessor** - 資料後處理（選填）
6. **Constrainer** - 約束條件驗證（選填）
7. **Evaluator** - 資料評測（選填）
8. **Reporter** - 結果報告（選填）

## 內部組件

### ExecutorConfig

執行器專用配置類別：

```python
@dataclass
class ExecutorConfig:
    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"
```

### Config

配置管理類別，負責解析 YAML 配置並建立執行序列。詳細說明請參閱 [`Config API`](../config-api/)。

### Status

狀態追蹤類別，負責記錄執行歷史和詮釋資料變化。詳細說明請參閱 [`Status API`](../status-api/)。

## 多實驗處理

Executor 自動處理多個實驗的組合：

```yaml
Loader:
  experiment_1:
    filepath: data1.csv
  experiment_2:
    filepath: data2.csv

Synthesizer:
  method_a:
    method: sdv
    model: GaussianCopula
  method_b:
    method: sdv
    model: CTGAN
```

這會產生 4 個實驗組合：
- `Loader[experiment_1]_Synthesizer[method_a]`
- `Loader[experiment_1]_Synthesizer[method_b]`
- `Loader[experiment_2]_Synthesizer[method_a]`
- `Loader[experiment_2]_Synthesizer[method_b]`

## 注意事項

- **輸入類型偵測**：Executor 會自動偵測 `config` 是檔案路徑還是 YAML 字串
- **配置驗證**：Config 會在初始化時自動驗證配置內容
- **路徑處理**：檔案路徑支援絕對路徑和相對路徑
- **錯誤報告**：提供詳細的配置錯誤和 YAML 解析錯誤訊息
- **日誌記錄**：執行過程會產生詳細的日誌記錄
- **模組順序**：Executor 會自動按照正確順序執行模組
- **單一實例**：每個 Executor 實例管理一個工作流程
- **執行順序**：必須先呼叫 `run()`，再呼叫 `get_result()` 和 `get_timing()`