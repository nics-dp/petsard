---
title: "eval"
weight: 383
---

執行評估並返回結果。

## 語法

```python
def eval(data: dict) -> dict[str, pd.DataFrame]
```

## 參數

- **data** : dict
    - 評估所需的資料字典
    - 必要的鍵值依評估方法而異
    - 詳細的資料需求請參考 YAML 配置文件中的 Evaluator 章節

## 返回值

- **dict[str, pd.DataFrame]**
    - 評估結果字典，包含不同粒度的評估結果
    - 返回格式依評估方法而異，請參考 YAML 配置文件中的評估指標詳解

## 基本範例

```python
from petsard import Evaluator

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

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 確保提供的資料符合評估方法的需求
- 資料的欄位必須一致（ori、syn、control）
- 必須先呼叫 `create()` 方法才能使用 `eval()`
- 返回的 DataFrame 可直接用於後續分析或視覺化