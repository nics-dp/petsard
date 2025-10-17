---
title: "create()"
weight: 362
---

處理報告資料並返回準備用於輸出的處理後資料。

## 語法

```python
def create(data: dict) -> dict | pd.DataFrame | None
```

## 參數

- **data** : dict, required
    - 報告資料字典
    - 鍵值對結構：
        - **鍵**：實驗元組 `(模組名稱, 實驗名稱, ...)`
        - **值**：要報告的資料 (`pd.DataFrame` 或 `None`)
    - 特殊鍵：
        - `'exist_report'`：用於合併先前結果（dict 格式）
        - `'timing_data'`：用於 save_timing 模式的時間資料

## 返回值

- **dict | pd.DataFrame | None**
    - 返回類型取決於報告器模式：
        - **save_data 模式**：返回處理後的 DataFrame 字典 `{expt_name: DataFrame}`
        - **save_report 模式**：返回包含粒度特定結果的字典 `{'Reporter': {...}}`
        - **save_timing 模式**：返回包含時間資訊的 DataFrame
        - **save_validation 模式**：返回驗證結果字典
        - **無資料處理時**：返回 `None` 或空字典

## 說明

`create()` 方法是 Reporter 函式化設計的第一步，用於處理輸入資料但不將其儲存在實例變數中。此方法會根據初始化時的配置，執行以下操作：

1. **驗證輸入資料格式**（透過 `_verify_create_input()`）
2. **根據報告器類型進行資料轉換**
3. **套用過濾條件**（source、eval、granularity 等）
4. **返回處理後的資料**供 `report()` 方法使用

### 資料驗證規則

輸入資料會經過嚴格驗證：
- 實驗元組必須有偶數個元素（模組名稱、實驗名稱成對）
- 模組名稱必須是有效的 PETsARD 模組
- 不允許重複的模組名稱
- DataFrame 值必須是 `pd.DataFrame` 或 `None`

## 基本範例

### save_data 模式

```python
from petsard import Reporter

# 初始化報告器
reporter = Reporter(method='save_data', source='Synthesizer')

# 準備資料（使用 tuple 作為 key）
data_dict = {
    ('Synthesizer', 'exp1'): synthetic_df
}

# 處理資料
processed = reporter.create(data_dict)

# processed 包含處理後的 DataFrame 字典
print(type(processed))  # <class 'dict'>
print(processed.keys())  # dict_keys(['Synthesizer[exp1]'])
```

### save_report 模式

```python
from petsard import Reporter

# 初始化報告器（單一粒度）
reporter = Reporter(method='save_report', granularity='global')

# 準備評估結果（注意實驗名稱包含粒度標記）
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results_df
}

# 處理資料
processed = reporter.create(eval_data)

# 產生報告
reporter.report(processed)
```

### save_timing 模式

```python
from petsard import Reporter
import pandas as pd

# 初始化報告器
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)

# 準備時間資料（使用特殊鍵 'timing_data'）
timing_data = {
    'timing_data': timing_df
}

# 處理資料
processed = reporter.create(timing_data)

# processed 是處理後的 DataFrame
print(type(processed))  # <class 'pandas.core.frame.DataFrame'>
```

## 進階範例

### 多重粒度報告

```python
from petsard import Reporter

# 初始化多粒度報告器
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)

# 準備多個粒度的資料
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
}

# 處理資料
processed = reporter.create(eval_data)

# processed 包含所有粒度的處理後結果
# 結構：{'Reporter': {'[global]': {...}, '[columnwise]': {...}, '[details]': {...}}}
```

### 合併先前報告

```python
from petsard import Reporter
import pandas as pd

# 讀取先前的報告
previous_global = pd.read_csv('previous_global.csv')
previous_columnwise = pd.read_csv('previous_columnwise.csv')

# 初始化報告器
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)

# 準備資料並合併先前結果
eval_data = {
    ('Evaluator', 'eval2_[global]'): new_global_results,
    ('Evaluator', 'eval2_[columnwise]'): new_columnwise_results,
    'exist_report': {  # 特殊鍵用於合併
        '[global]': previous_global,
        '[columnwise]': previous_columnwise
    }
}

# 處理資料（會合併新舊結果）
processed = reporter.create(eval_data)

# 產生合併後的報告
reporter.report(processed)
```

### 使用簡化命名策略

```python
from petsard import Reporter

# 使用簡化命名策略
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# 準備資料
data_dict = {
    ('Synthesizer', 'experiment_1'): df1,
    ('Synthesizer', 'experiment_2'): df2
}

# 處理資料
processed = reporter.create(data_dict)

# 產生報告（檔名將使用簡化格式）
reporter.report(processed)
# 輸出：petsard_Sy.experiment_1.csv
#       petsard_Sy.experiment_2.csv
```

### 過濾特定評估實驗

