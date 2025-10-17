---
title: "產生評估報告"
weight: 2
---

使用 `save_report` 方法產生評估結果報告，支援多種粒度層級。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-data.ipynb)

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Evaluator:
  validity_check:
    method: sdmetrics-diagnosticreport
  fidelity_check:
    method: sdmetrics-qualityreport
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    n_cols: 3
    max_attempts: 4000
  classification_utility:
    method: mlutility
    task_type: classification
    target: income
    random_state: 42
Reporter:
  save_report:
    method: save_report    # 必要：固定使用 save_report 方法
    granularity:           # 必要：指定報告粒度層級
      - global                  # 整體摘要統計
      - columnwise              # 逐欄分析
      - details                 # 詳細分解
    # eval:                # 選用：目標評估實驗名稱（預設：全部評估）
    # output: petsard      # 選用：輸出檔案名稱前綴（預設：petsard）
    # naming_strategy: traditional  # 選用：檔名命名策略，可選 traditional 或 compact（預設：traditional）
```

## 參數說明

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 固定為 `save_report` | `save_report` |
| `granularity` | `string` 或 `list` | 報告詳細度 | `global` 或 `["global", "columnwise"]` |

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `eval` | `string` 或 `list` | 全部 | 目標評估實驗名稱 | `eval1` 或 `["eval1", "eval2"]` |
| `output` | `string` | `petsard` | 輸出檔案名稱前綴 | `evaluation_results` |
| `naming_strategy` | `string` | `traditional` | 檔名命名策略 | `compact` |

## 粒度類型

不同評估方法支援不同的粒度層級：

- **global（整體摘要統計）**：提供資料集層級的整體評估指標
- **details（詳細分解）**：提供完整的評估細節和額外指標
- **columnwise（逐欄分析）**：針對每個欄位提供詳細的評估指標
- **pairwise（欄位間成對關係）**：分析欄位之間的相關性和關聯
- **tree（階層樹狀結構）**：以樹狀結構呈現評估結果的層級關係

### 支援的評估器

| 評估器 | global | details | columnwise | pairwise | tree |
|--------|--------|---------|------------|----------|------|
| mlutility | ✓ | ✓ | - | - | - |
| anonymeter | ✓ | ✓ | - | - | - |
| sdmetrics | ✓ | - | ✓ | ✓ | - |
| mpuccs | ✓ | ✓ | - | - | ✓ |
| describer | ✓ | - | ✓ | ✓ | - |

## 輸出格式

所有報告會儲存為 CSV 格式，檔案命名遵循主頁面說明的命名策略。

### CSV 檔案內容

報告檔案的欄位結構依粒度而異：

**Global 粒度：**
- `metric_name`：指標名稱
- `value`：指標數值
- `category`：指標類別

**Columnwise 粒度：**
- `column`：欄位名稱
- `metric_name`：指標名稱
- `value`：指標數值

**Pairwise 粒度：**
- `column_1`：第一個欄位
- `column_2`：第二個欄位
- `metric_name`：指標名稱
- `value`：指標數值

## 常見問題

### Q: 如何選擇適當的粒度？

**A:** 根據分析需求選擇：
- **快速概覽**：使用 `global`
- **欄位層級分析**：使用 `columnwise`
- **相關性分析**：使用 `pairwise`

### Q: 可以同時產生所有粒度嗎？

**A:** 可以，在 `granularity` 參數中列出所有需要的粒度：

### Q: 如何過濾特定評估實驗？

**A:** 使用 `eval` 參數指定：

```yaml
Reporter:
  save_specific:
    method: save_report
    granularity: global
    eval: my_evaluation  # 只處理這個評估
```

### Q: 報告檔案太大怎麼辦？

**A:** 考慮：
1. 只選擇需要的粒度
2. 使用 `eval` 參數過濾
3. 分批產生報告
4. 使用壓縮工具處理輸出檔案

## 注意事項

- **粒度匹配**：資料中的粒度標記必須與設定一致
- **記憶體使用**：`details` 和 `tree` 粒度可能產生較大的檔案
- **評估順序**：必須先執行 Evaluator 才能產生報告
- **命名衝突**：使用不同的 `output` 前綴避免檔案覆寫
- **資料完整性**：確保評估結果包含所需的粒度資訊
- **命名策略**：詳細的檔名格式說明請參考主頁面
