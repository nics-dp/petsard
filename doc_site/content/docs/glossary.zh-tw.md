---
title: "名詞定義"
weight: 999
prev: docs/experimental-new-format
next: docs
---

PETsARD 文件中的專有名詞與術語說明（按注音符號排序）。

## A

- **Adapter**：在 PETsARD 中指標準化執行包裝器，為所有模組提供一致的執行介面，是 PETsARD 架構的核心設計模式。
- **Anonymeter**：隱私風險評測工具，其開發廠商 Statice 獲得法國資料保護機構 (CNIL) 認可符合歐盟規範，評估指認性、連結性、推斷性三種風險。

## C

- **Cohen's Kappa**：衡量分類一致性的指標，考慮隨機一致的可能性。
- **CTGAN (Conditional Tabular GAN)**：使用生成對抗網路的表格資料合成方法，專門處理混合型資料。

## D

- **Docker**：容器化技術，PETsARD 提供 Docker 映像檔供快速部署使用。
- **Docker Compose**：定義和執行多容器 Docker 應用程式的工具，用於協調 PETsARD 服務。

## F

- **F1 Score**：精確率和召回率的調和平均數，分類任務的綜合評估指標。
- **FNR (False Negative Rate)**：假陰性率，實際為正但預測為負的比例。
- **FPR (False Positive Rate)**：假陽性率，實際為負但預測為正的比例。

## G

- **GitHub Container Registry (GHCR)**：GitHub 提供的容器映像儲存服務，PETsARD 的 Docker 映像檔託管於此。

## J

- **Jaccard Score**：衡量集合相似度的指標，用於分類任務評估。
- **Jensen-Shannon Divergence**：測量兩個機率分佈差異的對稱性指標。

## K

- **K-S 檢定 (Kolmogorov-Smirnov Test)**：比較兩個經驗分布差異的統計檢定方法。

## L

- **Log Loss**：對數損失，衡量分類模型預測機率準確性的指標。

## M

- **MAE (Mean Absolute Error)**：平均絕對誤差，迴歸任務的評估指標。
- **Matthews 相關係數 (MCC)**：綜合考慮混淆矩陣所有要素的分類評估指標。
- **MLUtility**：PETsARD 中評估合成資料機器學習實用性的模組，分為 V1（使用決策樹）和 V2（使用 XGBoost）版本。
- **MSE (Mean Squared Error)**：均方誤差，迴歸任務的評估指標。
- **mpUCCs (Maximal Partial Unique Column Combinations)**：最大部分唯一欄位組合，用於先進的指認性風險評估的理論基礎。

## N

- **NPV (Negative Predictive Value)**：陰性預測值，預測為陰性中實際為陰性的比例。

## P

- **PETsARD (Privacy-Enhanced Technology for Synthetic Assessment Reporting and Decision)**：隱私強化技術合成評估報告決策系統，國家資通訊安全研究院開發的開源合成資料評測框架。
- **PPV (Positive Predictive Value)**：陽性預測值，即精確率，預測為陽性中實際為陽性的比例。
- **PR AUC**：Precision-Recall 曲線下面積，適用於不平衡資料集的評估指標。
- **Precision**：精確率，預測為正例中實際為正例的比例。

## R

- **R² Score**：決定係數，衡量迴歸模型解釋變異量的指標。
- **Recall**：召回率，實際為正例中被正確預測的比例，又稱敏感度。
- **RMSE (Root Mean Squared Error)**：均方根誤差，迴歸任務的評估指標。
- **ROC AUC**：接收者操作特徵曲線下面積，分類模型的綜合表現指標。

## S

- **SDMetrics**：SDV 生態系的評測工具，用於評估合成資料的品質、保真度和診斷報告。
- **SDV (Synthetic Data Vault)**：一套開源的合成資料生成框架，提供多種合成演算法。
- **Sensitivity**：敏感度，即召回率，實際為正例中被正確預測的比例。
- **SMOTE**：合成少數類別過採樣技術，用於處理不平衡資料。
- **SMOTE-ENN**：結合 SMOTE 與 Edited Nearest Neighbors 的不平衡資料處理方法，先過採樣再清理邊界樣本。
- **SMOTE-Tomek**：結合 SMOTE 與 Tomek Links 的不平衡資料處理方法，先過採樣再移除 Tomek 連結。
- **Specificity**：特異度，實際為負例中被正確預測為負的比例。

## T

- **TVAE (Tabular Variational Autoencoder)**：使用變分自編碼器的表格資料合成方法，注重資料分布特徵。

## X

- **XGBoost**：在 PETsARD MLUtility V2 中用於分類和迴歸任務的梯度提升決策樹演算法。


