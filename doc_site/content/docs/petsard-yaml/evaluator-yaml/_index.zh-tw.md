---
title: "Evaluator YAML"
weight: 180
---

Evaluator 模組的 YAML 設定檔案格式。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/evaluator.ipynb)

### 建議評估流程

我們建議採用以下評估流程，確保合成資料符合需求：

#### 1. 評估流程概覽

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-overview.zh-tw.mmd" >}}

#### 2. 資料診斷性標準

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-diagnostic.zh-tw.mmd" >}}

#### 3. 隱私保護力標準

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-privacy.zh-tw.mmd" >}}

#### 4. 資料保真度標準

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-fidelity.zh-tw.mmd" >}}

#### 5. 資料實用性標準

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-utility.zh-tw.mmd" >}}

> **圖例說明：**
> - 淺藍色方框：開始/結束點
> - 白色方框：評估步驟
> - 菱形：決策點
> - 綠色方框：成功結果
> - 紅色方框：失敗狀態，需要採取行動
> - 黃色方框：需要改進
> - 橙色方框：評估方法

### 1. 基礎評估（必要）

首先確認資料的**有效性**和**隱私保護力**：

### 2. 目標導向評估

通過基礎評估後，根據合成資料的**使用目的**選擇評估重點：

#### 情境 A：資料釋出（無特定下游任務）

若合成資料將對外釋出，應追求**最高的保真度**：

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
  # Step 1: 資料有效性診斷（應接近 1.0）
  validity_check:
    method: sdmetrics-diagnosticreport
  # Step 2: 隱私保護力評估（風險應 < 0.09）
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    max_attempts: 4000
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
    method: anonymeter-inference
    secret: income
  # 重點：追求高保真度（分數越高越好）
  fidelity_assessment:
    method: sdmetrics-qualityreport
  # 實用性評估可選（非必要）
```

#### 情境 B：特定任務應用（資料增益、模型訓練等）

若合成資料用於特定機器學習任務，應追求**高實用性**：

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
  # Step 1: 資料有效性診斷（應接近 1.0）
  validity_check:
    method: sdmetrics-diagnosticreport
  # Step 2: 隱私保護力評估（風險應 < 0.09）
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400
    max_attempts: 4000
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
  # 保真度達標即可（≥ 0.75）
  quality_assessment:
    method: sdmetrics-qualityreport
  # 重點：追求高實用性（依任務類型評估）
  ml_utility_assessment:
    method: mlutility
    task_type: classification  # 或 regression/clustering
    target: income
```

## 主要參數

- **method** (`string`, 必要參數)
  - 評估方法名稱
  - 支援的方法見下方表格

## 支援的評估方法

| 類型 | 方法名稱 | 說明 | 建議標準 |
|------|---------|------|----------|
| **預設方法** | `default` | 預設評估（等同於 `sdmetrics-qualityreport`） | 分數 ≥ 0.75¹ |
| **資料有效性** | `sdmetrics-diagnosticreport` | 檢查資料結構和基本特性 | 分數 ≈ 1.0² |
| **隱私保護力** | `anonymeter-singlingout` | 單挑風險評估 | 風險 < 0.09³ |
| | `anonymeter-linkability` | 連結性風險評估 | 風險 < 0.09³ |
| | `anonymeter-inference` | 推論性風險評估 | 風險 < 0.09³ |
| **資料保真度** | `sdmetrics-qualityreport` | 統計分佈相似度評估 | 分數 ≥ 0.75¹ |
| **資料實用性** | `mlutility` | 機器學習模型效用 | 依任務類型⁴ |
| **自訂評估** | `custom_method` | 自訂評估方法 | - |

### 建議標準說明

¹ **保真度標準**（分數 ≥ 0.75）：基於統計分佈相似度

² **有效性標準**（分數 ≈ 1.0）：資料結構完整性檢查

³ **隱私風險標準**（風險 < 0.09）：基於 PDPC Singapore 指引

⁴ **實用性標準**（依任務類型）：
- 分類任務（XGBoost）：F1 ≥ 0.7
- 迴歸任務（XGBoost）：R² ≥ 0.7
- 聚類任務（K-means）：輪廓係數 ≥ 0.5

> **預設方法**：當 `method: default` 時，系統會自動執行 `sdmetrics-qualityreport` 評估資料保真度。

> **閾值調整**：以上建議標準為一般參考值，請根據您的具體應用場景和風險容忍度調整適當的閾值。各指標的詳細理論基礎和參考文獻請見對應子文件。

## 執行說明

- 大型資料集的評估可能需要較長時間，特別是 Anonymeter 方法
- 建議依序執行評估，確保前置條件達標後再進行後續評估