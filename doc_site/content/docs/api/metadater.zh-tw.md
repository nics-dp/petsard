---
title: Metadater
type: docs
weight: 53
prev: docs/api/executor
next: docs/api/processor
---


```python
Metadater
```

詮釋資料管理系統，提供資料結構描述與管理功能。採用三層架構設計，配合操作與設定分離的模式。

## 架構設計

### 📊 三層架構對應
| 設定層級 | 對應資料 | 說明 |
|---------|---------|------|
| **Metadata** | Datasets | 管理多個表格的資料集 |
| **Schema** | Table | 定義單一表格結構 |  
| **Attribute** | Field | 描述單一欄位屬性 |

### 🔧 操作與設定分離
- **操作類別**：`Metadater`、`SchemaMetadater`、`AttributeMetadater`
- **設定類別**：`Metadata`、`Schema`、`Attribute`（凍結資料類別）
- **資料抽象層**：`Datasets`、`Table`、`Field`

## 基本使用方式

### 從資料推斷結構
```python
from petsard.metadater import Metadater, SchemaMetadater
import pandas as pd

# 單表格資料
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# 自動推斷 Schema
schema = SchemaMetadater.from_data(df)

# 多表格資料集
data = {
    'users': df,
    'orders': pd.DataFrame({
        'order_id': [101, 102],
        'user_id': [1, 2],
        'amount': [99.99, 149.99]
    })
}

# 建立詮釋資料
metadata = Metadater.from_data(data)
```

### 從設定建立
```python
# 從 YAML 設定建立
config = {
    'id': 'my_dataset',
    'schemas': {
        'users': {
            'id': 'users',
            'fields': {  # YAML 中使用 fields
                'id': {
                    'type': 'int64',
                    'nullable': False
                },
                'email': {
                    'type': 'object',
                    'logical_type': 'email'
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)
```

## 主要方法

### `from_data()`

```python
Metadater.from_data(
    data: dict[str, pd.DataFrame],
    enable_stats: bool = False
) -> Metadata
```

從資料自動推斷並建立詮釋資料結構。

**參數**
- `data` (dict[str, pd.DataFrame])：資料表字典
- `enable_stats` (bool, 選填)：是否計算統計資料，預設為 `False`

**回傳值**
- `Metadata`：詮釋資料物件（當 `enable_stats=True` 時包含統計資訊）

### `from_dict()`

```python
Metadater.from_dict(config: dict) -> Metadata
```

從設定字典建立詮釋資料。

**參數**
- `config` (dict)：詮釋資料設定

**回傳值**
- `Metadata`：詮釋資料物件

### `diff()`

```python
Metadater.diff(metadata: Metadata, data: dict[str, pd.DataFrame]) -> dict
```

比較詮釋資料定義與實際資料的差異。

**參數**
- `metadata` (Metadata)：詮釋資料定義
- `data` (dict[str, pd.DataFrame])：實際資料

**回傳值**
- `dict`：差異報告

### `align()`

```python
Metadater.align(metadata: Metadata, data: dict[str, pd.DataFrame], strategy: dict = None) -> dict[str, pd.DataFrame]
```

根據詮釋資料定義對齊資料結構。

**參數**
- `metadata` (Metadata)：詮釋資料定義
- `data` (dict[str, pd.DataFrame])：待對齊資料
- `strategy` (dict, 選填)：對齊策略

**回傳值**
- `dict[str, pd.DataFrame]`：對齊後的資料

## 資料結構

### Metadata（最上層）
```python
@dataclass(frozen=True)
class Metadata:
    id: str                        # 資料集識別碼
    schemas: dict[str, Schema]     # 表格結構字典
    stats: DatasetsStats | None    # 資料集統計（enable_stats=True 時產生）
    diffs: dict | None             # 差異記錄
    change_history: list | None    # 變更歷史
```

### Schema（中間層）
```python
@dataclass(frozen=True)
class Schema:
    id: str                              # 表格識別碼
    attributes: dict[str, Attribute]     # 欄位屬性字典
    stats: TableStats | None             # 表格統計（enable_stats=True 時產生）
```

