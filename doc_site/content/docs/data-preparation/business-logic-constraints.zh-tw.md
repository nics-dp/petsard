---
title: 商業邏輯約束資料
type: docs
weight: 330
prev: docs/data-preparation/multi-table-relationships
next: docs/data-preparation
---

適用於**需要確保業務規則**的情境。

透過 Constraints YAML 定義欄位間的邏輯關係、範圍限制與比例維護，確保合成資料符合業務規範。支援四種約束類型：遺失值群組、欄位約束、欄位組合、欄位比例。

> 如果您的資料**沒有特殊約束需求**，可以直接使用預設合成方式，參考[快速入門](../../getting-started)。

## Constraints YAML 範例

將以下內容儲存為 `business_constraints.yaml`：

```yaml
# 空值處理規則
nan_groups:
  # 當資本額為空時刪除整筆資料（企業基本資訊不完整）
  capital: 'delete'

# 欄位約束條件
field_constraints:
  # 時間邏輯約束：成立日期 < 第一次申請日期 <= 最新申請日期 < 最新追蹤日期
  - "established_date < first_apply_date"
  - "first_apply_date <= latest_apply_date"
  - "latest_apply_date < latest_track_date"

  # 數值關係約束：核准金額不超過申請金額
  - "latest_apply_amount_approved <= latest_apply_amount_requested"

  # 範圍約束
  - "capital > 0"  # 資本額必須為正
  - "latest_track_profit_ratio >= -1.0 & latest_track_profit_ratio <= 1.0"  # 利潤率範圍
  - "latest_apply_amount_requested > 0"  # 申請金額必須為正

# 欄位組合約束（正面表列）
field_combinations:
  # 申請狀態與核准金額的配對關係
  -
    - latest_apply_status: latest_apply_amount_approved
    - approved:  # 核准時必須有金額
        - 1000000
        - 5000000
        - 10000000
        - 20000000
      rejected:  # 拒絕時金額為空
        - "pd.NA"
      withdrawn:  # 撤回時金額為空
        - "pd.NA"

# 欄位比例維護
field_proportions:
  # 維護產業分布，容許 10% 誤差
  - fields: 'industry'
    mode: 'all'
    tolerance: 0.1

  # 維護風險等級分布，容許 5% 誤差
  - fields: 'latest_track_risk_level'
    mode: 'all'
    tolerance: 0.05
```

## 約束類型詳細說明

### nan_groups（遺失值群組約束）

定義當特定欄位為空值時的處理規則。

**`capital: 'delete'`**
- 說明：當 `capital` 欄位為空值時，刪除整筆資料
- 適用情境：某欄位為空時整筆資料無意義（如企業沒有資本額資訊）
- 處理方式：`delete`（刪除整筆）、`erase`（清除關聯欄位）、`copy`（複製其他欄位值）

### field_constraints（欄位約束）

定義單一或多欄位的數值範圍與邏輯關係。

**時間邏輯約束**
- `"established_date < first_apply_date"`
  - 說明：企業成立日期必須早於第一次申請日期
  - 適用情境：時間先後順序的業務邏輯

- `"first_apply_date <= latest_apply_date"`
  - 說明：第一次申請日期必須早於或等於最新申請日期
  - 適用情境：允許相等是因為可能只有一次申請

**數值關係約束**
- `"latest_apply_amount_approved <= latest_apply_amount_requested"`
  - 說明：核准金額不能超過申請金額
  - 適用情境：金融機構的基本審核原則

**範圍約束**
- `"capital > 0"`
  - 說明：資本額必須為正數
  - 適用情境：邏輯上不可能為零或負數的欄位

- `"latest_track_profit_ratio >= -1.0 & latest_track_profit_ratio <= 1.0"`
  - 說明：利潤率範圍在 -100% 到 100% 之間
  - 適用情境：比率類欄位的合理範圍
  - 語法：使用 `&`（AND）組合多個條件

### field_combinations（欄位組合約束）

定義欄位值之間的有效配對關係（正面表列）。

