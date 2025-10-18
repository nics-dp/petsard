---
title: "run()"
weight: 51
---

執行完整的實驗管線工作流程。

## 語法

```python
def run() -> None
```

## 參數

無

## 返回值

無

## 說明

`run()` 方法根據配置檔案執行完整的實驗管線。必須在 `__init__()` 之後呼叫此方法。

此方法會按順序執行以下操作：
1. 從 Config 取得模組執行序列
2. 依序執行每個模組的 Adapter
3. 透過 Status 記錄執行結果和狀態
4. 在 Loader/Splitter 執行後推論 Preprocessor Schema
5. 收集最終結果到 result 屬性

執行順序：
- Loader（資料載入）
- Preprocessor（資料前處理，選填）
- Splitter（資料分割，選填）
- Synthesizer（資料合成）
- Postprocessor（資料後處理，選填）
- Constrainer（約束條件，選填）
- Evaluator（資料評測，選填）
- Reporter（結果報告，選填）

## 基本範例

```python
from petsard import Executor

# 初始化執行器
exec = Executor('config.yaml')

# 執行工作流程
exec.run()

# 檢查執行完成
if exec.is_execution_completed():
    print("執行完成")
```

## 進階範例

### 完整工作流程

```python
from petsard import Executor
import time

# 記錄開始時間
start_time = time.time()

# 初始化並執行
exec = Executor('config.yaml')
exec.run()

# 計算執行時間
elapsed_time = time.time() - start_time
print(f"總執行時間：{elapsed_time:.2f} 秒")

# 取得詳細時間報告
timing_df = exec.get_timing()
print("\n各模組執行時間：")
print(timing_df)

# 取得結果
if exec.is_execution_completed():
    results = exec.get_result()
    print(f"\n共產生 {len(results)} 組結果")
```

### 錯誤處理

```python
from petsard import Executor
from petsard.exceptions import ConfigError

try:
    exec = Executor('config.yaml')
    exec.run()
    
    if exec.is_execution_completed():
        results = exec.get_result()
        print("執行成功")
    else:
        print("執行未完成")
        
except ConfigError as e:
    print(f"配置錯誤：{e}")
except Exception as e:
    print(f"執行錯誤：{e}")
```

### 多實驗配置

```python
from petsard import Executor

# 配置包含多個實驗組合
exec = Executor('multi_experiment.yaml')

print("開始執行多實驗配置")
exec.run()

# 取得所有實驗結果
results = exec.get_result()

print(f"\n實驗組合數量：{len(results)}")
for experiment_name in results.keys():
    print(f"- {experiment_name}")

# 取得執行時間
timing_df = exec.get_timing()
total_time = timing_df['duration_seconds'].sum()
print(f"\n總執行時間：{total_time:.2f} 秒")
```

## 執行狀態追蹤

執行過程中，Status 會自動記錄：

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 取得狀態摘要
summary = exec.status.get_status_summary()
print(f"執行序列：{summary['sequence']}")
print(f"活躍模組：{summary['active_modules']}")
print(f"總快照數：{summary['total_snapshots']}")

# 取得快照歷史
snapshots = exec.status.get_snapshots()
for snapshot in snapshots:
    print(f"{snapshot.module_name}[{snapshot.experiment_name}] at {snapshot.timestamp}")
```

## 注意事項

- **單次執行**：每個 Executor 實例只應呼叫一次 `run()`
- **阻塞操作**：`run()` 是同步阻塞操作，會等待所有模組執行完畢
- **錯誤中斷**：若任何模組執行失敗，整個工作流程會中斷
- **記憶體使用**：大型資料集或複雜工作流程可能需要較多記憶體
- **日誌記錄**：執行過程會產生詳細日誌，可透過 Executor 配置控制
- **返回值變更**：v2.0.0 起 `run()` 將返回執行狀態（success/failed），目前版本返回 None
- **狀態檢查**：使用 `is_execution_completed()` 檢查執行是否完成
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API