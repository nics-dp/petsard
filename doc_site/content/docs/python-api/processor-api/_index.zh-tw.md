---
title: "Processor API（更新中）"
weight: 330
---

資料處理模組，支援前處理（preprocessing）和後處理（postprocessing）功能。

## 類別架構

{{< mermaid-file file="content/docs/python-api/processor-api/processor-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 橘色框：子處理器類別
> - 淺紫框：配置與資料類別
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 基本使用

### 前處理（Preprocessing）

```python
from petsard import Processor

# 建立處理器
processor = Processor(metadata=schema)

# 訓練並轉換資料
processor.fit(data)
processed_data = processor.transform(data)
```

### 後處理（Postprocessing）

```python
# 使用相同的 processor 實例進行後處理
restored_data = processor.inverse_transform(synthetic_data)
```

### 完整工作流程

```python
from petsard import Loader, Processor, Synthesizer

# 1. 載入資料
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 2. 前處理
processor = Processor(metadata=schema)
processor.fit(data)
processed_data = processor.transform(data)

# 3. 合成資料
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit_sample(processed_data)
synthetic_data = synthesizer.data_syn

# 4. 後處理（還原）
restored_data = processor.inverse_transform(synthetic_data)
```

## 建構函式 (__init__)

初始化資料處理器實例。

### 語法

```python
def __init__(
    metadata: Schema,
    config: dict = None
)
```

### 參數

- **metadata** : Schema, required
    - 資料結構定義（Schema 物件）
    - 必要參數
    - 提供資料欄位的詮釋資料和型別資訊

- **config** : dict, optional
    - 自訂資料處理設定
    - 預設值：`None`
    - 用於覆寫預設的處理程序
    - 結構為 `{處理類型: {欄位名稱: 處理方式}}`

### 返回值

- **Processor**
    - 初始化後的處理器實例

### 使用範例

```python
from petsard import Loader, Processor

# 載入資料和 schema
loader = Loader('data.csv', schema='schema.yaml')
data, schema = loader.load()

# 基本使用 - 使用預設配置
processor = Processor(metadata=schema)

# 使用自訂配置
custom_config = {
    'missing': {
        'age': 'missing_mean',
        'income': 'missing_median'
    },
    'outlier': {
        'age': 'outlier_zscore',
        'income': 'outlier_iqr'
    },
    'encoder': {
        'gender': 'encoder_onehot',
        'education': 'encoder_label'
    },
    'scaler': {
        'age': 'scaler_minmax',
        'income': 'scaler_standard'
    }
}
processor = Processor(metadata=schema, config=custom_config)
```

## 處理序列

Processor 支援以下處理步驟：

1. **missing**：缺失值處理
2. **outlier**：離群值處理
3. **encoder**：類別變數編碼
4. **scaler**：數值正規化
5. **discretizing**：離散化（與 encoder 互斥）

預設序列：`['missing', 'outlier', 'encoder', 'scaler']`

## 預設處理方式

| 處理類型 | 數值型 | 類別型 | 日期時間型 |
|---------|--------|--------|-----------|
| **missing** | `MissingMean` | `MissingDrop` | `MissingDrop` |
| **outlier** | `OutlierIQR` | 無 | `OutlierIQR` |
| **encoder** | 無 | `EncoderUniform` | 無 |
| **scaler** | `ScalerStandard` | 無 | `ScalerStandard` |
| **discretizing** | `DiscretizingKBins` | `EncoderLabel` | `DiscretizingKBins` |

## 前處理 vs 後處理

| 操作 | 前處理方法 | 後處理方法 | 說明 |
|-----|----------|-----------|------|
| 訓練 | `fit()` | - | 學習資料統計特性 |
| 轉換 | `transform()` | - | 執行前處理轉換 |
| 還原 | - | `inverse_transform()` | 執行後處理還原 |

**注意**：前處理和後處理使用同一個 Processor 實例，確保轉換的一致性。

## 可用的處理器

### 缺失值處理器

- `missing_mean`：使用平均值填補
- `missing_median`：使用中位數填補
- `missing_mode`：使用眾數填補
- `missing_simple`：使用指定值填補
- `missing_drop`：刪除含缺失值的列

### 離群值處理器

- `outlier_zscore`：Z-Score 方法（閾值 3）
- `outlier_iqr`：四分位距方法（1.5 IQR）
- `outlier_isolationforest`：隔離森林演算法
- `outlier_lof`：局部離群因子演算法

### 編碼器

- `encoder_uniform`：均勻編碼（依頻率分配範圍）
- `encoder_label`：標籤編碼（整數映射）
- `encoder_onehot`：獨熱編碼
- `encoder_date`：日期格式轉換

### 縮放器

- `scaler_standard`：標準化（均值 0，標準差 1）
- `scaler_minmax`：最小-最大縮放（範圍 [0, 1]）
- `scaler_zerocenter`：零中心化（均值 0）
- `scaler_log`：對數轉換
- `scaler_log1p`：log(1+x) 轉換
- `scaler_timeanchor`：時間錨點縮放

### 離散化

- `discretizing_kbins`：K-bins 離散化

## 注意事項

- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **處理順序**：
  - 前處理：必須先呼叫 `fit()` 再呼叫 `transform()`
  - 後處理：必須先完成前處理才能呼叫 `inverse_transform()`
- **序列限制**：
  - `discretizing` 和 `encoder` 不能同時使用
  - `discretizing` 必須是序列中的最後一步
  - 最多支援 4 個處理步驟
- **全域轉換**：某些處理器（如 `outlier_isolationforest`、`outlier_lof`）會套用到所有欄位
- **實例重用**：前處理和後處理應使用同一個 Processor 實例
- **Schema 使用**：建議使用 Schema 來定義資料結構，詳細設定請參閱 Metadater API 文檔
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容