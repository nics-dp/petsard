---
title: "儲存驗證結果"
type: docs
weight: 704
prev: docs/petsard-yaml/reporter-yaml/save-schema
next: docs/petsard-yaml/reporter-yaml/save-timing
---

使用 `save_validation` 方法將 Constrainer 的驗證結果匯出為 CSV 檔案，包含摘要統計、違規統計及詳細違規記錄。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-validation.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Constrainer:
  validate_constraints:
    method: validate
    constraints:
      age:
        range: [17, 90]
      workclass:
        categories: ['Private', 'Self-emp-not-inc', 'Self-emp-inc', 'Federal-gov', 'Local-gov', 'State-gov', 'Without-pay', 'Never-worked']

Reporter:
  save_validation:
    method: save_validation     # 必要：固定使用 save_validation 方法
    # output: petsard           # 選用：輸出檔案名稱前綴（預設：petsard）
    # include_details: true     # 選用：是否包含詳細違規記錄（預設：true）
```

## 主要參數

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 固定為 `save_validation`（不區分大小寫） | `save_validation` 或 `SAVE_VALIDATION` |

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `output` | `string` | `petsard` | 輸出檔案名稱前綴 | `my_validation` |
| `include_details` | `boolean` | `true` | 是否包含詳細違規記錄 | `true`, `false` |

#### include_details 參數詳細說明

`include_details` 參數控制是否輸出詳細的違規記錄檔案：

1. **啟用詳細記錄** (`true`)：
   ```yaml
   include_details: true
   ```
   - 會額外產生 `*_details.csv` 檔案
   - 包含每條違規的具體資料列
   - 每條規則最多顯示 10 筆違規範例
   - 包含欄位：Constraint Type、Rule、Violation Index、實際資料欄位

2. **停用詳細記錄** (`false`)：
   ```yaml
   include_details: false
   ```
   - 只產生摘要和統計檔案
   - 節省儲存空間
   - 適合只需要統計數據的場景

## 輸出格式

此 Reporter 會針對每個 Constrainer 驗證結果產生最多 3 個 CSV 檔案：

### 1. 摘要檔案 (Summary)

**檔名格式：**
```
{output}[Validation]_Constrainer[實驗名稱]_summary.csv
```

**範例檔名：**
- 單一來源：`petsard_[Validation]_Constrainer[validate_constraints]_summary.csv`
- 多來源：`petsard_[Validation]_Source[synthetic_data]_Constrainer[validate_constraints]_summary.csv`

**檔案內容：**
| Metric | Value |
|--------|-------|
| total_rows | 總資料筆數 |
| passed_rows | 通過驗證的筆數 |
| failed_rows | 未通過驗證的筆數 |
| pass_rate | 通過率（0-1 之間的浮點數） |
| is_fully_compliant | 是否完全符合（True/False） |

### 2. 違規統計檔案 (Violations)

**檔名格式：**
```
{output}[Validation]_Constrainer[實驗名稱]_violations.csv
```

**檔案內容：**
| Constraint Type | Rule | Failed Count | Fail Rate | Violation Examples | Error Message |
|----------------|------|--------------|-----------|-------------------|---------------|
| 條件類型 | 規則名稱 | 違規筆數 | 違規率 | 違規範例索引 | 錯誤訊息 |

**範例：**
| Constraint Type | Rule | Failed Count | Fail Rate | Violation Examples | Error Message |
|----------------|------|--------------|-----------|-------------------|---------------|
| range | age_range_check | 15 | 0.015000 | 42, 87, 123, 256, 489 | - |
| categories | workclass_valid_categories | 8 | 0.008000 | 12, 34, 56, 78 | - |

### 3. 詳細違規記錄檔案 (Details)

**檔名格式：**
```
{output}[Validation]_Constrainer[實驗名稱]_details.csv
```

**說明：**
- 僅當 `include_details: true` 時產生
- 每條規則最多顯示 10 筆違規範例
- 包含完整的違規資料列內容

**檔案內容：**
| Constraint Type | Rule | Violation Index | [原始資料欄位...] |
|----------------|------|-----------------|-------------------|
| 條件類型 | 規則名稱 | 違規索引 | 實際欄位值 |

**範例：**
| Constraint Type | Rule | Violation Index | age | workclass | education | ... |
|----------------|------|-----------------|-----|-----------|-----------|-----|
| range | age_range_check | 1 | 15 | Private | HS-grad | ... |
| range | age_range_check | 2 | 95 | Self-emp | Masters | ... |
| categories | workclass_valid_categories | 1 | 45 | Unknown | Bachelors | ... |

## 檔名命名規則

### 使用預設 output 時 (`petsard`)

系統會自動依據實驗類型產生完整的檔名：

1. **單一來源的 Constrainer**：
   ```
   petsard_[Validation]_Constrainer[實驗名稱]_[類型].csv
   ```
   範例：`petsard_[Validation]_Constrainer[validate_constraints]_summary.csv`

2. **多來源的 Constrainer**（有指定 source）：
   ```
   petsard_[Validation]_Source[來源名稱]_Constrainer[實驗名稱]_[類型].csv
   ```
   範例：`petsard_[Validation]_Source[synthetic_data]_Constrainer[validate_constraints]_summary.csv`

### 使用自訂 output 時

直接使用指定的名稱：
```yaml
Reporter:
  save_validation:
    method: save_validation
    output: my_validation_report
```

輸出檔案：
- `my_validation_report_summary.csv`
- `my_validation_report_violations.csv`
- `my_validation_report_details.csv`（如果 include_details 為 true）

## 使用場景

1. **驗證報告生成**：將資料驗證結果匯出為正式報告
2. **品質監控**：持續追蹤資料品質指標
3. **問題診斷**：透過詳細違規記錄找出資料問題
4. **合規性文檔**：提供資料合規性證明文件

## 常見問題

### Q: save_validation 和 save_report 有什麼差別？

**A:**
- `save_validation`：專門用於匯出 Constrainer 的驗證結果，產生結構化的 CSV 報告（摘要、統計、詳細記錄）
- `save_report`：匯出效用指標評估結果，支援多種格式（CSV、Markdown、HTML）

### Q: 為什麼我的驗證結果沒有被儲存？

**A:** 請檢查：
1. 是否有在 Reporter 之前執行 Constrainer 的 `validate` 方法
2. Constrainer 是否成功產生驗證結果
3. 驗證結果的資料結構是否正確

### Q: 詳細違規記錄太多，會影響效能嗎？

**A:**
- 系統會自動限制每條規則最多輸出 10 筆違規範例
- 如果不需要詳細記錄，可設定 `include_details: false` 以節省空間
- 摘要和統計檔案始終會產生，不受此設定影響

### Q: 可以調整每條規則的違規範例數量嗎？

**A:** 目前系統固定為每條規則最多 10 筆範例。如需更多記錄，建議：
1. 使用 `save_data` 匯出完整的驗證結果資料
2. 或結合 Constrainer 的 `return_details=True` 選項自行處理

## 注意事項

- **檔案覆寫**：同名檔案會被覆寫，請注意備份
- **資料量控制**：詳細違規記錄會自動限制為每條規則最多 10 筆
- **編碼格式**：所有 CSV 檔案使用 UTF-8 編碼
- **大小寫不敏感**：`method` 參數不區分大小寫（`save_validation`、`SAVE_VALIDATION` 或 `Save_Validation` 皆可）
- **執行順序**：必須在 Constrainer 的 validate 方法之後執行
- **空值處理**：如果某個驗證結果為空或無效，該結果會被略過並記錄警告