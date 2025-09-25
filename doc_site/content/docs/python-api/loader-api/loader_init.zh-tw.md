---
title: "init"
weight: 311
---

初始化資料載入器實例。

## 語法

```python
def __init__(
    filepath: str = None,
    method: str = None,
    column_types: dict = None,
    header_names: list = None,
    na_values: str | list | dict = None,
    schema: SchemaConfig | dict | str = None,
    **kwargs
)
```

## 參數

- **filepath** : str, optional
    - 資料檔案路徑或 benchmark 資料集名稱
    - 預設值：`None`

- **method** : str, optional
    - 載入方法名稱
    - 預設值：`None`（根據檔案副檔名自動判斷）

- **schema** : SchemaConfig | dict | str, optional
    - 資料結構定義配置
    - 預設值：`None`（自動推論）

- **kwargs** : dict
    - 依據不同檔案格式的額外參數
    - 詳細參數請參考 YAML 配置文件中的 Loader 章節

## 返回值

- **Loader**
    - 初始化後的載入器實例

## 基本範例

```python
from petsard import Loader

# 載入 CSV 檔案
loader = Loader('data.csv')

# 載入 benchmark 資料集
loader = Loader('benchmark://adult-income')

# 使用 schema
loader = Loader('data.csv', schema='schema.yaml')
```

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 檔案路徑支援相對路徑和絕對路徑
- 支援的檔案格式和詳細參數請參考 YAML 配置文件中的 Loader 章節
- 初始化只建立配置，實際載入資料需呼叫 `load()` 方法
- 本段文件僅供開發團隊內部參考，不保證向後相容