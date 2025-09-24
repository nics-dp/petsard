---
title: Loader
type: docs
weight: 52
prev: docs/api/executor
next: docs/api/metadater
---


```python
Loader(
    filepath=None,
    column_types=None,
    header_names=None,
    na_values=None,
    schema=None
)
```

用於載入表格式資料的模組。

## 參數

- `filepath` (`str`)：資料集檔案路徑
  - 必要參數，指定要載入的本地檔案路徑
  - 支援格式：CSV、Excel (XLS, XLSX, XLSM, XLSB, ODF, ODS, ODT)
- `column_types` (`dict`, optional)：**⚠️ v2.0.0 版本將下架移除** 欄位型態定義
  - 預設值：無
  - 格式：`{type: [colname]}`
  - 支援型態（不分大小寫）：
    - 'category'：類別型欄位
    - 'datetime'：日期時間型欄位
- `header_names` (`list`, optional)：無標題資料的欄位名稱列
  - 預設值：無
- `na_values` (`str` | `list` | `dict`, optional)：**⚠️ v2.0.0 版本將下架移除** 指定要視為 NA/NaN 的值
  - 預設值：無
  - 若為字串或列表：套用於所有欄位
  - 若為字典：以 `{colname: na_values}` 格式指定各欄位
  - 範例：`{'workclass': '?', 'age': [-1]}`
- `schema` (`SchemaConfig` | `dict` | `str`, optional)：資料處理的架構定義
  - 預設值：無
  - **SchemaConfig 物件**：直接的架構設定物件
  - **字典**：內嵌架構定義，會轉換為 SchemaConfig
  - **字串**：外部 YAML 架構檔案路徑（例如：`'my_schema.yaml'`）
  - 支援所有架構參數：`optimize_dtypes`、`nullable_int`、`fields` 等
  - 優先於已棄用的 `column_types` 和 `na_values` 參數
  - **衝突檢測**：若 `schema` 和 `column_types` 同時定義相同欄位，將拋出 `ConfigError`
  - **外部架構檔案的優勢**：
    - **可重複使用性**：同一架構可在多個元件中使用（Loader、Metadater、Splitter、Synthesizer）
    - **可維護性**：集中式架構定義，更新更容易
    - **評測便利性**：可直接用於評測過程，確保一致性
    - **版本控制**：獨立的架構版本控制和演進追蹤

## 範例

```python
from petsard import Loader


# 基本用法
load = Loader('data.csv')
data, meta = load.load()

# 使用外部架構檔案（推薦方式）
load = Loader('data.csv', schema='my_schema.yaml')
data, meta = load.load()

# 使用內嵌架構定義
schema_dict = {
    'optimize_dtypes': True,
    'nullable_int': 'force',
    'fields': {
        'age': {
            'type': 'int',
            'na_values': ['unknown', 'N/A', '?']
        },
        'salary': {
            'type': 'float',
            'precision': 2,
            'na_values': ['missing']
        },
        'active': {
            'type': 'bool'
        },
        'category': {
            'type': 'str',
            'category_method': 'force'
        }
    }
}
load = Loader('data.csv', schema=schema_dict)
data, meta = load.load()

# 進階 schema 配置請參考 Metadater API 文檔
```

## 方法

### `load()`

讀取與載入資料。

**參數**

無

**回傳值**

- `data` (`pd.DataFrame`)：載入的 DataFrame
- `schema` (`SchemaMetadata`)：包含欄位資訊和統計資料的資料集架構詮釋資料

```python
loader = Loader('data.csv')
data, meta = loader.load()  # 得到載入的資料
```

## 屬性

- `config` (`LoaderConfig`)：設定物件，包含：
  - `filepath` (`str`)：本地端資料檔案路徑
  - `column_types` (`dict`)：使用者定義的欄位型態（已棄用）
  - `header_names` (`list`)：欄位標題
  - `na_values` (`str` | `list` | `dict`)：NA 值定義（已棄用）
  - `schema` (`SchemaConfig` | `None`)：架構設定物件
  - `schema_path` (`str` | `None`)：若從 YAML 檔案載入時的架構檔案路徑
  - 檔案路徑元件：
    - `dir_name` (`str`)：目錄名稱
    - `base_name` (`str`)：含副檔名的基本檔名
    - `file_name` (`str`)：不含副檔名的檔名
    - `file_ext` (`str`)：檔案副檔名
    - `file_ext_code` (`int`)：用於內部處理的檔案副檔名代碼

> **注意事項**：若需要使用基準資料集（benchmark://），請透過 LoaderAdapter 來處理。Loader 現在專注於純檔案載入功能。