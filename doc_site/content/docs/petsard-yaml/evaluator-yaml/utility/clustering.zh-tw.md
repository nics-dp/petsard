---
title: "聚類任務"
type: docs
weight: 3
prev: docs/petsard-yaml/evaluator-yaml/utility/regression
next: docs/petsard-yaml/evaluator-yaml/utility
---

評估合成資料在無監督聚類問題上的實用性。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/utility-clustering.ipynb)

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
  clustering_utility:
    method: mlutility
    task_type: clustering
    experiment_design: domain_transfer   # 實驗設計（預設：domain_transfer）
    n_clusters: 3                        # 群集數量（預設：3）
    metrics:                             # 評測指標
      - silhouette_score
    random_state: 42                     # 隨機種子（預設：42）
```

## 任務特定參數

| 參數 | 類型 | 預設值 | 說明 |
|-----|------|--------|------|
| **n_clusters** | `integer` | `3` | K-means 的群集數量 |
| **metrics** | `array` | `[silhouette_score]` | 評測指標（目前僅支援 silhouette_score） |

注意：聚類任務不需要 `target` 參數，因為它們是無監督的。

## 支援的指標

| 指標 | 說明 | 範圍 | 預設 |
|-----|------|------|------|
| `silhouette_score` | 測量群集凝聚度和分離度 | -1 到 1 | ✓ |

## 關鍵指標建議

| 指標 | 說明 | 建議標準 |
|-----|------|----------|
| **輪廓係數** | 評估群集緊密度和分離度<br>• 1：完美聚類<br>• 0：重疊群集<br>• 負值：錯位群集 | ≥ 0.5 |

## 使用考量

### 何時使用聚類

- **無目標變數可用**：探索性資料分析
- **需要模式發現**：客戶分群、異常偵測
- **所有數值特徵**：聚類在數值資料上效果最佳

### 選擇群集數量

考慮以下方法：
- **領域知識**：產業標準或業務需求
- **肘部法**：繪製慣性對 k 並找到「肘部」
- **輪廓分析**：測試不同 k 值並比較分數
- **間隙統計**：估計最佳 k 的統計方法

### 資料前處理

MLUtility 會自動對輸入資料進行以下前處理：

1. **缺失值處理**
   - 移除包含缺失值的樣本（使用 `dropna()`）

2. **欄位類型識別**
   - 檢查所有資料集（ori、syn、control）
   - 如果任一資料集中該欄位為類別型態，則視為類別欄位
   - 保守判斷確保不會遺漏類別特徵

3. **類別特徵編碼**
   - 使用 OneHotEncoder 進行獨熱編碼
   - 只使用 ori 和 syn 資料訓練編碼器（避免資料洩漏）
   - `handle_unknown='ignore'`：控制組中未見過的類別編碼為全零向量

4. **特徵標準化**
   - 使用 StandardScaler 對所有特徵（數值+編碼後的類別）進行標準化
   - 只使用 ori 和 syn 資料計算均值和標準差（避免資料洩漏）
   - 控制組使用相同的轉換參數

5. **資料對齊**
   - 確保所有資料集的特徵維度一致
   - 處理後的資料準備進行聚類分析

{{< callout type="info" >}}
**資料洩漏防範**：編碼器和標準化器只在 ori 和 syn 資料上訓練，避免控制組資訊洩漏到訓練過程。
{{< /callout >}}

### 模型細節

- **演算法**：K-means 聚類
- **距離度量**：歐氏距離
- **初始化**：k-means++（預設）
- **最大迭代次數**：300

### 侷限性

{{< callout type="warning" >}}
**目前侷限性：**
- 僅支援 K-means 聚類
- 僅提供輪廓係數指標
- 假設球形群集（K-means 假設）
{{< /callout >}}

### 解釋結果

**輪廓係數解釋（基於 Kaufman & Rousseeuw, 1990）：**
- **0.71-1.00**：強結構
- **0.51-0.70**：合理結構
- **0.26-0.50**：弱結構
- **< 0.25**：無實質結構

該分數測量：
- **凝聚度**：點與其自身群集的接近程度
- **分離度**：點與其他群集的距離

{{< callout type="info" >}}
對於具有非球形群集的資料集，請考慮 K-means 可能表現不佳，影響實用性評測的準確性。
{{< /callout >}}

## 參考文獻

1. Kaufman, L., & Rousseeuw, P. J. (1990). *Finding groups in data: An introduction to cluster analysis*. John Wiley & Sons.

2. Kodinariya, T. M., & Makwana, P. R. (2013). Review on determining number of Cluster in K-Means Clustering. *International Journal*, 1(6), 90-95.

3. Pham, D. T., Dimov, S. S., & Nguyen, C. D. (2005). Selection of K in K-means clustering. *Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science*, 219(1), 103-119.