## ㄊ

- **推斷性風險 (Inference Risk)**：敏感資訊可被推斷出的風險程度，評估是否能從已知資訊推斷出其他屬性。

- **離散化 (Discretization)**：將連續數值轉換為類別資料的前處理技術，如 K-bins 離散化。
- **列聯表 (Contingency Table)**：顯示兩個類別變數間關係的交叉表格。
- **連結性風險 (Linkability Risk)**：不同資料來源間記錄可被連結的風險程度，評估是否能連結不同資料集中的相同個體。
- **領域轉移 (Domain Transfer)**：在 PETsARD MLUtility 中，評估用合成資料訓練的模型在真實資料上的部署效能。
- **輪廓係數 (Silhouette Coefficient)**：評估聚類品質的指標，範圍從 -1 到 1。


## ㄏ

- **合成器 (Synthesizer)**：在 PETsARD 中指生成合成資料的核心系統模組，整合 SDV、自定義等各種合成演算法。
- **合成資料 (Synthetic Data)**：透過機器學習模型生成的人工資料，保留原始資料的統計特性但不包含真實個體資訊。
- **後處理 (Postprocessing)**：在 PETsARD 中指合成資料生成後的還原處理步驟，將經過前處理轉換的資料還原為原始格式。
- **迴歸任務 (Regression)**：機器學習中預測連續數值的任務類型。

## ㄍ

- **高斯耦合 (Gaussian Copula)**：PETsARD 預設使用的合成方法，利用高斯分布和 Copula 函數保留資料間的相關性結構。

## ㄗ

- **載入器 (Loader)**：在 PETsARD 中指負責讀取和載入資料的系統模組，支援多種檔案格式和基準資料集。

## ㄐ

- **基數 (Cardinality)**：類別欄位中不同數值的數量。高基數表示類別值很多，低基數表示類別值較少。
- **基準資料集 (Benchmark Dataset)**：用於測試和驗證的標準資料集，如 Adult Income Dataset。
- **極端值處理 (Outlier Handling)**：識別並處理資料中異常值的技術，包括 Z-score、IQR、LOF 等方法。
- **架構 (Schema)**：在 PETsARD 中指定義資料結構的詮釋資料，包括欄位型別、約束和關係。
- **交叉驗證 (Cross-Validation)**：評估模型泛化能力的技術，將資料分成多個折進行訓練和驗證。
- **均勻編碼 (Uniform Encoding)**：由 Datacebo 提出的類別變數處理方法，將離散類別值映射到連續的 [0,1] 區間，保留類別分布的統計特性。
- **聚類任務 (Clustering)**：機器學習中將資料分組的無監督學習任務。

## ㄑ

- **全變差距離 (Total Variation Distance, TVD)**：測量兩個機率分佈差異的統計量。
- **詮釋資料 (Metadata)**：描述資料特性的資訊，包括欄位型別、分佈、約束條件等。
- **詮釋資料管理器 (Metadater)**：在 PETsARD 中指負責管理和維護資料架構資訊的核心系統元件，統一處理所有模組的詮釋資料需求。
- **前處理 (Preprocessing)**：在 PETsARD 中指資料合成前的準備處理步驟，包括遺失值處理、異常值處理、編碼、縮放等。

## ㄎ

- **控制資料 (Control Data)**：在 PETsARD 評測中指未用於合成、保留作為獨立測試的資料集。
- **控制組 (Control Group)**：在隱私風險評估中用於比較的基準資料集。

## ㄒ

- **相關係數 (Correlation Coefficient)**：衡量兩個變數線性關係強度的統計量。


## ㄔ

- **差分隱私 (Differential Privacy)**：一種數學定義的隱私保護方法，確保個體資訊不會被洩露。
- **尺度轉換 (Scaling)**：調整數值範圍的前處理技術，包括標準化、最小最大縮放、時間錨定縮放等。

## ㄌ

- **粒度 (Granularity)**：在 PETsARD 報告中指評測結果的層級，包括 global、columnwise、pairwise、details、tree 等。

## ㄕ

- **時間定錨 (Time Anchoring)**：處理多時間點資料的方法，將最重要的時間欄位設為錨點，其他時間點轉化為相對時間差。
- **實用性 (Utility)**：合成資料在機器學習任務中的表現能力。
- **實驗元組 (Experiment Tuple)**：在 PETsARD 中由模組名稱和實驗名稱組成的識別對，格式為 (module_name, experiment_name)。
- **實驗重複 (Experiment Repetition)**：在 PETsARD 中為確保結果可靠性而多次執行相同實驗的機制。
- **雙模型控制 (Dual Model Control)**：同時使用原始資料和合成資料訓練模型，在控制資料上比較表現的實驗設計。

