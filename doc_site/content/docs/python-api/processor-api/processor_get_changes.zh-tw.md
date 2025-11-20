---
title: "get_changes()"
weight: 337
---

比較當前配置與預設配置的差異。

## 語法

```python
def get_changes() -> pd.DataFrame
```

## 參數

無

## 返回值

- **pd.DataFrame**
    - 記錄配置差異的資料表
    - 欄位：`processor`（處理類型）、`col`（欄位名稱）、`current`（當前配置）、`default`（預設配置）

## 說明

`get_changes()` 方法用於檢視哪些配置被自訂修改過。此方法會：

1. 比較當前配置與預設配置
2. 列出所有差異
3. 以 DataFrame 格式返回結果

這對於除錯和文件記錄非常有用。

## 基本範例

```python
from petsard import Loader, Processor

# 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 建立處理器並更新配置
processor = Processor(metadata=schema)
processor.update_config({
    'missing': {
        'age': 'missing_median',
        'income': 'missing_mean'
    },
    'encoder': {
        'gender': 'encoder_onehot'
    },
    'scaler': {
        'age': 'scaler_minmax'
    }
})

# 查看修改了哪些配置
changes = processor.get_changes()
print(changes)
```

## 輸出範例

```
  processor      col           current         default
0   missing      age    MissingMedian     MissingMean
1   encoder   gender   EncoderOneHot  EncoderUniform
2    scaler      age    ScalerMinMax  ScalerStandard
```

## 檢查特定處理類型的變更

```python
processor = Processor(metadata=schema, config=custom_config)
changes = processor.get_changes()

# 只查看編碼器的變更
encoder_changes = changes[changes['processor'] == 'encoder']
print("編碼器的變更：")
print(encoder_changes)

# 只查看特定欄位的變更
age_changes = changes[changes['col'] == 'age']
print("\nage 欄位的變更：")
print(age_changes)
```

## 統計變更數量

```python
changes = processor.get_changes()

print(f"總共有 {len(changes)} 個配置被修改")
print(f"修改的處理類型：{changes['processor'].unique()}")
print(f"受影響的欄位：{changes['col'].unique()}")
```

## 導出變更記錄

```python
changes = processor.get_changes()

# 儲存為 CSV
changes.to_csv('processor_config_changes.csv', index=False)

# 或儲存為 Markdown 表格
print(changes.to_markdown(index=False))
```

## 使用案例

### 1. 驗證自訂配置

```python
# 確保重要欄位使用了自訂配置
processor = Processor(metadata=schema, config=custom_config)
changes = processor.get_changes()

# 檢查 age 是否使用中位數填補
age_missing = changes[
    (changes['col'] == 'age') &
    (changes['processor'] == 'missing')
]
assert 'Median' in age_missing['current'].values[0]
print("age 欄位配置驗證通過！")
```

### 2. 文件記錄

```python
# 記錄實驗使用的配置
processor = Processor(metadata=schema, config=experiment_config)
changes = processor.get_changes()

print("實驗配置記錄：")
print(f"日期：{datetime.now()}")
print(f"修改項目數：{len(changes)}")
print("\n詳細變更：")
print(changes.to_string(index=False))
```

### 3. 比較不同配置

```python
# 建立兩個不同配置的處理器
processor1 = Processor(metadata=schema, config=config1)
processor2 = Processor(metadata=schema, config=config2)

changes1 = processor1.get_changes()
changes2 = processor2.get_changes()

print("配置1的變更：")
print(changes1)
print("\n配置2的變更：")
print(changes2)
```

### 4. 偵測意外的配置變更

```python
processor = Processor(metadata=schema)

# 進行一些操作...
processor.update_config(some_config)

# 檢查是否有意外的變更
changes = processor.get_changes()
unexpected_cols = ['critical_field1', 'critical_field2']

unexpected_changes = changes[changes['col'].isin(unexpected_cols)]
if not unexpected_changes.empty:
    print("警告：關鍵欄位的配置被修改了！")
    print(unexpected_changes)
```

## 輸出格式

DataFrame 包含以下欄位：

| 欄位 | 說明 | 範例 |
|-----|------|------|
| `processor` | 處理類型 | `'missing'`, `'encoder'`, `'scaler'` |
| `col` | 欄位名稱 | `'age'`, `'gender'`, `'income'` |
| `current` | 當前使用的處理器 | `'MissingMedian'`, `'EncoderOneHot'` |
| `default` | 預設的處理器 | `'MissingMean'`, `'EncoderUniform'` |

## 注意事項

- 只顯示與預設配置不同的項目
- 如果沒有任何變更，返回空的 DataFrame
- 可以在任何時候呼叫此方法，不需要先 `fit()`
- 當前配置和預設配置都顯示類別名稱（不是實例）
- 如果欄位的處理器設為 `None`，也可能出現在變更列表中
- 全域轉換處理器（如 `outlier_isolationforest`）會影響所有欄位的顯示