---
title: "Metadater API"
weight: 320
---

資料結構描述管理器，提供資料集的詮釋資料（Metadata）定義、推斷、比較與對齊功能。

## 模組概覽

Metadater 採用三層架構：

### 配置類別（Configuration）

定義資料結構的靜態配置：

- **`Metadata`**：資料集層級配置
- **`Schema`**：表格層級配置
- **`Attribute`**：欄位層級配置

### 操作類別（Operations）

提供類別方法來操作配置：

- **`Metadater`**：多表格操作
- **`SchemaMetadater`**：單表格操作
- **`AttributeMetadater`**：單欄位操作

### 資料抽象類別（Data Abstraction）

結合資料與配置的高階抽象：

- **`Datasets`**：多表格資料集（資料 + Metadata）
- **`Table`**：單一表格（資料 + Schema）
- **`Field`**：單一欄位（資料 + Attribute）

### Schema 推斷工具

- **`SchemaInferencer`**：推斷 Processor 轉換後的 Schema
- **`ProcessorTransformRules`**：定義轉換規則
- **`TransformRule`**：單一轉換規則的資料類別

## 基本使用

### 透過 Loader 使用（推薦）

```python
# 在 YAML 中定義
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

### 直接使用 Metadater

```python
from petsard.metadater import Metadater
import pandas as pd

# 從資料推斷
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# 從字典建立
config = {'schemas': {'users': {...}}}
metadata = Metadater.from_dict(config)

# 比較差異
diff = Metadater.diff(metadata, new_data)

# 對齊資料
aligned = Metadater.align(metadata, new_data)
```

## 配置類別

### Metadata

資料集層級配置：

```python
from petsard.metadater import Metadata, Schema

metadata = Metadata(
    id="my_dataset",
    schemas={'users': Schema(...)}
)
```

**主要屬性**：
- `id`: 資料集識別碼
- `schemas`: 表格結構字典 `{table_name: Schema}`
- `enable_stats`: 是否啟用統計資訊
- `stats`: 資料集統計（DatasetsStats）

### Schema

表格層級配置：

```python
from petsard.metadater import Schema, Attribute

schema = Schema(
    id="users",
    attributes={
        'user_id': Attribute(name='user_id', type='int'),
        'email': Attribute(name='email', type='str'),
    }
)
```

**主要屬性**：
- `id`: 表格識別碼
- `attributes`: 欄位屬性字典 `{field_name: Attribute}`
- `primary_key`: 主鍵欄位列表
- `enable_stats`: 是否啟用統計
- `stats`: 表格統計（TableStats）

### Attribute

欄位層級配置：

```python
from petsard.metadater import Attribute

attribute = Attribute(
    name="age",
    type="int",
    type_attr={
        "nullable": True,
        "category": False,
    }
)
```

**主要屬性**：
- `name`: 欄位名稱
- `type`: 資料型別（`int`, `float`, `str`, `date`, `datetime`）
- `type_attr`: 型別屬性字典
  - `nullable`: 是否允許空值
  - `category`: 是否為類別資料
  - `precision`: 數值精度
  - `format`: 日期時間格式
  - `width`: 字串寬度
- `logical_type`: 邏輯型別（`email`, `phone`, `url` 等）
- `enable_stats`: 是否啟用統計
- `is_constant`: 所有值都相同的欄位

## 操作類別

### Metadater

多表格操作的類別方法：

#### 建立方法

- **`from_data(data, enable_stats=False)`**：從資料推斷並建立 Metadata
- **`from_dict(config)`**：從配置字典建立 Metadata
- **`from_metadata(metadata)`**：複製 Metadata

#### 操作方法

- **`diff(metadata, data)`**：比較差異
- **`align(metadata, data, strategy=None)`**：對齊資料
- **`get(metadata, name)`**：取得指定 Schema
- **`add(metadata, schema)`**：新增 Schema
- **`update(metadata, schema)`**：更新 Schema
- **`remove(metadata, name)`**：移除 Schema

### SchemaMetadater

單表格操作的類別方法：

#### 建立方法

- **`from_data(data, enable_stats=False, base_schema=None)`**：從 DataFrame 建立 Schema
- **`from_dict(config)`**：從配置字典建立 Schema
- **`from_yaml(filepath)`**：從 YAML 載入 Schema
- **`from_metadata(schema)`**：複製 Schema

#### 操作方法

- **`diff(schema, data)`**：比較差異
- **`align(schema, data, strategy=None)`**：對齊資料
- **`get(schema, name)`**：取得欄位屬性
- **`add(schema, attribute)`**：新增欄位
- **`update(schema, attribute)`**：更新欄位
- **`remove(schema, name)`**：移除欄位

### AttributeMetadater

單欄位操作的類別方法：

#### 建立方法

- **`from_data(data, enable_stats=True, base_attribute=None)`**：從 Series 建立欄位屬性
- **`from_dict(config)`**：從配置字典建立欄位屬性
- **`from_metadata(attribute)`**：複製欄位屬性

#### 操作方法

- **`diff(attribute, data)`**：比較差異
- **`align(attribute, data, strategy=None)`**：對齊資料
- **`validate(attribute, data)`**：驗證資料
- **`cast(attribute, data)`**：轉換資料型別

## 資料抽象類別

### Datasets

多表格資料集抽象：

```python
from petsard.metadater import Datasets

