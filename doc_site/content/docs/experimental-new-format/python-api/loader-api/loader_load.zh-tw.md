---
title: "Loader.load()"
weight: 312
---

載入資料並返回 DataFrame 與 SchemaMetadata。

## 語法

```python
def load() -> tuple[pd.DataFrame, SchemaMetadata]
```

## 參數

無

## 返回值

- **tuple[pd.DataFrame, SchemaMetadata]**
    - 包含兩個元素的元組：
        - `data` (`pd.DataFrame`): 載入的資料表
        - `schema` (`SchemaMetadata`): 資料結構詮釋資料

## 說明

`load()` 方法用於實際載入資料。必須在 `__init__()` 之後呼叫此方法。

此方法會根據初始化時的配置，執行以下操作：
1. 讀取資料檔案或下載 benchmark 資料集
2. 處理資料格式（標題、分隔符號、編碼等）
3. 推論或載入資料 schema
4. 返回處理後的 DataFrame 與 SchemaMetadata

## 返回格式詳解

### DataFrame 結構

返回的 `pd.DataFrame` 包含：
- 所有資料列與欄位
- 適當的資料類型（根據 schema 或自動推論）
- 處理後的缺失值
- 解析後的日期時間欄位（如有指定）

### SchemaMetadata 結構

返回的 `SchemaMetadata` 物件包含：

```python
class SchemaMetadata:
    column_types: dict         # 欄位類型定義
    primary_key: str | None    # 主鍵欄位
    relationships: list        # 資料關聯
    constraints: dict          # 資料約束條件
    
    # 欄位類型格式
    column_types = {
        'column_name': {
            'type': 'numerical' | 'categorical' | 'datetime' | 'text',
            'subtype': str,    # 更細分的類型（可選）
            'min': float,      # 數值最小值（數值型）
            'max': float,      # 數值最大值（數值型）
            'values': list,    # 可能的值（類別型）
            'format': str      # 格式（日期時間型）
        }
    }
```

## 基本範例

```python
from petsard import Loader

# 初始化載入器
loader = Loader('data.csv')

# 載入資料
data, schema = loader.load()

# 查看結果
print(f"資料形狀: {data.shape}")
print(f"欄位類型: {schema.column_types}")
```

## 錯誤處理

### 檔案不存在

```python
try:
    loader = Loader('non_existent.csv')
    data, schema = loader.load()
except FileNotFoundError as e:
    print(f"錯誤：{e}")
```

### 不支援的檔案格式

```python
try:
    loader = Loader('data.unknown')
    data, schema = loader.load()
except ValueError as e:
    print(f"錯誤：{e}")
```

### Schema 不符

```python
try:
    loader = Loader('data.csv', schema='wrong_schema.yaml')
    data, schema = loader.load()
except ValueError as e:
    print(f"錯誤：{e}")
```

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 必須先呼叫 `__init__()` 初始化載入器
- 大型檔案建議使用 `nrows`、`usecols` 或 `chunksize` 參數
- Schema 不符時會拋出例外，請確保 schema 與資料一致
- Benchmark 資料集首次載入需要網路連線
- 返回的 DataFrame 是複製而非參照，修改不會影響原始檔案