### Attribute（最底層）
```python
@dataclass(frozen=True)
class Attribute:
    name: str                # 欄位名稱
    type: str                # 資料型別
    nullable: bool           # 是否允許空值
    logical_type: str | None # 邏輯型別
    stats: FieldStats | None # 欄位統計（enable_stats=True 時產生）
```

## 資料抽象層

### Field
```python
@dataclass
class Field:
    data: pd.Series      # 資料序列
    attribute: Attribute # 欄位屬性
    
    @classmethod
    def create(cls, data: pd.Series, attribute: Attribute = None) -> Field:
        """建立 Field 實例"""
```

### Table  
```python
@dataclass
class Table:
    data: pd.DataFrame  # 資料框架
    schema: Schema      # 表格架構
    
    @classmethod
    def create(cls, data: pd.DataFrame, schema: Schema = None) -> Table:
        """建立 Table 實例"""
```

### Datasets
```python
@dataclass
class Datasets:
    data: dict[str, pd.DataFrame]  # 資料表字典
    metadata: Metadata              # 詮釋資料
    
    @classmethod
    def create(cls, data: dict[str, pd.DataFrame], metadata: Metadata = None) -> Datasets:
        """建立 Datasets 實例"""
```

## 對齊策略

```python
strategy = {
    'add_missing_columns': True,    # 新增缺失欄位
    'remove_extra_columns': False,  # 移除額外欄位  
    'reorder_columns': True,        # 重新排序欄位
    'add_missing_tables': False     # 新增缺失表格
}
```

## 範例

### 基本使用

```python
from petsard.metadater import Metadater
import pandas as pd

# 準備資料
data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com']
    })
}

# 從資料建立詮釋資料
metadata = Metadater.from_data(data)

print(f"資料集 ID：{metadata.id}")
print(f"表格數量：{len(metadata.schemas)}")

# 包含統計資料
metadata_with_stats = Metadater.from_data(data, enable_stats=True)
users_schema = metadata_with_stats.schemas['users']
print(f"總列數：{users_schema.stats.row_count if users_schema.stats else 'N/A'}")
```

### 差異比較

```python
# 修改後的資料
new_data = {
    'users': pd.DataFrame({
        'id': [1, 2, 3, 4],  # 多一筆資料
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 40]  # 多一個欄位
    })
}

# 比較差異
diff_result = Metadater.diff(metadata, new_data)

print(f"缺失表格：{diff_result.get('missing_tables', [])}")
print(f"額外表格：{diff_result.get('extra_tables', [])}")
```

### 資料對齊

```python
# 不一致的資料
messy_data = {
    'users': pd.DataFrame({
        'id': ['1', '2', '3'],  # 型別錯誤
        'email': ['a@test.com', 'b@test.com', 'c@test.com'],
        'extra_col': [1, 2, 3]  # 額外欄位
    })
}

# 對齊資料
aligned_data = Metadater.align(metadata, messy_data)

# aligned_data 現在符合 metadata 定義
```

### 使用資料抽象層

```python
from petsard.metadater import Field, Table, Datasets

# Field 層級
series = pd.Series([1, 2, 3], name='numbers')
field = Field.create(series)
print(f"欄位名稱：{field.name}")
print(f"唯一值數量：{field.unique_count}")

# Table 層級
df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
table = Table.create(df)
print(f"欄位：{table.columns}")
print(f"資料筆數：{table.row_count}")

# Datasets 層級
data = {'table1': df}
datasets = Datasets.create(data)
print(f"表格名稱：{datasets.table_names}")
```

## YAML Schema 配置

在 YAML 中定義 Schema：

```yaml
# schemas/user_schema.yaml
id: user_data
fields:  # 使用 fields 定義欄位屬性
  user_id:
    type: int64
    nullable: false
  username:
    type: object
  email:
    type: object
    logical_type: email
```

在 Loader 中使用：

```yaml
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```