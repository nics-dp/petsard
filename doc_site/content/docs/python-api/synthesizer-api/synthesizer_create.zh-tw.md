---
title: "create()"
weight: 362
---

建立並初始化合成器。

## 語法

```python
def create(metadata: SchemaMetadata = None)
```

## 參數

- **metadata** : SchemaMetadata, optional
    - 資料集的結構描述元資料
    - 包含資料的結構定義
    - 預設值：`None`

## 返回值

無。初始化合成器的內部狀態。

## 說明

`create()` 方法用於建立並初始化合成器實例。此方法會根據初始化時指定的合成方法（如 SDV、自訂方法等）來設定合成器的內部實作。

此方法執行以下操作：
1. 根據 `method` 參數選擇適當的合成器實作
2. 傳遞 metadata 給實作類別
3. 初始化合成器的內部狀態
4. 準備合成器以進行後續的訓練（`fit()`）操作

## 基本範例

```python
from petsard import Synthesizer, Metadater

# 從資料建立 metadata
df = pd.read_csv('data.csv')
metadata = Metadater.from_data(df)

# 建立合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)

# 現在可以進行訓練
synthesizer.fit(data=df)
```

## 進階範例

### 使用 SDV CTGAN

```python
from petsard import Synthesizer, Metadater

# 準備 metadata
metadata = Metadater.from_data(df)

# 使用 CTGAN 合成器
synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)

# 訓練並生成
synthesizer.fit_sample(data=df, sample_num_rows=1000)
```

### 使用自訂合成器

```python
from petsard import Synthesizer

# 使用自訂合成器（需要自訂類別實作）
synthesizer = Synthesizer(
    method='custom_method',
    module_path='my_synthesizer.py',
    class_name='MyCustomSynthesizer'
)

# metadata 會傳遞給自訂合成器
synthesizer.create(metadata=metadata)
```

## 注意事項

- 必須在呼叫 `fit()` 或 `fit_sample()` 之前先呼叫 `create()`
- metadata 參數是選用的，但建議提供以確保正確的資料結構處理
- 對於 SDV 合成器，metadata 會自動轉換為 SDV 所需的格式
- 自訂合成器必須實作相容的介面以接收 metadata
- 此方法不會返回值，而是更新合成器的內部狀態
- 重複呼叫 `create()` 會重新初始化合成器