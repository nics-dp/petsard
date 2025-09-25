---
title: "隱私保護力評測"
weight: 142
---

評測資料處理後的隱私保護程度，模擬三種隱私攻擊情境。

## 配置範例

### Singling Out 風險

```yaml
Evaluator:
  singling_out_risk:
    method: anonymeter-singlingout
    n_attacks: 2000          # 攻擊次數（預設：2,000）
    n_cols: 3                # 每次查詢欄位數（預設：3）
    max_attempts: 500000     # 最大嘗試次數（預設：500,000）
```

### Linkability 風險

```yaml
Evaluator:
  linkability_risk:
    method: anonymeter-linkability
    n_attacks: 2000
    max_n_attacks: false
    aux_cols:
      -                         # 公開資料欄位
        - gender
        - zip_code
      -                         # 私密資料欄位
        - age
        - medical_history
    n_neighbors: 10
```

### Inference 風險

```yaml
Evaluator:
  inference_risk:
    method: anonymeter-inference
    n_attacks: 2000
    max_n_attacks: false
    secret: sensitive_column    # 要推論的敏感欄位（必要）
    aux_cols:                   # 用於推論的欄位（可選）
      - col1
      - col2
      - col3
```

## 參數說明

### 共同參數

- **method** (`string`, 必要參數)
  - `anonymeter-singlingout`：單挑風險
  - `anonymeter-linkability`：連結性風險
  - `anonymeter-inference`：推論風險

- **n_attacks** (`integer`)
  - 攻擊執行次數
  - 預設值：2,000
  - 建議：統一設為 2,000

### Singling Out 專用參數

- **n_cols** (`integer`)
  - 每個查詢使用的欄位數量
  - 預設值：3
  - 建議：使用 3 個欄位的多變量模式

- **max_attempts** (`integer`)
  - 尋找成功攻擊的最大嘗試次數
  - 預設值：500,000
  - 建議：僅在執行時間過久時減少

### Linkability 專用參數

- **max_n_attacks** (`boolean`)
  - 是否強制使用最大攻擊次數
  - 預設值：false

- **aux_cols** (`array`)
  - 輔助資訊欄位
  - 格式：兩個互不重複的列表，模擬不同單位持有資料

- **n_neighbors** (`integer`)
  - 考慮的最近鄰數量
  - 預設值：10
  - 建議：設為最嚴格的 1

### Inference 專用參數

- **secret** (`string`, 必要參數)
  - 要推論的敏感欄位名稱
  - 建議：使用建模目標欄位（Y）或最機敏欄位

- **aux_cols** (`array`)
  - 用於推論的欄位列表
  - 預設：除 secret 外的所有欄位

- **max_n_attacks** (`boolean`)
  - 是否強制使用最大攻擊次數
  - 預設值：false

## 評估指標

| 指標 | 說明 | 數值範圍 | 建議標準 |
|-----|------|---------|---------|
| **risk** | 隱私風險分數<br>計算：`(主要攻擊率 - 控制攻擊率) / (1 - 控制攻擊率)` | 0-1 | < 0.09¹ |
| **attack_rate** | 主要隱私攻擊率（使用合成資料推斷訓練資料的成功率） | 0-1 | - |
| **baseline_rate** | 基線隱私攻擊率（隨機猜測的成功率基準） | 0-1 | - |
| **control_rate** | 控制隱私攻擊率（使用合成資料推斷控制資料的成功率） | 0-1 | - |

## 參考文獻

¹ Personal Data Protection Commission Singapore. (2023). *Proposed guide on synthetic data generation*. https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/proposed-guide-on-synthetic-data-generation.pdf

## 注意事項

{{< callout type="warning" >}}
Anonymeter 計算的風險僅是各攻擊模式的其中一套評測方式，0.0 不代表完全沒風險。為避免「先收集、後解密」(HNDL) 的潛在風險，使用者需對結果持保留態度。
{{< /callout >}}

- 若主要攻擊率 ≤ 基線攻擊率，評測不適合參考
- 可能原因：攻擊次數過少、輔助資訊不足、資料特性問題
- 建議結合其他保護措施來保護合成資料