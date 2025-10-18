---
title: "report()"
weight: 364
---

產生並儲存 CSV 格式的報告檔案。

## 語法

```python
def report(processed_data: dict | pd.DataFrame | None = None) -> dict | None
```

## 參數

- **processed_data** : dict | pd.DataFrame | None, required
    - 來自 `create()` 方法的輸出
    - 必要參數
    - 類型取決於報告器模式：
        - **save_data**：DataFrame 字典 `{expt_name: DataFrame}`
        - **save_report**：粒度結果字典 `{'Reporter': {...}}`
        - **save_timing**：時間資訊 DataFrame
        - **save_validation**：驗證結果字典

## 返回值

- **dict | None**
    - 返回處理後的報告資料
    - save_data：返回儲存的資料字典
    - save_report：返回原始 processed_data
    - save_timing：返回空字典或 processed_data
    - 無資料時：返回空字典 `{}`

## 說明

`report()` 方法是 Reporter 函式化設計的第二步，用於將 `create()` 處理後的資料儲存為 CSV 檔案。此方法會：

1. **接收處理後的資料**
2. **根據命名策略產生檔名**（使用 `_generate_report_filename()`）
3. **將資料寫入 CSV 檔案**（透過 `_save()` 方法）
4. **儲存到當前工作目錄**

### 檔名生成邏輯

報告檔名由以下組成：
- **輸出前綴**：來自 `output` 參數（預設 'petsard'）
- **命名策略**：traditional 或 compact
- **實驗資訊**：模組名稱、實驗名稱、粒度等

## 輸出檔名格式

檔名格式取決於 `naming_strategy` 參數設定：

### Traditional 策略（預設）

| 方法 | 格式 | 範例 |
|------|------|------|
| **save_data** | `{output}_{module-expt_name-pairs}.csv` | `petsard_Synthesizer[exp1].csv` |
| **save_report** | `{output}_Reporter[{eval}_[{granularity}]].csv` | `petsard_Reporter[eval1_[global]].csv` |
| **save_timing** | `{output}_timing_report.csv` | `petsard_timing_report.csv` |
| **save_validation** | `{output}_validation_report.csv` | `petsard_validation_report.csv` |

### Compact 策略

| 方法 | 格式 | 範例 |
|------|------|------|
| **save_data** | `{output}_{module}.{experiment}.csv` | `petsard_Sy.exp1.csv` |
| **save_report** | `{output}.report.{module}.{experiment}.{G}.csv` | `petsard.report.Ev.eval1.G.csv` |
| **save_timing** | `{output}_timing_report.csv` | `petsard_timing_report.csv` |
| **save_validation** | `{output}_validation_report.csv` | `petsard_validation_report.csv` |

**粒度縮寫（Compact 模式）：**
- G = Global
- C = Columnwise  
- P = Pairwise
- D = Details
- T = Tree

## 基本範例

### save_data 模式

```python
from petsard import Reporter

# 初始化報告器
reporter = Reporter(method='save_data', source='Synthesizer')

# 準備並處理資料
data_dict = {
    ('Synthesizer', 'exp1'): synthetic_df
}
processed = reporter.create(data_dict)

# 產生報告檔案
reporter.report(processed)
# 輸出：petsard_Synthesizer[exp1].csv
```

### save_report 模式

```python
from petsard import Reporter

# 初始化報告器
reporter = Reporter(method='save_report', granularity='global')

# 準備並處理資料
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results
}
processed = reporter.create(eval_data)

# 產生報告檔案
reporter.report(processed)
# 輸出：petsard[Report]_eval1_[global].csv
```

### save_timing 模式

```python
from petsard import Reporter

# 初始化報告器
reporter = Reporter(
    method='save_timing',
    time_unit='minutes'
)

# 準備並處理資料
timing_data = {'timing_data': timing_df}
processed = reporter.create(timing_data)

# 產生報告檔案
reporter.report(processed)
# 輸出：petsard_timing_report.csv
```

## 進階範例

### 使用簡化命名策略

```python
from petsard import Reporter

# 使用簡化命名
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# 處理資料
data_dict = {
    ('Synthesizer', 'experiment_1'): df1
}
processed = reporter.create(data_dict)

# 產生簡化檔名的報告
reporter.report(processed)
# 輸出：petsard_Sy.experiment_1.csv（更簡潔）
```

### 自訂輸出檔名前綴

```python
from petsard import Reporter

# 自訂前綴
reporter = Reporter(
    method='save_report',
    granularity='global',
    output='my_experiment'
)

# 處理資料
eval_data = {
    ('Evaluator', 'eval1_[global]'): results
}
processed = reporter.create(eval_data)

# 產生自訂前綴的報告
reporter.report(processed)
# 輸出：my_experiment[Report]_eval1_[global].csv
```

### 多粒度報告產生

```python
from petsard import Reporter

# 多粒度報告器
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)

# 準備多粒度資料
eval_data = {
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
}
processed = reporter.create(eval_data)

# 為每個粒度產生個別報告
reporter.report(processed)
# 輸出：
# - petsard[Report]_eval1_[global].csv
# - petsard[Report]_eval1_[columnwise].csv
# - petsard[Report]_eval1_[details].csv
```

### 批次處理多個實驗

```python
from petsard import Reporter

# 初始化報告器
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact'
)

# 準備多個實驗的資料
experiments = {
    ('Synthesizer', 'exp1'): synthetic_df1,
    ('Synthesizer', 'exp2'): synthetic_df2,
    ('Synthesizer', 'exp3'): synthetic_df3
}

# 處理所有資料
processed = reporter.create(experiments)

# 一次產生所有報告
reporter.report(processed)
# 輸出：
# - petsard_Sy.exp1.csv
# - petsard_Sy.exp2.csv
# - petsard_Sy.exp3.csv
```

