---
title: "Evaluator.create()"
weight: 342
---

建立並初始化內部評估器實例。

## 語法

```python
def create() -> None
```

## 參數

無

## 返回值

無

## 說明

`create()` 方法用於初始化評估器的內部實例。必須在 `__init__()` 之後、`eval()` 之前呼叫此方法。

此方法會根據初始化時指定的 `method` 參數，建立對應的評估器子類別實例：
- AnonymeterEvaluator
- SDMetricsEvaluator  
- MLUtilityEvaluator
- MLUtilityV2Evaluator
- StatsEvaluator
- CustomEvaluator

## 範例

### 基本使用

```python
from petsard import Evaluator

# 初始化評估器
evaluator = Evaluator('sdmetrics-qualityreport')

# 建立內部實例
evaluator.create()

# 現在可以使用 eval() 方法
result = evaluator.eval(data)
```

### 隱私風險評估

```python
# Singling Out 風險
evaluator = Evaluator(
    method='anonymeter-singlingout',
    n_attacks=2000  # 2,000
)
evaluator.create()  # 建立 AnonymeterEvaluator 實例

# Linkability 風險
evaluator = Evaluator(
    method='anonymeter-linkability',
    aux_cols=[['public'], ['private']]
)
evaluator.create()  # 建立 AnonymeterEvaluator 實例

# Inference 風險
evaluator = Evaluator(
    method='anonymeter-inference',
    secret='sensitive_column'
)
evaluator.create()  # 建立 AnonymeterEvaluator 實例
```

### 資料品質評估

```python
# Diagnostic Report
evaluator = Evaluator('sdmetrics-diagnosticreport')
evaluator.create()  # 建立 SDMetricsEvaluator 實例

# Quality Report
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()  # 建立 SDMetricsEvaluator 實例
```

### 機器學習效用評估

```python
# 新版 MLUtility
evaluator = Evaluator(
    method='mlutility',
    task_type='classification',
    target='label'
)
evaluator.create()  # 建立 MLUtilityV2Evaluator 實例

# 舊版 MLUtility
evaluator = Evaluator(
    method='mlutility-classification',
    target='label'
)
evaluator.create()  # 建立 MLUtilityEvaluator 實例
```

### 統計評估

```python
evaluator = Evaluator(
    method='stats',
    stats_method=['mean', 'std']
)
evaluator.create()  # 建立 StatsEvaluator 實例
```

### 自訂評估器

```python
evaluator = Evaluator(
    method='custom_method',
    module_path='/path/to/evaluator.py',
    class_name='MyEvaluator'
)
evaluator.create()  # 載入並建立自訂評估器實例
```

## 錯誤處理

### 未知的評估方法

```python
try:
    evaluator = Evaluator('unknown-method')
    evaluator.create()
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Unknown evaluation method: unknown-method
```

### 缺少必要參數

```python
try:
    # Inference 需要 secret 參數
    evaluator = Evaluator('anonymeter-inference')
    evaluator.create()
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Missing required parameter: secret
```

### 自訂評估器載入失敗

```python
try:
    evaluator = Evaluator(
        method='custom_method',
        module_path='/invalid/path.py',
        class_name='NonExistent'
    )
    evaluator.create()
except ImportError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Failed to load custom evaluator
```

## 內部運作

`create()` 方法的內部運作流程：

1. **方法驗證**：檢查 `method` 是否為支援的評估方法
2. **參數驗證**：確認所有必要參數都已提供
3. **實例建立**：根據方法類型建立對應的評估器子類別
4. **配置初始化**：將參數傳遞給子類別進行初始化
5. **狀態設定**：標記評估器為就緒狀態

## 注意事項

- 必須在 `__init__()` 之後呼叫
- 必須在 `eval()` 之前呼叫
- 只需呼叫一次，重複呼叫不會有額外效果
- 如果初始化參數有誤，會在此階段拋出例外
- 自訂評估器會在此階段載入外部模組