## ㄓ

- **執行器 (Executor)**：在 PETsARD 中指管線的主要執行介面，是 PETsARD 系統的核心控制元件，負責協調所有模組的執行流程。
- **指認性風險 (Singling Out Risk)**：個體記錄可被單獨識別出的風險程度，評估是否能從資料中識別出特定個體。
- **直接識別欄位 (Direct Identifier)**：可直接識別個體身份的欄位，如身分證號、姓名等。
- **主鍵 (Primary Key)**：資料表中唯一識別每筆記錄的欄位。
- **準識別符 (Quasi-identifier, QID)**：雖非直接識別符，但結合後可能識別出個體的欄位組合。

## ㄈ

- **反正規化 (Denormalization)**：將多個關聯表格合併成單一寬表的資料庫處理技術，用於簡化多表格資料的合成。
- **分割器 (Splitter)**：在 PETsARD 中指將資料分割為訓練集和驗證集的系統模組，支援隱私評估所需的多次分割。
- **分類任務 (Classification)**：機器學習中預測類別標籤的任務類型。

## ㄆ

- **配置 (Config)**：在 PETsARD 中指管理實驗設定的系統元件，負責處理 YAML 配置檔案並協調各模組執行。
- **評測器 (Evaluator)**：在 PETsARD 中指執行隱私、保真度、實用性評估的系統模組，整合 Anonymeter、SDMetrics 等第三方工具。

## ㄉ

- **獨熱編碼 (One-Hot Encoding)**：將每個類別值轉換為獨立二元特徵的編碼方法，適用於無序類別變數。
- **對數轉換 (Log Transformation)**：使用對數函數轉換偏態分布資料的前處理技術。

## ㄅ

- **報告器 (Reporter)**：在 PETsARD 中指生成和儲存實驗結果報告的系統模組，支援多種輸出格式。
- **保真度 (Fidelity)**：合成資料與原始資料在統計分佈上的相似程度。
- **標籤編碼 (Label Encoding)**：將類別值轉換為連續整數的編碼方法，適用於有序類別變數。
- **邊界一致性 (Boundary Adherence)**：數值或日期欄位是否在原始資料的上下界內。
- **平衡準確率 (Balanced Accuracy)**：考慮類別不平衡的分類準確率指標。
- **布萊爾分數 (Brier Score)**：評估機率預測準確性的指標，越小越好。

## ㄧ

- **異常值 (Outlier)**：偏離資料正常分佈的極端值。
- **遺失值處理 (Missing Value Handling)**：處理資料缺失的技術，包括刪除、平均值填補、眾數填補、中位數填補等方法。
- **遺失值群組約束 (NaN Groups)**：處理遺失值的約束規則，包括刪除、填充或複製等操作。
- **隱私保護力 (Privacy Protection)**：資料處理後防止個體資訊洩露的程度。
- **有效性 (Validity)**：資料是否準確反映基本特性和結構的程度。

## ㄇ

- **描述器 (Describer)**：在 PETsARD 中指分析和描述資料統計特性的系統模組，生成資料概覽報告。
- **命名策略 (Naming Strategy)**：在 PETsARD Reporter 中控制輸出檔名格式的設定，包括 traditional 和 compact 兩種模式。
- **模型參數 (Model Parameters)**：機器學習模型的內部配置，如神經網路的權重。
- **模型超參數 (Hyperparameters)**：控制模型訓練過程的外部設定，如學習率、批次大小。

## ㄨ

- **外部合成 (External Synthesis)**：使用 PETsARD 以外的工具或方法生成的合成資料。PETsARD 可以載入這些外部生成的合成資料，並使用內建的評測框架進行品質評估，協助比較不同合成方法的效果。

## ㄩ

- **約束器 (Constrainer)**：在 PETsARD 中指執行約束條件檢查和強制的系統模組。
- **約束條件 (Constraints)**：在 PETsARD 中指確保合成資料符合業務規範的規則系統，包括欄位約束、欄位組合約束、遺失值群組約束等。
- **原始資料 (Original Data)**：在 PETsARD 中指用於訓練合成模型的資料集，可能是真實資料或經過處理的資料。
- **預設合成 (Default Synthesis)**：PETsARD 系統提供的預設合成資料生成方法，使用 SDV 的 Gaussian Copula 模型。
- **預設評測 (Default Evaluation)**：PETsARD 系統提供的預設評估方法，包含隱私、保真度和實用性三個面向的基本指標。
- **閾值 (Threshold)**：決策邊界值，用於將連續預測值轉換為類別標籤。