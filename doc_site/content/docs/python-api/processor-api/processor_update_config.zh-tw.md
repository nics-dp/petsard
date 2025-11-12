---
title: "update_config()"
weight: 336
---

更新處理器的配置設定。

## 語法

```python
def update_config(
    config: dict
) -> None
```

## 參數

- **config** : dict, required
    - 新的處理器配置
    - 必要參數
    - 結構：`{處理類型: {欄位名稱: 處理方式}}`

## 返回值

無（方法會修改實例狀態）

## 說明

`update_config()` 方法用於更新處理器的配置。可以：

1. 覆寫預設的處理方式
2. 為特定欄位設定自訂處理器
3. 停用特定欄位的處理（設為 `None` 或 `"none"`）

## 基本範例

```python
from petsard import Loader, Processor

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 建立處理器
processor = Processor(metadata=schema)

# 更新配置
new_config = {
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot',
        'education': 'encoder_label'
    }
}
processor.update_config(new_config)

# 使用更新後的配置
processor.fit(data)
processed_data = processor.transform(data)
```

## 配置格式

### 1. 使用處理器名稱（字串）

```python
config = {
    'missing': {
        'age': 'missing_mean',
        'income': 'missing_median'
    },
    'outlier': {
        'age': 'outlier_zscore',
        'income': 'outlier_iqr'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    },
    'scaler': {
        'age': 'scaler_minmax',
        'income': 'scaler_standard'
    }
}
processor.update_config(config)
```

### 2. 使用帶參數的處理器（字典）

```python
config = {
    'missing': {
        'age': {
            'method': 'missing_simple',
            'value': 0.0
        }
    },
    'scaler': {
        'created_at': {
            'method': 'scaler_timeanchor',
            'reference': 'event_time',
            'unit': 'D'
        }
    },
    'encoder': {
        'doc_date': {
            'method': 'encoder_date',
            'input_format': '%MinguoY-%m-%d',
            'date_type': 'date'
        }
    }
}
processor.update_config(config)
```

### 3. 停用特定處理

```python
config = {
    'outlier': {
        'age': None,  # 不處理 age 的離群值
        'income': 'outlier_iqr'
    },
    'scaler': {
        'gender': 'none'  # 字串 "none" 也可以停用
    }
}
processor.update_config(config)
```

## 部分更新

```python
# 只更新部分欄位，其他欄位保持預設
processor = Processor(metadata=schema)

# 只更新 age 欄位的缺失值處理
processor.update_config({
    'missing': {
        'age': 'missing_median'
    }
})

# 其他欄位仍使用預設配置
```

## 多次更新

```python
processor = Processor(metadata=schema)

# 第一次更新
processor.update_config({
    'missing': {'age': 'missing_median'}
})

# 第二次更新（會覆蓋或新增）
processor.update_config({
    'missing': {'income': 'missing_mean'},
    'encoder': {'gender': 'encoder_onehot'}
})

# 最終配置包含所有更新
```

## 在初始化時設定配置

```python
# 也可以在建立處理器時直接提供配置
custom_config = {
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    }
}

processor = Processor(metadata=schema, config=custom_config)
# 不需要再呼叫 update_config()
```

## 驗證配置更新

```python
processor = Processor(metadata=schema)

# 更新配置
new_config = {
    'missing': {'age': 'missing_median'},
    'encoder': {'gender': 'encoder_onehot'}
}
processor.update_config(new_config)

# 驗證更新
config = processor.get_config(col=['age', 'gender'])
print("age missing:", type(config['missing']['age']).__name__)
print("gender encoder:", type(config['encoder']['gender']).__name__)
```

## 可用的處理器名稱

### 缺失值處理器
- `missing_mean`：平均值填補
- `missing_median`：中位數填補
- `missing_mode`：眾數填補
- `missing_simple`：自訂值填補（需要 `value` 參數）
- `missing_drop`：刪除含缺失值的列

### 離群值處理器
- `outlier_zscore`：Z-Score 方法
- `outlier_iqr`：四分位距方法
- `outlier_isolationforest`：隔離森林（全域）
- `outlier_lof`：局部離群因子（全域）

### 編碼器
- `encoder_uniform`：均勻編碼
- `encoder_label`：標籤編碼
- `encoder_onehot`：獨熱編碼
- `encoder_date`：日期格式轉換（需要參數）

### 縮放器
- `scaler_standard`：標準化
- `scaler_minmax`：最小-最大縮放
- `scaler_zerocenter`：零中心化
- `scaler_log`：對數轉換
- `scaler_log1p`：log(1+x) 轉換
- `scaler_timeanchor`：時間錨點縮放（需要參數）

### 離散化
- `discretizing_kbins`：K-bins 離散化（需要參數）

## 注意事項

- 更新配置會覆寫該欄位的預設設定
- 必須在 `fit()` 之前呼叫此方法
- 如果在 `fit()` 之後更新配置，需要重新訓練
- 無效的處理器名稱會拋出 `ConfigError`
- 設為 `None` 或 `"none"` 會停用該處理
- 帶參數的處理器必須使用字典格式
- 更新是累加的，不會清除其他欄位的配置