---
title: "get_config()"
weight: 335
---

取得處理器的配置設定。

## 語法

```python
def get_config(
    col: list = None
) -> dict
```

## 參數

- **col** : list, optional
    - 要取得配置的欄位名稱列表
    - 預設值：`None`（返回所有欄位的配置）

## 返回值

- **dict**
    - 處理器配置字典
    - 結構：`{處理類型: {欄位名稱: 處理器實例}}`

## 說明

[`get_config()`](processor_get_config.zh-tw.md:1) 方法用於檢視處理器的當前配置。可以用來：

1. 查看所有欄位的處理方式
2. 檢查特定欄位的配置
3. 驗證配置是否符合預期

## 基本範例

```python
from petsard import Loader, Processor

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 建立處理器
processor = Processor(metadata=schema)

# 取得所有欄位的配置
config = processor.get_config()

# 檢視配置
for proc_type, fields in config.items():
    print(f"\n{proc_type}:")
    for field, proc_obj in fields.items():
        if proc_obj is not None:
            print(f"  {field}: {type(proc_obj).__name__}")
```

## 取得特定欄位配置

```python
from petsard import Processor

processor = Processor(metadata=schema)

# 只取得特定欄位的配置
config = processor.get_config(col=['age', 'income', 'gender'])

print("age, income, gender 的配置：")
for proc_type, fields in config.items():
    print(f"\n{proc_type}:")
    for field, proc_obj in fields.items():
        if proc_obj is not None:
            print(f"  {field}: {type(proc_obj).__name__}")
```

## 返回結構範例

```python
{
    'missing': {
        'age': <MissingMean instance>,
        'income': <MissingMean instance>,
        'gender': <MissingDrop instance>
    },
    'outlier': {
        'age': <OutlierIQR instance>,
        'income': <OutlierIQR instance>,
        'gender': None
    },
    'encoder': {
        'age': None,
        'income': None,
        'gender': <EncoderUniform instance>
    },
    'scaler': {
        'age': <ScalerStandard instance>,
        'income': <ScalerStandard instance>,
        'gender': None
    }
}
```

## 使用案例

### 1. 驗證配置

```python
processor = Processor(metadata=schema, config=custom_config)
config = processor.get_config()

# 驗證特定欄位使用正確的處理器
assert type(config['encoder']['gender']).__name__ == 'EncoderOneHot'
print("配置驗證通過！")
```

### 2. 檢查預設配置

```python
# 使用預設配置
processor = Processor(metadata=schema)
config = processor.get_config()

# 查看數值型欄位的預設處理方式
numerical_fields = ['age', 'income', 'hours_per_week']
for field in numerical_fields:
    print(f"{field}:")
    for proc_type in ['missing', 'outlier', 'scaler']:
        proc = config[proc_type][field]
        if proc:
            print(f"  {proc_type}: {type(proc).__name__}")
```

### 3. 比較配置差異

```python
# 建立兩個不同配置的處理器
processor1 = Processor(metadata=schema)
processor2 = Processor(metadata=schema, config=custom_config)

config1 = processor1.get_config(col=['age'])
config2 = processor2.get_config(col=['age'])

print("處理器1的配置：")
for proc_type, fields in config1.items():
    if fields['age']:
        print(f"  {proc_type}: {type(fields['age']).__name__}")

print("\n處理器2的配置：")
for proc_type, fields in config2.items():
    if fields['age']:
        print(f"  {proc_type}: {type(fields['age']).__name__}")
```

## 注意事項

- 返回的配置是處理器實例，不是字串名稱
- `None` 值表示該處理類型不套用於該欄位
- 可以在任何時候呼叫此方法，不需要先 [`fit()`](processor_fit.zh-tw.md:1)
- 配置會在 [`update_config()`](processor_update_config.zh-tw.md:1) 後更新
- 如果提供的欄位名稱不存在，會在返回的配置中被忽略
- 全域轉換處理器（如 `outlier_isolationforest`）會套用到所有欄位