```python
from petsard import Reporter

# 只處理特定評估實驗
reporter = Reporter(
    method='save_report',
    granularity='global',
    eval='eval1'  # 只處理 eval1 的結果
)

# 準備多個實驗的資料
eval_data = {
    ('Evaluator', 'eval1_[global]'): eval1_results,
    ('Evaluator', 'eval2_[global]'): eval2_results  # 這個會被過濾掉
}

# 處理資料（只有 eval1 會被處理）
processed = reporter.create(eval_data)

# 產生報告
reporter.report(processed)
```

### 多步驟管線的資料

```python
from petsard import Reporter

# 儲存經過多個處理步驟的資料
reporter = Reporter(method='save_data', source='Synthesizer')

# 多步驟實驗元組
data_dict = {
    ('Loader', 'load1', 'Synthesizer', 'syn1'): synthetic_data
}

# 處理資料
processed = reporter.create(data_dict)

# processed 的鍵會包含完整的實驗路徑
# 例如：'Loader[load1]_Synthesizer[syn1]'
```

## 資料格式要求

### 實驗元組格式

實驗元組必須遵循以下格式：

```python
# 單步驟：(模組名稱, 實驗名稱)
('Synthesizer', 'exp1')
('Evaluator', 'eval1_[global]')

# 多步驟：(模組1, 實驗1, 模組2, 實驗2, ...)
('Loader', 'data_load', 'Synthesizer', 'syn1')
('Loader', 'load1', 'Evaluator', 'eval1_[global]')
```

**重要規則：**
- 元組長度必須是偶數
- 奇數位置是模組名稱
- 偶數位置是實驗名稱
- 模組名稱不能重複

### 特殊鍵

#### exist_report

用於合併先前的報告結果：

```python
{
    ('Evaluator', 'eval1_[global]'): new_data,
    'exist_report': {
        '[global]': previous_report_df,
        '[columnwise]': previous_columnwise_df
    }
}
```

#### timing_data

save_timing 模式專用：

```python
{
    'timing_data': timing_dataframe
}
```

## 錯誤處理

### 無效的資料格式

```python
from petsard import Reporter

reporter = Reporter(method='save_data', source='Synthesizer')

# 錯誤：鍵不是元組
invalid_data = {
    'Synthesizer_exp1': df  # 應該是 ('Synthesizer', 'exp1')
}

# 錯誤會在 _verify_create_input() 中被捕獲並記錄
processed = reporter.create(invalid_data)
# 無效的資料會被移除，可能返回空字典
```

### 缺少必要資料

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# 空資料字典
empty_data = {}

processed = reporter.create(empty_data)
# 返回包含警告的結果
# {'Reporter': {'[global]': {'report': None, 'warnings': '...'}}}
```

### 粒度不匹配

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# 資料包含錯誤的粒度標記
wrong_granularity = {
    ('Evaluator', 'eval1_[columnwise]'): data  # 期望 [global]
}

processed = reporter.create(wrong_granularity)
# 資料會被忽略，返回警告
```

## DataFrame 值處理

### None 值

`create()` 方法接受 `None` 作為 DataFrame 值：

```python
data_dict = {
    ('Evaluator', 'eval1_[global]'): None  # 允許 None
}

processed = reporter.create(data_dict)
# None 值會被適當處理，不會產生錯誤
```

### 資料驗證

輸入資料會經過嚴格驗證：

```python
# 有效的資料類型
valid_data = {
    ('Synthesizer', 'exp1'): pd.DataFrame(),  # ✓
    ('Evaluator', 'eval1_[global]'): None,    # ✓
}

# 無效的資料類型（會被移除）
invalid_data = {
    ('Synthesizer', 'exp1'): "string",        # ✗
    ('Evaluator', 'eval1_[global]'): [1,2,3], # ✗
}
```

## 注意事項

- **函式化設計**：`create()` 不會將資料儲存在實例變數中，返回值必須傳遞給 `report()` 方法
- **資料驗證**：方法會驗證輸入資料格式，無效格式會被記錄並移除
- **記憶體效率**：處理大量資料時，建議分批處理以節省記憶體
- **返回值類型**：根據報告器類型不同，返回值類型也不同
- **必須呼叫 report()**：`create()` 只處理資料，必須呼叫 `report()` 才會產生輸出檔案
- **粒度匹配**：對於 save_report 模式，資料中的粒度標記必須與初始化時指定的粒度一致
- **命名約定**：實驗元組的命名會影響最終的檔案名稱
- **模組名稱驗證**：只接受有效的 PETsARD 模組名稱
- **無狀態操作**：每次呼叫 `create()` 都是獨立的，不會受前次呼叫影響

## 相關文件

- Reporter API 主頁：Reporter 模組完整說明
- `report()` 方法：報告產生方法
- Reporter YAML：YAML 配置說明