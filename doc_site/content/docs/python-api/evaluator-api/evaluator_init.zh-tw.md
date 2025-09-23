---
title: "init"
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
    - 支援的方法請參考 YAML 配置文件中的 Evaluator 章節

- **kwargs** : dict
    - 依據不同評估方法的額外參數
    - 各方法的詳細參數請參考 YAML 配置文件中的 Evaluator 章節

## 返回值

- **Evaluator**
    - 初始化後的評估器實例

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
- 不同評估方法需要不同的參數配置，請參考 YAML 配置文件中的 Evaluator 章節
- 初始化後必須呼叫 `create()` 方法才能使用 `eval()`
- 本段文件僅供開發團隊內部參考，不保證向後相容