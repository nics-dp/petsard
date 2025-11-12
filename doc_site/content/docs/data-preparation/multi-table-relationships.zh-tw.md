---
title: 多表格關聯資料
type: docs
weight: 2
prev: docs/data-preparation/data-describing
next: docs/data-preparation/business-logic-constraints
---

適用於**資料分散在多個關聯表格**的情境。

在進行合成前需先使用資料庫反正規化技術整合多表，避免使用不成熟的多表格合成技術。根據下游任務選擇適當的顆粒度與聚合方式。

> 如果您的資料**已經整合為單一表格**，可以直接跳到[商業邏輯約束](../business-logic-constraints)。

## 個案背景

某政策性金融機構擁有豐富的企業融資相關數據，包含企業基本資訊、融資申請、財務變化等多面向歷史紀錄。機構希望透過合成資料技術來推動與金融科技業者的創新合作，讓第三方能在確保資料隱私的前提下，利用這些資料開發風險預測模型，協助機構提升風險管理效能。

### 資料特性

- **複雜的表格結構**：原始資料分散在多個業務系統的資料表中，涉及企業基本資料、申請紀錄、財務追蹤等不同面向
- **時序性資料**：包含多個關鍵時間點（如申請日期、核准日期、追蹤時間等），且這些時間點之間具有邏輯順序關係

### 資料表關聯與業務意義

本案例的資料結構反映了企業融資的完整業務流程，主要包含三個核心資料表：

**企業基本資料表**
- 包含企業識別碼、產業類別、子產業、地理位置和資本額等靜態資訊
- 每筆記錄代表一個獨立的企業實體
- 此表作為主表，與其他資料表形成一對多的關係

**融資申請紀錄表**
- 記錄企業向金融機構提出的每一次融資申請詳情
- 包含申請類型、申請日期、核准日期、申請狀態及金額等資訊
- 一個企業可能有多次融資申請，時間跨度可達數年
- 申請結果分為核准、拒絕和撤回三種狀態

**財務追蹤紀錄表**
- 記錄企業獲得融資後的財務表現追蹤資料
- 包含利潤率指標、追蹤時間範圍、營收指標及風險等級評估
- 每個融資申請可能產生多筆追蹤紀錄，代表不同時間點的財務狀況

這三個資料表之間形成層次性的關聯結構：企業基本資料(1) → 融資申請紀錄(N) → 財務追蹤紀錄(N)。在實際業務流程中，企業首先建立基本檔案，隨後提交融資申請，而每筆申請案件均會觸發財務追蹤機制。

### 模擬資料示範

考量資料隱私，以下使用模擬資料展示資料結構與商業邏輯。這些資料雖然是模擬的，但保留了原始資料的關鍵特性與業務限制：

#### 企業基本資料

| company_id | industry | sub_industry | city | district | established_date | capital |
|------------|----------|--------------|------|----------|------------------|---------|
| C000001 | 營建工程 | 環保工程 | 新北市 | 板橋區 | 2019-11-03 | 19899000 |
| C000002 | 營建工程 | 建築工程 | 臺北市 | 內湖區 | 2017-01-02 | 17359000 |
| C000003 | 製造業 | 金屬加工 | 臺北市 | 內湖區 | 2012-05-29 | 5452000 |

#### 融資申請紀錄

| application_id | company_id | loan_type | apply_date | approval_date | status | amount_requested | amount_approved |
|----------------|------------|-----------|------------|---------------|--------|------------------|-----------------|
| A00000001 | C000001 | 廠房擴充 | 2022-01-21 | 2022-03-19 | approved | 12848000 | 12432000.0 |
| A00000002 | C000001 | 營運週轉金 | 2025-01-05 | 2025-02-11 | approved | 2076000 | 1516000.0 |
| A00000004 | C000002 | 營運週轉金 | 2020-12-12 | NaN | rejected | 5533000 | NaN |

#### 財務追蹤紀錄

