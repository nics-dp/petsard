---
title: 保真度或實用性
weight: 2
---

在確認隱私保護力達標後，下一步是根據合成資料的使用目的來決定評測重點。不同的應用情境對合成資料的品質要求不同：當合成資料將對外公開或分享給多個不特定用途的接收方時，應追求高保真度以保持資料的通用價值；而當合成資料用於特定機器學習任務（如分類、迴歸、聚類）時，則應追求高實用性以確保任務表現。

## 保真度與實用性的差異

保真度 (Fidelity) 和實用性 (Utility) 是評估合成資料品質的兩個互補面向。保真度衡量合成資料在統計特性上與原始資料的相似程度，透過統計分佈比較（如 SDMetrics Quality Report）進行評測，適用於資料釋出或通用用途的情境。實用性則衡量合成資料在特定任務中的實際表現，透過機器學習模型效用 (ML Utility) 進行評測，適用於特定任務建模的情境。

保真度著重於「資料長什麼樣」，關注統計分佈與變數關係是否與原始資料相似；實用性則著重於「資料能做什麼」，關注在特定任務中能否達成與原始資料相當的效能。值得注意的是，高保真度不一定保證高實用性，反之亦然，因此選擇評測重點應基於資料的實際用途。

### 評測流程圖

{{< mermaid-file file="content/docs/petsard-yaml/evaluator-yaml/evaluator-workflow-overview.zh-tw.mmd" >}}

## 選擇評測重點的考量

### 資料釋出情境：追求高保真度

當合成資料的用途未定或需要支援多種用途時，應以保真度為主要評測面向。公開資料釋出情境下，由於無法預知所有可能的使用方式，必須確保合成資料在統計特性上與原始資料高度相似，保持資料的通用價值。

此時使用 SDMetrics Quality Report 評測，重點關注三個層面：單一欄位的分佈形狀相似度 (Column Shapes)、欄位間的關聯性保留程度 (Column Pair Trends)、以及整體品質綜合評分 (Overall Score)。根據差分隱私合成資料評測基準研究，整體分數應達到 0.75 以上作為品質標準。

學術研究分享情境與公開釋出類似，但可能需要額外針對特定領域進行實用性驗證，例如在生物醫學領域可能需要確認特定生物標記的關聯性是否被保留。演算法開發情境同樣以保真度為主，因為演算法設計需要資料的統計特性相似來支持測試與驗證。

### 特定任務建模：追求高實用性

當合成資料有明確的下游任務時，應以實用性為主要評測面向，此時保真度只需達到基本門檻（≥ 0.75）即可。任務類型的選擇取決於資料特性和領域知識：若資料全為數值特徵且無明確目標變數，最適合進行聚類任務；若有目標變數，則根據目標類型選擇分類（類別型目標）或迴歸（數值型目標）任務；若資料混合類別與數值特徵，則可根據實際用途選擇任何任務類型。

評測時需要考慮資料的預期用途：
- **預測建模場景**：應選擇分類或迴歸任務
- **模式發現場景**：適合使用聚類進行探索性分析
- **風險評估場景**：以分類任務最能提供清晰的洞察

實用性評測的關鍵在於選擇適當的評測指標和實驗設計。

#### 分類任務的主要指標

- **F1 Score**：精確率與召回率的調和平均，一般標準 ≥ 0.7
- **ROC AUC**：整體分類能力，一般標準 ≥ 0.8
- **MCC**：Matthews Correlation Coefficient，在不平衡資料集中特別重要，一般標準 ≥ 0.5

#### 迴歸任務的主要指標

- **R²**：模型解釋變異程度，一般標準 ≥ 0.7

#### 聚類任務的主要指標

- **Silhouette Score**：聚類品質，一般標準 ≥ 0.5

實驗設計方面，預設使用領域遷移設計（在合成資料上訓練，在原始資料上測試），評估合成資料是否能捕捉到可泛化到真實資料的基本模式。需要特別注意的是，當資料存在高度不平衡的情況時（例如欺詐偵測中正例率僅 1-2%），ROC AUC 可能產生誤導性的樂觀結果。此時應優先使用 MCC 作為主要指標（因其考慮所有混淆矩陣元素且對不平衡資料穩健），並輔以 PR AUC (Precision-Recall AUC，聚焦於正類品質)。

## 實際應用案例

### 案例 1：政府資料公開釋出

某政府單位欲釋出人口普查合成資料供學術研究使用，釋出對象眾多且用途不明確。此情境應優先確保資料在統計特性上與原始資料高度相似：

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
    n_attacks: 100
    max_attempts: 1000

  # 重點：追求高保真度（分數越高越好）
  fidelity_assessment:
    method: sdmetrics-qualityreport
