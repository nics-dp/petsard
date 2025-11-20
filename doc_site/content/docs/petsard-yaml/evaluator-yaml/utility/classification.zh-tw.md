---
title: "分類任務"
type: docs
weight: 1
prev: docs/petsard-yaml/evaluator-yaml/utility
next: docs/petsard-yaml/evaluator-yaml/utility/regression
---

評估合成資料在分類問題上的實用性。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-classification.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

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
  classification_utility:
    method: mlutility
    task_type: classification
    target: income                       # 目標欄位（必要）
    experiment_design: domain_transfer   # 實驗設計（預設：domain_transfer）
    resampling: None                     # 不平衡處理（預設無，不需要時省略）
    metrics:                             # 評測指標
      - f1_score
      - roc_auc
      - pr_auc
      - mcc
    random_state: 42                     # 隨機種子（預設：42）
    xgb_params:                          # XGBoost 參數（不需要時省略）
      scale_pos_weight: 3                # 正負樣本權重比（預設：1）
      max_depth: 5                       # 樹的最大深度（預設：6）
      min_child_weight: 3                # 葉節點最小樣本權重（預設：1）
      subsample: 0.8                     # 樣本採樣比例（預設：1.0）
      colsample_bytree: 0.8              # 特徵採樣比例（預設：1.0）
```

## 任務特定參數

| 參數 | 類型 | 預設值 | 說明 |
|-----|------|--------|------|
| **target** | `string` | 必要 | 分類的目標變數欄位名稱 |
| **resampling** | `string` | 無 | 不平衡資料處理：省略表示不處理，或使用 `smote-enn`、`smote-tomek` |
| **metrics** | `array` | 見下方 | 要計算的評測指標 |
| **xgb_params** | `dict` | 無 | XGBoost 超參數（省略使用預設值） |

### 預設指標
- `f1_score`、`roc_auc`、`accuracy`
- `precision`、`recall`、`specificity`
- `mcc`、`pr_auc`
- `tp`、`tn`、`fp`、`fn`

### XGBoost 參數說明

| 參數 | 預設值 | 說明 |
|-----|--------|------|
| `n_estimators` | 100 | 提升輪數（樹的數量） |
| `max_depth` | 6 | 樹的最大深度 |
| `learning_rate` | 0.3 | 學習率（eta） |
| `subsample` | 1.0 | 訓練每棵樹的樣本採樣比例 |
| `colsample_bytree` | 1.0 | 訓練每棵樹的特徵採樣比例 |
| `scale_pos_weight` | 1 | 正樣本的權重比例（用於不平衡資料） |
| `min_child_weight` | 1 | 葉節點最小樣本權重和 |

{{< callout type="info" >}}
如不需要調整 XGBoost 參數，可完全省略 `xgb_params` 區塊，系統將使用預設值。
{{< /callout >}}

詳細參數說明與調校指引，請參閱 [XGBoost 套件文件](https://xgboost.readthedocs.io/en/stable/parameter.html)。

## 支援的指標

| 指標 | 說明 | 範圍 | 預設 |
|-----|------|------|------|
| `f1_score` | 精確率和召回率的調和平均 | 0-1 | ✓ |
| `roc_auc` | ROC 曲線下面積 | 0-1 | ✓ |
| `accuracy` | 整體正確預測 | 0-1 | ✓ |
| `precision` | 真陽性 / (真陽性 + 偽陽性) | 0-1 | ✓ |
| `recall` | 真陽性 / (真陽性 + 偽陰性) | 0-1 | ✓ |
| `specificity` | 真陰性 / (真陰性 + 偽陽性) | 0-1 | ✓ |
| `mcc` | Matthews 相關係數 | -1 到 1 | ✓ |
| `pr_auc` | Precision-Recall 曲線下面積 | 0-1 | ✓ |
| `tp` | 真陽性（計數） | ≥0 | ✓ |
| `tn` | 真陰性（計數） | ≥0 | ✓ |
| `fp` | 偽陽性（計數） | ≥0 | ✓ |
| `fn` | 偽陰性（計數） | ≥0 | ✓ |
| `sensitivity` | 同 recall | 0-1 | ✗ |

## 關鍵指標建議

### 標準分類

| 指標 | 說明 | 建議標準 |
|-----|------|----------|
| **F1 Score** | 精確率和召回率之間的平衡 | ≥ 0.7 |
| **ROC AUC** | 跨所有閾值的綜合效能 | ≥ 0.8 |

### 不平衡分類

| 指標 | 說明 | 建議標準 |
|-----|------|----------|
| **PR AUC** | 少數類別的效能（不受負例稀釋） | ≥ 0.3* |
| **MCC** | 考慮所有混淆矩陣元素的平衡測量 | ≥ 0.5 |

*PR AUC 標準依不平衡比例而定：
- 輕度不平衡（少數類別 10-20%）：≥ 0.5
- 中度不平衡（少數類別 5-10%）：≥ 0.3
- 嚴重不平衡（少數類別 <5%）：≥ 0.2

## 處理不平衡資料

### 何時使用重採樣

- **類別不平衡 > 10:1**：考慮重採樣
- **少數類別 < 10%**：強烈建議
- **少數類別 < 1%**：必要

### 重採樣方法

**SMOTE-ENN**：合成少數類別樣本並積極移除雜訊，適用於資料有雜訊且邊界不清的情況。

**SMOTE-Tomek**：合成少數類別樣本並保守移除邊界衝突，適用於資料較乾淨但類別重疊的情況。

{{< callout type="info" >}}
重採樣僅應用於訓練資料（ori 和 syn），絕不應用於測試資料（control）。
{{< /callout >}}