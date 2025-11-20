---
title: "mpUCCs 隱私風險評估（實驗性功能）"
type: docs
weight: 696
prev: docs/petsard-yaml/evaluator-yaml/utility
next: docs/petsard-yaml/evaluator-yaml/privacy-mpuccs
---

{{< callout type="warning" >}}
**實驗性功能**：mpUCCs 是一個仍在開發中的實驗性隱私風險評估方法。API 和行為可能在未來版本中改變。
{{< /callout >}}

使用最大部分唯一欄位組合（Maximal Partial Unique Column Combinations, mpUCCs）評估隱私風險，這是一種進階的單挑風險評估演算法，能識別可唯一識別記錄的欄位組合。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/privacy-mpuccs.ipynb)
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
  mpuccs_assessment:
    method: mpuccs
    max_baseline_cols: 2        # 要評估的最大欄位數（預設：null = 所有欄位）
    min_entropy_delta: 0.01     # 最小熵增益閾值（預設：0.0）
    field_decay_factor: 0.5     # 欄位組合加權衰減（預設：0.5）
    renyi_alpha: 2.0            # Rényi 熵參數（預設：2.0）
    numeric_precision: null     # 自動偵測或指定小數位數（預設：null）
    datetime_precision: null    # 自動偵測或指定時間精度（預設：null）
    calculate_baseline: true     # 計算基線保護指標（預設：true）
