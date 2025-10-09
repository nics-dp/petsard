---
title: "SDV 合成方法"
weight: 131
---

PETsARD 整合了 [SDV (Synthetic Data Vault)](https://sdv.dev/) 套件，提供多種先進的合成資料生成演算法。

## 方法一覽表

| 方法名稱 | method 設定值 | 適用情境 | 執行速度 |
|----------|--------------|----------|----------|
| GaussianCopula | `default` 或 `sdv-single_table-gaussiancopula` | 快速原型測試、大型資料集 | 快 |
| CTGAN | `sdv-single_table-ctgan` | 需要高品質合成資料 | 慢 |
| CopulaGAN | `sdv-single_table-copulagan` | 混合型資料（連續+離散） | 慢 |
| TVAE | `sdv-single_table-tvae` | 需要穩定訓練過程 | 中 |

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

所有 SDV 方法都支援以下通用參數：

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `enforce_rounding` | `bool` | `True` | 強制整數欄位四捨五入 |
| `enforce_min_max_values` | `bool` | `True` | 強制數值範圍限制（僅 TVAE 和 GaussianCopula） |

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

## 注意事項

1. **計算資源**：深度學習方法（CTGAN、CopulaGAN、TVAE）需要 GPU 加速
2. **訓練時間**：深度學習方法可能需要數小時訓練
3. **記憶體使用**：大型資料集配合深度學習方法可能需要大量記憶體
4. **參數調校**：深度學習方法的參數對結果影響較大，建議仔細調校
