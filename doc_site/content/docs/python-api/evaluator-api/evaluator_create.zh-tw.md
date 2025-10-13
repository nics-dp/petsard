---
title: "create()"
weight: 341
---

初始化評測器實例並準備進行評測。

## 語法

```python
def create() -> None
```

## 參數

無

## 返回值

無

## 說明

`create()` 方法用於初始化評測器實例。必須在 `__init__()` 之後、`eval()` 之前呼叫此方法。

此方法會根據初始化時指定的評測方法，執行以下操作：
1. 載入對應的評測模組
2. 設定評測參數
3. 初始化評測器
4. 準備評測環境

不同的評測方法會執行不同的初始化操作：
- **Anonymeter**：初始化隱私風險評測器
- **SDMetrics**：初始化資料品質評測器
- **MLUtility**：初始化機器學習效用評測器
- **Stats**：初始化統計評測器
- **Custom**：載入並初始化自訂評測器

## 基本範例

```python
from petsard import Evaluator

# 初始化隱私風險評測器
evaluator = Evaluator('anonymeter-singlingout')
evaluator.create()  # 初始化評測器

# 初始化資料品質評測器
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()  # 初始化評測器

# 初始化機器學習效用評測器
evaluator = Evaluator(
    'mlutility',
    task_type='classification',
    target='income'
)
evaluator.create()  # 初始化評測器
```

## 注意事項

- **必要步驟**：必須在 `eval()` 之前呼叫此方法
- **單次呼叫**：每個評測器實例只需呼叫一次 `create()`
- **參數設定**：所有評測參數必須在 `__init__()` 時設定，`create()` 不接受參數
- **錯誤處理**：若評測方法不存在或參數錯誤，會在此階段拋出異常
- **資源初始化**：某些評測器可能會在此階段載入模型或分配資源
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API