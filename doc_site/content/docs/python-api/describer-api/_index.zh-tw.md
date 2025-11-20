---
title: "Describer API"
type: docs
weight: 1110
---

資料描述模組，提供資料集的統計摘要與洞察分析。

## 類別架構

{{< mermaid-file file="content/docs/python-api/describer-api/describer-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色方塊：主要類別
> - 橘色方塊：實作類別
> - 淺紫色方塊：設定類別
> - `<|--`：繼承關係
> - `*--`：組合關係
> - `..>`：相依關係

## 基本使用

```python
from petsard.evaluator import Describer

# 基本描述
describer = Describer(method='describe')
describer.create()
results = describer.eval(data={'data': df})

# 比較模式
describer = Describer(method='describe', mode='compare')
describer.create()
results = describer.eval(data={'base': df1, 'target': df2})
```

## 建構函式 (__init__)

初始化 Describer 實例以進行資料描述與分析。

### 語法

```python
def __init__(
    method: str,
    mode: str = "describe",
    **kwargs
)
```

### 參數

- **method** : str, 必要
    - 使用的評估方法
    - Describer 通常使用 "describe"
    - 預設值：無預設值，必須指定

- **mode** : str, 選填
    - 描述器的運作模式
    - "describe"：單一資料集描述（預設）
    - "compare"：資料集比較
    - 預設值：`"describe"`

- **\*\*kwargs** : dict, 選填
    - 傳遞給底層評估器的額外參數
    - describe 模式：支援 DescriberDescribe 參數
    - compare 模式：支援 DescriberCompare 參數

### 返回值

- **Describer**
    - 初始化的 Describer 實例

### 使用範例

```python
from petsard.evaluator import Describer

# 基本描述模式
describer = Describer(method='describe')

# 比較模式與額外參數
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)

# 自訂描述方法
describer = Describer(
    method='describe',
    describe_method=['mean', 'median', 'std', 'corr']
)
```

## 注意事項

- **模式選擇**：單一資料集分析選擇 "describe"，比較多個資料集選擇 "compare"
- **參數命名**：compare 模式推薦使用 `base`/`target` 取代舊的 `ori`/`syn`（仍向後相容）
- **方法彈性**：透過 describe_method 參數支援多種統計方法
- **建議使用**：複雜設定建議使用 YAML 配置
- **向後相容**：維持與現有 Evaluator 介面的相容性
- **文件說明**：本文件僅供內部開發團隊參考使用