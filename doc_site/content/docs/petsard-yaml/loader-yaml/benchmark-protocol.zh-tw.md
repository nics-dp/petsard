---
title: "benchmark://"
type: docs
weight: 621
prev: docs/petsard-yaml/loader-yaml
next: docs/petsard-yaml/loader-yaml
---

Loader 支援使用 `benchmark://` 協議自動下載並載入基準資料集。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/loader-yaml/benchmark-protocol.ipynb)

### 載入基準資料集

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
```

### 載入基準資料集與基準資料集詮釋資料

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
```

本地或基準資料所提供的 filepath 跟 schema 都可以交替使用。

## 可用的基準資料集

### Demographic 資料集

| 資料集名稱 | 協議路徑 | 說明 |
|-----------|---------|------|
| Adult Income | `benchmark://adult-income` | UCI Adult Income 人口普查資料集（48,842 筆，15 欄位） |
| Adult Income Schema | `benchmark://adult-income_schema` | Adult Income 資料集的詮釋資料定義 |
| Adult Income (Original) | `benchmark://adult-income_ori` | 原始訓練資料（用於 demo） |
| Adult Income (Control) | `benchmark://adult-income_control` | 控制組資料（用於 demo） |
| Adult Income (Synthetic) | `benchmark://adult-income_syn` | SDV Gaussian Copula 合成資料（用於 demo） |
| Taiwan Salary Statistics | `benchmark://taiwan-salary-statistics-300k` | 臺灣薪資統計資料集（300K 筆資料） |
| Taiwan Salary Statistics (No DI) | `benchmark://taiwan-salary-statistics-300k-no-di` | 臺灣薪資統計資料集 - 無直接識別資料（300K 筆，已移除姓名、身分證字號，拆分生日與地址） |

#### 臺灣薪資統計 Taiwan Salaries Statistics

這是 2024 年 InnoServe 團隊用來出題目的模擬資料集，模擬勞動部職類別薪資調查統計。

**說明**

- 本資料參考行政院主計總處按月辦理之「[受僱員工薪資調查](https://earnings.dgbas.gov.tw/replies.aspx)」之編撰方法，模擬運用綜合所得稅檔連結勞工保險檔、勞退月提繳工資檔、全民健康保險檔之資料寬表結構
- 模擬過程使用公開的 112 年彙總統計，參酌多項政府開放資料做數值模擬，資料內容皆不涉及任何真實存在的個人與法人單位。如有姓名或公司名稱雷同，純屬巧合
- 本資料僅模擬本國籍勞工，但包含金門與連江等全國 20 個直轄市與縣市

### Best Practices 範例資料集

| 資料集名稱 | 協議路徑 | 說明 |
|-----------|---------|------|
| Multi-table Companies | `benchmark://best-practices_multi-table_companies` | 多表格範例 - 公司資料 |
| Multi-table Applications | `benchmark://best-practices_multi-table_applications` | 多表格範例 - 申請資料 |
| Multi-table Tracking | `benchmark://best-practices_multi-table_tracking` | 多表格範例 - 追蹤資料 |
| Multi-timestamp | `benchmark://best-practices_multi-table` | 多時間戳範例資料 |
| Categorical & High-cardinality | `benchmark://best-practices_categorical_high-cardinality` | 類別型與高基數範例資料 |

## 工作原理

1. **協議偵測**：Loader 偵測到 `benchmark://` 協議
2. **自動下載**：從 AWS S3 儲存區下載資料集
3. **驗證檢查**：使用 SHA256 驗證資料完整性
4. **本地快取**：資料儲存在 `benchmark/` 目錄
5. **載入資料**：使用本地路徑載入資料

## 使用時機

基準資料集適合用於：

- **測試新演算法**：在已知特性的資料上測試
- **參數調校**：比較不同參數設定的效果
- **效能基準**：與學術研究結果比較
- **教學示範**：提供標準化的範例資料

## 注意事項

- 首次使用需要網路連線下載資料
- 資料集會快取在本地 `benchmark/` 目錄
- 大型資料集下載可能需要較長時間
- 協議名稱不區分大小寫（但建議使用小寫）
- 所有資料集都經過 SHA256 驗證確保完整性
