---
title: "儲存表詮釋資料"
type: docs
weight: 703
prev: docs/petsard-yaml/reporter-yaml/save-report
next: docs/petsard-yaml/reporter-yaml/save-validation
---

使用 `save_schema` 方法將指定來源模組的表詮釋資料 (Schema) 資訊匯出為 CSV 檔案（預設）或 YAML 檔案。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-schema.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 1
    train_split_ratio: 0.8
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
  save_schema:
    method: save_schema  # 必要：固定使用 save_schema 方法
    source:              # 必要：指定要匯出表詮釋資料的模組
      - Loader
      - Preprocessor
      - Synthesizer
      - Postprocessor
    yaml_output: true    # 選用：是否輸出個別 YAML 檔案（預設：false）
    # output: petsard    # 選用：輸出檔案名稱前綴（預設：petsard）
    # properties:        # 選用：指定要輸出的屬性（預設：所有屬性）
    #   - dtype
    #   - nullable
    #   - min
    #   - max
```

## 主要參數

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 固定為 `save_schema`（不區分大小寫） | `save_schema` 或 `SAVE_SCHEMA` |
| `source` | `string` 或 `list` | 目標模組名稱 | `Loader` 或 `["Loader", "Preprocessor"]` |

#### source 參數詳細說明

`source` 參數用於指定要匯出表詮釋資料的模組，支援以下格式：

1. **單一模組**：匯出單一模組的表詮釋資料
   ```yaml
   source: Preprocessor
   ```

2. **多個模組**：匯出多個模組的表詮釋資料
   ```yaml
   source:
     - Loader
     - Preprocessor
     - Synthesizer
   ```

**支援的模組**：
- `Loader`：原始資料的表詮釋資料
- `Splitter`：分割資料的表詮釋資料
- `Preprocessor`：預處理後資料的表詮釋資料
- `Synthesizer`：合成資料的表詮釋資料
- `Postprocessor`：後處理資料的表詮釋資料
- `Constrainer`：約束處理後資料的表詮釋資料

**引用注意事項**：
- **執行順序**：只能引用在當前 Reporter 之前執行的模組
- **模組名稱**：必須與 YAML 配置中定義的模組名稱完全一致
- **資料可用性**：表詮釋資料匯出需要模組已成功執行

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `output` | `string` | `petsard` | 輸出檔案名稱前綴 | `my_experiment` |
| `yaml_output` | `boolean` | `false` | 是否額外輸出 YAML 格式 | `true`, `false` |
| `properties` | `string` 或 `list` | 所有屬性 | 指定要輸出的屬性名稱 | `dtype` 或 `["dtype", "nullable", "min", "max"]` |

#### properties 參數詳細說明

`properties` 參數用於篩選要輸出的屬性，只有指定的屬性會出現在輸出檔案中。支援以下格式：

1. **單一屬性**：只輸出指定的屬性
   ```yaml
   properties: dtype
   ```

2. **多個屬性**：輸出多個指定的屬性
   ```yaml
   properties:
     - dtype
     - nullable
     - min
     - max
   ```

**常見屬性**：
- `dtype`：資料型別
- `nullable`：是否允許空值
- `min`、`max`、`mean`、`std`：數值型欄位的統計值
- `categories`：類別型欄位的類別值列表
- `unique_count`：唯一值數量

**使用範例**：
```yaml
Reporter:
  save_schema:
    method: save_schema
    source:
      - Loader
      - Synthesizer
    properties:
      - dtype
      - nullable
    output: filtered_schema
```

**效果**：
- CSV 檔案中只會包含 `{欄位名}_dtype` 和 `{欄位名}_nullable` 欄位
- 其他屬性（如 min、max、categories 等）不會被輸出
- 適用於所有欄位，無論其資料型別

## 輸出格式

### 預設 CSV 格式（Summary）

表詮釋資料預設輸出為 CSV 格式，每個 source（實驗）一行，所有欄位的屬性展開成列：

**檔名格式：**
```
{output}_schema_{來源1-來源2-...}_summary.csv
```

檔名會包含所有來源模組名稱，以連字號（`-`）串接，類似 `save_data` 方法的命名方式。

**範例：**
- 當 `output: "petsard"` 且 `source: ["Loader", "Preprocessor", "Synthesizer"]` 時：
  ```
  petsard_schema_Loader-Preprocessor-Synthesizer_summary.csv
  ```
- 當 `output: "petsard"` 且 `source: "Loader"` 時：
  ```
  petsard_schema_Loader_summary.csv
  ```

**CSV 結構**：
- 第一欄：`source`（來源實驗名稱）
- 其餘欄：`{欄位名}_{屬性名}`，例如：
  - `age_dtype`：age 欄位的資料型別
  - `age_nullable`：age 欄位是否允許空值
  - `age_min`、`age_max`、`age_mean`：age 欄位的統計值
  - `workclass_categories`：workclass 欄位的類別值列表

**使用 properties 參數時**：
- 只有指定的屬性會被輸出
- 例如設定 `properties: ["dtype", "nullable"]` 時，CSV 只會包含 `age_dtype`、`age_nullable`、`workclass_dtype`、`workclass_nullable` 等欄位
- 其他未指定的屬性（如 min、max、categories）不會出現在輸出中

**優點**：
- 易於比較不同實驗的 schema 差異
- 可用 Excel 或其他工具直接開啟分析
- 適合版本控制和差異比較

### 可選 YAML 格式

設定 `yaml_output: true` 時，會額外輸出各個實驗的 YAML 檔案：

```
{output}_schema_{完整實驗名稱}.yaml
```

**輸出檔案範例**：
- `petsard_schema_Loader[load_benchmark_with_schema].yaml`
- `petsard_schema_Loader[load_benchmark_with_schema]_Preprocessor[scaler].yaml`

**使用方式**：
```yaml
Reporter:
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
    yaml_output: true  # 額外輸出 YAML 檔案
```

## 使用場景

1. 資料轉換追蹤：追蹤資料結構在處理流程中的變化
2. 品質檢查：驗證合成資料是否維持預期的結構
3. 文檔生成：為專案生成完整的資料文檔

## 常見問題

### Q: save_schema 和 save_data 有什麼差別？

**A:**
- `save_schema`：匯出資料結構資訊（欄位型別、統計資料），預設以 CSV 格式儲存（攤平表格），可選 YAML 格式
- `save_data`：匯出實際資料內容，以 CSV 格式儲存

### Q: 可以指定自訂儲存路徑嗎？

**A:** 可以，使用 `output` 參數指定相對路徑。檔案會儲存在當前工作目錄的相對位置。

### Q: 為什麼我的模組表詮釋資料沒有被儲存？

**A:** 請檢查：
1. `source` 中的模組名稱拼寫是否正確
2. 模組是否在 Reporter 之前已執行
3. 模組是否有可用的資料（非空或失敗）

## 注意事項

- **檔案覆寫**：同名檔案會被覆寫
- **模組執行**：只有成功執行的模組才能匯出其表詮釋資料
- **編碼格式**：所有 CSV 和 YAML 檔案使用 UTF-8 編碼
- **大小寫不敏感**：`method` 參數不區分大小寫（`save_schema`、`SAVE_SCHEMA` 或 `Save_Schema` 皆可）
- **效能**：表詮釋資料匯出速度快，不需載入完整資料集
- **比較用途**：CSV 格式特別適合用於比較不同實驗間的資料結構變化
- **缺失值處理**：如果某個欄位在某個 source 中沒有某個屬性（例如從數值變類別），該欄位會留空（NA）