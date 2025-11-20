---
title: 以外部合成資料做預設評測
type: docs
weight: 130
prev: docs/getting-started/default-synthesis-default-evaluation
next: docs/getting-started
---


使用預設方式評測外部合成資料。
讓使用者評估外部解決方案獲得的合成資料。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/getting-started/external-synthesis-default-evaluation.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark/adult-income_ori.csv
      control: benchmark/adult-income_control.csv
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark/adult-income_syn.csv
Evaluator:
  validity_check:
    method: sdmetrics-diagnosticreport
  fidelity_check:
    method: sdmetrics-qualityreport
  singling_out_risk:
    method: anonymeter-singlingout
  linkability_risk:
    method: anonymeter-linkability
    aux_cols:
      -
        - workclass
        - education
        - occupation
        - race
        - gender
      -
        - age
        - marital-status
        - relationship
        - native-country
        - income
  inference_risk:
    method: 'anonymeter-inference'
    secret: 'income'
  classification_utility:
    method: mlutility
    task_type: classification
    target: income
Reporter:
  data:
    method: 'save_data'
    source: 'Postprocessor'
  rpt:
    method: 'save_report'
    granularity:
      - 'global'
      - 'columnwise'
      - 'pairwise'
      - 'details'
```

## YAML 參數詳細說明

### Splitter（資料分割模組）- 使用外部預分割資料

本範例使用 `custom_data` 方法載入外部已分割的資料集，這與[預設合成與預設評測](../default-synthesis-default-evaluation)中使用的自動分割不同。

- **`external_split`**: 實驗名稱，可自由命名
- **`method`**: 資料分割方法
  - 值：`custom_data`
  - 說明：用於載入外部提供的預分割資料集，而非自動分割
  - 適用場景：當您已經有預先分割好的訓練集和測試集時使用
- **`filepath`**: 資料檔案路徑
  - **`ori`**: 訓練集（原始資料）路徑
    - 值：`benchmark/adult-income_ori.csv`
    - 說明：用於訓練合成模型的資料集
  - **`control`**: 測試集（控制資料）路徑
    - 值：`benchmark/adult-income_control.csv`
    - 說明：用於隱私風險評估的獨立測試集

**重要提醒**：
- 訓練集和測試集必須完全獨立，不能有重疊的資料列
- 建議分割比例為 80% 訓練集、20% 測試集
- 測試集不應該用於合成資料的生成過程

### Synthesizer（合成資料載入模組）- 使用外部合成資料

本範例使用 `custom_data` 方法載入外部工具產生的合成資料，這是與[預設合成與預設評測](../default-synthesis-default-evaluation)的主要差異。

- **`external_data`**: 實驗名稱，可自由命名
- **`method`**: 合成方法
  - 值：`custom_data`
  - 說明：用於載入外部工具產生的合成資料（如 SDV、CTGAN 等）
  - 此方法不會執行合成，只是載入現有的合成資料進行評測
- **`filepath`**: 合成資料檔案路徑
  - 值：`benchmark/adult-income_syn.csv`
  - 說明：外部工具產生的合成資料檔案位置

**重要提醒**：
- 合成資料必須僅基於訓練集（`ori`）生成
- 不應該使用測試集（`control`）的資訊來生成合成資料
- 這樣才能確保隱私評測的準確性

### Evaluator、Reporter

這些模組的參數說明請參考 [預設合成與預設評測](../default-synthesis-default-evaluation)。

### 為何沒有 Loader、Preprocessor、Postprocessor？

在外部合成評測場景中：
- **無需 Loader**：資料載入由 Splitter 的 `custom_data` 方法完成
- **無需 Preprocessor**：前處理應該在外部合成工具中完成
- **無需 Postprocessor**：合成資料應該已經是最終格式

## 執行流程說明

1. **Splitter** 載入預分割的資料：
   - 訓練集：[`adult-income_ori.csv`](benchmark/adult-income_ori.csv)
   - 測試集：[`adult-income_control.csv`](benchmark/adult-income_control.csv)
2. **Synthesizer** 載入外部工具產生的合成資料：[`adult-income_syn.csv`](benchmark/adult-income_syn.csv)
3. **Evaluator** 執行多項評測：
   - 資料有效性診斷
   - 隱私風險評估（單挑、連結性、推斷性）
   - 資料保真度評估
   - 機器學習實用性評估
4. **Reporter** 儲存合成資料和多層級評測報告

## 外部資料準備概觀

預先合成資料的評測需要注意三個關鍵組成：

1. 訓練集 - 用於生成合成資料
2. 測試集 - 用於隱私風險評估
3. 合成資料 - 僅基於訓練集產生

> 注意：如果同時使用訓練和測試資料來合成，會影響隱私評測的準確性

## 外部資料要求

1. `Splitter`（資料分割）：

- `method: 'custom_data'`：用於外部提供的預分割資料集
- `filepath`: 指向原始 (`ori`) 和控制 (`control`) 資料集
- 建議比例：除非有特殊理由，否則採用 80% 訓練、20% 測試

2. `Synthesizer`（資料合成）：

- `method: 'custom_data'`：用於外部生成的合成資料
- `filepath`：指向預先合成的資料集
- 必須僅使用資料的訓練部分來生成

3. `Evaluator`（資料評測）：

- 確保不同合成資料解決方案之間的公平比較
