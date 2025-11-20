---
title: "Synthesizer API"
type: docs
weight: 1090
---

合成資料產生模組，支援多種合成方法並提供資料生成功能。

## 類別架構

{{< mermaid-file file="content/docs/python-api/synthesizer-api/synthesizer-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色框：主要類別
> - 橘色框：子類別實作
> - 淺紫框：配置與資料類別
> - `<|--`：繼承關係 (inheritance)
> - `*--`：組合關係 (composition)
> - `..>`：依賴關係 (dependency)

## 基本使用

```python
from petsard import Synthesizer

# 使用預設方法（PETsARD Gaussian Copula）
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df)
synthetic_data = synthesizer.data_syn

# 使用特定 SDV 方法（需額外安裝 SDV）
synthesizer = Synthesizer(method='sdv-single_table-ctgan')
synthesizer.create(metadata=metadata)
synthesizer.fit_sample(data=df, sample_num_rows=1000)
```

## 建構函式 (__init__)

初始化合成資料產生器實例。

### 語法

```python
def __init__(
    method: str,
    **kwargs
)
```

### 參數

- **method** : str, required
    - 合成方法名稱
    - 必要參數
    - 支援的方法：
        - `'default'` 或 `'petsard-gaussian_copula'`：使用 PETsARD 內建 Gaussian Copula
        - `'sdv-single_table-{method}'`：使用 SDV 提供的單表方法（需額外安裝：`pip install 'sdv>=1.26.0,<2'`，僅供參考）
        - `'custom_method'`：自訂合成方法（需要額外參數）

- **kwargs** : dict, optional
    - 傳遞給特定合成器的額外參數
    - 自訂方法需要：
        - `module_path`：自訂模組路徑
        - `class_name`：自訂類別名稱

### 返回值

- **Synthesizer**
    - 初始化後的合成器實例

### 使用範例

```python
from petsard import Synthesizer

# 使用預設方法
synthesizer = Synthesizer(method='default')

# 使用 SDV CTGAN（需額外安裝 SDV）
synthesizer = Synthesizer(method='sdv-single_table-ctgan')

# 使用 SDV GaussianCopula 並設定參數（需額外安裝 SDV）
synthesizer = Synthesizer(
    method='sdv-single_table-gaussiancopula',
    default_distribution='truncnorm'
)

# 使用自訂合成器
synthesizer = Synthesizer(
    method='custom_method',
    module_path='custom_synthesis.py',
    class_name='MySynthesizer'
)
```

## 預設參數

SDV 合成器（如使用）會使用以下預設參數進行初始化，以確保數值精度：

- **`enforce_rounding=True`**：套用至所有 SDV 合成器類型，維持數值欄位的整數精度
- **`enforce_min_max_values=True`**：僅套用於 TVAE 和 GaussianCopula 合成器，用於強制數值範圍限制

## 精度四捨五入

所有合成器會根據 schema metadata 自動套用精度四捨五入。當 schema 中指定了精度設定（無論是 v1.0 或 v2.0 格式），合成器會將生成的數值四捨五入到指定的小數位數。

此功能確保合成資料維持與原始資料相同的數值精度，這對以下應用非常重要：
- 金融資料（價格、金額）
- 科學測量
- 統計報告
- 任何對精度敏感的應用

## 注意事項

- **custom_data 方法**：`'custom_data'` 方法用於載入外部合成資料，由框架層級處理，不需要合成器實例化
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API
- **方法調用順序**：必須先呼叫 `create()` 再呼叫 `fit()` 或 `fit_sample()`
- **資料輸出**：生成的合成資料儲存於 `data_syn` 屬性
- **文件說明**：本段文件僅供開發團隊內部參考，不保證向後相容
- **Schema 使用**：建議使用 SchemaMetadata 來定義資料結構，詳細設定請參閱 Metadater API 文檔