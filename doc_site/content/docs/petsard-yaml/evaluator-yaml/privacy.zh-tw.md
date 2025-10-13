---
title: "隱私保護力評測"
weight: 142
---

評測資料處理後的隱私保護程度，模擬三種隱私攻擊情境。評測工具使用 Anonymeter，這是一套由 [Statice](https://www.statice.ai/) 開發的 Python 函式庫，專門用於評估合成表格資料的隱私風險。此工具實作了歐盟個人資料保護指令第29條工作小組 (WP29) 於 2014 年提出的匿名化技術評估標準，並於 2023 年獲得法國國家資訊自由委員會 (CNIL) 的認可。

## 評測架構

Anonymeter 從三個面向評估隱私風險：

### 指認性風險 (Singling Out Risk)
評估從資料中識別出特定個體的可能性。例如：「能找出唯一具有特徵 X、Y、Z 的個體」。

### 連結性風險 (Linkability Risk)
評估連結不同資料集中相同個體紀錄的可能性。例如：「能判斷紀錄 A 和 B 屬於同一人」。

為處理混合資料類型，此評測使用高爾距離 (Gower's Distance)：
- 數值變數：歸一化後的絕對差值
- 類別變數：不相等時距離為 1

### 推斷性風險 (Inference Risk)
評估從已知特徵推斷其他屬性的可能性。例如：「具有特徵 X 和 Y 的人，其特徵 Z 為何」。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/privacy.ipynb)

### 指認性風險

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
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Evaluator:
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 400          # 攻擊次數（預設：2,000）
    n_cols: 3               # 每次查詢欄位數（預設：3）
    max_attempts: 4000      # 最大嘗試次數（預設：500,000）
```

### 連結性風險

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
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Evaluator:
  linkability_risk:
    method: anonymeter-linkability
    max_n_attacks: true      # 使用控制資料集大小（預設：true）
    n_neighbors: 1           # 最近鄰數量（預設：1）
    aux_cols:                # 輔助欄位（預設：None）
      -                      # 第一組：公開資料欄位
        - workclass
        - education
        - occupation
        - race
        - gender
      -                      # 第二組：私密資料欄位
        - age
        - marital-status
        - relationship
        - native-country
        - income
```

### 推論性風險

```yaml
Evaluator:
  inference_risk:
    method: anonymeter-inference
    max_n_attacks: true      # 使用控制資料集大小（預設：true）
    secret: income           # 要推論的敏感欄位（必要）
```

## 參數說明

### 指認性風險參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|-----|------|--------|--------|------|
| **method** | `string` | 必要 | - | 固定值：`anonymeter-singlingout` |
| **n_attacks** | `integer` | 選用 | 2,000 | 攻擊執行次數<br>建議：統一設為 2,000 |
| **n_cols** | `integer` | 選用 | 3 | 每個查詢使用的欄位數量<br>建議：使用 3 個欄位的多變量模式 |
| **max_attempts** | `integer` | 選用 | 500,000 | 尋找成功攻擊的最大嘗試次數<br>建議：僅在執行時間過久時減少 |

{{< callout type="info" >}}
**運算效率注意事項**：由於 anonymeter 的 singling out 僅是做反覆取出放回的攻擊嘗試，如果資料本身不可能達成預期的攻擊次數，也沒有檢查機制，仍然會試圖抽滿最大嘗試，造成巨大的運算時間負擔。

**資安院建議的經驗法則**：
- **n_attacks**：介於 100 到 n_rows/100 之間
- **max_attempts**：介於 1,000 到 n_rows/10 之間
{{< /callout >}}

### 連結性風險參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|-----|------|--------|--------|------|
| **method** | `string` | 必要 | - | 固定值：`anonymeter-linkability` |
| **n_attacks** | `integer` | 選用 | None | 攻擊執行次數<br>當 max_n_attacks=true 時可省略<br>**注意**：當 max_n_attacks 為 true 時會被忽略 |
| **max_n_attacks** | `boolean` | 選用 | true | 是否自動調整 n_attacks 以符合控制資料集大小<br>**設為 false**：使用設定的 n_attacks 值（必須指定 n_attacks）<br>**設為 true（預設）**：忽略 n_attacks 設定，改用控制資料集大小 |
| **aux_cols** | `array` | 選用 | None | 輔助資訊欄位<br>格式：兩個互不重複的列表，模擬不同單位持有資料<br>**欄位選擇指引**：將資料欄位名稱分成兩個列表，分法主要基於對相關系統、功能和業務的理解。這種分法模擬了資料被不同單位持有或釋出的情境，其中攻擊者試圖連結這兩部分資料之間的關係。不需要包含所有變數，但建議至少應涵蓋關鍵變數。這種設置有助於評估在實際場景中，資料可能面臨的連結性攻擊風險。 |
| **n_neighbors** | `integer` | 選用 | 1 | 考慮的最近鄰數量<br>**建議**：設為最嚴格的 1。連結性屬於較困難的攻擊模式，在查找最接近的資料失敗後，其他較不接近的資料似無立即風險。 |

### 推論性風險參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|-----|------|--------|--------|------|
| **method** | `string` | 必要 | - | 固定值：`anonymeter-inference` |
| **n_attacks** | `integer` | 選用 | None | 攻擊執行次數<br>當 max_n_attacks=true 時可省略<br>**注意**：當 max_n_attacks 為 true 時會被忽略 |
| **max_n_attacks** | `boolean` | 選用 | true | 是否自動調整 n_attacks 以符合控制資料集大小<br>**設為 false**：使用設定的 n_attacks 值（必須指定 n_attacks）<br>**設為 true（預設）**：忽略 n_attacks 設定，改用控制資料集大小 |
| **secret** | `string` | 必要 | - | 要推論的敏感欄位名稱<br>建議：使用建模目標欄位（Y）或最機敏欄位 |
| **aux_cols** | `array` | 選用 | 除 secret 外的所有欄位 | 用於推論的欄位列表 |

### 其他

{{< callout type="info" >}}
**缺失值處理**

對於 Linkability 和 Inference 攻擊，PETsARD 會自動處理缺失值：
- **類別型欄位**：缺失值填充為字串 "missing"
- **數值型欄位**：欄位轉換為 float64 型別，缺失值填充為 -999999

這確保與 anonymeter 評估函數的相容性，因為 numba JIT 編譯需要一致的資料類型。
{{< /callout >}}

{{< callout type="warning" >}}
**常見警告與解決方案**

如果您遇到類似以下的警告訊息：
```
Reached maximum number of attempts 4000 when generating singling out queries.
Returning 1 instead of the requested 400.
Attack `multivariate` could generate only 1 singling out queries out of the requested 400.
```

**這代表的意義**：資料的獨特組合太少，無法產生足夠多的不同攻擊查詢。這通常發生在：
- 資料集太小
- 欄位的基數太低（唯一值太少）
- 欄位間高度相關，限制了獨特組合的數量

**解決方案**：
1. **減少 n_attacks**：對小資料集設定較小的值（例如 100-500）
2. **增加 max_attempts**：允許更多嘗試來找到獨特查詢（但會增加運算時間）
3. **調整 n_cols**：嘗試每次查詢使用較少的欄位（例如 2 個而非 3 個）
4. **接受限制**：如果警告持續出現，表示資料本質上的攻擊面有限，這實際上可能代表較好的隱私保護
{{< /callout >}}

## 評估指標

| 指標 | 說明 | 數值範圍 | 建議標準 |
|-----|------|---------|---------|
| **risk** | 隱私風險分數<br>計算：`(主要攻擊率 - 控制攻擊率) / (1 - 控制攻擊率)` | 0-1 | < 0.09¹ |
| **attack_rate** | 主要隱私攻擊率（使用合成資料推斷訓練資料的成功率） | 0-1 | - |
| **baseline_rate** | 基線隱私攻擊率（隨機猜測的成功率基準） | 0-1 | - |
| **control_rate** | 控制隱私攻擊率（使用合成資料推斷控制資料的成功率） | 0-1 | - |

## 風險計算詳解

### 隱私風險分數公式

隱私風險分數量化合成資料帶來的額外風險：

$$
\text{隱私風險} = \frac{\text{主要攻擊率} - \text{控制攻擊率}}{1 - \text{控制攻擊率}}
$$

此公式衡量：
- **分子**：合成資料帶來的額外風險（相對於控制組）
- **分母**：理想攻擊的最大效果（相對於控制組）

分數範圍為 0-1，越高代表隱私風險越大。

### 攻擊成功率計算

攻擊成功率使用威爾遜分數計算，提供更準確的統計結果：

$$
\text{攻擊率} = \frac{N_{\text{成功}} + \frac{Z^2}{2}}{N_{\text{總數}} + Z^2}
$$

其中：
- N_成功：成功攻擊次數
- N_總數：總攻擊次數
- Z：95% 信心水準的 Z 分數 (1.96)

### 三種攻擊率說明

1. **主要攻擊率** (Main Attack Rate)：使用合成資料推斷原始訓練資料的成功率

2. **基線攻擊率** (Baseline Attack Rate)：隨機猜測的成功率
   - 如果主要攻擊率 ≤ 基線攻擊率，表示評測結果無意義
   - 可能原因：攻擊次數不足、輔助資訊太少、資料本身問題

3. **控制攻擊率** (Control Attack Rate)：使用合成資料推斷控制組資料（保留集）的成功率

## 參考文獻

1. Personal Data Protection Commission Singapore. (2023). *Proposed guide on synthetic data generation*. https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/proposed-guide-on-synthetic-data-generation.pdf

2. Article 29 Working Party. (2014). *Opinion 05/2014 on Anonymisation Techniques* (WP216). https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf

3. Anonymeter GitHub Repository. https://github.com/statice/anonymeter

4. French Data Protection Authority (CNIL). https://www.cnil.fr/en/home

## 注意事項

{{< callout type="warning" >}}
Anonymeter 計算的風險僅是各攻擊模式的其中一套評測方式，0.0 不代表完全沒風險。為避免「先收集、後解密」(HNDL) 的潛在風險，使用者需對結果持保留態度。
{{< /callout >}}

- 若主要攻擊率 ≤ 基線攻擊率，評測不適合參考
- 可能原因：攻擊次數過少、輔助資訊不足、資料特性問題
- 建議結合其他保護措施來保護合成資料