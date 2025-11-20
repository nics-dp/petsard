---
title: "自訂評測方法"
type: docs
weight: 695
prev: docs/petsard-yaml/evaluator-yaml/utility
next: docs/petsard-yaml/evaluator-yaml/privacy-mpuccs
---

要建立自己的評測器，需要實作一個含有必要屬性和方法的 Python 類別，並設定 YAML 檔案來使用它。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/custom-evaluation.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Evaluator:
  your-custom-evaluator:
    method: custom_method
    module_path: custom-evaluation.py  # Python 檔案名稱
    class_name: MyEvaluator_Pushover   # 檔案中的類別名稱
```

## 必要實作

您的 Python 類別必須包含：

```python
class YourEvaluator:
    # 必要屬性
    REQUIRED_INPUT_KEYS = ['ori', 'syn']  # 或 ['ori', 'syn', 'control']
    AVAILABLE_SCORES_GRANULARITY = ['global', 'columnwise', 'pairwise', 'details']

    def __init__(self, config):
        """初始化評測器"""
        self.config = config

    def eval(self, data: dict) -> dict:
        """執行評測並回傳結果"""
        # data 包含 'ori', 'syn', 可能有 'control'
        # 回傳 dict[str, pd.DataFrame]
        return results
```

## 參數說明

| 參數 | 類型 | 必要性 | 說明 |
|-----|------|--------|------|
| **method** | `string` | 必要 | 固定值：`custom_method` |
| **module_path** | `string` | 必要 | Python 檔案路徑（相對於專案根目錄） |
| **class_name** | `string` | 必要 | 類別名稱（必須存在於指定檔案中） |
| **其他參數** | `any` | 選用 | 傳遞給評測器 `__init__` 的自訂參數 |

## 實作範例：Pushover 評測器

我們的範例 `custom-evaluation.py` 實作了一個示範用評測器，它會：
1. **接收資料**：在 `eval()` 時接收原始、合成和控制資料
2. **計算評分**：對所有粒度回傳固定分數（用於測試）
3. **回傳結果**：提供 global、columnwise、pairwise 和 details 結果

## 關鍵概念

### REQUIRED_INPUT_KEYS
- `['ori', 'syn']`：基本配置，需要原始和合成資料
- `['ori', 'syn', 'control']`：進階配置，額外需要控制組資料

### AVAILABLE_SCORES_GRANULARITY
定義評測器回傳的結果粒度：
- `global`：整體評分（單行 DataFrame）
- `columnwise`：每欄位評分（索引為欄位名稱）
- `pairwise`：欄位對評分（MultiIndex 索引）
- `details`：自訂詳細資訊

### 回傳格式要求
- 每個粒度都必須回傳 `pd.DataFrame`
- `columnwise` 必須包含所有欄位
- `pairwise` 必須包含所有欄位對
- 索引必須符合預期格式

## 適用情境

- **領域特定評測**：醫療、金融等特定領域的評測需求
- **整合外部工具**：使用現有的評測函式庫
- **新演算法實作**：實作研究中的新評測方法
- **客製化流程**：符合組織特定需求的評測

## 注意事項

{{< callout type="warning" >}}
**路徑設定重要提示**
- 如果 Python 檔案與 YAML 檔案在同目錄：使用檔名即可（如 `custom-evaluation.py`）
- 如果從其他目錄執行：使用相對路徑（如 `petsard-yaml/evaluator-yaml/custom-evaluation.py`）
- 路徑是相對於執行 PETsARD 的工作目錄
{{< /callout >}}

{{< callout type="info" >}}
評測器可以選擇性地繼承 `BaseEvaluator`，但並非必要。關鍵是實作必要的屬性和方法。
{{< /callout >}}