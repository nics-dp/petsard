---
title: Synthesizer
type: docs
weight: 56
prev: docs/api/processor
next: docs/api/constrainer
---


```python
Synthesizer(
    method,
    **kwargs
)
```

合成資料產生器。支援多種合成方法並提供資料生成功能。

## 參數

- `method` (str)：合成方法
  - 'default'：使用 SDV-GaussianCopula
  - 'custom_data'：從檔案載入自定義資料
  - 'sdv-single_table-{method}'：使用 SDV 提供的方法
    - copulagan：CopulaGAN 生成模型
    - ctgan：CTGAN 生成模型
    - gaussiancopula：高斯耦合模型
    - tvae：TVAE 生成模型

## 預設參數

所有 SDV 合成器都會使用以下預設參數進行初始化，以確保數值精度：

- **`enforce_rounding=True`**：套用至所有 SDV 合成器類型，維持數值欄位的整數精度
- **`enforce_min_max_values=True`**：僅套用於 TVAE 和 GaussianCopula 合成器，用於強制數值範圍限制

## 精度四捨五入

所有合成器會根據 schema metadata 自動套用精度四捨五入。當 schema 中指定了精度設定（無論是 v1.0 或 v2.0 格式），合成器會將生成的數值四捨五入到指定的小數位數。

此功能確保合成資料維持與原始資料相同的數值精度，這對以下應用非常重要：
- 金融資料（價格、金額）
- 科學測量
- 統計報告
- 任何對精度敏感的應用

如需詳細的 schema 配置說明，請參考[指定資料表架構](../tutorial/use-cases/specify-schema)教學。

## 範例

```python
from petsard import Synthesizer


# 使用 SDV 的 GaussianCopula
syn = Synthesizer(method='sdv-single_table-gaussiancopula')

# 使用預設方法
syn = Synthesizer(method='default')

# 合成
syn.create(metadata=metadata)
syn.fit_sample(data=df)
synthetic_data = syn.data_syn
```

## 方法

### `create()`

```python
syn.create(metadata)
```

建立合成器。

**參數**

- `metadata` (Metadata, optional)：資料集的 Metadata 物件

**回傳值**

無。初始化合成器物件

### `fit()`

```python
syn.fit(data=data)
```

訓練合成模型。

**參數**

- `data` (pd.DataFrame)：用於訓練的資料集

**回傳值**

無。更新合成器的內部狀態

### `sample()`

```python
syn.sample(
    sample_num_rows=None,
    reset_sampling=False,
    output_file_path=None
)
```

訓練合成模型。

**參數**

- `sample_num_rows` (int, optional)：要生成的資料列數
  - 預設值：無（使用原始資料列數）
- `reset_sampling` (bool, optional)：是否重置採樣狀態
  - 預設值：False
- `output_file_path` (str, optional): Output file path
  - 預設值：無

**回傳值**

無。生成的資料儲存於 `data_syn` 屬性

### `fit_sample()`

```python
syn.fit_sample(data, **kwargs)
```

Perform training and generation in sequence. Combines functionality of `fit()` and `sample()`.

**參數**

與 `sample()` 相同

**回傳值**

無。生成的資料儲存於 `data_syn` 屬性

## 屬性

- `data_syn`：生成的合成資料 (pd.DataFrame)
- `config`：設定字典，包含：
  - `method` (str)：合成方法名稱
  - `method_code` (int)：方法類型代碼
  - 各方法特定的其他參數
- `synthesizer`：實例化的合成器物件（用於 SDV 方法）
- `loader`：載入器物件（僅用於 'custom_data' 方法）