---
title: "Metadater API"
weight: 320
---

資料結構描述管理器，提供資料集的詮釋資料（Metadata）定義、推斷、比較與對齊功能。

## 類別架構

{{< mermaid-file file="content/docs/python-api/metadater-api/metadater-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要操作類別
> - 橘色框：資料配置類別
> - 淺藍框：資料抽象類別
> - `..>`：建立/操作關係
> - `*--`：組合關係
> - `-->`：呼叫關係

## 模組概覽

Metadater 模組提供三層架構的資料結構描述系統：

### 配置類別（Configuration Classes）

定義資料結構的靜態配置：

- [`Metadata`](#metadata)：資料集層級的詮釋資料配置
- [`Schema`](#schema)：表格層級的結構配置
- [`Attribute`](#attribute)：欄位層級的屬性配置

### 操作類別（Operation Classes）

提供類別方法來操作配置物件：

- [`Metadater`](#metadater)：多表格操作（對應 [`Metadata`](#metadata)）
- [`SchemaMetadater`](#schemametadater)：單表格操作（對應 [`Schema`](#schema)）
- [`AttributeMetadater`](#attributemetadater)：單欄位操作（對應 [`Attribute`](#attribute)）

### 資料抽象類別（Data Abstraction Classes）

結合資料與配置的高階抽象：

- [`Datasets`](#datasets)：多表格資料集（資料 + [`Metadata`](#metadata)）
- [`Table`](#table)：單一表格（資料 + [`Schema`](#schema)）
- [`Field`](#field)：單一欄位（資料 + [`Attribute`](#attribute)）

### Schema 推斷工具

- [`SchemaInferencer`](#schemainferencer)：推斷 Processor 轉換後的 Schema 變化
- [`ProcessorTransformRules`](#processortransformrules)：定義 Processor 的 Schema 轉換規則
- [`TransformRule`](#transformrule)：單一轉換規則的資料類別

## 基本使用

### 透過 Loader 使用（推薦）

Metadater 主要作為內部元件使用，通常透過 Loader 的 schema 參數間接使用：

```python
# 在 YAML 中定義
Loader:
  my_experiment:
    filepath: data/users.csv
    schema: schemas/user_schema.yaml
```

### 直接使用 Metadater

若需直接操作詮釋資料：

```python
from petsard.metadater import Metadater
import pandas as pd

# 從資料自動推斷結構
data = {'users': pd.DataFrame(...)}
metadata = Metadater.from_data(data)

# 從字典建立詮釋資料
config = {'schemas': {'users': {...}}}
metadata = Metadater.from_dict(config)

# 比較資料差異
diff = Metadater.diff(metadata, new_data)

# 對齊資料結構
aligned = Metadater.align(metadata, new_data)
```

### 使用資料抽象層

結合資料與詮釋資料的物件導向操作：

```python
from petsard.metadater import Datasets, Table, Field

# 建立資料集抽象
datasets = Datasets.create(data={'users': df}, metadata=metadata)

# 取得表格
table = datasets.get_table('users')
print(f"表格有 {table.row_count} 列，{table.column_count} 欄")

# 取得欄位
field = table.get_field('age')
print(f"欄位型別：{field.dtype}，空值數量：{field.null_count}")

# 驗證資料
is_valid, errors = datasets.validate()
if not is_valid:
    print("驗證失敗：", errors)
```

## 配置類別

### Metadata

最上層配置類別，管理整個資料集：

```python
from petsard.metadater import Metadata, Schema

metadata = Metadata(
    id="my_dataset",
    name="我的資料集",
    description="資料集描述",
    schemas={
        'users': Schema(...),
        'orders': Schema(...),
    }
)
```

**主要屬性**：
- `id`: 資料集識別碼
- `name`: 資料集名稱（選填）
- `description`: 資料集描述（選填）
- `schemas`: 表格結構字典 `{table_name: Schema}`
- `enable_stats`: 是否啟用統計資訊
- `stats`: 資料集統計資訊（DatasetsStats）

### Schema

中間層配置類別，描述單一表格：

```python
from petsard.metadater import Schema, Attribute

schema = Schema(
    id="users",
    name="使用者表格",
    description="使用者資訊",
    attributes={
        'user_id': Attribute(name='user_id', type='int'),
        'email': Attribute(name='email', type='str', logical_type='email'),
    }
)
```

**主要屬性**：
- `id`: 表格識別碼
- `name`: 表格名稱（選填）
- `description`: 表格描述（選填）
- `attributes`: 欄位屬性字典 `{field_name: Attribute}`
- `primary_key`: 主鍵欄位列表
- `enable_stats`: 是否啟用統計資訊
- `stats`: 表格統計資訊（TableStats）

### Attribute

最底層配置類別，定義單一欄位：

```python
from petsard.metadater import Attribute

attribute = Attribute(
    name="age",
    type="int",
    type_attr={
        "nullable": True,
        "category": False,
    },
    logical_type=None,
    description="使用者年齡",
)
```

**主要屬性**：
- `name`: 欄位名稱
- `type`: 資料型別（`int`, `float`, `str`, `date`, `datetime`）
- `type_attr`: 型別屬性字典
  - `nullable`: 是否允許空值
  - `category`: 是否為類別資料
  - `precision`: 數值精度（小數位數）
  - `format`: 日期時間格式
  - `width`: 字串寬度（用於前導零）
- `logical_type`: 邏輯型別（如 `email`, `phone`, `url` 等）
- `enable_stats`: 是否啟用統計資訊
- `stats`: 欄位統計資訊（FieldStats）
- `is_constant`: 標記所有值都相同的欄位（自動偵測）

## 操作類別

### Metadater

多表格操作類別，提供類別方法：

#### 建立方法

- [`from_data(data, enable_stats=False)`](metadater_from_data)：從資料自動推斷並建立 Metadata
- [`from_dict(config)`](metadater_from_dict)：從配置字典建立 Metadata
- `from_metadata(metadata)`：複製 Metadata 配置

#### 操作方法

- [`diff(metadata, data)`](metadater_diff)：比較 Metadata 與實際資料的差異
- [`align(metadata, data, strategy=None)`](metadater_align)：根據 Metadata 對齊資料結構
- `get(metadata, name)`：從 Metadata 取得指定 Schema
- `add(metadata, schema)`：新增 Schema 到 Metadata
- `update(metadata, schema)`：更新 Metadata 中的 Schema
- `remove(metadata, name)`：從 Metadata 移除 Schema

### SchemaMetadater

單表格操作類別，提供類別方法：

#### 建立方法

- `from_data(data, enable_stats=False, base_schema=None)`：從 DataFrame 建立 Schema
- `from_dict(config)`：從配置字典建立 Schema
- `from_yaml(filepath)`：從 YAML 檔案載入 Schema
- `from_metadata(schema)`：複製 Schema 配置

#### 操作方法

- `diff(schema, data)`：比較 Schema 與 DataFrame 的差異
- `align(schema, data, strategy=None)`：根據 Schema 對齊 DataFrame
- `get(schema, name)`：從 Schema 取得指定 Attribute
- `add(schema, attribute)`：新增 Attribute 到 Schema
- `update(schema, attribute)`：更新 Schema 中的 Attribute
- `remove(schema, name)`：從 Schema 移除 Attribute

### AttributeMetadater

單欄位操作類別，提供類別方法：

#### 建立方法

- `from_data(data, enable_stats=True, base_attribute=None)`：從 Series 建立 Attribute
- `from_dict(config)`：從配置字典建立 Attribute
- `from_metadata(attribute)`：複製 Attribute 配置

#### 操作方法

- `diff(attribute, data)`：比較 Attribute 與 Series 的差異
- `align(attribute, data, strategy=None)`：根據 Attribute 對齊 Series
- `validate(attribute, data)`：驗證 Series 是否符合 Attribute 定義
- `cast(attribute, data)`：根據 Attribute 定義轉換資料型別

## 資料抽象類別

### Datasets

多表格資料集抽象，結合資料與 Metadata：

```python
from petsard.metadater import Datasets

# 建立資料集
datasets = Datasets.create(
    data={'users': df1, 'orders': df2},
    metadata=metadata  # 選填，自動推斷
)

# 取得資訊
print(f"表格數量：{datasets.table_count}")
print(f"表格名稱：{datasets.table_names}")

# 操作表格
table = datasets.get_table('users')
tables = datasets.get_tables()

# 驗證與對齊
is_valid, errors = datasets.validate()
aligned_data = datasets.align()
diff = datasets.diff()
```

### Table

單一表格抽象，結合 DataFrame 與 Schema：

```python
from petsard.metadater import Table

# 建立表格
table = Table.create(
    data=df,
    schema=schema  # 選填，自動推斷
)

# 取得資訊
print(f"列數：{table.row_count}")
print(f"欄數：{table.column_count}")
print(f"欄位名稱：{table.columns}")

# 操作欄位
field = table.get_field('age')
fields = table.get_fields()

# 驗證與對齊
is_valid, errors = table.validate()
aligned_df = table.align()
diff = table.diff()
```

### Field

單一欄位抽象，結合 Series 與 Attribute：

```python
from petsard.metadater import Field

# 建立欄位
field = Field.create(
    data=series,
    attribute=attribute  # 選填，自動推斷
)

# 取得資訊
print(f"欄位名稱：{field.name}")
print(f"資料型別：{field.dtype}")
print(f"期望型別：{field.expected_type}")
print(f"空值數量：{field.null_count}")
print(f"唯一值數量：{field.unique_count}")

# 驗證與對齊
is_valid = field.is_valid
errors = field.get_validation_errors()
aligned_series = field.align()
```

## Schema 推斷工具

### SchemaInferencer

推斷 Processor 轉換後的 Schema 變化：

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# 推斷 Preprocessor 輸出 Schema
output_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# 推斷整個管線的 Schema 變化
pipeline_schemas = inferencer.infer_pipeline_schemas(
    loader_schema=loader_schema,
    pipeline_config=pipeline_config
)

# 取得推斷歷史
history = inferencer.get_inference_history()
```

### ProcessorTransformRules

定義 Processor 的 Schema 轉換規則：

```python
from petsard.metadater import ProcessorTransformRules

# 取得轉換規則
rule = ProcessorTransformRules.get_rule('encoder_label')

# 應用規則到 Attribute
transformed_attr = ProcessorTransformRules.apply_rule(attribute, rule)

# 應用動態轉換資訊
transformed_attr = ProcessorTransformRules.apply_transform_info(
    attribute, transform_info
)
```

### TransformRule

單一轉換規則的資料類別：

```python
from petsard.metadater import TransformRule

rule = TransformRule(
    processor_type='encoder',
    processor_method='encoder_label',
    input_types=['categorical', 'string'],
    output_type='int',
    output_logical_type='encoded_categorical',
    affects_nullable=True,
    nullable_after=False,
)
```

## 使用情境

### 1. 資料載入時的 Schema 管理

Loader 內部使用 Metadater 處理 schema：

```python
# Loader 內部流程（簡化）
metadata = Metadater.from_dict(schema_config)  # 從 YAML 載入
data = pd.read_csv(filepath)                    # 讀取資料
aligned_data = Metadater.align(metadata, {'table': data})  # 對齊資料結構
```

### 2. 資料結構驗證

使用資料抽象層進行驗證：

```python
# 建立資料集抽象
datasets = Datasets.create(data={'users': df}, metadata=expected_metadata)

# 驗證資料
is_valid, errors = datasets.validate()

if not is_valid:
    for table_name, table_errors in errors.items():
        print(f"表格 {table_name} 驗證失敗：")
        for field_name, field_errors in table_errors.items():
            print(f"  - {field_name}: {field_errors}")
```

### 3. 多資料集結構統一

確保多個資料集具有相同結構：

```python
# 定義標準結構
standard_metadata = Metadater.from_data({'users': reference_data})

# 對齊其他資料集
aligned_data1 = Metadater.align(standard_metadata, {'users': data1})
aligned_data2 = Metadater.align(standard_metadata, {'users': data2})
```

### 4. 推斷 Processor 轉換後的 Schema

在執行管線前預測 Schema 變化：

```python
from petsard.metadater import SchemaInferencer

inferencer = SchemaInferencer()

# 推斷 Preprocessor 輸出
preprocessed_schema = inferencer.infer_preprocessor_output(
    input_schema=loader_schema,
    processor_config=preprocessor_config
)

# 檢查欄位型別變化
for col_name, attr in preprocessed_schema.attributes.items():
    original_type = loader_schema.attributes[col_name].type
    new_type = attr.type
    if original_type != new_type:
        print(f"欄位 {col_name} 型別變化：{original_type} → {new_type}")
```

## 型別系統

Metadater 使用簡化的型別系統：

### 基本型別

- `int`：整數型別
- `float`：浮點數型別
- `str`：字串型別
- `date`：日期型別
- `datetime`：日期時間型別

### 邏輯型別

選填的語義型別，用於更精確的資料描述：

- `email`：電子郵件
- `phone`：電話號碼
- `url`：網址
- `encoded_categorical`：編碼後的類別資料
- `onehot_encoded`：One-hot 編碼
- `standardized`：標準化數值
- `normalized`：正規化數值
- 其他自訂邏輯型別

### 型別屬性

`type_attr` 字典包含額外的型別資訊：

- `nullable`: 是否允許空值（`True`/`False`）
- `category`: 是否為類別資料（`True`/`False`）
- `precision`: 數值精度（小數位數）
- `format`: 日期時間格式字串
- `width`: 字串寬度（用於前導零）

## 注意事項

- **內部使用為主**：Metadater 主要供 PETsARD 內部模組使用，一般使用者透過 Loader 的 `schema` 參數即可
- **類別方法設計**：所有操作類別的方法都是類別方法，不需要實例化
- **不可變設計**：配置物件採用 dataclass 設計，修改時會返回新物件
- **自動推斷**：`from_data()` 會自動推斷欄位類型、空值處理和統計資訊
- **對齊行為**：`align()` 會根據配置調整欄位順序、補充缺失欄位、轉換資料類型
- **差異檢測**：`diff()` 檢測欄位名稱、類型、空值處理等差異
- **統計資訊**：設定 `enable_stats=True` 可啟用詳細的統計資訊計算
- **YAML 配置**：詳細的 Schema YAML 配置請參閱 [Schema YAML 文檔](../../schema-yaml/)

## API 文檔

### Metadater 方法

- [`from_data()`](metadater_from_data)：從資料自動推斷並建立 Metadata
- [`from_dict()`](metadater_from_dict)：從配置字典建立 Metadata
- [`diff()`](metadater_diff)：比較 Metadata 與實際資料的差異
- [`align()`](metadater_align)：根據 Metadata 對齊資料結構

### 其他 API

詳細的 API 文檔請參考各個方法的專屬頁面。