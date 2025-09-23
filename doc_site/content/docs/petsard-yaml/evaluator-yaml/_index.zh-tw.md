---
title: "Evaluator YAML"
weight: 140
---

Evaluator 模組的 YAML 設定檔案格式。

## 主要參數

- **method** (`string`, 必要參數)
  - 評估方法名稱
  - 支援的方法見下方表格

## 支援的評估方法

| 類型 | 方法名稱 | 說明 | 建議標準 |
|------|---------|------|----------|
| **資料有效性** | `sdmetrics-diagnosticreport` | 檢查資料結構和基本特性 | 分數 ≈ 1.0¹ |
| **隱私保護力** | `anonymeter-singlingout` | 單挑風險評估 | 風險 < 0.09² |
| | `anonymeter-linkability` | 連結性風險評估 | 風險 < 0.09² |
| | `anonymeter-inference` | 推論風險評估 | 風險 < 0.09² |
| **資料保真度** | `sdmetrics-qualityreport` | 統計分佈相似度評估 | 分數 ≥ 0.75³ |
| **資料實用性** | `mlutility` | 機器學習模型效用（新版） | 依任務而異⁴ |
| | `mlutility-classification` | 分類效用（舊版） | - |
| | `mlutility-regression` | 迴歸效用（舊版） | - |
| | `mlutility-cluster` | 聚類效用（舊版） | - |
| **統計評估** | `stats` | 統計差異比較 | - |
| **自訂評估** | `custom_method` | 自訂評估方法 | - |

### 建議標準參考文獻

¹ DataCebo. (2023). *SDMetrics: Metrics for synthetic data evaluation* (Version 0.12.1) [Software]. https://github.com/sdv-dev/SDMetrics

² Personal Data Protection Commission Singapore. (2023). *Proposed guide on synthetic data generation*. https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/proposed-guide-on-synthetic-data-generation.pdf

³ Tao, Y., McKenna, R., Hay, M., Machanavajjhala, A., & Miklau, G. (2021). Benchmarking differentially private synthetic data generation algorithms. *arXiv preprint arXiv:2112.09238*. https://doi.org/10.48550/arXiv.2112.09238

⁴ 依據任務類型：
- 分類：Chicco, D., & Jurman, G. (2020). The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. *BMC Genomics*, *21*(1), Article 6. https://doi.org/10.1186/s12864-019-6413-7（建議 MCC ≥ 0.5）
- 迴歸：調整後決定係數 ≥ 0.7（依領域慣例）
- 聚類：輪廓係數 ≥ 0.5（依領域慣例）

## 使用範例

### 基本評估

```yaml
Evaluator:
  privacy_check:
    method: anonymeter-singlingout
    n_attacks: 3000
```

### 多個評估實驗

```yaml
Evaluator:
  # 資料有效性診斷
  validity_check:
    method: sdmetrics-diagnosticreport
    
  # 隱私保護力評估
  privacy_assessment:
    method: anonymeter-singlingout
    n_attacks: 3000
    n_cols: 4
    
  # 資料保真度評估
  quality_assessment:
    method: sdmetrics-qualityreport
    
  # 資料實用性評估
  ml_utility_assessment:
    method: mlutility
    task_type: classification
    target: label
```

## 執行說明

- 建議使用新版 MLUtility（`method: mlutility`）而非舊版
- 大型資料集的評估可能需要較長時間，特別是 Anonymeter 方法