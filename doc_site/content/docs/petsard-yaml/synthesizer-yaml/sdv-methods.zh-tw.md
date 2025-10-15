---
title: "SDV 合成方法"
weight: 131
---

PETsARD 整合了 [SDV (Synthetic Data Vault)](https://sdv.dev/) 套件，提供多種先進的合成資料生成演算法。

{{< callout type="info" >}}
**注意**：本文件說明 PETsARD 內建的 SDV 整合方式。若需要更靈活的使用方式或自訂參數，請參考 [SDV Custom Methods](../sdv-custom-methods)。
{{< /callout >}}

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-methods.ipynb)

## 方法一覽表

| 方法名稱 | method 設定值 | 適用情境 | GPU 支援 |
|----------|--------------|----------|----------|
| GaussianCopula | `default` 或 `sdv-single_table-gaussiancopula` | 快速原型測試、大型資料集 | ✗ |
| CTGAN | `sdv-single_table-ctgan` | 需要高品質合成資料 | ✓ |
| CopulaGAN | `sdv-single_table-copulagan` | 混合型資料（連續+離散） | ✓ |
| TVAE | `sdv-single_table-tvae` | 需要穩定訓練過程 | ✓ |

## 支援的 SDV 方法詳細說明

### 1. GaussianCopula

基於統計分布的經典方法，適合快速生成合成資料。

**特點：**
- 執行速度快
- 適合數值型資料
- 可自訂分布類型

**設定範例：**
```yaml
Synthesizer:
  gaussian_synthesis:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm  # 預設分布
    numerical_distributions:          # 特定欄位分布
      age: beta
      income: gamma
```

**參數說明：**
| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `default_distribution` | `string` | `truncnorm` | 預設的數值分布類型 |
| `numerical_distributions` | `dict` | `{}` | 各欄位的特定分布設定 |

### 2. CTGAN

基於 GAN (Generative Adversarial Network) 的深度學習方法。

**特點：**
- 高品質合成資料
- 適合複雜資料模式
- 需要較長訓練時間

**設定範例：**
```yaml
Synthesizer:
  ctgan_synthesis:
    method: sdv-single_table-ctgan
    epochs: 300
    batch_size: 500
    discriminator_steps: 1
    generator_lr: 0.0002
    discriminator_lr: 0.0002
```

**參數說明：**
| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `discriminator_steps` | `int` | `1` | 判別器訓練步數 |
| `generator_lr` | `float` | `0.0002` | 生成器學習率 |
| `discriminator_lr` | `float` | `0.0002` | 判別器學習率 |

### 3. CopulaGAN

結合 Copula 統計方法和 GAN 的混合模型。

**特點：**
- 結合統計和深度學習優點
- 更好的邊際分布模擬
- 適合混合型資料

**設定範例：**
```yaml
Synthesizer:
  copulagan_synthesis:
    method: sdv-single_table-copulagan
    epochs: 300
    batch_size: 500
    discriminator_steps: 1
    default_distribution: beta
```

**參數說明：**
| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `discriminator_steps` | `int` | `1` | 判別器訓練步數 |
| `default_distribution` | `string` | `beta` | 預設分布類型 |

### 4. TVAE

基於 VAE (Variational Autoencoder) 的生成模型。

**特點：**
- 穩定的訓練過程
- 較好的收斂性
- 適合中等規模資料

**設定範例：**
```yaml
Synthesizer:
  tvae_synthesis:
    method: sdv-single_table-tvae
    epochs: 500
    batch_size: 1000
    encoder_layers: [256, 256]
    decoder_layers: [256, 256]
```

**參數說明：**
| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `encoder_layers` | `list` | `[128, 128]` | 編碼器層設定 |
| `decoder_layers` | `list` | `[128, 128]` | 解碼器層設定 |

## 預設方法

使用 `method: default` 會自動選擇 GaussianCopula 方法：

```yaml
Synthesizer:
  default_synthesis:
    method: default  # 等同於 sdv-single_table-gaussiancopula
```

## 通用參數

### 自動啟用的參數

PETsARD 內建的 SDV 整合會自動設定以下參數：

| 參數 | 設定值 | 適用方法 | 說明 |
|------|--------|----------|------|
| `enforce_rounding` | `True` | 所有方法 | 自動將整數欄位四捨五入為整數 |
| `enforce_min_max_values` | `True` | TVAE、GaussianCopula | 自動強制數值範圍在原始資料的最小/最大值內 |

### Schema 自動轉換

PETsARD 會自動將內部的 Schema 格式轉換為 SDV 的 Metadata 格式：

