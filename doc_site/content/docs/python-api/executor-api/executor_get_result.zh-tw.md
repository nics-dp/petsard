---
title: "get_result()"
weight: 52
---

取得實驗管線的執行結果。

## 語法

```python
def get_result() -> dict
```

## 參數

無

## 返回值

- **dict**
    - 包含所有實驗結果的字典
    - 鍵為完整的實驗名稱組合
    - 值為對應的執行結果

## 說明

`get_result()` 方法用於取得執行完成後的結果。必須在 `run()` 完成後呼叫此方法。

結果字典的鍵格式為：`Module1[experiment1]_Module2[experiment2]_...`，包含完整的模組執行路徑。

## 基本範例

```python
from petsard import Executor

# 執行工作流程
exec = Executor('config.yaml')
exec.run()

# 取得結果
results = exec.get_result()

# 檢視結果
print(f"共產生 {len(results)} 組結果")
for exp_name, result in results.items():
    print(f"\n實驗：{exp_name}")
    print(f"結果類型：{type(result)}")
```

## 進階範例

### 單一實驗結果

```python
from petsard import Executor

# YAML 配置包含單一實驗路徑
exec = Executor('single_experiment.yaml')
exec.run()

results = exec.get_result()

# 取得唯一的結果
experiment_name = list(results.keys())[0]
result = results[experiment_name]

print(f"實驗名稱：{experiment_name}")
print(f"結果內容：{result.keys() if isinstance(result, dict) else type(result)}")
```

### 多實驗結果處理

```python
from petsard import Executor
import pandas as pd

# YAML 配置包含多個實驗組合
exec = Executor('multi_experiment.yaml')
exec.run()

results = exec.get_result()

# 分析每組實驗結果
for exp_name, result in results.items():
    print(f"\n處理實驗：{exp_name}")
    
    # 根據結果類型處理
    if isinstance(result, dict):
        if 'data' in result:
            data = result['data']
            if isinstance(data, pd.DataFrame):
                print(f"  資料形狀：{data.shape}")
        if 'schema' in result:
            print(f"  Schema ID：{result['schema'].id}")
    elif isinstance(result, pd.DataFrame):
        print(f"  DataFrame 形狀：{result.shape}")
```

### 提取特定模組結果

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

results = exec.get_result()

# 篩選包含特定模組的結果
synthesizer_results = {
    name: result 
    for name, result in results.items() 
    if 'Synthesizer' in name
}

print(f"Synthesizer 相關結果數量：{len(synthesizer_results)}")

# 或使用 Reporter 的特定實驗結果
reporter_results = {
    name: result 
    for name, result in results.items() 
    if 'Reporter[save_data]' in name
}
```

### 結果格式範例

不同最終模組的結果格式：

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

results = exec.get_result()

for exp_name, result in results.items():
    # Reporter 模組結果
    if 'Reporter' in exp_name:
        # 通常是 dict，包含來源模組的資料
        print(f"{exp_name}:")
        print(f"  類型：{type(result)}")
        if isinstance(result, dict):
            print(f"  鍵：{result.keys()}")
    
    # Evaluator 模組結果
    elif 'Evaluator' in exp_name:
        # 通常是 dict，包含評測報告
        print(f"{exp_name}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}：{type(value)}")
```

## 結果結構

### Synthesizer 結尾

當管線以 Synthesizer 結束時：

```python
{
    'Loader[load_data]_Synthesizer[generate]': {
        'data': pd.DataFrame,  # 合成資料
        'schema': Schema       # Schema 物件
    }
}
```

### Evaluator 結尾

當管線以 Evaluator 結束時：

```python
{
    'Loader[load_data]_Synthesizer[generate]_Evaluator[evaluate]': {
        'global': pd.DataFrame,      # 整體評測結果
        'columnwise': pd.DataFrame,  # 欄位評測結果（若有）
        'pairwise': pd.DataFrame     # 配對評測結果（若有）
    }
}
```

### Reporter 結尾

當管線以 Reporter 結束時：

```python
{
    'Loader[load_data]_Synthesizer[generate]_Reporter[save_data]': {
        'data': pd.DataFrame,  # 儲存的資料
        'schema': Schema,      # Schema 物件
        'filepath': str        # 儲存路徑
    }
}
```

## 注意事項

- **執行狀態**：建議先使用 `is_execution_completed()` 確認執行完成
- **結果格式**：結果格式取決於管線的最終模組
- **記憶體使用**：結果儲存在記憶體中，大型資料集請注意記憶體用量
- **實驗名稱**：實驗名稱包含完整的模組執行路徑
- **空結果**：若 `run()` 未執行或執行失敗，結果字典可能為空
- **嵌套結構**：多實驗配置會產生多組結果，每組獨立儲存
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API