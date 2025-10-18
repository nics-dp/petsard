---
title: 預設合成
type: docs
weight: 7
---

產生隱私強化合成資料的最簡單方式。
目前的預測合成方式採用 SDV 的 Gaussian Copula。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-dp/petsard/blob/main/demo/tutorial/default-synthesis.ipynb)

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default' # sdv-single_table-gaussiancopula
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
```

## YAML 參數詳細說明

### Loader（資料載入模組）

- **`load_csv`**: 實驗名稱，可自由命名，建議使用描述性名稱
- **`filepath`**: 資料檔案路徑
  - 值：`benchmark/adult-income.csv`
  - 說明：指定要載入的資料檔案位置
  - 支援格式：CSV、TSV、Excel（需安裝 openpyxl）、OpenDocument
  - 可使用相對路徑或絕對路徑
  - 也支援 `benchmark://` 協議來自動下載標準資料集

**建議使用 Schema：**
為了確保資料載入的正確性和一致性，強烈建議使用 `schema` 參數預先定義資料結構。Schema 可以明確指定每個欄位的資料型別（數值、類別、日期時間等）、約束條件，以及欄位之間的關係。

使用 schema 的範例：
```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml
```

關於 Schema 的詳細說明，請參考 [Schema YAML 文檔](../../petsard-yaml/loader-yaml/#schema-yaml)。

### Preprocessor（資料前處理模組）

- **`demo`**: 實驗名稱，可自由命名
- **`method`**: 前處理方法
  - 值：`default`
  - 說明：使用預設的處理序列，包含以下步驟：
    1. **missing**（缺失值處理）：數值型欄位使用平均值填補，類別型欄位刪除
    2. **outlier**（離群值處理）：數值型使用 IQR 方法處理
    3. **encoder**（編碼）：類別型欄位使用均勻編碼（`encoder_uniform`）
    4. **scaler**（縮放）：數值型欄位使用標準化（`scaler_standard`）

### Synthesizer（合成資料產生模組）

- **`demo`**: 實驗名稱，可自由命名
- **`method`**: 合成方法
  - 值：`default`
  - 說明：使用預設的合成方法，即 **SDV Gaussian Copula**
  - Gaussian Copula 是一種基於統計的合成方法，能夠捕捉變數間的相關性
  - 註解中標示的 `sdv-single_table-gaussiancopula` 說明其完整方法名稱

### Postprocessor（資料後處理模組）

- **`demo`**: 實驗名稱，可自由命名
- **`method`**: 後處理方法
  - 值：`default`
  - 說明：自動執行 Preprocessor 的逆向操作，將合成資料還原為原始格式
  - 還原順序（與前處理相反）：
    1. **inverse scaler**：反縮放，將標準化的數值還原
    2. **inverse encoder**：反編碼，將編碼後的類別變數還原
    3. **restore missing**：依原始比例重新插入缺失值
  - 注意：離群值處理（outlier）無法還原

### Reporter（結果輸出模組）

- **`output`**: 實驗名稱，可自由命名
- **`method`**: 報告方法
  - 值：`save_data`
  - 說明：將指定模組的輸出資料儲存為 CSV 檔案
- **`source`**: 資料來源模組
  - 值：`Synthesizer`
  - 說明：儲存來自 Synthesizer 模組產生的合成資料
  - 也可選擇其他模組，如 `Preprocessor`、`Postprocessor` 等
  - 輸出檔案預設命名格式：`petsard_Synthesizer[output].csv`

## 執行流程說明

1. **Loader** 載入 [`adult-income.csv`](benchmark/adult-income.csv) 資料
2. **Preprocessor** 進行前處理（填補缺失值、處理離群值、編碼、縮放）
3. **Synthesizer** 使用 Gaussian Copula 方法產生合成資料
4. **Postprocessor** 將合成資料還原為原始格式（反縮放、反編碼、插入缺失值）
5. **Reporter** 將最終的合成資料儲存為 CSV 檔案

## 進階使用

若需要自訂參數，可參考以下文檔：

- [Loader YAML 參數說明](../../petsard-yaml/loader-yaml/)
- [Preprocessor YAML 參數說明](../../petsard-yaml/preprocessor-yaml/)
- [Synthesizer YAML 參數說明](../../petsard-yaml/synthesizer-yaml/)
- [Postprocessor YAML 參數說明](../../petsard-yaml/postprocessor-yaml/)
- [Reporter YAML 參數說明](../../petsard-yaml/reporter-yaml/)