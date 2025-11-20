---
title: "迴歸任務"
type: docs
weight: 2
prev: docs/petsard-yaml/evaluator-yaml/utility/classification
next: docs/petsard-yaml/evaluator-yaml/utility/clustering
---

評估合成資料在迴歸問題上的實用性。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-regression.ipynb)


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
  regression_utility:
    method: mlutility
    task_type: regression
    target: capital-gain                 # 目標欄位（必要）
    experiment_design: domain_transfer   # 實驗設計（預設：domain_transfer）
    metrics:                             # 評測指標
      - r2_score
      - rmse
    random_state: 42                     # 隨機種子（預設：42）
    xgb_params:                          # XGBoost 參數（不需要時省略）
      n_estimators: 200                  # 樹的數量（預設：100）
      max_depth: 8                       # 樹的最大深度（預設：6）
```

## 任務特定參數

| 參數 | 類型 | 預設值 | 說明 |
|-----|------|--------|------|
| **target** | `string` | 必要 | 迴歸的目標變數欄位名稱 |
| **metrics** | `array` | 見下方 | 要計算的評測指標 |
| **xgb_params** | `dict` | 無 | XGBoost 超參數（省略使用預設值） |

### 預設指標
- `r2_score`、`rmse`

### XGBoost 參數說明

| 參數 | 預設值 | 說明 |
|-----|--------|------|
| `n_estimators` | 100 | 提升輪數（樹的數量） |
| `max_depth` | 6 | 樹的最大深度 |
| `learning_rate` | 0.3 | 學習率（eta） |
| `subsample` | 1.0 | 訓練每棵樹的樣本採樣比例 |
| `colsample_bytree` | 1.0 | 訓練每棵樹的特徵採樣比例 |
| `min_child_weight` | 1 | 葉節點最小樣本權重和 |

{{< callout type="info" >}}
如不需要調整 XGBoost 參數，可完全省略 `xgb_params` 區塊，系統將使用預設值。
{{< /callout >}}

詳細參數說明與調校指引，請參閱 [XGBoost 套件文件](https://xgboost.readthedocs.io/en/stable/parameter.html)。

## 支援的指標

| 指標 | 說明 | 範圍 | 預設 | 適用情境 |
|-----|------|------|------|----------|
| `r2_score` | 決定係數 | -∞ 到 1 | ✓ | 主要判斷指標，跨資料集比較 |
| `rmse` | 均方根誤差 | 0-∞ | ✓ | 了解實際預測誤差，懲罰大誤差 |
| `mse` | 均方誤差 | 0-∞ | ✗ | 數學優化方便，但單位為平方 |
| `mae` | 平均絕對誤差 | 0-∞ | ✗ | 資料有離群值時較穩健 |
| `mape` | 平均絕對百分比誤差 | 0-∞ | ✗ | 需要相對誤差，但避免用於包含 0 的資料 |

## 關鍵指標建議

### 主要判斷標準

| 指標 | 優秀 | 良好 | 可接受 | 需改進 |
|-----|------|------|--------|--------|
| **R²** | ≥ 0.9 | ≥ 0.7 | ≥ 0.5 | < 0.5 |
| **RMSE** | < Y標準差×0.3 | < Y標準差×0.5 | < Y標準差×0.7 | ≥ Y標準差×0.7 |

*Y標準差：目標變數（target column）的標準差

### 合成資料效用判斷

對於 dual_model_control 實驗設計，比較 ori 與 syn 的差異：

| 評估等級 | R² 差異 | RMSE 增加幅度 |
|---------|---------|---------------|
| 優秀 | < 0.05 | < 10% |
| 良好 | < 0.10 | < 20% |
| 可接受 | < 0.20 | < 30% |
| 需改進 | ≥ 0.20 | ≥ 30% |

{{< callout type="info" >}}
**RMSE 判斷提示**：
- RMSE 的絕對值需結合資料範圍判斷
- RMSE/Y標準差 比值（標準化 RMSE）提供無單位的效能指標
- 範例：房價預測（單位：萬元）RMSE = 10 可能很好；溫度預測（單位：°C）RMSE = 10 可能很差
{{< /callout >}}

## 使用考量

### 何時使用迴歸

- **連續目標變數**：價格、溫度、分數等
- **需要數值預測**：預測、估計
- **所有特徵都是數值**：通常表示適合迴歸

### 資料前處理

評測器會自動：
1. 移除缺失值
2. 編碼類別變數（OneHotEncoder）
3. 標準化數值特徵
4. 標準化目標變數

### 模型細節

- **演算法**：XGBoost 迴歸器
- **目標**：最小化平方誤差
- **特徵重要性**：可透過 XGBoost 取得

{{< callout type="info" >}}
對於高度偏斜的目標分布，考慮在評測前進行對數轉換。
{{< /callout >}}

## 參考文獻

1. Despotovic, M., Nedic, V., Despotovic, D., & Cvetanovic, S. (2016). Evaluation of empirical models for predicting monthly mean horizontal diffuse solar radiation. *Renewable and Sustainable Energy Reviews*, 56, 246-260.

2. Chai, T., & Draxler, R. R. (2014). Root mean square error (RMSE) or mean absolute error (MAE)?–Arguments against avoiding RMSE in the literature. *Geoscientific model development*, 7(3), 1247-1250.