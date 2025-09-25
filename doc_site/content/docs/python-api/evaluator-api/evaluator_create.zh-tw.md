---
title: "create"
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

此方法會根據初始化時指定的 `method` 參數，建立對應的評估器子類別實例。

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

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 必須在 `__init__()` 之後呼叫
- 必須在 `eval()` 之前呼叫
- 只需呼叫一次，重複呼叫不會有額外效果
- 如果初始化參數有誤，會在此階段拋出例外
- 自訂評估器會在此階段載入外部模組