| application_id | profit_ratio_avg | tracking_months | last_tracking_date | avg_revenue | risk_level |
|----------------|------------------|-----------------|--------------------|--------------|-----------------------|
| A00000001 | 0.033225 | 3.0 | 2024-09-04 | 1.840486e+07 | high_risk |
| A00000002 | -0.002636 | 3.0 | 2027-07-31 | 1.926350e+07 | normal |

### 為何選擇反正規化而非多表格合成？

目前開源的多表格合成技術（如 SDV 的 HMA）雖然能夠直接處理多表格資料，但存在明顯限制：

1. **規模與複雜度限制**：最適合不超過 5 張表格且僅有一層父子關係的結構
2. **欄位類型限制**：主要支援數值欄位，類別欄位需要前處理
3. **約束處理限制**：複雜的業務邏輯約束支援不足
4. **品質問題**：實際測試顯示跨表相關性和類別變數關聯度偏低

相較之下，採用反正規化策略整合為單一寬表後：
- 可以使用成熟穩定的單表合成技術
- 能夠完整定義業務邏輯約束
- 合成品質更可控且可預測
- 明確保留業務邏輯關係

## 步驟 1：資料探索與分析

### 分析表格關聯結構

繪製 ER 圖（Entity-Relationship Diagram）理解表格間的關係：

- 識別主表與子表的關聯（一對多、多對多）
- 確認主鍵/外鍵的對應關係
- 觀察資料的時序性依賴

### 確認下游需求

與資料使用者（如資料科學家、業務分析師）討論分析目的：

- **企業級分析**：以企業為單位（一筆資料代表一家企業）
- **申請案分析**：以申請案為單位（一筆資料代表一次申請）
- **時間點分析**：以特定時間點為單位（一筆資料代表某個時間切面）

## 步驟 2：設計整合策略

### 選擇合適的顆粒度

延續上述企業融資個案，若下游任務關心每家企業的整體風險評估，適合的顆粒度為「一筆資料一家企業」。我們將整合以下資訊：

**企業基本資料**（直接帶入）
- 企業識別碼 (`company_id`)
- 產業類別 (`industry`)、子產業 (`sub_industry`)
- 城市 (`city`)、行政區 (`district`)
- 資本額 (`capital`)
- 成立日期 (`established_date`)

**第一次申請記錄**（保留時序起點）
- 申請日期 (`first_apply_date`)
- 申請類型 (`first_apply_loan_type`)
- 申請金額 (`first_apply_amount_requested`)
- 核准金額 (`first_apply_amount_approved`)
- 申請狀態 (`first_apply_status`)

**最新申請記錄**（反映當前狀態）
- 申請日期 (`latest_apply_date`)
- 申請類型 (`latest_apply_loan_type`)
- 申請金額 (`latest_apply_amount_requested`)
- 核准金額 (`latest_apply_amount_approved`)
- 申請狀態 (`latest_apply_status`)

**最新財務追蹤**（當前財務健康度）
- 追蹤日期 (`latest_track_date`)
- 平均利潤率 (`latest_track_profit_ratio_avg`)
- 追蹤月數 (`latest_track_tracking_months`)
- 平均營收 (`latest_track_avg_revenue`)
- 風險等級 (`latest_track_risk_level`)

### 處理一對多關係

對於一對多關係，選擇適當的處理方式：

- **取特定記錄**：如最新、最早、最大、最小值
- **統計聚合**：如計算平均值、總和、計數
- **展開欄位**：為不同時間點或狀態創建獨立欄位
- **保留多筆**：如果下游任務確實需要，標記序號

## 步驟 3：執行反正規化

### 方式 A：使用 Python pandas

適用於資料量適中且需要靈活處理的情境：

