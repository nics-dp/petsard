---
title: "Executor API（更新中）"
weight: 50
---

實驗管線的執行器，負責協調整個 PETsARD 工作流程的執行。

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

## 建構函式 (__init__)

初始化執行器實例。

### 語法

```python
def __init__(
    config: str
)
```

### 參數

- **config** : str, required
    - YAML 配置檔案路徑
    - 必要參數
    - 支援相對路徑和絕對路徑

### 返回值

- **Executor**
    - 初始化後的執行器實例

### 使用範例

```python
from petsard import Executor

# 基本使用
exec = Executor('config.yaml')

# 使用絕對路徑
exec = Executor('/path/to/config.yaml')

# 使用相對路徑
exec = Executor('./configs/experiment.yaml')
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

- **log_output_type** : str, optional
    - 日誌輸出位置
    - 可選值：`"stdout"`, `"file"`, `"both"`
    - 預設值：`"file"`

- **log_level** : str, optional
    - 日誌等級
    - 可選值：`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`
    - 預設值：`"INFO"`

- **log_dir** : str, optional
    - 日誌檔案儲存目錄
    - 預設值：`"."`（當前目錄）

- **log_filename** : str, optional
    - 日誌檔案名稱模板
    - 支援 `{timestamp}` 佔位符
    - 預設值：`"PETsARD_{timestamp}.log"`

## 執行流程

Executor 會按照以下順序執行各模組：

1. **Loader** - 資料載入
2. **Preprocessor** - 資料前處理（選填）
3. **Splitter** - 資料分割（選填）
4. **Synthesizer** - 資料合成
5. **Postprocessor** - 資料後處理（選填）
6. **Constrainer** - 約束條件（選填）
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

配置管理類別，負責解析 YAML 配置並建立執行序列。詳細說明請參閱 [Config API](../config-api/)。

### Status

狀態追蹤類別，負責記錄執行歷史和詮釋資料變化。詳細說明請參閱 [Status API](../status-api/)。

## 注意事項

- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **配置驗證**：Executor 會在初始化時驗證配置檔案
- **日誌記錄**：執行過程會產生詳細的日誌記錄
- **模組順序**：Executor 會自動按照正確順序執行模組
- **錯誤處理**：配置錯誤會在初始化時拋出 `ConfigError`
- **執行狀態**：使用 `is_execution_completed()` 檢查執行完成狀態
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容