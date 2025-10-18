---
title: "Config API（更新中）"
weight: 60
---

配置管理類別，負責解析 YAML 配置並建立模組執行序列。

## 類別架構

{{< mermaid-file file="content/docs/python-api/config-api/config-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 橘色框：抽象基類
> - 淺紫框：具體 Adapter 實作
> - `..>`：依賴關係 (dependency)
> - `<|--`：繼承關係 (inheritance)

## 基本使用

```python
from petsard.config import Config

# 從配置字典建立 Config
config_dict = {
    "Loader": {
        "load_data": {
            "filepath": "data.csv"
        }
    },
    "Synthesizer": {
        "generate": {
            "method": "sdv",
            "model": "GaussianCopula"
        }
    }
}

config = Config(config_dict)

# Config 通常由 Executor 內部使用
from petsard import Executor
exec = Executor('config.yaml')  # Executor 內部會建立 Config
```

## 建構函式 (__init__)

初始化配置管理實例。

### 語法

```python
def __init__(
    config: dict
)
```

### 參數

- **config** : dict, required
    - 配置字典
    - 必要參數
    - 包含所有模組的配置資訊

### 返回值

- **Config**
    - 初始化後的配置管理實例

### 使用範例

```python
from petsard.config import Config

# 基本配置
config_dict = {
    "Loader": {
        "load_data": {"filepath": "benchmark://adult-income"}
    },
    "Synthesizer": {
        "generate": {"method": "default"}
    }
}

config = Config(config_dict)

# 檢視配置屬性
print(f"模組序列：{config.sequence}")
print(f"操作器數量：{config.config.qsize()}")
```

## 配置結構

Config 期望的字典結構：

```python
{
    "ModuleName": {
        "experiment_name": {
            "parameter1": "value1",
            "parameter2": "value2"
        }
    }
}
```

## 核心屬性

- **config** : queue.Queue
    - 實例化的 Adapter 佇列
    - 準備執行的操作器序列

- **module_flow** : queue.Queue
    - 模組名稱佇列
    - 與 config 佇列對應

- **expt_flow** : queue.Queue
    - 實驗名稱佇列
    - 與 config 佇列對應

- **sequence** : list
    - 模組執行順序列表
    - 依照 PETsARD 工作流程順序排列

- **yaml** : dict
    - 處理後的配置字典
    - 儲存原始配置資訊

## 自動處理機制

### 1. 模組排序

Config 會自動按照正確順序安排模組：

```
Loader → Preprocessor → Splitter → Synthesizer → 
Postprocessor → Constrainer → Evaluator → Reporter
```

### 2. Splitter 展開

當 Splitter 配置包含 `num_samples > 1` 時自動展開：

```python
# 輸入
"Splitter": {
    "split_data": {
        "train_split_ratio": 0.8,
        "num_samples": 3
    }
}

# 自動展開為
"Splitter": {
    "split_data_[3-1]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-2]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-3]": {"train_split_ratio": 0.8, "num_samples": 1}
}
```

### 3. Adapter 實例化

為每個實驗配置建立對應的 Adapter：

```python
config_dict = {
    "Loader": {"load": {...}},
    "Synthesizer": {"synth": {...}}
}

# Config 會建立：
# - LoaderAdapter 實例（用於 load 實驗）
# - SynthesizerAdapter 實例（用於 synth 實驗）
```

### 4. 笛卡爾積生成

多實驗配置會產生所有組合：

```python
config_dict = {
    "Loader": {
        "load_v1": {...},
        "load_v2": {...}
    },
    "Synthesizer": {
        "method_a": {...},
        "method_b": {...}
    }
}

# 產生 4 個執行路徑：
# load_v1 → method_a
# load_v1 → method_b
# load_v2 → method_a
# load_v2 → method_b
```

## 配置驗證

### 命名規則驗證

Config 會檢查實驗名稱是否符合規則：

```python
# ✓ 有效的實驗名稱
"experiment_name"
"load_data"
"method_v2"

# ✗ 無效的實驗名稱（保留模式）
"experiment_[1]"
"load_data_[test]"
```

### 結構驗證

檢查配置字典的結構是否正確：
- 確認為字典格式
- 驗證模組名稱
- 檢查實驗配置完整性

## 與 Executor 整合

Config 通常由 Executor 內部使用：

```python
from petsard import Executor

# Executor 內部會：
# 1. 載入 YAML 檔案
# 2. 建立 Config 實例
# 3. 使用 Config 建立執行佇列
exec = Executor('config.yaml')
exec.run()
```

## 執行流程

1. **初始化**：解析配置字典
2. **驗證**：檢查命名規則和結構
3. **展開**：處理 Splitter 多樣本配置
4. **排序**：建立模組執行序列
5. **實例化**：為每個實驗建立 Adapter
6. **佇列化**：將 Adapter 放入執行佇列

## 注意事項

- **內部使用**：Config 主要由 Executor 內部使用
- **建議作法**：使用 YAML 配置檔和 Executor，而非直接使用 Config
- **命名限制**：實驗名稱不能使用 `_[xxx]` 模式（保留給系統）
- **自動處理**：Splitter 多樣本配置會自動展開
- **執行順序**：模組順序由 Config 自動決定，無法手動指定
- **笛卡爾積**：多實驗配置會產生所有可能組合
- **記憶體使用**：大量實驗組合會佔用較多記憶體
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容

## 相關文檔

- [Executor API](../executor-api/) - 使用 Config 的主要介面
- [Status API](../status-api/) - 與 Config 配合的狀態管理
- [Executor YAML](../../petsard-yaml/executor-yaml/config/) - YAML 配置說明