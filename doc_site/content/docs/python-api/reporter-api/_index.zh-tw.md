---
title: "Reporter API"
type: docs
weight: 1130
---

報告產生模組，支援多種報告格式的輸出與檔案儲存。

## 類別架構

{{< mermaid-file file="content/docs/python-api/reporter-api/reporter-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：工廠類別
> - 淺紫框：抽象基底類別
> - 橘色框：子類別實作
> - 淺紫框（其他）：配置與枚舉類別
> - `<|--`：繼承關係 (inheritance)
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 基本使用

```python
from petsard import Reporter

# 儲存合成資料
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report(processed)

# 產生評估報告
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report(processed)

# 儲存時間資訊
reporter = Reporter(method='save_timing', time_unit='minutes')
processed = reporter.create({'timing_data': timing_df})
reporter.report(processed)
```

## 建構函式 (__new__)

初始化報告產生器實例。Reporter 使用工廠模式（通過 `__new__` 方法），根據指定的 method 參數自動創建並返回對應的報告器實例。

### 語法

```python
Reporter(**kwargs)
```

### 參數

- **method** : str, required
    - 報告產生方式
    - 必要參數
    - 支援的方法：
        - `'save_data'`：將資料集儲存為 CSV
        - `'save_report'`：產生評估報告
        - `'save_timing'`：儲存時間資訊
        - `'save_validation'`：儲存驗證結果

- **output** : str, optional
    - 輸出檔案名稱前綴
    - 預設值：`'petsard'`

- **naming_strategy** : str, optional
    - 檔名命名策略
    - 可選值：
        - `'traditional'`：使用傳統命名格式（預設）
        - `'compact'`：使用簡化命名格式

#### save_data 方法專用參數

- **source** : str | List[str], required for save_data
    - 目標模組或實驗名稱
    - 指定要儲存資料的來源模組
    - 可為單一字串或字串列表

#### save_report 方法專用參數

- **granularity** : str | List[str], required for save_report
    - 報告詳細度
    - 單一粒度：`'global'`、`'columnwise'`、`'pairwise'`、`'details'`、`'tree'`
    - 多重粒度：`['global', 'columnwise']` 或 `['details', 'tree']`

- **eval** : str | List[str], optional
    - 目標評估實驗名稱
    - 用於過濾特定評估實驗的結果
    - 可為單一字串或字串列表

#### save_timing 方法專用參數

- **time_unit** : str, optional
    - 時間單位
    - 可選值：`'seconds'`、`'minutes'`、`'hours'`、`'days'`
    - 預設值：`'seconds'`

- **module** : str | List[str], optional
    - 依特定模組過濾時間資訊
    - 可為單一字串或字串列表

### 返回值

- **BaseReporter**
    - 根據 method 參數返回對應的報告器實例
    - 實際類別：
        - `ReporterSaveData`：儲存資料模式
        - `ReporterSaveReport`：評估報告模式
        - `ReporterSaveTiming`：時間資訊模式
        - `ReporterSaveValidation`：驗證結果模式

### 使用範例

```python
from petsard import Reporter

# 儲存合成資料
reporter = Reporter(method='save_data', source='Synthesizer')

# 產生評估報告（單一粒度）
reporter = Reporter(method='save_report', granularity='global')

# 產生評估報告（多重粒度）
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise']
)

# 使用簡化命名策略
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact'
)

# 儲存時間資訊（指定時間單位）
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)

# 自訂輸出檔名前綴
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    output='my_experiment'
)
```

## 函式化設計模式

Reporter 採用函式化的「拋出再拋回」設計模式，具有以下特性：

- **無狀態設計**：`create()` 處理資料但不將其儲存在實例變數中
- **純函式操作**：`report()` 接收處理後的資料並產生輸出檔案
- **記憶體效率**：不維護內部狀態，減少記憶體使用量
- **靈活流程**：允許靈活的資料處理流程

### 工作流程

```python
# 步驟 1：初始化報告器
reporter = Reporter(method='save_report', granularity='global')

# 步驟 2：處理資料（create 返回處理後的資料）
processed_data = reporter.create({
    ('Evaluator', 'eval1_[global]'): results
})

# 步驟 3：產生報告（report 接收處理後的資料）
reporter.report(processed_data)
```

## 粒度類型

Reporter 支援多種報告粒度，用於評估報告的不同層級分析：

### 傳統粒度
- **global**：整體摘要統計
- **columnwise**：逐欄分析
- **pairwise**：欄位間成對關係

### 擴展粒度
- **details**：詳細分解與額外指標
- **tree**：階層樹狀結構分析

### 多粒度支援

Reporter 支援在單一操作中處理多個粒度：

```python
# 同時處理多個粒度
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)
result = reporter.create(evaluation_data)
reporter.report(result)  # 為每個粒度產生個別報告
```

當使用多粒度時：
- 每個粒度會產生獨立的報告檔案
- 報告檔名會包含粒度資訊
- 可以一次性收集所有粒度的結果

## 命名策略

Reporter 支援兩種檔名命名策略：

### Traditional 策略（預設）

使用原有的命名格式，保持向後相容性：
- 包含完整的模組和實驗資訊
- 使用方括號標記特殊資訊
- 適合需要詳細檔名資訊的場景

**範例：**
- `petsard_Synthesizer[exp1].csv`
- `petsard_Reporter[eval1_global].csv`
- `petsard_timing_report.csv`

### Compact 策略

使用簡化的命名格式：
- 使用模組簡寫（如 Sy = Synthesizer, Ev = Evaluator）
- 使用點號分隔各部分
- 產生更簡潔易讀的檔名

**範例：**
- `petsard_Sy.exp1.csv`
- `petsard.report.Ev.eval1.G.csv`（G = Global）
- `petsard_timing_report.csv`

**命名策略使用範例：**

```python
# Traditional 策略範例
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='traditional'
)
# 輸出：petsard_Reporter[eval1_global].csv

# Compact 策略範例
reporter = Reporter(
    method='save_report',
    granularity='global',
    naming_strategy='compact'
)
# 輸出：petsard.report.Ev.eval1.G.csv
```

## 範例場景

### 儲存合成資料

```python
from petsard import Reporter

# 儲存合成資料
reporter = Reporter(method='save_data', source='Synthesizer')
processed = reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report(processed)
# 產生：petsard_Synthesizer[exp1].csv
```

### 產生評估報告（單一粒度）

```python
from petsard import Reporter

# 產生全域評估報告
reporter = Reporter(method='save_report', granularity='global')
processed = reporter.create({('Evaluator', 'eval1_[global]'): global_results})
reporter.report(processed)
# 產生：petsard_Reporter[eval1_global].csv
```

### 產生評估報告（多重粒度）

```python
from petsard import Reporter

# 產生多粒度評估報告
reporter = Reporter(
    method='save_report',
    granularity=['global', 'columnwise', 'details']
)
processed = reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results,
    ('Evaluator', 'eval1_[details]'): details_results
})
reporter.report(processed)
# 產生：
# - petsard_Reporter[eval1_global].csv
# - petsard_Reporter[eval1_columnwise].csv
# - petsard_Reporter[eval1_details].csv
```

### 儲存時間資訊

```python
from petsard import Reporter

# 儲存特定模組的時間資訊
reporter = Reporter(
    method='save_timing',
    time_unit='minutes',
    module=['Loader', 'Synthesizer']
)
processed = reporter.create({'timing_data': timing_df})
reporter.report(processed)
# 產生：petsard_timing_report.csv
```

### 使用簡化命名策略

```python
from petsard import Reporter

# 使用簡化命名
reporter = Reporter(
    method='save_data',
    source='Synthesizer',
    naming_strategy='compact',
    output='results'
)
processed = reporter.create({('Synthesizer', 'exp1'): df})
reporter.report(processed)
# 產生：results_Sy.exp1.csv（更簡潔的檔名）
```

## 版本相容性

### 預計在 v2.0 移除的功能

以下功能已標記為 deprecated，將在 v2.0 版本中移除：

- **ReporterMap 類別**：請改用 `ReporterMethod` enum
- **ReporterSaveReportMap 類別**：請改用 `ReportGranularity` enum
- **Tuple-based 實驗命名系統**：將被 `ExperimentConfig` 系統取代

建議使用者開始遷移至新的 API 以確保未來相容性。

## 注意事項

- **工廠模式**：Reporter 使用 `__new__` 方法實作工廠模式，自動創建對應的報告器類別
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **方法調用順序**：必須先呼叫 `create()` 再呼叫 `report()`
- **資料處理**：`create()` 返回的資料必須傳遞給 `report()` 方法
- **檔案輸出**：報告檔案會儲存在當前工作目錄
- **檔案覆寫**：同名檔案會被覆寫，請謹慎使用
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容
- **記憶體效率**：函式化設計確保不會在實例中保留大量資料
- **多粒度處理**：使用多粒度時，每個粒度會產生獨立的報告檔案
- **命名策略選擇**：根據專案需求選擇合適的命名策略，traditional 保持向後相容，compact 更簡潔

## 相關文件

- `create()` 方法：資料處理方法詳細說明
- `report()` 方法：報告產生方法詳細說明
- Reporter YAML：YAML 配置說明
- ReporterAdapter：Adapter 模式說明