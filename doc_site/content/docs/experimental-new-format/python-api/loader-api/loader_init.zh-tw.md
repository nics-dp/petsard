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
    - 欄位類型定義，格式：`{type: [colname]}`
    - 範例：`{'categorical': ['gender', 'city'], 'numerical': ['age', 'income']}`

- **header_names** : list, optional
    - 無標題列資料的欄位名稱
    - 用於 CSV 檔案沒有標題列的情況
    - 範例：`['col1', 'col2', 'col3']`
    - 預設值：`None`（自動從第一列讀取）

- **na_values** : str | list | dict, optional
    - **⚠️ 已棄用，將在 v2.0.0 移除**
    - 視為 NA/NaN 的值
    - 字串：單一值，如 `'N/A'`
    - 列表：多個值，如 `['N/A', 'null', '-']`
    - 字典：每欄位不同，如 `{'age': [-1], 'name': ['N/A']}`

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
    date_parser=None,        # 日期解析器（預設：None）
    thousands=None,          # 千分位符號（預設：None）
    decimal='.',             # 小數點符號（預設：'.'）
    compression='infer',     # 壓縮格式（預設：'infer'）
    header_names=['col1', 'col2']  # 無標題列時的欄位名稱
)
```

### Excel 檔案

```python
loader = Loader(
    filepath='data.xlsx',
    sheet_name=0,            # 工作表名稱或索引（預設：0）
    header=0,                # 標題列位置（預設：0）
    skiprows=None,           # 跳過的列（預設：None）
    nrows=None,              # 讀取列數（預設：None）
    usecols=None,            # 使用的欄位（預設：None）
    dtype=None,              # 資料類型（預設：None）
    engine=None,             # 解析引擎（預設：None，自動選擇）
    converters=None,         # 欄位轉換器（預設：None）
    true_values=None,        # 視為 True 的值（預設：None）
    false_values=None,       # 視為 False 的值（預設：None）
    skipfooter=0,            # 跳過的尾部列數（預設：0）
    thousands=None           # 千分位符號（預設：None）
)
```

### Parquet 檔案

```python
loader = Loader(
    filepath='data.parquet',
    engine='auto',           # 引擎：'auto', 'pyarrow', 'fastparquet'（預設：'auto'）
    columns=None,            # 讀取的欄位（預設：None，全部讀取）
    use_pandas_metadata=True, # 使用 pandas 詮釋資料（預設：True）
    filters=None             # 資料篩選條件（預設：None）
)
```

### Benchmark 資料集

```python
loader = Loader(
    filepath='benchmark://adult-income',
    cache_dir='~/.petsard/data',  # 快取目錄（預設：'~/.petsard/data'）
    force_download=False,         # 強制重新下載（預設：False）
    version='latest'               # 資料集版本（預設：'latest'）
)
```

### 使用 Schema 配置

```python
# 使用 YAML 檔案
loader = Loader(
    filepath='data.csv',
    schema='schema.yaml'
)

# 使用字典配置
loader = Loader(
    filepath='data.csv',
    schema={
        'columns': {
            'age': {'type': 'numerical', 'min': 0, 'max': 120},
            'gender': {'type': 'categorical', 'values': ['M', 'F']},
            'income': {'type': 'numerical', 'min': 0}
        },
        'primary_key': 'id',
        'relationships': [],
        'constraints': {}
    }
)

# 使用 SchemaConfig 物件
from petsard import SchemaConfig

schema_config = SchemaConfig(
    columns={
        'age': {'type': 'numerical'},
        'gender': {'type': 'categorical'}
    }
)

loader = Loader(
    filepath='data.csv',
    schema=schema_config
)
```

## 範例

### 基本使用

```python
from petsard import Loader

# 載入 CSV 檔案
loader = Loader('data.csv')

# 載入 Excel 檔案的特定工作表
loader = Loader('data.xlsx', sheet_name='Sheet2')

# 載入 Parquet 檔案
loader = Loader('data.parquet')

# 載入 benchmark 資料集
loader = Loader('benchmark://adult-income')

# 使用預設方法
loader = Loader(method='default')
```

### 進階設定

```python
from petsard import Loader

# CSV 檔案無標題列
loader = Loader(
    filepath='data.csv',
    header_names=['id', 'name', 'age', 'salary']
)

# 指定分隔符號和編碼
loader = Loader(
    filepath='data.tsv',
    sep='\t',
    encoding='latin-1'
)

# 選擇特定欄位
loader = Loader(
    filepath='large_data.csv',
    usecols=['id', 'feature1', 'feature2', 'target']
)

# 讀取部分資料
loader = Loader(
    filepath='huge_data.csv',
    skiprows=100,  # 跳過前 100 列
    nrows=10000    # 只讀取 10,000 列
)
```

### 完整範例

```python
from petsard import Loader
import pandas as pd

# 初始化載入器（CSV 檔案，含 schema）
loader = Loader(
    filepath='customer_data.csv',
    schema='customer_schema.yaml',
    sep=',',
    encoding='utf-8',
    parse_dates=['registration_date', 'last_purchase_date'],
    dtype={'customer_id': str}  # 強制 customer_id 為字串
)

# 載入資料
data, schema = loader.load()

# 查看資料資訊
print(f"資料形狀: {data.shape}")
print(f"欄位類型: {schema.column_types}")
print(f"主鍵: {schema.primary_key}")

# 資料預覽
print(data.head())

# 存取載入器配置
config = loader.config
print(f"檔案名稱: {config.file_name}")
print(f"副檔名: {config.file_ext}")
```

### Benchmark 資料集範例

```python
from petsard import Loader

# 載入 Adult Income 基準資料集
loader = Loader('benchmark://adult-income')
data, schema = loader.load()

print(f"資料集形狀: {data.shape}")  # (48842, 15)
print(f"欄位數: {len(data.columns)}")  # 15
print(f"資料筆數: {len(data)}")  # 48,842

# 查看資料集特性
print("\n數值型欄位:")
numeric_cols = [col for col, dtype in schema.column_types.items() if dtype.get('type') == 'numerical']
print(numeric_cols)

print("\n類別型欄位:")
categorical_cols = [col for col, dtype in schema.column_types.items() if dtype.get('type') == 'categorical']
print(categorical_cols)
```

## 注意事項

- 檔案路徑支援相對路徑和絕對路徑
- 副檔名用於自動判斷檔案格式（.csv, .xlsx, .xls, .parquet）
- Benchmark 資料集會自動下載並快取到本地
- `column_types` 和 `na_values` 參數已棄用，請使用 `schema` 參數
- 大型檔案建議使用 `nrows` 或 `usecols` 參數以節省記憶體
- Schema 配置優先順序：參數指定 > YAML 檔案 > 自動推論
- 初始化只建立配置，實際載入資料需呼叫 `load()` 方法