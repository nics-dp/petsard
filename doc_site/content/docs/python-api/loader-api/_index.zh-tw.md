---
title: "Loader API"
weight: 340
---

資料載入模組，支援多種檔案格式的資料載入。

## 類別架構

{{< mermaid-file file="content/docs/python-api/loader-api/loader-class-diagram.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 橘色框：子類別實作
> - 淺紫框：配置與資料類別
> - `<|--`：繼承關係 (inheritance)
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 基本使用

```python
from petsard import Loader

# 載入 CSV 檔案
loader = Loader('data.csv')
data, schema = loader.load()

# 使用自訂 schema
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()
```

## 建構函式 (__init__)

初始化資料載入器實例。

### 語法

```python
def __init__(
    filepath: str = None,
    column_types: dict = None,
    header_names: list = None,
    na_values: str | list | dict = None,
    schema: Schema | dict | str = None
)
```

### 參數

- **filepath** : str, required
    - 資料檔案路徑
    - 必要參數
    - 支援相對路徑和絕對路徑

- **column_types** : dict, optional
    - **已棄用** - 將在 v2.0.0 移除
    - 請改用 `schema` 參數

- **header_names** : list, optional
    - **已棄用** - 將在 v2.0.0 移除
    - 無標題列資料的欄位名稱
    - 預設值：`None`

- **na_values** : str | list | dict, optional
    - **已棄用** - 將在 v2.0.0 移除
    - 請改用 `schema` 參數

- **schema** : Schema | dict | str, optional
    - 資料結構定義配置
    - 可為 Schema 物件、字典或 YAML 檔案路徑
    - 預設值：`None`（自動推論）
    - Schema 詳細設定請參閱 Metadater API 文檔

### 返回值

- **Loader**
    - 初始化後的載入器實例

### 使用範例

```python
from petsard import Loader

# 基本使用 - 載入 CSV 檔案
loader = Loader('data.csv')

# 使用 schema YAML 配置檔
loader = Loader('data.csv', schema='schema.yaml')

# 使用 schema 字典
schema_dict = {
    'id': 'my_schema',
    'name': 'My Schema'
}
loader = Loader('data.csv', schema=schema_dict)

# 載入資料
data, schema = loader.load()
```

詳細參數配置請參閱 Loader YAML 文檔。

## 支援格式

- **CSV**: `.csv`, `.tsv`
- **Excel**: `.xlsx`, `.xls`, `.xlsm`, `.xlsb` *
- **OpenDocument**: `.ods`, `.odf`, `.odt` *
- **Benchmark**: `benchmark://` 協議

\* 使用 Excel 和 OpenDocument 格式需要安裝額外套件，請參閱 Loader YAML 文檔了解詳細配置。

## 注意事項

- **已棄用參數**：`column_types`、`na_values` 和 `header_names` 參數已棄用，將在 v2.0.0 移除
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **Schema 使用**：建議使用 Schema 來定義資料結構，詳細設定請參閱 Metadater API 文檔
- **載入流程**：初始化只建立配置，實際載入資料需呼叫 `load()` 方法
- **Excel 支援**：Excel 格式需要安裝 `openpyxl` 套件
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容
- **檔案格式**：支援的檔案格式請參考 Loader YAML 文檔