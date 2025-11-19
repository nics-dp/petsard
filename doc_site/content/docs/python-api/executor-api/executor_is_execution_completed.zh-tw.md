---
title: "is_execution_completed()"
weight: 54
---

檢查執行工作流程是否已完成。

## 語法

```python
def is_execution_completed() -> bool
```

## 參數

無

## 返回值

- **bool**
    - `True`：執行已完成
    - `False`：執行尚未完成或未執行

## 說明

`is_execution_completed()` 方法用於檢查 `run()` 是否已成功執行完畢。

此方法在以下情況下返回 `True`：
- `run()` 方法已被呼叫且成功執行完所有模組

此方法在以下情況下返回 `False`：
- `run()` 尚未被呼叫
- `run()` 正在執行中
- `run()` 執行過程中發生錯誤

{{< callout type="info" >}}
**版本變更**：此方法將在 v2.0.0 被棄用。未來版本的 `run()` 方法將直接返回執行狀態（success/failed），使此方法變得多餘。
{{< /callout >}}

## 基本範例

```python
from petsard import Executor

exec = Executor('config.yaml')

# 執行前檢查
print(f"執行前：{exec.is_execution_completed()}")  # False

# 執行工作流程
exec.run()

# 執行後檢查
print(f"執行後：{exec.is_execution_completed()}")  # True

# 根據狀態取得結果
if exec.is_execution_completed():
    results = exec.get_result()
    print(f"成功取得 {len(results)} 組結果")
```

## 進階範例

### 安全的結果取得

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 確認執行完成後才取得結果
if exec.is_execution_completed():
    results = exec.get_result()
    timing = exec.get_timing()

    print("執行完成，結果已取得")
    print(f"結果數量：{len(results)}")
    print(f"執行時間：{timing['duration_seconds'].sum():.2f} 秒")
else:
    print("執行未完成，無法取得結果")
```

### 錯誤處理流程

```python
from petsard import Executor
from petsard.exceptions import ConfigError

try:
    exec = Executor('config.yaml')
    exec.run()

    if exec.is_execution_completed():
        print("✓ 執行成功")
        results = exec.get_result()
    else:
        print("✗ 執行未完成")

except ConfigError as e:
    print(f"✗ 配置錯誤：{e}")
except Exception as e:
    print(f"✗ 執行錯誤：{e}")
```

### 條件式後續處理

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 根據執行狀態決定後續操作
if exec.is_execution_completed():
    # 成功：處理結果
    results = exec.get_result()

    # 儲存結果
    for exp_name, result in results.items():
        print(f"處理實驗：{exp_name}")
        if isinstance(result, dict) and 'data' in result:
            result['data'].to_csv(f"{exp_name}_output.csv", index=False)

    print("所有結果已儲存")
else:
    # 失敗：記錄錯誤
    print("執行失敗，請檢查日誌")
    print("日誌位置：./PETsARD_*.log")
```

### 在測試中使用

```python
from petsard import Executor
import unittest

class TestExecutor(unittest.TestCase):
    def test_execution_completion(self):
        """測試執行完成狀態"""
        exec = Executor('test_config.yaml')

        # 執行前應為 False
        self.assertFalse(exec.is_execution_completed())

        # 執行工作流程
        exec.run()

        # 執行後應為 True
        self.assertTrue(exec.is_execution_completed())

        # 應該能取得結果
        results = exec.get_result()
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
```

### 長時間執行的監控

```python
from petsard import Executor
import time
import threading

def monitor_execution(exec, check_interval=5):
    """監控執行狀態"""
    while not exec.is_execution_completed():
        print(f"執行中... (已等待 {check_interval} 秒)")
        time.sleep(check_interval)
    print("執行完成！")

# 建立執行器
exec = Executor('long_running_config.yaml')

# 在另一個線程中監控
monitor_thread = threading.Thread(
    target=monitor_execution, 
    args=(exec, 10)
)
monitor_thread.start()

# 執行工作流程
exec.run()

# 等待監控線程結束
monitor_thread.join()

# 取得結果
if exec.is_execution_completed():
    results = exec.get_result()
```

## 使用場景

### 1. 結果取得前驗證

在取得結果前確認執行完成：

```python
if exec.is_execution_completed():
    results = exec.get_result()
```

### 2. 錯誤處理

區分執行失敗和未執行：

```python
if not exec.is_execution_completed():
    print("執行未完成，請檢查錯誤")
```

### 3. 條件式處理

根據執行狀態執行不同邏輯：

```python
if exec.is_execution_completed():
    # 成功路徑
    process_results(exec.get_result())
else:
    # 失敗路徑
    handle_failure()
```

### 4. 測試驗證

在測試中驗證執行完成：

```python
self.assertTrue(exec.is_execution_completed())
```

## 注意事項

- **執行順序**：必須在 `run()` 之後呼叫才有意義
- **錯誤狀態**：執行過程中發生錯誤會導致返回 `False`
- **多次執行**：每個 Executor 實例只應執行一次 `run()`
- **版本變更**：v2.0.0 起此方法將被棄用，改用 `run()` 的返回值
- **狀態持續**：狀態在 Executor 實例的生命週期內持續
- **線程安全**：此方法不保證線程安全
- **建議作法**：在取得結果前始終檢查執行狀態