### 過濾特定模組的時間報告

```python
from petsard import Reporter

# 只報告特定模組的時間資訊
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']  # 只包含這兩個模組
)

# 準備時間資料（包含所有模組）
timing_data = {'timing_data': all_timing_df}
processed = reporter.create(timing_data)

# 產生過濾後的報告
reporter.report(processed)
# 輸出：petsard_timing_report.csv（只包含 Loader 和 Synthesizer）
```

## 完整工作流程範例

### 典型使用模式

```python
from petsard import Reporter
import pandas as pd

# 步驟 1：初始化報告器
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact',
    output='my_analysis'
)

# 步驟 2：準備評估資料
evaluation_results = pd.DataFrame({
    'metric': ['accuracy', 'precision', 'recall'],
    'value': [0.85, 0.82, 0.88]
})

# 步驟 3：創建資料字典
data_dict = {
    ('Evaluator', 'eval1_[global]'): evaluation_results
}

# 步驟 4：處理資料
processed_data = reporter.create(data_dict)

# 步驟 5：產生報告
reporter.report(processed_data)
# 輸出：my_analysis.report.Ev.eval1.G.csv

print("✓ 報告已成功產生")
```

### 鏈式調用模式

```python
from petsard import Reporter

# 初始化
reporter = Reporter(method='save_data', source='Synthesizer')

# 鏈式調用：create -> report
reporter.report(
    reporter.create({
        ('Synthesizer', 'exp1'): synthetic_df
    })
)
# 一行完成處理和報告產生
```

## 檔案操作說明

### 輸出位置

報告檔案儲存在**當前工作目錄**：

```python
import os
from petsard import Reporter

# 切換到指定目錄
os.chdir('/path/to/output/directory')

# 產生報告
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create(data_dict)
reporter.report(processed)
# 檔案將儲存在 /path/to/output/directory/
```

### 檔案覆寫行為

同名檔案會被**覆寫**，建議使用不同的 `output` 前綴或實驗名稱避免覆寫：

```python
from petsard import Reporter
import datetime

# 使用時間戳避免覆寫
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    output=f'petsard_{timestamp}'
)

processed = reporter.create(data_dict)
reporter.report(processed)
# 輸出：petsard_20241016_153000_Synthesizer[exp1].csv
```

### CSV 格式說明

所有報告檔案使用以下設定儲存：
- **格式**：CSV (逗號分隔)
- **編碼**：UTF-8
- **索引**：不包含索引欄位（`index=False`）
- **標頭**：包含欄位名稱

## 錯誤處理

### 處理 None 資料

```python
from petsard import Reporter

reporter = Reporter(method='save_report', granularity='global')

# create() 返回 None（無資料）
processed = reporter.create({})

# report() 會優雅地處理 None
result = reporter.report(processed)
# 返回空字典，不會產生檔案，也不會報錯
print(result)  # {}
```

### 處理無效資料

```python
from petsard import Reporter

reporter = Reporter(method='save_data', source='Synthesizer')

try:
    # 傳入錯誤的資料類型
    reporter.report("invalid_data")
except Exception as e:
    print(f"錯誤：{e}")
```

### 處理警告訊息

對於 save_report 模式，當沒有匹配的資料時會記錄警告：

```python
from petsard import Reporter

reporter = Reporter(
    method='save_report',
    granularity='global'
)

# 資料不匹配（錯誤的粒度）
data = {
    ('Evaluator', 'eval1_[columnwise]'): results  # 期望 [global]
}
processed = reporter.create(data)

# 會記錄警告但不會產生錯誤
reporter.report(processed)
# 日誌：WARNING - No CSV file will be saved...
```

## 多粒度處理細節

### 單一粒度（向後相容）

```python
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create(eval_data)
reporter.report(processed)
# processed 結構：
# {
#     'Reporter': {
#         'eval_expt_name': '[global]',
#         'granularity': 'global',
#         'report': DataFrame
#     }
# }
```

### 多重粒度（新格式）

```python
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)
processed = reporter.create(eval_data)
reporter.report(processed)
# processed 結構：
# {
#     'Reporter': {
#         '[global]': {
#             'eval_expt_name': '[global]',
#             'granularity': 'global',
#             'report': DataFrame
#         },
#         '[columnwise]': {
#             'eval_expt_name': '[columnwise]',
#             'granularity': 'columnwise',
#             'report': DataFrame
#         }
#     }
# }
```

## 注意事項

- **必須先呼叫 create()**：直接呼叫 `report()` 而不先呼叫 `create()` 會導致錯誤或無效輸出
- **檔案覆寫**：同名檔案會被覆寫，請謹慎使用
- **當前目錄**：檔案儲存在當前工作目錄，不是專案根目錄
- **CSV 格式**：所有報告都以 CSV 格式儲存
- **編碼格式**：預設使用 UTF-8 編碼
- **None 處理**：當 processed_data 為 None 或包含警告時，不會產生檔案
- **記憶體釋放**：報告產生後，傳入的 processed_data 可以被垃圾回收
- **多檔案產生**：多粒度或多實驗模式會產生多個檔案
- **檔名限制**：檔名長度和特殊字元受作業系統限制
- **日誌記錄**：檔案儲存會記錄在日誌中（INFO 級別）
- **命名策略**：檔名格式由初始化時的 `naming_strategy` 決定，不能在 report() 階段修改

## 相關文件

- Reporter API 主頁：Reporter 模組完整說明
- `create()` 方法：資料處理方法
- Reporter YAML：YAML 配置說明