- **Numerical columns** 數值欄位：`int*`、`float*` 類型 → SDV `numerical`
- **Categorical columns** 類別欄位：`category` 邏輯類型 → SDV `categorical`
- **Boolean columns** 布林欄位：`bool` 類型 → SDV `boolean`
- **Datetime columns** 日期時間欄位：`datetime*` 類型 → SDV `datetime`
- **PII columns** 個人識別資訊：`email`、`phone` 邏輯類型 → SDV `pii`

## 可用的分布類型

對於 GaussianCopula 和 CopulaGAN，可指定以下分布類型：

- `norm`：常態分布
- `truncnorm`：截斷常態分布（預設）
- `beta`：Beta 分布
- `gamma`：Gamma 分布
- `uniform`：均勻分布
- `gaussian_kde`：高斯核密度估計

## 方法選擇建議

| 情境 | 建議方法 | 理由 |
|------|----------|------|
| 快速原型測試 | GaussianCopula | 執行速度快，結果可接受 |
| 高品質合成 | CTGAN | 生成品質最佳，但需要時間 |
| 混合型資料 | CopulaGAN | 平衡統計和深度學習優點 |
| 中等規模資料 | TVAE | 訓練穩定，收斂快速 |
| 大型資料集 | GaussianCopula | 深度學習方法可能過於耗時 |

## 完整範例

### 比較多種 SDV 方法

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income

Synthesizer:
  # 快速方法
  exp1_gaussian:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm
  
  # 高品質方法
  exp2_ctgan:
    method: sdv-single_table-ctgan
    epochs: 300
    batch_size: 500
  
  # 平衡方法
  exp3_copulagan:
    method: sdv-single_table-copulagan
    epochs: 200
    default_distribution: beta
  
  # VAE 方法
  exp4_tvae:
    method: sdv-single_table-tvae
    epochs: 400
    batch_size: 1000

Evaluator:
  eval_quality:
    method: sdmetrics-single_table-quality_report

Reporter:
  save_comparison:
    method: save_report
    granularity: global
```

## GPU 加速

深度學習方法（CTGAN、CopulaGAN、TVAE）會自動偵測並使用 GPU：

```python
# 內建實現會自動使用 CUDA（如果可用）
if torch.cuda.is_available():
    # 使用 GPU 訓練
else:
    # 使用 CPU 訓練
```

{{< callout type="warning" >}}
**限制**：內建的 SDV 整合不支援手動選擇 CPU/GPU。如需此功能，請使用 [SDV Custom Methods](../sdv-custom-methods)。
{{< /callout >}}

## 實際參數與預設值

以下是基於 PETsARD 實際實現的參數說明：

### GaussianCopula
- `enforce_rounding`: 自動啟用
- `enforce_min_max_values`: 自動啟用
- 不支援自訂 `default_distribution` 或 `numerical_distributions`

### CTGAN
- `enforce_rounding`: 自動啟用
- 其他參數使用 SDV 預設值：
  - `epochs`: 300
  - `batch_size`: 500
  - `generator_lr`: 0.0002
  - `discriminator_lr`: 0.0002

### CopulaGAN
- `enforce_rounding`: 自動啟用
- 其他參數使用 SDV 預設值：
  - `epochs`: 300
  - `batch_size`: 500
  - `default_distribution`: beta

### TVAE
- `enforce_rounding`: 自動啟用
- `enforce_min_max_values`: 自動啟用
- 其他參數使用 SDV 預設值：
  - `epochs`: 300
  - `batch_size`: 500
  - `compress_dims`: (128, 128)
  - `decompress_dims`: (128, 128)

## 限制與建議

### 內建整合的限制

1. **參數無法自訂**：無法調整 epochs、batch_size 等訓練參數
2. **分布無法指定**：GaussianCopula 和 CopulaGAN 的分布類型固定
3. **設備無法選擇**：無法手動選擇使用 CPU 或 GPU

### 使用建議

- **快速測試**：內建整合適合快速測試和預設配置
- **進階使用**：需要調整參數時，請使用 [SDV Custom Methods](../sdv-custom-methods)
- **GPU 訓練**：深度學習方法建議在有 NVIDIA GPU 的環境執行

## 注意事項

1. **計算資源**：深度學習方法（CTGAN、CopulaGAN、TVAE）在 GPU 上訓練更快
2. **訓練時間**：使用預設 300 epochs，CPU 訓練可能需要較長時間
3. **記憶體使用**：大型資料集配合深度學習方法可能需要大量記憶體
4. **參數固定**：內建整合使用固定參數，無法調整