```python
import pandas as pd

# 讀取原始資料表
companies = pd.read_csv('companies.csv')
applications = pd.read_csv('applications.csv')
tracking = pd.read_csv('tracking.csv')

# 標記每個公司的第一次和最新一次申請
applications['sort_tuple'] = list(zip(applications['apply_date'], applications['application_id']))

# 找出每個公司的最早申請
min_tuples = applications.groupby('company_id')['sort_tuple'].transform('min')
applications['is_first_application'] = (applications['sort_tuple'] == min_tuples)

# 找出每個公司的最晚申請
max_tuples = applications.groupby('company_id')['sort_tuple'].transform('max')
applications['is_latest_application'] = (applications['sort_tuple'] == max_tuples)

applications.drop(columns=['sort_tuple'], inplace=True, errors='ignore')

# 將財務追蹤資料串接上申請資料，以獲得公司編號
tracking_w_company = tracking.merge(
    applications[['company_id', 'application_id']],
    how='left',
    left_on='application_id',
    right_on='application_id'
)

# 標記每個公司的最新一次財務追蹤
tracking_w_company['sort_tuple'] = list(zip(
    tracking_w_company['tracking_date_last_tracking_date'],
    tracking_w_company['application_id']
))

max_tuples = tracking_w_company.groupby('company_id')['sort_tuple'].transform('max')
tracking_w_company['is_latest_tracking'] = (tracking_w_company['sort_tuple'] == max_tuples)

tracking_w_company.drop(columns=['sort_tuple'], inplace=True, errors='ignore')

# 合併企業資料與申請資料
denorm_data = companies.merge(
    applications[applications['is_first_application']].add_prefix('first_apply_'),
    how='left',
    left_on='company_id',
    right_on='first_apply_company_id'
).drop(columns=['first_apply_company_id', 'first_apply_is_first_application', 'first_apply_is_latest_application']).merge(
    applications[applications['is_latest_application']].add_prefix('latest_apply_'),
    how='left',
    left_on='company_id',
    right_on='latest_apply_company_id'
).drop(columns=['latest_apply_company_id', 'latest_apply_is_first_application', 'latest_apply_is_latest_application'])

# 加入彙整後的追蹤資料
denorm_data = denorm_data.merge(
    tracking_w_company[tracking_w_company['is_latest_tracking']].drop(columns=['sort_tuple'], errors='ignore').add_prefix('latest_track_'),
    how='left',
    left_on='company_id',
    right_on='latest_track_company_id'
).drop(columns=['latest_track_company_id', 'latest_track_is_latest_tracking'])

# 儲存整合後的寬表
denorm_data.to_csv('denormalized_data.csv', index=False)
```

### 方式 B：使用 SQL

適用於資料量大且已在資料庫中的情境：

```sql
-- 在資料庫中直接執行反正規化
WITH first_applications AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY apply_date) as rn
    FROM applications
),
latest_applications AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY apply_date DESC) as rn
    FROM applications
),
latest_tracking AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY application_id ORDER BY tracking_date DESC) as rn
    FROM tracking
)
SELECT 
    c.*,
    fa.* AS first_apply_,
    la.* AS latest_apply_,
    lt.* AS latest_track_
FROM companies c
LEFT JOIN first_applications fa ON c.company_id = fa.company_id AND fa.rn = 1
LEFT JOIN latest_applications la ON c.company_id = la.company_id AND la.rn = 1
LEFT JOIN latest_tracking lt ON la.application_id = lt.application_id AND lt.rn = 1;
```

## 整合後使用 PETsARD

整合完成後，即可使用標準的 PETsARD 流程：

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
Postprocessor:
  default:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
```

## 注意事項

在進行資料整合時，需特別注意：

- **確認資料的主鍵關係**：避免重複或遺漏
- **妥善處理時間序列資訊**：例如使用摘要統計保留重要特徵
- **資料表合併順序**：會影響最終結果，建議先處理關聯性較強的表格
- **下游任務需求**：為了降低合成複雜度，可以僅保留必要的欄位

透過預先的反正規化處理，能夠明確保留業務邏輯關係、降低合成過程中的資料失真、提升最終合成資料的實用性與品質。