```

## 概述

mpUCCs（最大部分唯一欄位組合）實作了基於以下理論的進階隱私風險評估：
- **理論基礎**：mpUCCs = QIDs（準識別符）
- **核心概念**：單挑攻擊尋找合成資料中的唯一欄位組合，這些組合對應到原始資料中的唯一記錄
- **優勢**：透過只關注最大組合來避免過度估計
- **框架**：實作基於 SAFE 框架的三層保護指標

### 主要特點
1. 基於熵值修剪的漸進式樹狀搜尋
2. 自動處理數值和日期時間欄位的精度
3. 使用欄位衰減因子的加權風險計算
4. 完善的進度追蹤
5. **三層保護指標**：
   - 主要保護：直接對抗識別的保護
   - 基線保護：基於屬性分佈的理論保護
   - 整體保護：標準化保護分數（0-1）

## 理論基礎

### 核心概念

#### UCC (Unique Column Combinations，唯一欄位組合)
UCC 是指在資料集中的所有記錄上，此欄位組合的值都是唯一的，沒有重複。

**範例：**
對於門牌資料，地址是唯一值。而地址也可視為縣市、鄉鎮、道路、與門牌的唯一值組合。

#### pUCC (Partial Unique Column Combinations，部分唯一欄位組合)
pUCC 則是只有在特定條件或特定值的情況下才具有唯一性，而不是在全部資料集上都唯一。

**範例：**
在大部分情況，路街名、門牌號碼不是唯一的，因為在不同鄉鎮市具有許多重名的街道，只有 (1.) 特殊的道路名稱 或 (2.) 特殊的門牌號碼，才會是唯一值。

#### mpUCCs (Maximal Partial Unique Column Combinations，最大部分唯一欄位組合)
mpUCCs 指具有最大形式 (Maximal form) 的 pUCCs，意味著不存在比它更小的子集能達到相同的識別效果。

**範例：**
對於「忠孝東路」「一段」「1號」，由於其他縣市也有忠孝東路，精簡任何欄位屬性都無法達到唯一識別，此時即為 mpUCCs。

### 關鍵理論洞察

#### mpUCCs = QIDs (準識別符)
指認性攻擊的本質是：
1. 在合成資料中識別出一個獨特的欄位組合
2. 該組合在原始資料中也僅對應到一個獨特記錄

本質上可視為找 pUCC 之後，比對是否也為 pUCC。

#### 自包含匿名性 (Self-contained Anonymity)
當資料集中沒有任何特徵組合 (IDs + QIDs) 能唯一識別原始實體時，該資料集被視為匿名化。

**尋找 QIDs (Find-QIDs problem) 即為發現 mpUCCs！**

重複計算非最大形式的欄位組合會高估風險 - 此即指認性風險具集合意義的反面表述！

## 演算法實現

### Find-QIDs 問題的困難

1. 對於 k 個屬性，潛在的 QIDs 為 2^k - 1 組
2. 被證明為 W[2]-complete 問題 (Bläsius et al., 2017)
3. 問題沒有最優子結構，故沒辦法動態規劃

**範例：** 知道 {A, B} 跟 {B, C} 並沒有 pUCCs，並不等於 {A, B, C} 沒有。

### 我們的解決方案：啟發式貪婪基數優先演算法

#### 1. 以高基數欄位為優先
- 計算所有欄位的基數
- 對於數值型欄位，依最低精度四捨五入
- 欄位組合廣度優先：由少到多，高基數先進

#### 2. 對欄位跟值域組合做集合運算
- 運用 `collections.Counter` 抓僅有一筆的合成資料值域組合
- 比對出同樣值域組合且僅有一筆的原始資料
- 紀錄對應之原始與合成資料索引

#### 3. 剪枝策略
若該欄位組合所有值域組合都唯一且碰撞，則跳過其超集。

#### 4. 遮罩機制
對於已被高基數少欄位識別過的合成資料，該列不再碰撞。

#### 5. 基於條件熵的早停機制
我們基於過去對於功能相依 (Functional Dependencies) 的資訊熵研究 (Mandros et al., 2020)，提出以下的演算法：

**對於 k ≥ 2 的欄位組合：**

1. **欄位組合熵** H(XY) = entropy(Counter(syn_data[XY]) / syn_n_rows)
2. **條件熵** H(Y|X) = Σ p(X = x)*H(Y | X = x)，其中 x ∈ {pUCC, ¬pUCC}
3. **互資訊** I(X; Y) = H(Y) - H(Y|X)

**早停：** 如果互資訊為負，則後續繼承的欄位組合不再確認。

#### 6. Rényi 熵（α=2，碰撞熵）
我們使用 Rényi 熵而非 Shannon 熵，以更好地進行碰撞機率分析：

- **理論最大熵** = log(n_rows)
- **合成資料最大熵** = scipy.stats.entropy(Counter(syn_data))
- **欄位組合熵** = scipy.stats.entropy(Counter(syn_data[column_combos]))
- **正規化** = 合成資料最大熵 - 欄位組合熵

## 參數說明

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|-----|------|--------|--------|------|
| **method** | `string` | 必要 | - | 固定值：`mpuccs` |
| **max_baseline_cols** | `int`、`null` | 選用 | null | 要評估和計算基線的最大欄位數<br>- `null`（預設）：評估所有可能的組合（1 到總欄位數）<br>- `int`：評估從 1 到 n 欄位的組合<br>範例：5 = 只評估 1、2、3、4、5 欄位組合<br>**同時控制評估範圍和基線計算**<br>適用於限制多欄位資料集的計算量 |
| **min_entropy_delta** | `float` | 選用 | 0.0 | 修剪用的最小熵增益閾值<br>較高值 = 更積極的修剪 |
| **field_decay_factor** | `float` | 選用 | 0.5 | 欄位組合加權的衰減因子<br>降低較大組合的權重 |
| **renyi_alpha** | `float` | 選用 | 2.0 | Rényi 熵計算的 alpha 參數<br>- α=0：Hartley 熵（最大熵）<br>- α=1：Shannon 熵<br>- α=2：碰撞熵（預設）<br>- α→∞：最小熵<br>較高的 α 值會給予頻繁值更多權重 |
| **numeric_precision** | `int`、`null` | 選用 | null | 數值欄位比較的精度<br>- `null`：自動偵測<br>- `int`：小數位數 |
| **datetime_precision** | `string`、`null` | 選用 | null | 日期時間欄位比較的精度<br>- `null`：自動偵測<br>- 選項：'D'、'H'、'T'、's'、'ms'、'us'、'ns' |
| **calculate_baseline** | `boolean` | 選用 | true | 啟用基線保護指標計算<br>基於屬性值分佈 |

### 日期時間精度選項
- `D`：天
- `H`：小時
- `T`：分鐘
- `s`：秒
- `ms`：毫秒
- `us`：微秒
- `ns`：奈秒

## 資料前處理細節

MPUCCs 執行多個前處理步驟以確保準確的隱私風險評估：

### 缺失值處理
- **NA 比較**：比較值時，`pd.NA`（pandas 缺失值）會被單獨處理
- **安全比較**：使用 `fillna(False)` 將 NA 比較結果轉換為布林遮罩中的 False
- **備援邏輯**：對於邊緣情況，透過明確的 NA 檢查來迭代處理值

### 精度處理

#### 數值精度
- **自動偵測**：自動偵測浮點數的小數位數
- **四捨五入**：使用 `round()` 對指定的小數位數進行一致的四捨五入
- **整數保留**：整數欄位保持不變

#### 日期時間精度
- **自動偵測**：偵測最小時間精度（日、小時、分鐘、秒、毫秒、微秒、奈秒）
- **向下取整**：使用 `dt.floor()` 向下取整到指定精度
- **不區分大小寫**：支援各種精度格式輸入（例如：'D'、'd'、'H'、'h'）

### 去重複化
- **完全重複**：分析前移除完全重複的資料列
- **索引重設**：去重複後重設 DataFrame 索引
- **記錄日誌**：報告移除的重複資料數量

### 欄位處理順序
- **基於基數**：按唯一值數量（降序）排序欄位
- **高基數優先**：優先處理具有較多唯一值的欄位
- **效率考量**：此順序通常能更快識別並達到更好的剪枝效果

## 評估結果

mpUCCs 回傳三種類型的結果：

### 1. 全域統計（`global`）
簡化的隱私風險指標，採用方案 B（三層保護架構）：

#### 核心指標（依重要性排序）
當 `calculate_baseline=true` 時：
1. **`privacy_risk_score`** ⭐ - 整體隱私風險（0=安全，1=危險）
   - 公式：`1 - overall_protection`
   - **決策時最重要的指標**

2. **`overall_protection`** - 標準化保護分數（0-1）
   - 公式：`min(main_protection / baseline_protection, 1.0)`
   - 比較實際保護與理論最佳值

3. **`main_protection`** - 直接對抗識別的保護
   - 公式：`1 - identification_rate`
   - 合成資料提供的原始保護

4. **`baseline_protection`** - 資料結構的理論保護
   - 基於屬性基數（cardinality）
   - 代表完全隨機資料的保護能力

5. **`identification_rate`** - 被識別記錄的比例
   - 公式：`identified_records / total_records`

6. **`total_identified`** - 被識別的記錄數
7. **`total_syn_records`** - 合成記錄總數

當 `calculate_baseline=false` 時：
- `identification_rate` - 主要風險指標
- `main_protection` - 簡單保護（1 - 識別率）
- `total_identified` - 被識別的記錄數
- `total_syn_records` - 合成記錄總數

### 2. 詳細結果（`details`）
簡化的碰撞資訊，採用風險優先排序：

#### 欄位順序（依重要性）
1. **`risk_level`** ⭐ - 風險分類（高/中/低）
   - 置於首位便於快速風險評估
2. **`syn_idx`** - 合成資料中的索引
3. **`ori_idx`** - 原始資料中的對應索引
4. **`combo_size`** - 識別組合的大小
5. **`field_combo`** - 使用的欄位組合
6. **`value_combo`** - 造成識別的實際值
7. **`baseline_protection`** - 此組合的基線保護（如果啟用）

#### 風險等級分類
- **高風險**：保護比率 < 0.3 或 combo_size ≤ 2
- **中風險**：保護比率 0.3-0.7 或 combo_size 3-4
- **低風險**：保護比率 > 0.7 或 combo_size ≥ 5

### 3. 樹狀搜尋結果（`tree`）
簡化的搜尋樹，將必要欄位置於前方：

#### 核心欄位（總是顯示）
1. **`check_order`** - 評估序號
2. **`field_combo`** - 測試的欄位組合
3. **`combo_size`** - 組合中的欄位數量
4. **`is_pruned`** - 組合是否被修剪（true/false）
5. **`mpuccs_cnt`** - 在合成資料中發現的唯一組合
6. **`mpuccs_collision_cnt`** - 成功識別的記錄數

#### 保護指標（如果啟用基線）
7. **`baseline_protection`** - 此組合的理論保護
8. **`overall_protection`** - 標準化保護分數（如果有碰撞）

#### 技術細節（僅在非預設設定時顯示）
這些欄位只在使用非預設熵值或衰減設定時出現：
- **`entropy`** - 組合熵值
- **`entropy_gain`** - 相對於基礎組合的熵改善
- **`field_weight`** - 此組合的權重因子
- **`weighted_collision`** - 加權碰撞數

{{< callout type="info" >}}
**簡化輸出**：樹狀結果現在優先顯示必要資訊。使用預設設定時隱藏技術細節以減少混亂。
{{< /callout >}}

## 最佳實踐

1. **從小組合開始**：從 `n_cols: [1, 2, 3]` 開始評估基本風險
2. **調整熵閾值**：增加 `min_entropy_delta` 以獲得更快的評估和更多修剪
3. **精度設定**：除非有特定需求，否則讓自動偵測處理精度
4. **解釋結果**：
   - 使用 `overall_protection` 進行標準化風險評估（0-1 範圍）
   - 比較 `main_protection` 與 `baseline_protection` 以了解風險來源
   - 關注 `privacy_risk_score` 用於主管報告

## 相較於 Anonymeter 的關鍵改進

### 1. 理論基礎
- **明確理論基礎**：mpUCCs = QIDs 提供堅實的數學基礎
- **避免風險高估**：專注於最大形式組合
- **集合論意義**：正確理解指認性風險的本質

### 2. 演算法優化
- **漸進式樹狀搜尋**：高效的欄位組合探索
- **基於熵的剪枝**：智能早停機制
- **基數優先處理**：高基數欄位優先處理
- **碰撞導向分析**：直接聚焦於實際隱私風險

### 3. 精度處理
- **自動數值精度檢測**：處理浮點數比較問題
- **日期時間精度支援**：適當處理時間資料
- **手動精度覆蓋**：允許自訂精度設定

### 4. 效能改進
- **更快執行**：在 adult-income 資料集上 44 秒 vs 12+ 分鐘
- **更好擴展性**：高效處理高維度資料
- **記憶體優化**：基於 Counter 的唯一性檢測

### 5. 全面進度追蹤
- **雙層進度條**：欄位層級和組合層級進度
- **詳細執行樹**：演算法決策的完整審計軌跡
- **剪枝統計**：優化決策的透明度

### 與 Anonymeter 的效能比較
| 指標 | Anonymeter | mpUCCs | 改進 |
|------|------------|--------|------|
| 執行時間 (adult-income, n_cols=3) | 12+ 分鐘 | 44 秒 | 16x 更快 |
| 指認性攻擊檢測 | ~1,000-2,000 (隨機抽樣) | 7,999 (完整評估) | 完整覆蓋 |
| 理論基礎 | 啟發式 | 數學理論 | 堅實理論 |
| 風險高估 | 高 | 低 | 準確評估 |
| 進度可見性 | 不支援 | 全面 | 完全透明 |
| 精度處理 | 不支援 | 自動 | 更好可用性 |

## 效能特性

### 計算複雜度
- **時間複雜度**：最壞情況 O(2^k)，但有顯著剪枝
- **空間複雜度**：O(n*k)，其中 n 為記錄數，k 為欄位數
- **實際效能**：由於剪枝，在真實資料集上為線性到次二次方

### 擴展性
- **欄位擴展性**：透過剪枝具有高度擴展性 - 能高效處理具有許多欄位的資料集
- **記錄擴展性**：在 100K+ 記錄的資料集上測試過
- **記憶體效率**：基於 Counter 的操作最小化記憶體使用

## 與傳統方法的比較

| 層面 | mpUCCs | 傳統單挑風險 |
|------|--------|--------------|
| **組合選擇** | 僅最大組合 | 所有組合 |
| **風險估計** | 更準確 | 可能過度估計 |
| **效能** | 使用修剪優化 | 窮舉搜尋 |
| **加權** | 欄位衰減因子 | 通常均勻 |
| **精度處理** | 內建 | 手動預處理 |
| **基線比較** | 三層保護 | 簡單識別率 |
| **風險標準化** | 0-1 範圍含基線 | 原始百分比 |

## 注意事項

{{< callout type="info" >}}
**效能考量**
- 具有許多欄位的大型資料集可能需要大量計算時間
- 使用 `n_cols` 參數限制組合大小
- 增加 `min_entropy_delta` 以進行更積極的修剪
{{< /callout >}}

{{< callout type="warning" >}}
**解釋指引**
- 分數 0.0 不代表零風險
- 結合其他隱私指標一起考慮結果
- 考慮「先收集、後解密」（HNDL）風險
{{< /callout >}}

## 風險閾值建議 🎯

### 執行摘要
對於大多數使用案例，我們建議目標為 **privacy_risk_score < 0.1**（相當於 overall_protection > 0.9）。

### 依使用案例的詳細風險閾值

| 使用案例 | 隱私風險分數 | 整體保護 | 建議 |
|---------|-------------|---------|------|
| **公開發布** | < 0.05 | > 0.95 | 風險極低，適合公開資料集 |
| **研究分享** | < 0.10 | > 0.90 | 低風險，適合研究合作 |
| **內部分析** | < 0.20 | > 0.80 | 可接受的內部使用（需存取控制） |
| **開發/測試** | < 0.30 | > 0.70 | 適合使用合成資料進行開發 |
| **高風險資料** | < 0.01 | > 0.99 | 醫療/金融資料需要最大保護 |

### 其他指標指引

#### 識別率閾值
- **優秀**：< 1% 記錄被識別
- **良好**：1-5% 記錄被識別
- **可接受**：5-10% 記錄被識別
- **不佳**：> 10% 記錄被識別

#### 基線保護考量
- 若 `baseline_protection > 0.95`：資料結構本身提供良好保護
- 若 `baseline_protection < 0.90`：考慮加入雜訊或概化屬性
- 若 `baseline_protection < 0.80`：高風險資料結構，需要顯著保護措施

### 依風險等級的緩解策略

{{< callout type="info" >}}
**高風險（privacy_risk_score > 0.3）**
- 加入差分隱私雜訊
- 概化或抑制高風險屬性
- 增加 k-匿名性參數
- 考慮使用完全合成資料
{{< /callout >}}

{{< callout type="warning" >}}
**中風險（0.1 < privacy_risk_score ≤ 0.3）**
- 檢視並概化準識別符
- 對稀有值進行針對性抑制
- 實施存取控制
- 監控使用模式
{{< /callout >}}

{{< callout type="success" >}}
**低風險（privacy_risk_score ≤ 0.1）**
- 適用標準發布程序
- 記錄所採取的隱私措施
- 建議定期重新評估
- 適合大多數使用案例
{{< /callout >}}

### 持續監控建議
1. **季度審查**：每 3 個月重新評估隱私指標
2. **資料漂移監控**：檢查資料分佈是否顯著改變
3. **攻擊演進**：根據新攻擊技術更新閾值
4. **法規更新**：根據新隱私法規調整閾值

## 理解簡化後的指標

### 為什麼隱私風險分數放在最前面？
**privacy_risk_score** 放在第一位，因為它是決策時最重要的單一指標：
- **0.0 - 0.1**：風險極低，可安全發布
- **0.1 - 0.3**：風險可接受，適合內部使用
- **0.3 - 0.5**：中等風險，需額外保護措施
- **0.5 - 1.0**：高風險，不建議發布

### 三層保護模型解釋

1. **隱私風險分數**（最高層 - 決策指標）
   - 主管需要知道的關鍵數字
   - 單一數值用於風險評估
   - 公式：`1 - 整體保護`

2. **整體保護**（標準化比較）
   - 比較合成資料品質與理論最佳值
   - 考慮資料結構的限制
   - 值為 1.0 表示「與隨機資料一樣好」

3. **主要 vs 基線保護**（詳細分析）
   - **主要**：實際達到的保護
   - **基線**：給定資料結構下的最大可能保護
   - 比率顯示合成品質

### 解讀範例
```
privacy_risk_score: 0.15     # 低風險（很好！）
overall_protection: 0.85      # 達到理論最大值的 85%
main_protection: 0.90         # 90% 記錄受保護
baseline_protection: 0.95     # 隨機資料可達 95% 保護
identification_rate: 0.10     # 10% 記錄被識別
total_identified: 100         # 100 筆記錄有風險
total_syn_records: 1000       # 總共 1000 筆
```
**結論**：合成資料表現良好（達到理論最佳的 85%），風險等級可接受（0.15）。

## 限制與未來工作

### 目前限制
1. **實驗狀態**：仍在積極開發和驗證中
2. **記憶體使用**：對於非常高維度的資料可能記憶體密集
3. **風險加權**：合乎學理的風險加權方式正在研究中，目前僅設定為 field_decay_factor = 0.5

### 未來增強
1. **分散式計算**：支援大資料集的平行處理（nice-to-have）

## 參考文獻

1. Abedjan, Z., & Naumann, F. (2011). Advancing the discovery of unique column combinations. In Proceedings of the 20th ACM international conference on Information and knowledge management (pp. 1565-1570).

2. Mandros, P., Kaltenpoth, D., Boley, M., & Vreeken, J. (2020). Discovering Functional Dependencies from Mixed-Type Data. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 1404-1414).

3. Bläsius, T., Friedrich, T., Lischeid, J., Meeks, K., & Schirneck, M. (2017). Efficiently enumerating hitting sets of hypergraphs arising in data profiling. In Proceedings of the 16th International Symposium on Experimental Algorithms (pp. 130-145).

## 支援與回饋

作為實驗性功能，mpUCCs 正在積極開發和改進中。我們歡迎回饋、錯誤報告和改進建議。請參考專案的問題追蹤器來報告問題或請求功能。