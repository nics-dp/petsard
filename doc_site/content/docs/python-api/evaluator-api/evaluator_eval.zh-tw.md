---
title: "eval()"
weight: 342
---

執行資料評測並返回評測結果。

## 語法

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## 參數

- **data** : dict, required
    - 評測用資料字典
    - 根據評測方法不同，需要不同的資料組合：
        - **Anonymeter 與 MLUtility**：
            - `'ori'`：用於合成的原始資料 (`pd.DataFrame`)
            - `'syn'`：合成資料 (`pd.DataFrame`)
            - `'control'`：未用於合成的對照資料 (`pd.DataFrame`)
        - **SDMetrics 與 Stats**：
            - `'ori'`：原始資料 (`pd.DataFrame`)
            - `'syn'`：合成資料 (`pd.DataFrame`)

## 返回值

- **dict[str, pd.DataFrame]**
    - 評測結果字典，根據評測方法不同包含不同的鍵值：
        - `'global'`：整體資料集評測結果（單列 DataFrame）
        - `'columnwise'`：各欄位評測結果（每列代表一個欄位）
        - `'pairwise'`：欄位對評測結果（每列代表一組欄位配對）
        - `'details'`：其他細節資訊

## 說明

`eval()` 方法用於執行實際的評測作業。必須在 `create()` 之後呼叫此方法。

不同評測方法的返回結果：

### 隱私風險評測 (Anonymeter)

返回包含風險分數與信賴區間的評測結果：
- `'risk'`：隱私風險分數 (0-1)
- `'risk_CI_btm'`：風險信賴區間下界
- `'risk_CI_top'`：風險信賴區間上界
- `'attack_rate'`：主要攻擊成功率
- `'baseline_rate'`：基線攻擊成功率
- `'control_rate'`：控制組攻擊成功率

### 資料品質評測 (SDMetrics)

**診斷報告**返回：
- `'Score'`：整體診斷分數
- `'Data Validity'`：資料效度分數
- `'Data Structure'`：資料結構分數

**品質報告**返回：
- `'Score'`：整體品質分數
- `'Column Shapes'`：欄位分布相似度
- `'Column Pair Trends'`：欄位關係保持度

### 機器學習效用評測 (MLUtility)

返回模型效能比較結果：
- **雙模型控制組模式**：
    - `'ori_score'`：原始資料模型分數
    - `'syn_score'`：合成資料模型分數
    - `'difference'`：分數差異
    - `'ratio'`：分數比率
- **領域遷移模式**：
    - `'syn_to_ori_score'`：合成資料模型在原始資料上的分數

### 統計評測 (Stats)

返回統計量比較結果：
- 各欄位的統計量（原始與合成）
- 兩者差異或百分比變化
- 整體分數

## 範例

```python
from petsard import Evaluator
import pandas as pd

# 準備資料
ori_data = pd.read_csv('original.csv')
syn_data = pd.read_csv('synthetic.csv')

# 預設評測
evaluator = Evaluator('default')
evaluator.create()
eval_result = evaluator.eval({
    'ori': ori_data,
    'syn': syn_data
})

# 檢視結果
print(f"評測分數: {eval_result['global']['Score'].values[0]:.4f}")
```

## 注意事項

- **資料需求**：確保提供的資料符合評測方法的需求
- **資料格式**：所有資料必須是 `pd.DataFrame` 格式
- **欄位一致性**：ori、syn、control 資料應有相同的欄位結構
- **缺失值處理**：某些評測方法會自動處理缺失值，請參閱具體方法說明
- **記憶體使用**：大型資料集可能需要較多記憶體，建議分批處理
- **執行時間**：隱私風險評測和機器學習效用評測可能需要較長執行時間
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API