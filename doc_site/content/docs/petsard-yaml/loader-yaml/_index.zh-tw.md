---
title: "Loader YAML"
weight: 110
---

Loader 模組的 YAML 設定檔案格式。

## 主要參數

- **filepath** (`string`, 必要)
  - 資料檔案路徑
  - 支援本地檔案路徑

- **schema** (`string | dict`, 選用)
  - 資料結構定義
  - 可為外部 YAML 檔案路徑（string）或內嵌的完整 Schema YAML（dict）

## 支援的檔案格式

| 格式 | 副檔名 | 說明 | 額外需求 |
|------|--------|------|----------|
| **CSV** | `.csv`, `.tsv` | 逗號/製表符分隔檔案 | - |
| **Excel** | `.xlsx`, `.xls` | Excel 試算表 | 需安裝 `openpyxl` |
| **OpenDocument** | `.ods`, `.odf`, `.odt` | OpenDocument 格式 | 需安裝 `openpyxl` |
| **Benchmark** | `benchmark://` | 基準資料集協議 | 需網路連線（首次下載） |

\* 使用 Excel 和 OpenDocument 格式需要安裝 `openpyxl` 套件，請參閱安裝說明。

## 參數詳細說明

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `filepath` | `string` | 資料檔案路徑 | `data/users.csv` |

### 選用參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `schema` | `string\|dict` | 資料結構定義 | `schemas/user.yaml` 或內嵌 dict |

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/loader-yaml/loader-yaml.ipynb)

### 基本載入

```yaml
Loader:
  load_csv:
    filepath: benchmark/adult-income.csv
```

### 使用表詮釋資料檔案
表詮釋資料就是 Schema，用於定義資料的結構與類型。

```yaml
Loader:
  load_with_schema:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml
```

### 多個資料載入

```yaml
Loader:
  # Load training data
  load_train:
    filepath: benchmark/adult-income_ori.csv
    schema: benchmark/adult-income_schema.yaml

  # Load test data
  load_test:
    filepath: benchmark/adult-income_control.csv
    schema: benchmark/adult-income_schema.yaml

  # Load synthesizing data
  load_synthesizer:
    filepath: benchmark/adult-income_syn.csv
    schema: benchmark/adult-income_schema.yaml
```

## 相關說明

- **基準資料集**：使用 benchmark:// 協議可自動下載並載入標準化的資料集，詳見 benchmark:// 文檔。
- **表詮釋資料**：Schema 用於定義資料的結構、類型和約束條件，詳見 Schema YAML 文檔。

## 執行說明

- 實驗名稱（第二層）可自由命名，建議使用描述性名稱
- 可定義多個實驗，系統會依序執行
- 每個實驗的結果會傳遞給下一個模組使用

## 注意事項

- 檔案路徑支援相對路徑和絕對路徑
- Schema 配置優先順序：參數指定 > 自動推論
- `column_types`、`na_values` 和 `header_names` 參數已棄用，將在 v2.0.0 移除
- Excel 和 OpenDocument 格式需要安裝 `openpyxl` 套件
- Schema 的詳細設定請參閱 Schema YAML 文檔