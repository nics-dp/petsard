---
title: "init"
weight: 311
---

初始化資料載入器實例。

## 語法

```python
def __init__(
    filepath: str = None,
    column_types: dict = None,
    header_names: list = None,
    na_values: str | list | dict = None,
    schema: Schema | dict | str = None
)
```

## 參數

- **filepath** : str, required
    - 資料檔案路徑
    - 必要參數

- **column_types** : dict, optional
    - **已棄用** - 將在 v2.0.0 移除
    - 請改用 `schema` 參數

- **header_names** : list, optional
    - 無標題列資料的欄位名稱
    - 預設值：`None`

- **na_values** : str | list | dict, optional
    - **已棄用** - 將在 v2.0.0 移除
    - 請改用 `schema` 參數

- **schema** : Schema | dict | str, optional
    - 資料結構定義配置
    - 可為 Schema 物件、字典或 YAML 檔案路徑
    - 預設值：`None`（自動推論）

## 返回值

- **Loader**
    - 初始化後的載入器實例

## 基本範例

```python
from petsard import Loader

# 載入 CSV 檔案
loader = Loader('data.csv')

# 使用 schema YAML
loader = Loader('data.csv', schema='schema.yaml')

# 使用 schema 字典
schema_dict = {
    'id': 'my_schema',
    'name': 'My Schema'
}
loader = Loader('data.csv', schema=schema_dict)
```

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 檔案路徑支援相對路徑和絕對路徑
- 支援的檔案格式請參考 Loader YAML 文檔
- 初始化只建立配置，實際載入資料需呼叫 `load()` 方法
- Excel 格式需要安裝 `openpyxl` 套件
- 本段文件僅供開發團隊內部參考，不保證向後相容