datasets = Datasets.create(
    data={'users': df},
    metadata=metadata
)

# 基本操作
table = datasets.get_table('users')
is_valid, errors = datasets.validate()
aligned_data = datasets.align()
```

**主要屬性**：
- `table_count`: 表格數量
- `table_names`: 表格名稱列表

**主要方法**：
- `get_table(name)`: 取得表格
- `get_tables()`: 取得所有表格
- `validate()`: 驗證資料
- `align()`: 對齊資料
- `diff()`: 比較差異

### Table

單一表格抽象：

```python
from petsard.metadater import Table

table = Table.create(data=df, schema=schema)

# 基本操作
field = table.get_field('age')
is_valid, errors = table.validate()
```

**主要屬性**：
- `row_count`: 列數
- `column_count`: 欄數
- `columns`: 欄位名稱

**主要方法**：
- `get_field(name)`: 取得欄位
- `get_fields()`: 取得所有欄位
- `validate()`: 驗證資料
- `align()`: 對齊資料

### Field

單一欄位抽象：

```python
from petsard.metadater import Field

field = Field.create(data=series, attribute=attribute)

# 基本資訊
print(field.dtype, field.null_count, field.unique_count)
```

**主要屬性**：
- `name`: 欄位名稱
- `dtype`: 資料型別
- `expected_type`: 期望型別
- `null_count`: 空值數量
- `unique_count`: 唯一值數量

**主要方法**：
- `is_valid`: 驗證狀態
- `get_validation_errors()`: 取得錯誤
- `align()`: 對齊資料

## Schema 推斷工具

### SchemaInferencer

推斷 Processor 轉換後的 Schema：

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# 推斷 Preprocessor 輸出
output_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# 推斷管線 Schema 變化
pipeline_schemas = inferencer.infer_pipeline_schemas(
    loader_schema=loader_schema,
    pipeline_config=pipeline_config
)
```

### ProcessorTransformRules

定義 Processor 的轉換規則：

```python
from petsard.metadater import ProcessorTransformRules

# 取得轉換規則
rule = ProcessorTransformRules.get_rule('encoder_label')

# 應用規則
transformed_attr = ProcessorTransformRules.apply_rule(attribute, rule)
```

## 型別系統

### 基本型別

- **`int`**：整數
- **`float`**：浮點數
- **`str`**：字串
- **`date`**：日期
- **`datetime`**：日期時間

### 邏輯型別

選填的語義型別：

- `email`, `phone`, `url`
- `encoded_categorical`, `onehot_encoded`
- `standardized`, `normalized`

### 型別屬性

`type_attr` 包含額外的型別資訊：

- `nullable`: 是否允許空值
- `category`: 是否為類別資料
- `precision`: 數值精度（小數位數）
- `format`: 日期時間格式
- `width`: 字串寬度（前導零）

## 注意事項

- **內部使用為主**：主要供 PETsARD 內部模組使用，一般使用者透過 Loader 即可
- **類別方法設計**：所有方法都是類別方法，無需實例化
- **不可變設計**：配置物件修改時返回新物件
- **自動推斷**：`from_data()` 會自動推斷型別、空值和統計資訊
- **統計啟用**：設定 `enable_stats=True` 啟用詳細統計