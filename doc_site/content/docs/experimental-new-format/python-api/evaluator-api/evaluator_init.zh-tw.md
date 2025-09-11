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

```python
evaluator = Evaluator(
    method='anonymeter-singlingout',
    n_attacks=2000,          # 攻擊次數（預設：2,000）
    n_cols=3,                # 每次查詢欄位數（預設：3）
    max_attempts=500000      # 最大嘗試次數（預設：500,000）
)
```

### Anonymeter - Linkability

```python
evaluator = Evaluator(
    method='anonymeter-linkability',
    n_attacks=2000,          # 攻擊次數（預設：2,000）
    max_n_attacks=False,     # 強制最大攻擊（預設：False）
    aux_cols=[               # 輔助資訊欄位
        ['gender', 'zip'],   # 公開資料欄位列表
        ['age', 'medical']   # 私密資料欄位列表
    ],
    n_neighbors=10           # 最近鄰數量（預設：10）
)
```

### Anonymeter - Inference

```python
evaluator = Evaluator(
    method='anonymeter-inference',
    n_attacks=2000,          # 攻擊次數（預設：2,000）
    max_n_attacks=False,     # 強制最大攻擊（預設：False）
    secret='sensitive_col',  # 要推論的欄位（必要）
    aux_cols=['col1', 'col2']  # 輔助欄位列表（可選）
)
```

### SDMetrics

```python
# Diagnostic Report
evaluator = Evaluator(method='sdmetrics-diagnosticreport')

# Quality Report
evaluator = Evaluator(method='sdmetrics-qualityreport')
```

### MLUtility 新版

```python
# 分類任務
evaluator = Evaluator(
    method='mlutility',
    task_type='classification',              # 任務類型（必要）
    target='label',                          # 目標欄位（必要）
    experiment_design='dual_model_control',  # 實驗設計（預設）
    resampling='smote-enn',                  # 不平衡處理（可選）
    metrics=['mcc', 'f1_score', 'roc_auc'], # 評估指標（可選）
    xgb_params={'n_estimators': 100},       # XGBoost 參數（可選）
    random_state=42                          # 隨機種子（預設：42）
)

# 迴歸任務
evaluator = Evaluator(
    method='mlutility',
    task_type='regression',
    target='price',
    experiment_design='domain_transfer',
    metrics=['r2_score', 'mse', 'mae', 'rmse'],
    xgb_params={'max_depth': 6},
    random_state=42
)

# 聚類任務
evaluator = Evaluator(
    method='mlutility',
    task_type='clustering',
    experiment_design='dual_model_control',
    n_clusters=5,                            # 聚類數量（預設：5）
    metrics=['silhouette_score'],
    random_state=42
)
```

### MLUtility 舊版

```python
# 分類（使用多個模型）
evaluator = Evaluator(
    method='mlutility-classification',
    target='label'                           # 目標欄位（必要）
)

# 迴歸（使用多個模型）
evaluator = Evaluator(
    method='mlutility-regression',
    target='price'                           # 目標欄位（必要）
)

# 聚類（K-means）
evaluator = Evaluator(
    method='mlutility-cluster',
    n_clusters=[4, 5, 6]                     # 聚類數量列表（預設：[4, 5, 6]）
)
```

### Stats 統計評估

```python
evaluator = Evaluator(
    method='stats',
    stats_method=['mean', 'std', 'median', 'jsdivergence'],  # 統計方法
    compare_method='pct_change',             # 比較方法：'diff' 或 'pct_change'
    aggregated_method='mean',                # 聚合方法
    summary_method='mean'                    # 摘要方法
)
```

### Custom 自訂評估

```python
evaluator = Evaluator(
    method='custom_method',
    module_path='/path/to/custom_evaluator.py',  # 模組路徑（必要）
    class_name='MyCustomEvaluator',              # 類別名稱（必要）
    custom_param1='value1',                      # 自訂參數
    custom_param2='value2'
)
```

## 範例

### 基本使用

```python
from petsard import Evaluator

# 使用預設方法
evaluator = Evaluator('default')

# 使用特定方法
evaluator = Evaluator('anonymeter-singlingout')

# 使用參數
evaluator = Evaluator(
    method='mlutility',
    task_type='classification',
    target='label'
)
```

### 完整範例

```python
from petsard import Evaluator
import pandas as pd

# 準備資料
train_data = pd.read_csv('train.csv')
synthetic_data = pd.read_csv('synthetic.csv')
test_data = pd.read_csv('test.csv')

# 初始化評估器
evaluator = Evaluator(
    method='anonymeter-singlingout',
    n_attacks=3000,
    n_cols=4,
    max_attempts=1000000     # 1,000,000
)

# 建立評估器
evaluator.create()

# 執行評估
result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})

# 查看結果
print(result['global'])
```

## 注意事項

- 方法名稱不區分大小寫
- 不同評估方法需要不同的參數配置
- 建議使用新版 MLUtility (`method='mlutility'`) 而非舊版
- 自訂評估器必須實作標準介面
- 初始化後必須呼叫 `create()` 方法才能使用 `eval()`