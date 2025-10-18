---
title: 預設合成與預設評測
type: docs
weight: 8
---

使用預設方式進行合成與評測。
目前的預設評測方式採用 SDMetrics 品質報告。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/getting-started/default-synthesis-default-evaluation.ipynb)

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
Splitter:
  basic_split:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: 'default'
Synthesizer:
  default:
    method: 'default'
Postprocessor:
  default:
    method: 'default'
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

### Loader、Preprocessor、Synthesizer、Postprocessor

這些模組的參數說明請參考 [預設合成教學](../default-synthesis)。

### Splitter（資料分割模組）

- **`basic_split`**: 實驗名稱，可自由命名
- **`num_samples`**: 重複抽樣次數
  - 值：`1`
  - 說明：至少需要一組驗證組來評估隱私保護程度
  - 這個分割對於 Anonymeter 評測是必要的，因為它需要比較訓練資料和測試資料來評估隱私風險
  - 預設值：1
- **`train_split_ratio`**: 訓練集的資料比例
  - 值：`0.8`
  - 說明：使用 80% 的資料作為訓練集、20% 作為測試集
  - 這是交叉驗證的常見做法
  - 範圍：0.0 到 1.0
  - 預設值：0.8

### Evaluator（資料評測模組）

本範例包含多種評測方法，涵蓋資料有效性、隱私保護力、保真度和實用性：

#### validity_check（資料有效性診斷）
- **`method`**: `sdmetrics-diagnosticreport`
- **說明**：檢查資料結構和基本特性
- **標準**：診斷分數應接近 1.0

#### fidelity_check（資料保真度評測）
- **`method`**: `sdmetrics-qualityreport`
- **說明**：評估合成資料與原始資料的統計分佈相似度
- **標準**：保真度分數應高於 0.75

#### singling_out_risk（單挑風險評測）
- **`method`**: `anonymeter-singlingout`
- **說明**：評估攻擊者能否從合成資料中識別出特定個體
- **標準**：風險分數應低於 0.09

#### linkability_risk（連結性風險評測）
- **`method`**: `anonymeter-linkability`
- **`aux_cols`**: 輔助欄位組合
  - 說明：依據領域知識將變數分組進行連結性攻擊評估
  - 第一組：就業與人口統計資料（workclass, education, occupation, race, gender）
  - 第二組：個人狀態與收入資料（age, marital-status, relationship, native-country, income）

#### inference_risk（推斷性風險評測）
- **`method`**: `anonymeter-inference`
- **`secret`**: 敏感欄位
  - 值：`income`
  - 說明：將最敏感的欄位設為 secret，評估攻擊者能否推斷該欄位的值

#### classification_utility（分類實用性評測）
- **`method`**: `mlutility`
- **`task_type`**: 任務類型
  - 值：`classification`
  - 說明：指定機器學習任務為分類任務
- **`target`**: 目標變數
  - 值：`income`
  - 說明：評估使用合成資料訓練的分類模型效能
  - 這需要與實際分析目標一致

### Reporter（結果輸出模組）

關於 `save_data` 方法的說明請參考 [預設合成教學](../default-synthesis/#reporter結果輸出模組)。

本範例額外使用 `save_report` 方法來儲存評測報告：

#### rpt（儲存評測報告）
- **`method`**: `save_report`
- **`granularity`**: 報告粒度層級
  - 值：`[global, columnwise, pairwise, details]`
  - 說明：以不同粒度層級輸出評測結果
    - **global**：全域層級的總體評分
    - **columnwise**：各欄位的個別評分
    - **pairwise**：欄位間相關性的評分
    - **details**：詳細的評測數據

## 執行流程說明

1. **Loader** 載入 [`adult-income.csv`](benchmark/adult-income.csv) 資料
2. **Splitter** 將資料分割為訓練集（80%）和測試集（20%）
3. **Preprocessor** 對訓練集進行前處理（填補缺失值、處理離群值、編碼、縮放）
4. **Synthesizer** 使用 Gaussian Copula 方法在訓練集上產生合成資料
5. **Postprocessor** 將合成資料還原為原始格式（反縮放、反編碼、插入缺失值）
6. **Evaluator** 執行多項評測：
   - 資料有效性診斷
   - 隱私風險評估（單挑、連結性、推斷性）
   - 資料保真度評估
   - 機器學習實用性評估
7. **Reporter** 儲存合成資料和多層級評測報告

## 評測概觀

評估合成資料需要權衡三個關鍵面向：
1. 保護力 (Protection) - 評估安全程度
2. 保真度 (Fidelity) - 衡量與原始資料的相似程度
3. 實用性 (Utility) - 評估實際應用表現

> 注意：這三個面向通常存在取捨關係。較高的保護力可能導致較低的保真度，而高保真度可能降低保護程度。

## 評測參數

1. `Splitter`（資料分割）:
  - `num_samples: 1`：至少需要一組驗證組來評估隱私保護程度。這個分割對於 Anonymeter 來說是必要的，因為它需要比較訓練資料和測試資料來評估隱私風險
  - `train_split_ratio: 0.8`：使用 80% 的資料作為訓練集、20% 作為測試集，這是交叉驗證的常見做法

2. `Evaluator`（資料評測）:
  - 連結性風險評測中，`aux_cols` 依據領域知識將變數分組，例如個人人口統計資料和就業相關資料
  - 推斷性風險評測中，將最敏感的欄位（收入）設為 `secret` 欄位
  - 分類實用性評測中，使用主要的 `target` 變數（收入），這需要與實際分析目標一致

## 評測流程

依照以下步驟評估您的合成資料：

1. **資料有效性診斷**（使用 SDMetrics）
  - 目標：確保資料綱要一致性
  - 標準：診斷分數需達到 1.0
  - 原因：有效的資料是後續所有分析的基礎

2. **隱私保護力評測**（使用 Anonymeter）
  - 目標：驗證隱私保護程度
  - 標準：風險分數應低於 0.09
  - 評估：指認性風險 (Singling Out)、連結性風險 (Linkability) 及推斷性風險 (Inference)
  > 注意：風險分數 0.0 並不代表完全沒有風險。務必同時實施其他保護措施。

3. **應用場景評測**

  根據您的使用情境，著重於：

  A. 無特定任務（資料釋出情境）：
  - 著重於資料保真度（使用 SDMetrics）
  - 標準：保真度分數高於 0.75
  - 衡量：分布相似性和相關性保持程度

  B. 特定任務（模型訓練情境）：
  - 著重於資料實用性
  - 標準依任務類型而異：
    * 分群 (Classification)：ROC AUC > 0.8
    * 聚類 (Clustering)：輪廓係數 (Silhouette) > 0.5
    * 迴歸 (Regression)：調整後決定係數 (Adjusted R²) > 0.7
  > 注意：ROC AUC（受試者操作特徵曲線下面積）用於衡量模型區分不同類別的能力
