---
title: "Evaluator API"
weight: 350
---

合成資料品質評測模組，提供隱私風險度量、資料品質評測及機器學習效用分析。

## 類別架構

{{< mermaid-file file="content/docs/python-api/evaluator-api/evaluator-class-diagram.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 橘色框：子類別實作
> - 淺紫框：配置與資料類別
> - 淺綠框：輸入資料
> - `<|--`：繼承關係 (inheritance)
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)
> - `-->`：資料流向

## 基本使用

```python
from petsard import Evaluator

# 隱私風險評測
evaluator = Evaluator('anonymeter-singlingout')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
privacy_risk = eval_result['global']

# 資料品質評測
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data
})
quality_score = eval_result['global']

# 機器學習效用評測（新版）
evaluator = Evaluator('mlutility', task_type='classification', target='income')
evaluator.create()
eval_result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
ml_utility = eval_result['global']
```

## 建構函式 (__init__)

初始化評測器實例。

### 語法

```python
def __init__(
    method: str,
    **kwargs
)
```

### 參數

- **method** : str, required
    - 評測方法名稱
    - 必要參數
    - 支援的方法：
        - **隱私風險評測**：
            - `'anonymeter-singlingout'`：指認性風險
            - `'anonymeter-linkability'`：連結性風險
            - `'anonymeter-inference'`：推斷性風險
        - **資料品質評測**：
            - `'sdmetrics-diagnosticreport'`：資料診斷報告
            - `'sdmetrics-qualityreport'`：資料品質報告
        - **機器學習效用評測（舊版）**：
            - `'mlutility-classification'`：分類效用（多模型）
            - `'mlutility-regression'`：迴歸效用（多模型）
            - `'mlutility-cluster'`：聚類效用（K-means）
        - **機器學習效用評測（新版，推薦）**：
            - `'mlutility'`：統一介面（需搭配 task_type 參數）
        - **統計評測**：
            - `'stats'`：統計差異比較
        - **預設方法**：
            - `'default'`：使用 sdmetrics-qualityreport
        - **自訂方法**：
            - `'custom_method'`：自訂評測器

- **kwargs** : dict, optional
    - 傳遞給特定評測器的額外參數
    - 根據評測方法不同，可能包含：
        - **MLUtility 參數**：
            - `task_type`：任務類型 ('classification', 'regression', 'clustering')
            - `target`：目標欄位名稱
            - `experiment_design`：實驗設計方式
            - `resampling`：不平衡資料處理方法
        - **Anonymeter 參數**：
            - `n_attacks`：攻擊嘗試次數
            - `n_cols`：每次查詢使用的欄位數
            - `secret`：要被推斷的欄位（推斷性風險）
            - `aux_cols`：輔助資訊欄位（連結性風險）
        - **自訂方法參數**：
            - `module_path`：自訂模組路徑
            - `class_name`：自訂類別名稱

### 返回值

- **Evaluator**
    - 初始化後的評測器實例

### 使用範例

```python
from petsard import Evaluator

# 預設評測
evaluator = Evaluator('default')
evaluator.create()
eval_result = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

## 支援的評測類型

請參閱 PETsARD YAML 文件以了解詳情。

## 注意事項

- **方法選擇**：選擇適合您需求的評測方法，不同方法關注不同面向
- **資料需求**：不同評測方法需要不同的輸入資料組合
    - Anonymeter 和 MLUtility：需要 ori、syn、control 三組資料
    - SDMetrics 和 Stats：只需要 ori 和 syn 兩組資料
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **方法調用順序**：必須先呼叫 `create()` 再呼叫 `eval()`
- **MLUtility 版本**：建議使用新版 MLUtility（搭配 task_type）而非舊版分離介面
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容