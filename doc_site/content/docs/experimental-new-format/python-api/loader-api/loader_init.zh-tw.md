---
title: "Loader.__init__()"
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
    - 資料檔案路徑
    - 支援格式：
        - 本地檔案：`'path/to/file.csv'`、`'data.xlsx'`、`'file.parquet'`
        - Benchmark 資料集：`'benchmark://dataset_name'`
        - 相對路徑或絕對路徑
    - 預設值：`None`

- **method** : str, optional
    - 載入方法名稱
    - 支援的方法：
        - `'default'`：載入預設資料集 (adult-income)
        - `'custom'`：自訂載入器
    - 預設值：`None`（根據檔案副檔名自動判斷）

- **column_types** : dict, optional
    - **⚠️ 已棄用，將在 v2.0.0 移除**
    - 請改用 `schema` 參數

- **header_names** : list, optional
    - 無標題列資料的欄位名稱
    - 用於 CSV 檔案沒有標題列的情況
    - 範例：`['col1', 'col2', 'col3']`
    - 預設值：`None`（自動從第一列讀取）

- **na_values** : str | list | dict, optional
    - **⚠️ 已棄用，將在 v2.0.0 移除**
    - 請改用 `schema` 參數

- **schema** : SchemaConfig | dict | str, optional
    - 資料結構定義配置
    - 可接受的格式：
        - `SchemaConfig` 物件：程式化定義
        - `dict`：字典格式定義
        - `str`：YAML 檔案路徑
    - 預設值：`None`（自動推論）

- **kwargs** : dict
    - 依據不同檔案格式的額外參數
    - 詳見各檔案格式的參數說明

## 返回值

- **Loader**
    - 初始化後的載入器實例

## 各檔案格式參數說明

### CSV 檔案

```python
loader = Loader(
    filepath='data.csv',
    sep=',',                 # 分隔符號（預設：','）
    encoding='utf-8',        # 編碼（預設：'utf-8'）
    skiprows=0,              # 跳過的列數（預設：0）
    nrows=None,              # 讀取列數（預設：None，全部讀取）
    usecols=None,            # 使用的欄位（預設：None，全部使用）
    dtype=None,              # 資料類型（預設：None，自動推論）
    parse_dates=False,       # 解析日期（預設：False）
)
```

### Excel 檔案

```python
loader = Loader(
    filepath='data.xlsx',
    sheet_name=0,            # 工作表名稱或索引（預設：0）
    header=0,                # 標題列位置（預設：0）
)
```

### Parquet 檔案

```python
loader = Loader(
    filepath='data.parquet',
    engine='auto',           # 引擎：'auto', 'pyarrow', 'fastparquet'（預設：'auto'）
    columns=None,            # 讀取的欄位（預設：None，全部讀取）
)
```

### Benchmark 資料集

```python
loader = Loader(
    filepath='benchmark://adult-income',
    cache_dir='~/.petsard/data',  # 快取目錄（預設：'~/.petsard/data'）
    force_download=False,         # 強制重新下載（預設：False）
)
```

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
- 副檔名用於自動判斷檔案格式（.csv, .xlsx, .xls, .parquet）
- Benchmark 資料集會自動下載並快取到本地
- `column_types` 和 `na_values` 參數已棄用，請使用 `schema` 參數
- 大型檔案建議使用 `nrows` 或 `usecols` 參數以節省記憶體
- Schema 配置優先順序：參數指定 > YAML 檔案 > 自動推論
- 初始化只建立配置，實際載入資料需呼叫 `load()` 方法