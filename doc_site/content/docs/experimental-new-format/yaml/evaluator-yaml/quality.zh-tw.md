---
title: "資料保真度評測"
weight: 243
---

衡量合成資料與原始資料的相似程度，評估資料分佈和變量關係的保持程度。

## 配置範例

```yaml
Evaluator:
  quality_check:
    method: sdmetrics-qualityreport
```

## 參數說明

- **method** (`string`, 必要參數)
  - 固定值：`sdmetrics-qualityreport`

## 評估指標

| 指標 | 說明 | 建議標準 |
|-----|------|---------|
| **Score** | 保真度總分（欄位形態和欄位對趨勢的算術平均） | ≥ 0.75 |
| **Column Shapes** | 欄位形態 | ≥ 0.75 |
| - KSComplement | K-S 補數（數值欄位） | |
| - TVComplement | 全變差距離補數（類別欄位） | |
| **Column Pair Trends** | 欄位對趨勢 | ≥ 0.75 |
| - Correlation Similarity | 相關相似度（數值對） | |
| - Contingency Similarity | 列聯相似度（類別對） | |

## 指標計算說明

### Column Shapes（欄位形態）
各欄位形態保真度的算術平均，依欄位特性計算：

- **KSComplement**：數值或日期欄位
  - 使用 K-S test（柯爾莫哥洛夫-斯米爾諾夫檢定）
  - 以累積分布函數（CDF）檢查兩經驗分布差異
  - 計算 1 - K-S value 作為指標
  - 數值從 0 到 1，越大形態越相似

- **TVComplement**：類別或布林欄位
  - 計算全變差距離（Total Variation Distance, TVD）
  - 測量所有基數的機率差
  - 計算 1 - TVD 作為指標
  - 數值從 0 到 1，越大形態越相似

### Column Pair Trends（欄位對趨勢）
各欄位間兩兩相關性保真度的算術平均：

- **CorrelationSimilarity**：兩個欄位皆為數值或日期
  - 分別計算原始和合成資料的皮爾森相關係數
  - 公式：`1 - |r_合成 - r_原始| / 2`
  - 數值從 0 到 1，越大趨勢越相似

- **ContingencySimilarity**：兩個欄位皆為類別或布林
  - 計算歸一化列聯表的全變差距離
  - 公式：`1 - 1/2 * ΣΣ |r_合成 - r_原始|`
  - 數值從 0 到 1，越大趨勢越相似

- **混合型欄位對**：一個數值/日期，一個類別/布林
  - 先將數值/日期欄位離散化為區間
  - 區間數量依循 numpy 預設（Sturges' rule 或 FD rule）
  - 再計算列聯相似度

## 適用情境

- 評估合成過程的有效性
- 比較不同合成方法的品質
- 確認重要特徵和模式的保留程度

## 建議標準

- 0.75 以上為可接受¹
- Score、Column Shapes、Column Pair Trends 都應 ≥ 0.75
- 如果分數偏低，可能需要調整合成方法或參數

## 技術參考

- Sturges' rule：最佳區間數 = log₂(n) + 1
- FD rule：最佳區間寬度 = 2 × IQR / n^(1/3)
- 轉換點約在樣本數 1,000

## 參考文獻

¹ Tao, Y., McKenna, R., Hay, M., Machanavajjhala, A., & Miklau, G. (2021). Benchmarking differentially private synthetic data generation algorithms. *arXiv preprint arXiv:2112.09238*. https://doi.org/10.48550/arXiv.2112.09238