**申請狀態與核准金額配對**
```yaml
- 
  - latest_apply_status: latest_apply_amount_approved
  - approved: [1000000, 5000000, 10000000, 20000000]
    rejected: ["pd.NA"]
    withdrawn: ["pd.NA"]
```

- 說明：定義不同申請狀態允許的核准金額
- `approved`：核准狀態可以有具體金額（列出常見額度）
- `rejected`、`withdrawn`：拒絕或撤回狀態金額必須為空
- **注意**：這是正面表列，未列出的組合會被視為無效

**語法規則**
- 空值必須使用 `"pd.NA"`（注意大小寫）
- 字串值必須加引號如 `"approved"`
- 數值不需要引號

### field_proportions（欄位比例約束）

維護類別分布或空值比例接近原始資料。

**維護產業分布**
```yaml
- fields: 'industry'
  mode: 'all'
  tolerance: 0.1
```
- `fields`：要維護比例的欄位名稱
- `mode: 'all'`：維護所有類別的分布
- `tolerance: 0.1`：容許的誤差範圍（±10%）

**維護風險等級分布**
```yaml
- fields: 'latest_track_risk_level'
  mode: 'all'
  tolerance: 0.05
```
- `tolerance: 0.05`：更嚴格的容差（±5%）確保風險分布接近原始資料

**維護空值比例**
```yaml
- fields: 'workclass'
  mode: 'missing'
  tolerance: 0.03
```
- `mode: 'missing'`：僅維護遺失值（NA）的比例
- 適用情境：保持資料品質特徵

**注意**：此約束透過移除過量資料來達成比例，可能減少合成資料的總筆數。

## 使用方式

### 反覆抽樣模式（合成資料生成）

合成過程會自動過濾不符合約束的資料：

```yaml
Loader:
  data:
    filepath: 'denormalized_data.csv'
    schema: 'denormalized_schema.yaml'

Preprocessor:
  default:
    method: 'default'

Synthesizer:
  default:
    method: 'default'

Constrainer:
  apply_constraints:
    method: resample  # 或 auto（會自動判斷）
    constraints_yaml: 'business_constraints.yaml'
    target_rows: None  # 不指定則使用原始資料筆數
    sampling_ratio: 10.0  # 每次採樣為目標筆數的 10 倍
    max_trials: 300  # 最多嘗試 300 次

Postprocessor:
  default:
    method: 'default'

Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
```

### 驗證檢查模式（檢查現有資料）

如果要檢查原始資料或合成資料是否符合約束：

```yaml
Loader:
  original_data:
    filepath: 'denormalized_data.csv'
    schema: 'denormalized_schema.yaml'

Constrainer:
  check_constraints:
    method: validate
    source: Loader  # 指定要檢查的資料來源
    constraints_yaml: 'business_constraints.yaml'

Reporter:
  validation_report:
    method: save_validation
    output: 'data_validation'  # 輸出檔名前綴
    include_details: true  # 包含詳細違規記錄
```

這會產生三個 CSV 檔案：
- `data_validation_summary.csv`：總體統計（通過率、違規率等）
- `data_validation_violations.csv`：各約束的違規統計
- `data_validation_details.csv`：詳細違規記錄（每條規則最多 10 筆範例）

## 約束定義原則

實務上建議先與領域專家討論，確認業務規則中的硬性限制與資料品質要求。接著透過探索性資料分析識別約束模式，將識別的約束寫入 YAML 檔案。定義完成後，在 validate 模式下使用 Constrainer 檢查原始資料的符合情況。若違反比例過高（>5%），需要重新評估約束定義的合理性，並根據驗證結果逐步完善約束定義。

約束定義時需注意以下重要原則：

- 所有約束條件必須同時滿足（AND 邏輯）
- 四種約束類型的執行順序固定無法調整
- field_combinations 採用正面表列方式，只允許明確列出的組合
- 空值必須使用 `"pd.NA"`（注意大小寫）
- 字串值必須加引號如 `"approved"`
- field_constraints 支援 pandas 查詢語法，可以使用 `&`（AND）、`|`（OR）等運算子組合條件
