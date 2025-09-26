---
title: "Loader API"
weight: 310
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

## 主要類別

### Loader

主要的資料載入類別。

#### 建構函式

```python
Loader(
    filepath: str,
    column_types: dict = None,  # 已棄用 - 改用 schema
    header_names: list = None,
    na_values: Any = None,       # 已棄用 - 改用 schema
    schema: Schema | dict | str = None
)
```

#### 參數說明

- `filepath`: 資料檔案路徑
- `header_names`: 無標題列資料的欄位名稱
- `schema`: Schema 配置（可為 Schema 物件、字典或 YAML 路徑）

詳細參數配置請參閱 Loader YAML 文檔。

### LoaderConfig

Loader 的內部配置類別，包含檔案路徑解析與驗證邏輯。

### LoaderFileExt

檔案副檔名對應類別，用於判斷檔案類型。

## 支援格式

- **CSV**: `.csv`, `.tsv`
- **Excel**: `.xlsx`, `.xls`, `.xlsm`, `.xlsb` *
- **OpenDocument**: `.ods`, `.odf`, `.odt` *

\* 使用 Excel 和 OpenDocument 格式需要安裝額外套件，請參閱安裝說明。

## 注意事項

- `column_types` 和 `na_values` 參數已棄用，將在 v2.0.0 移除
- 建議使用 Schema 來定義資料結構
- Schema 詳細設定請參閱 Metadater API 文檔
- Excel 格式需要安裝 `openpyxl` 套件