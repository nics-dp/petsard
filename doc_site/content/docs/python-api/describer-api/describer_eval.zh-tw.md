---
title: "eval()"
weight: 2
---

評估資料並產生統計描述或比較結果。

## 語法

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## 參數

- **data** : dict, 必要
    - 輸入資料字典
    - describe 模式：`{"data": pd.DataFrame}`
    - compare 模式（推薦）：`{"base": pd.DataFrame, "target": pd.DataFrame}`
    - compare 模式（向後相容）：`{"ori": pd.DataFrame, "syn": pd.DataFrame}`
    - 根據設定可能支援其他鍵值

## 返回值

- **dict[str, pd.DataFrame]**
    - 包含評估結果的字典
    - 鍵值取決於分析的粒度：
        - `"global"`：整體統計
        - `"columnwise"`：欄位層級統計
        - `"pairwise"`：成對欄位關係（相關性等）

## 說明

`eval()` 方法對提供的資料執行統計評估。行為取決於模式：

- **Describe 模式**：為單一資料集產生全面的統計摘要
- **Compare 模式**：比較多個資料集並計算差異

該方法會根據資料類型和設定自動決定要計算哪些統計量。

## 基本範例

### Describe 模式

```python
from petsard.evaluator import Describer
import pandas as pd

# 建立範例資料
df = pd.DataFrame({
    'numeric': [1, 2, 3, 4, 5],
    'category': ['A', 'B', 'A', 'C', 'B']
})

# 初始化並評估
describer = Describer(method='describe')
describer.create()
results = describer.eval(data={'data': df})

# 存取結果
print(results['global'])      # 整體統計
print(results['columnwise'])  # 每欄統計
```

### Compare 模式（推薦寫法）

```python
from petsard.evaluator import Describer
import pandas as pd

# 建立基準和目標資料
base_df = pd.DataFrame({
    'value': [1, 2, 3, 4, 5],
    'type': ['A', 'B', 'A', 'C', 'B']
})

target_df = pd.DataFrame({
    'value': [1.1, 2.2, 2.9, 4.1, 5.2],
    'type': ['A', 'B', 'A', 'C', 'B']
})

# 初始化比較模式
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)
describer.create()

# 評估比較（推薦使用 base/target）
results = describer.eval(data={'base': base_df, 'target': target_df})

# 存取比較結果
print(results['global'])      # 全域比較分數
print(results['columnwise'])  # 欄位比較
```

### Compare 模式（向後相容）

```python
# 仍支援 ori/syn 命名（但建議使用 base/target）
results = describer.eval(data={'ori': base_df, 'syn': target_df})
```

## 注意事項

- **資料準備**：確保在評估前適當清理資料
- **記憶體使用**：大型資料集在評估期間可能消耗大量記憶體
- **資料類型**：數值和類別欄位會計算不同的統計量
- **缺失值**：NaN 值會根據統計方法自動處理
- **效能**：成對統計（相關性）對寬資料集可能計算成本較高
- **模式一致性**：資料結構必須符合設定的模式（describe vs compare）
- **參數命名**：compare 模式推薦使用 `base`/`target` 取代 `ori`/`syn`