```

評測時需確認：
- 資料有效性分數接近 1.0
- 所有隱私風險指標均低於 0.09（對外釋出建議低於 0.07）
- 保真度分數達到 0.75 以上作為主要目標（分數越高越好）

保真度評測關注三個面向：
- **Column Shapes**：單一欄位的分佈形狀相似度，目標 ≥ 0.75
- **Column Pair Trends**：欄位間的關聯性保留程度，目標 ≥ 0.75
- **Overall Score**：整體品質綜合評分，目標 ≥ 0.75

在此情境下，實用性評測並非必要，除非有特定領域需求需要額外驗證。

### 案例 2：金融機構風險模型開發

某金融機構欲使用合成資料訓練信用風險預測模型，明確的下游任務為二元分類（違約 vs. 正常）。此情境應優先確保合成資料能支持有效的模型訓練：

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
    n_attacks: 100
    max_attempts: 1000

  # 保真度達標即可（≥ 0.75）
  quality_assessment:
    method: sdmetrics-qualityreport

  # 重點：追求高實用性（依任務類型評估）
  ml_utility_assessment:
    method: mlutility
    task_type: classification
    target: income
    experiment_design: domain_transfer  # 預設：領域遷移
    random_state: 42
```

評測時需確認：
- 資料有效性分數接近 1.0
- 所有隱私風險指標均低於 0.09
- 保真度分數達到 0.75 的門檻即可

實用性指標達標是主要目標，分類任務的關鍵指標包括：
- **F1 Score**：精確率與召回率的調和平均，目標 ≥ 0.7
- **ROC AUC**：接收者操作特徵曲線下面積，目標 ≥ 0.8
- **Precision**：預測為正類中實際為正類的比例，目標 ≥ 0.7
- **Recall**：實際為正類中被正確預測的比例，目標 ≥ 0.7
- **Accuracy**：整體預測準確度，目標 ≥ 0.75

## 注意事項與常見問題

### 保真度和實用性可以同時追求嗎？

可以，但需要理解兩者的優先順序和權衡：
- **釋出情境**：以保真度為主要目標（≥ 0.75），實用性作為額外驗證
- **建模情境**：確保保真度達到基本門檻（≥ 0.75），重點追求實用性
- **混合情境**：需設定明確的優先順序，避免過度優化造成其他面向的犧牲

需要注意的是，過度追求保真度可能影響某些特定任務的實用性，過度針對特定任務優化可能降低其他用途的通用性，因此在隱私保護與品質之間需要找到平衡點。

### 保真度很高但實用性不佳怎麼辦？

這種情況可能有幾個原因：
- **任務不適配**：合成資料保留了統計特性但未捕捉到任務關鍵模式
- **類別不平衡**：罕見類別的特徵沒有被充分學習
- **複雜關係遺失**：高階交互作用或非線性關係未被保留
- **雜訊過多**：合成過程引入了影響任務表現的雜訊

解決方案包括：

**調整合成參數**
- 增加訓練輪數 epochs 到 500
- 調整 batch_size 到 500
- 增加判別器訓練步數 discriminator_steps 到 5

**針對任務優化**
- 評估是否需要額外的後處理步驟
- 考慮使用資料增益而非完全替代

**重新評估需求**
- 檢查實用性標準是否過於嚴格
- 評估是否需要更多原始資料用於訓練合成器
- 考慮任務本身的難度是否合理

### 實用性很高但保真度不佳怎麼辦？

這種情況可能有幾個原因：
- **過度擬合任務**：合成器針對特定任務優化而犧牲了整體統計相似度
- **簡化特徵**：為提升任務效能而簡化了某些複雜特徵
- **選擇性保留**：僅保留了對任務有用的特徵關係

解決方案包括：

**評估實際需求**
- 如果資料僅用於該特定任務則高實用性可能已足夠
- 若需要多用途使用則需要改善保真度

**調整合成策略**
- 使用 CTGAN 而不使用條件合成讓模型學習全部關係
- 設定 epochs 為 300
- 調整 discriminator_loss_weight 為 1.0 以平衡生成器與判別器

**採用混合方法**
- 使用高保真度的基礎合成資料
- 對特定任務進行微調或增益
- 為不同用途維護不同版本的合成資料

## 參考文獻

1. Tao, Y., McKenna, R., Hay, M., Machanavajjhala, A., & Miklau, G. (2021). Benchmarking differentially private synthetic data generation algorithms. *arXiv preprint arXiv:2112.09238*.

2. NIST SP 800-188. (2023). *De-Identifying Government Data Sets*. Section 4.4.5 "Synthetic Data with Validation"

3. Jordon, J., Yoon, J., & van der Schaar, M. (2019). Measuring the quality of synthetic data for use in competitions. *arXiv preprint arXiv:1806.11345*.

4. Dankar, F. K., & Ibrahim, M. (2021). Fake it till you make it: Guidelines for effective synthetic data generation. *Applied Sciences*, 11(5), 2158.

5. Hernandez, M., Epelde, G., Alberdi, A., Cilla, R., & Rankin, D. (2022). Synthetic data generation for tabular health records: A systematic review. *Neurocomputing*, 493, 28-45.

## 相關文件

- [隱私風險推估](privacy-risk-estimation)
- [實驗設計挑選](experiment-design-selection)
- [資料保真度評測詳細說明](../petsard-yaml/evaluator-yaml/#資料保真度)
- [資料實用性評測詳細說明](../petsard-yaml/evaluator-yaml/utility)
