---
title: "Reporter YAML"
weight: 190
---

Reporter 模組負責輸出實驗結果，支援資料儲存、評估報告和時間記錄等多種報告格式。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter.ipynb)

```yaml
Loader:
  load_data:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  synthesize:
    method: default
Evaluator:
  fidelity_check:
    method: sdmetrics-qualityreport

Reporter:
  save_synthetic:
    method: save_data
    source: Synthesizer

  save_report:
    method: save_report
    granularity: global

  save_timing:
    method: save_timing
```

## 支援的報告方法

本模組支援以下報告輸出方式，每種方法的詳細參數請參考各子頁面：

1. **儲存資料** - 將合成資料或其他模組的輸出儲存為 CSV 檔案
2. **產生評估報告** - 產生評估結果報告，支援多種粒度層級
3. **儲存時間資訊** - 記錄各模組的執行時間

## 命名策略與實驗名稱

PETsARD 採用統一的實驗命名規範，用於識別和追蹤實驗過程。
Reporter 模組支援兩種命名策略，可透過 `naming_strategy` 參數控制：

1. **TRADITIONAL**：維持向後相容性的傳統命名格式
2. **COMPACT**：提供更簡潔易讀的命名格式

```python
from petsard.reporter import Reporter

# 傳統命名（預設）
reporter = Reporter('save_report', granularity='global', naming_strategy='traditional')

# 簡潔命名
reporter = Reporter('save_report', granularity='global', naming_strategy='compact')
```

### 實驗名稱格式

#### 實驗元組

`full_expt_tuple` 是一個由模組名稱和實驗名稱組成的元組：
```python
(module_name, experiment_name)
```

此格式主要用於 Reporter 系統識別和組織實驗結果。

#### 實驗字串

`full_expt_name` 是將模組名稱和實驗名稱用連字號串接的字串：
```
{module_name}-{experiment_name}
```

### 檔案命名格式

#### save_data 方法

| 策略 | 格式 | 範例 |
|------|------|------|
| Traditional | `{output}_{module}[{experiment}].csv` | `petsard_Synthesizer[exp1].csv` |
| Compact | `{output}_{module}_{experiment}.csv` | `petsard_Synthesizer_exp1.csv` |

#### save_report 方法

| 策略 | 格式 | 範例 |
|------|------|------|
| Traditional | `{output}[Report]_{eval}_[{granularity}].csv` | `petsard[Report]_eval1_[global].csv` |
| Compact | `{output}_{eval}_{granularity}.csv` | `petsard_eval1_global.csv` |

#### save_timing 方法

所有策略使用相同格式：
```
{output}_timing_report.csv
```

### 模組簡寫對照表（Compact 策略）

| 模組名稱 | 簡寫 | 範例檔名 |
|---------|------|---------|
| Loader | Ld | `petsard_Ld.load_adult.csv` |
| Splitter | Sp | `petsard_Sp.train_test.csv` |
| Processor | Pr | `petsard_Pr.normalize.csv` |
| Synthesizer | Sy | `petsard_Sy.ctgan_baseline.csv` |
| Constrainer | Cn | `petsard_Cn.privacy_check.csv` |
| Evaluator | Ev | `petsard_Ev.utility_eval.csv` |
| Reporter | Rp | `petsard_Rp.summary.csv` |

### 粒度簡寫對照表（Compact 策略）

| 粒度名稱 | 簡寫 | 範例檔名 |
|---------|------|---------|
| global | G | `petsard_eval_privacy.G.csv` |
| columnwise | C | `petsard_eval_column.C.csv` |
| pairwise | P | `petsard_eval_correlation.P.csv` |
| details | D | `petsard_eval_detailed.D.csv` |
| tree | T | `petsard_eval_hierarchical.T.csv` |

### 命名建議

1. **模組名稱**
   - 使用標準模組名稱：'Synthesizer'、'Evaluator'、'Processor' 等
   - 注意大小寫需要完全匹配

2. **實驗名稱**
   - 使用有意義的前綴：'exp'、'eval'、'test' 等
   - 用底線分隔不同部分：方法名稱、參數設定等
   - 評估層級使用方括號：[global]、[columnwise]、[pairwise]

3. **參數編碼**
   - 參數名稱使用縮寫：method、batch、epoch 等
   - 數值使用簡潔表示：300、0.1 等
   - 多參數用底線連接：method_a_batch500

4. **策略選擇**
   - **新專案**：建議使用 `compact` 策略，檔名更簡潔
   - **現有專案**：使用 `traditional` 策略以保持相容性
   - **檔案管理**：`compact` 策略的檔名更易於排序和分類

## 通用參數

所有報告方法都支援以下通用參數：

- **output** (`string`, 選用) - 輸出檔案名稱前綴，預設為 `petsard`
- **naming_strategy** (`string`, 選用) - 檔名命名策略，可選 `traditional`（預設）或 `compact`

## 注意事項

- Reporter 應在所有需要報告的模組執行完畢後執行
- 同名檔案會被覆寫，建議使用不同的 `output` 前綴
- 所有報告都以 CSV 格式儲存，使用 UTF-8 編碼
- 建議新專案使用 `compact` 命名策略，現有專案保持 `traditional` 以確保相容性