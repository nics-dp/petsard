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

## 基本範例

```python
from petsard import Evaluator

# 初始化評估器
evaluator = Evaluator('sdmetrics-qualityreport')

# 建立內部實例
evaluator.create()

# 現在可以使用 eval() 方法
result = evaluator.eval(data)
```

## 錯誤處理

### 未知的評估方法

```python
try:
    evaluator = Evaluator('unknown-method')
    evaluator.create()
except ValueError as e:
    print(f"錯誤：{e}")
```

### 缺少必要參數

```python
try:
    # Inference 需要 secret 參數
    evaluator = Evaluator('anonymeter-inference')
    evaluator.create()
except ValueError as e:
    print(f"錯誤：{e}")
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
```

## 內部運作

`create()` 方法的內部運作流程：

1. **方法驗證**：檢查 `method` 是否為支援的評估方法
2. **參數驗證**：確認所有必要參數都已提供
3. **實例建立**：根據方法類型建立對應的評估器子類別
4. **配置初始化**：將參數傳遞給子類別進行初始化
5. **狀態設定**：標記評估器為就緒狀態

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 必須在 `__init__()` 之後呼叫
- 必須在 `eval()` 之前呼叫
- 只需呼叫一次，重複呼叫不會有額外效果
- 如果初始化參數有誤，會在此階段拋出例外
- 自訂評估器會在此階段載入外部模組