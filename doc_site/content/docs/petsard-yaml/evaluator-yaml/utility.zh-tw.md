---
title: "資料實用性評測"
weight: 144
---

衡量合成資料在機器學習任務的表現，判斷是否能有效替代原始資料。

## 配置範例

### 分類任務

```yaml
Evaluator:
  classification_utility:
    method: mlutility
    task_type: classification
    target: label                        # 目標欄位（必要）
    experiment_design: dual_model_control # 實驗設計
    resampling: smote-enn                # 不平衡處理（可選）
    metrics:                             # 評估指標（可選）
      - mcc
      - f1_score
      - roc_auc
      - accuracy
    xgb_params:                          # XGBoost 參數（可選）
      n_estimators: 100
      max_depth: 6
      learning_rate: 0.3
    random_state: 42
```

### 迴歸任務

```yaml
Evaluator:
  regression_utility:
    method: mlutility
    task_type: regression
    target: price                        # 目標欄位（必要）
    experiment_design: domain_transfer
    metrics:
      - r2_score
      - mse
      - mae
      - rmse
    xgb_params:
      n_estimators: 200
      max_depth: 8
    random_state: 42
```

### 聚類任務

```yaml
Evaluator:
  clustering_utility:
    method: mlutility
    task_type: clustering
    experiment_design: dual_model_control
    n_clusters: 5                # 聚類數量
    metrics:
      - silhouette_score
    random_state: 42
```

## 參數說明

### 共同參數

- **method** (`string`, 必要參數)
  - 新版：`mlutility`（建議使用）
  - 舊版：`mlutility-classification`、`mlutility-regression`、`mlutility-cluster`

- **task_type** (`string`, 新版必要)
  - `classification`：分類任務
  - `regression`：迴歸任務
  - `clustering`：聚類任務

- **target** (`string`, 分類和迴歸必要)
  - 目標變數欄位名稱

- **experiment_design** (`string`)
  - `dual_model_control`：雙模型控制（預設）
    - ori 訓練 → control 測試
    - syn 訓練 → control 測試
    - 比較兩者差異
  - `domain_transfer`：領域轉移
    - syn 訓練 → ori 測試
    - 評估泛化能力

- **random_state** (`integer`)
  - 隨機種子
  - 預設值：42

### 分類任務參數

- **resampling** (`string`)
  - 不平衡資料處理方法
  - 選項：
    - `null`：不處理（預設）
    - `smote-enn`：SMOTE + ENN（建議）
    - `smote-tomek`：SMOTE + Tomek Links

- **metrics** (`array`)
  - 評估指標列表
  - 預設：`[mcc, f1_score, roc_auc, pr_auc, accuracy, balanced_accuracy, precision, recall, specificity, tp, tn, fp, fn]`
  - 支援指標：
    - 基本：`accuracy`, `balanced_accuracy`, `f1_score`, `precision`, `recall`
    - 進階：`mcc`, `cohen_kappa`, `jaccard`
    - 機率：`roc_auc`, `pr_auc`, `log_loss`, `brier_score`
    - 混淆矩陣：`tp`, `tn`, `fp`, `fn`, `sensitivity`, `specificity`

### 迴歸任務參數

- **metrics** (`array`)
  - 評估指標列表
  - 預設：`[r2_score, mse, mae, rmse]`
  - 支援：`r2_score`, `mse`, `mae`, `rmse`, `mape`

### 聚類任務參數

- **n_clusters** (`integer`)
  - 聚類數量
  - 預設值：5

- **metrics** (`array`)
  - 評估指標列表
  - 預設：`[silhouette_score]`

### XGBoost 參數

- **xgb_params** (`dict`)
  - XGBoost 額外參數
  - 常用參數：
    - `n_estimators`：樹的數量
    - `max_depth`：最大深度
    - `learning_rate`：學習率
    - `subsample`：子樣本比例
    - `colsample_bytree`：特徵採樣比例

## CAPE 建議的關鍵指標

評估結果以表格形式呈現，包含訓練集交叉驗證的平均值和標準差，以及在測試集上的表現。CAPE 建議關注以下幾個關鍵指標在測試集上的表現：

### 分類任務

| 指標 | 說明 | 數值範圍 | 建議標準 | 適用情境 |
|-----|------|---------|---------|---------|
| **ROC AUC** | 反映模型在所有閾值的綜合表現能力 | 0-1 | ≥ 0.8 | 大部分分類狀況 |
| **MCC** | Matthews 相關係數，考慮所有預測類別（真陽性、真陰性、假陽性、假陰性）的全面評估<br>1：完美預測；0：隨機猜測；負值：反向預測 | -1到1 | ≥ 0.5 | 不平衡資料集 |
| **PR AUC** | Precision-Recall 曲線下面積 | 0-1 | 參考用 | 極度不平衡（正例 < 10%） |

### 迴歸任務

| 指標 | 說明 | 數值範圍 | 建議標準 |
|-----|------|---------|---------|
| **Adjusted R²** | 調整後決定係數<br>評估模型解釋應變量變異的比例<br>同時考慮模型複雜度，避免過擬合 | 0-1 | ≥ 0.7* |

*具體標準可根據領域和資料特性調整（例如樣本過小、或資料特性具大量雜訊等）

### 聚類任務

| 指標 | 說明 | 數值範圍 | 建議標準 |
|-----|------|---------|---------|
| **Silhouette** | 輪廓係數<br>評估聚類的緊密度和分離度<br>1：完美聚類；0：重疊；負值：錯誤分配 | -1到1 | ≥ 0.5 |

## 不平衡資料處理

### ROC AUC 的侷限性

在高度不平衡資料中，ROC AUC 容易被大量負例稀釋而產生樂觀偏差¹。例如，在正例僅佔 3-4% 的情況下，ROC AUC 可能達到 0.86-0.90，看似表現良好，但 sensitivity 僅 0.54-0.56，意味著近半正例被漏檢。

### 建議策略

1. **指標選擇**
   - 優先使用 MCC，因為它綜合考慮混淆矩陣所有要素²
   - 搭配 PR AUC 觀察，避免單一指標的局限性³⁴
   - MCC 能避免 F1 只看正例、忽略負例的問題
   - PR AUC 能避免 ROC AUC 的樂觀偏差

2. **重採樣方法**
   - **SMOTE-ENN**：合成少數類別 + 積極清理雜訊（噪音多時使用）
   - **SMOTE-Tomek**：合成少數類別 + 保守清理邊界（邊界不清時使用）

{{< callout type="warning" >}}
所有合成資料版本在處理極度不平衡問題時可能完全失效（sensitivity = 0），這表明罕見類別特徵可能完全流失，源於生成模型對極少數樣本學習能力不足。
{{< /callout >}}

## 舊版配置（不建議使用）

```yaml
# 分類（多模型）
Evaluator:
  old_classification:
    method: mlutility-classification
    target: label

# 迴歸（多模型）
Evaluator:
  old_regression:
    method: mlutility-regression
    target: price

# 聚類（K-means）
Evaluator:
  old_clustering:
    method: mlutility-cluster
    n_clusters:
      - 4
      - 5
      - 6
```

## 參考文獻

1. Davis, J., & Goadrich, M. (2006). The relationship between precision-recall and ROC curves. *Proceedings of the 23rd International Conference on Machine Learning*, 233-240.

2. Chicco, D., & Jurman, G. (2020). The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. *BMC Genomics*, 21(1), Article 6.

3. Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE*, 10(3), e0118432.

4. He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263-1284.
