---
title: "get_timing()"
weight: 53
---

取得所有模組的執行時間記錄。

## 語法

```python
def get_timing() -> pd.DataFrame
```

## 參數

無

## 返回值

- **pd.DataFrame**
    - 包含時間資訊的 DataFrame
    - 每列代表一個執行步驟的時間記錄

## 說明

`get_timing()` 方法用於取得詳細的執行時間報告。必須在 `run()` 完成後呼叫此方法。

返回的 DataFrame 包含以下欄位：
- `record_id`：唯一的時間記錄識別碼
- `module_name`：執行的模組名稱
- `experiment_name`：實驗配置名稱
- `step_name`：執行步驟名稱（如 'run', 'fit', 'sample'）
- `start_time`：執行開始時間（ISO 格式）
- `end_time`：執行結束時間（ISO 格式）
- `duration_seconds`：執行持續時間（秒，預設四捨五入至 2 位小數）
- `duration_precision`：duration_seconds 的小數位數精度（預設：2）
- 其他來自執行上下文的欄位

## 基本範例

```python
from petsard import Executor

# 執行工作流程
exec = Executor('config.yaml')
exec.run()

# 取得時間報告
timing_df = exec.get_timing()

# 檢視報告
print(timing_df)
print(f"\n總執行時間：{timing_df['duration_seconds'].sum():.2f} 秒")
```

## 進階範例

### 分析各模組執行時間

```python
from petsard import Executor
import pandas as pd

exec = Executor('config.yaml')
exec.run()

timing_df = exec.get_timing()

# 按模組統計執行時間
module_timing = timing_df.groupby('module_name')['duration_seconds'].agg([
    ('total_time', 'sum'),
    ('count', 'count'),
    ('avg_time', 'mean')
])

print("各模組執行時間統計：")
print(module_timing.sort_values('total_time', ascending=False))
```

### 識別效能瓶頸

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

timing_df = exec.get_timing()

# 找出最耗時的步驟
slowest_steps = timing_df.nlargest(5, 'duration_seconds')[
    ['module_name', 'experiment_name', 'step_name', 'duration_seconds']
]

print("最耗時的 5 個步驟：")
print(slowest_steps)
```

### 比較實驗組合的執行時間

```python
from petsard import Executor

exec = Executor('multi_experiment.yaml')
exec.run()

timing_df = exec.get_timing()

# 按實驗組合分組
experiment_timing = timing_df.groupby('experiment_name')['duration_seconds'].sum()

print("各實驗組合執行時間：")
print(experiment_timing.sort_values(ascending=False))
```

### 視覺化執行時間

```python
from petsard import Executor
import matplotlib.pyplot as plt

exec = Executor('config.yaml')
exec.run()

timing_df = exec.get_timing()

# 繪製各模組執行時間長條圖
module_times = timing_df.groupby('module_name')['duration_seconds'].sum()

plt.figure(figsize=(10, 6))
module_times.plot(kind='bar')
plt.title('各模組執行時間')
plt.xlabel('模組名稱')
plt.ylabel('執行時間（秒）')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('timing_report.png')
```

### 詳細時間分析

```python
from petsard import Executor
import pandas as pd

exec = Executor('config.yaml')
exec.run()

timing_df = exec.get_timing()

# 分析各步驟類型的時間分布
step_analysis = timing_df.groupby('step_name')['duration_seconds'].describe()

print("各步驟類型時間統計：")
print(step_analysis)

# 計算各模組佔總時間的百分比
total_time = timing_df['duration_seconds'].sum()
timing_df['time_percentage'] = (
    timing_df['duration_seconds'] / total_time * 100
)

print("\n各記錄佔總時間百分比：")
print(timing_df[['module_name', 'step_name', 'duration_seconds', 'time_percentage']])
```

### 輸出時間報告

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

timing_df = exec.get_timing()

# 儲存為 CSV
timing_df.to_csv('timing_report.csv', index=False)

# 產生摘要報告
summary = f"""
執行時間報告
{'='*50}
總執行時間：{timing_df['duration_seconds'].sum():.2f} 秒
總記錄數：{len(timing_df)}
模組數：{timing_df['module_name'].nunique()}
實驗數：{timing_df['experiment_name'].nunique()}

最快步驟：{timing_df.loc[timing_df['duration_seconds'].idxmin(), 'step_name']} ({timing_df['duration_seconds'].min():.2f}s)
最慢步驟：{timing_df.loc[timing_df['duration_seconds'].idxmax(), 'step_name']} ({timing_df['duration_seconds'].max():.2f}s)
平均執行時間：{timing_df['duration_seconds'].mean():.2f} 秒
"""

print(summary)

# 儲存摘要
with open('timing_summary.txt', 'w') as f:
    f.write(summary)
```

## DataFrame 欄位說明

### 基本欄位

- **record_id** (str)：唯一的記錄識別碼
- **module_name** (str)：模組名稱（如 'Loader', 'Synthesizer'）
- **experiment_name** (str)：實驗名稱（從 YAML 配置）
- **step_name** (str)：執行步驟（如 'run', 'fit', 'sample', 'eval'）

### 時間欄位

- **start_time** (str)：開始時間（ISO 8601 格式）
- **end_time** (str)：結束時間（ISO 8601 格式）
- **duration_seconds** (float)：持續時間（秒）
- **duration_precision** (int)：小數位數精度

### 上下文欄位

可能包含其他執行上下文相關的欄位，依模組而定。

## 注意事項

- **執行完成**：必須在 `run()` 完成後才能取得完整的時間報告
- **精度設定**：預設時間精度為 2 位小數，可透過 Status 配置調整
- **記錄粒度**：每個模組的主要步驟都會被記錄
- **多實驗**：多實驗配置會產生多組時間記錄
- **分析用途**：適合用於效能分析和瓶頸識別
- **儲存建議**：建議將時間報告儲存為檔案以供後續分析
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API