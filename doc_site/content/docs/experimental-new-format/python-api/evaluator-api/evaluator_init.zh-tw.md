---
title: "Evaluator.__init__()"
weight: 341
---

初始化評估器實例。

## 語法

```python
def __init__(method: str, **kwargs)
```

## 參數

- **method** : str
    - 評估方法名稱（大小寫不敏感）
    - 必要參數
    - 支援的方法：
        - 隱私風險評估：`'anonymeter-singlingout'`, `'anonymeter-linkability'`, `'anonymeter-inference'`
        - 資料品質評估：`'sdmetrics-diagnosticreport'`, `'sdmetrics-qualityreport'`
        - 機器學習效用（新版）：`'mlutility'`
        - 機器學習效用（舊版）：`'mlutility-classification'`, `'mlutility-regression'`, `'mlutility-cluster'`
        - 統計評估：`'stats'`
        - 自訂評估：`'custom_method'`
        - 預設值：`'default'`（使用 sdmetrics-qualityreport）

- **kwargs** : dict
    - 依據不同評估方法的額外參數
    - 詳見各評估方法的參數說明

## 返回值

- **Evaluator**
    - 初始化後的評估器實例

## 各評估方法參數說明

### Anonymeter - Singling Out

- `n_attacks` (int): 攻擊次數（預設：2,000）
- `n_cols` (int): 每次查詢欄位數（預設：3）
- `max_attempts` (int): 最大嘗試次數（預設：500,000）

### Anonymeter - Linkability

- `n_attacks` (int): 攻擊次數（預設：2,000）
- `max_n_attacks` (bool): 強制最大攻擊（預設：False）
- `aux_cols` (list): 輔助資訊欄位列表
- `n_neighbors` (int): 最近鄰數量（預設：10）

### Anonymeter - Inference

- `n_attacks` (int): 攻擊次數（預設：2,000）
- `max_n_attacks` (bool): 強制最大攻擊（預設：False）
- `secret` (str): 要推論的欄位（必要）
- `aux_cols` (list): 輔助欄位列表（可選）

### SDMetrics

- Diagnostic Report：無額外參數
- Quality Report：無額外參數

### MLUtility 新版

- `task_type` (str): 任務類型 - 'classification', 'regression', 'clustering'（必要）
- `target` (str): 目標欄位（分類和迴歸必要）
- `experiment_design` (str): 實驗設計（預設：'dual_model_control'）
- `metrics` (list): 評估指標列表（可選）
- `random_state` (int): 隨機種子（預設：42）

### MLUtility 舊版

- 分類：`target` (str) - 目標欄位（必要）
- 迴歸：`target` (str) - 目標欄位（必要）
- 聚類：`n_clusters` (list) - 聚類數量列表（預設：[4, 5, 6]）

### Stats 統計評估

- `stats_method` (list): 統計方法列表
- `compare_method` (str): 比較方法 - 'diff' 或 'pct_change'
- `aggregated_method` (str): 聚合方法
- `summary_method` (str): 摘要方法

### Custom 自訂評估

- `module_path` (str): 模組路徑（必要）
- `class_name` (str): 類別名稱（必要）
- 其他自訂參數

## 基本範例

```python
from petsard import Evaluator

# 使用預設方法
evaluator = Evaluator('default')

# 使用特定方法
evaluator = Evaluator('anonymeter-singlingout', n_attacks=3000)
```

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 方法名稱不區分大小寫
- 不同評估方法需要不同的參數配置
- 建議使用新版 MLUtility (`method='mlutility'`) 而非舊版
- 自訂評估器必須實作標準介面
- 初始化後必須呼叫 `create()` 方法才能使用 `eval()`