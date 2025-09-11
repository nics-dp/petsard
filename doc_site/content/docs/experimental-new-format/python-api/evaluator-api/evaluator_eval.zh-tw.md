---
title: "Evaluator.eval()"
weight: 343
---

執行評估並返回結果。

## 語法

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## 參數

- **data** : dict
    - 評估所需的資料字典
    - 必要的鍵值依評估方法而異：
        - Anonymeter 和 MLUtility：需要 `'ori'`、`'syn'`、`'control'`
        - SDMetrics 和 Stats：需要 `'ori'`、`'syn'`
        - Custom：依自訂評估器的需求

## 返回值

- **dict[str, pd.DataFrame]**
    - 評估結果字典，包含不同粒度的評估結果
    - 常見的鍵值：
        - `'global'`：整體評估結果（單列 DataFrame）
        - `'columnwise'`：欄位層級評估（每列代表一個欄位）
        - `'pairwise'`：欄位對評估（每列代表一對欄位）
        - `'details'`：詳細資訊（格式依方法而異）

## 資料需求

### Anonymeter 評估方法

```python
data = {
    'ori': train_data,      # pd.DataFrame - 原始訓練資料
    'syn': synthetic_data,  # pd.DataFrame - 合成資料
    'control': test_data    # pd.DataFrame - 控制組資料（未用於合成）
}
```

### SDMetrics 評估方法

```python
data = {
    'ori': original_data,   # pd.DataFrame - 原始資料
    'syn': synthetic_data   # pd.DataFrame - 合成資料
}
```

### MLUtility 評估方法

```python
# Dual Model Control 模式（預設）
data = {
    'ori': train_data,      # pd.DataFrame - 原始訓練資料
    'syn': synthetic_data,  # pd.DataFrame - 合成資料
    'control': test_data    # pd.DataFrame - 控制組資料
}

# Domain Transfer 模式
data = {
    'ori': original_data,   # pd.DataFrame - 原始資料
    'syn': synthetic_data   # pd.DataFrame - 合成資料
}
```

### Stats 評估方法

```python
data = {
    'ori': original_data,   # pd.DataFrame - 原始資料
    'syn': synthetic_data   # pd.DataFrame - 合成資料
}
```

## 返回格式詳解

### 返回格式示例

各評估方法返回不同的 DataFrame 結構，通常包含：
- **global**: 整體評估結果
- **columnwise**: 欄位層級結果（部分方法）
- **pairwise**: 欄位對結果（部分方法）
- **details**: 詳細資訊（部分方法）

具體的返回欄位和指標說明請參考 YAML 文件的「評估指標詳解」章節。

## 範例

### 基本使用

```python
from petsard import Evaluator
import pandas as pd

# 準備資料
train_data = pd.read_csv('train.csv')
synthetic_data = pd.read_csv('synthetic.csv')
test_data = pd.read_csv('test.csv')

# 初始化並建立評估器
evaluator = Evaluator('anonymeter-singlingout')
evaluator.create()

# 執行評估
result = evaluator.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})

# 查看結果
print(result['global'])
```

### 多個評估方法

```python
# 隱私風險評估
privacy_eval = Evaluator('anonymeter-singlingout')
privacy_eval.create()
privacy_result = privacy_eval.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})

# 資料品質評估
quality_eval = Evaluator('sdmetrics-qualityreport')
quality_eval.create()
quality_result = quality_eval.eval({
    'ori': train_data,
    'syn': synthetic_data
})

# 機器學習效用評估
utility_eval = Evaluator(
    method='mlutility',
    task_type='classification',
    target='label'
)
utility_eval.create()
utility_result = utility_eval.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})

# 綜合結果
print(f"隱私風險: {privacy_result['global']['risk'].values[0]:.2f}")
print(f"資料品質: {quality_result['global']['Score'].values[0]:.2f}")
print(f"ML效用 (MCC): {utility_result['global'].loc[0, 'syn']:.2f}")
```

### 處理結果

```python
# 執行評估
result = evaluator.eval(data)

# 提取整體分數
global_scores = result['global']

# 如果有欄位層級結果
if 'columnwise' in result:
    column_scores = result['columnwise']
    
    # 找出表現最差的欄位
    worst_column = column_scores.loc[column_scores['score'].idxmin()]
    print(f"表現最差的欄位: {worst_column['column']}")

# 如果有詳細資訊
if 'details' in result:
    details = result['details']
    # 進一步分析...

# 匯出結果
result['global'].to_csv('evaluation_results.csv', index=False)
```

## 錯誤處理

### 缺少必要資料鍵值

```python
try:
    # Anonymeter 需要 control 資料
    result = evaluator.eval({
        'ori': train_data,
        'syn': synthetic_data
        # 缺少 'control'
    })
except KeyError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Missing required data key: 'control'
```

### 資料型別錯誤

```python
try:
    result = evaluator.eval({
        'ori': "not_a_dataframe",  # 錯誤的資料型別
        'syn': synthetic_data
    })
except TypeError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Expected pandas DataFrame, got str
```

### 資料欄位不一致

```python
try:
    # 原始資料和合成資料欄位不同
    result = evaluator.eval({
        'ori': train_data[['col1', 'col2']],
        'syn': synthetic_data[['col1', 'col3']]  # col3 不存在於 ori
    })
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Column mismatch between ori and syn data
```

## 注意事項

- 確保提供的資料符合評估方法的需求
- 資料的欄位必須一致（ori、syn、control）
- 大型資料集可能需要較長的評估時間
- 某些評估方法（如 Anonymeter）需要大量計算資源
- 必須先呼叫 `create()` 方法才能使用 `eval()`
- 返回的 DataFrame 可直接用於後續分析或視覺化