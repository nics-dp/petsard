---
title: "自訂合成方法：SDV"
weight: 4
---

[SDV (Synthetic Data Vault)](https://sdv.dev/) 是業界主流且廣受歡迎的合成資料生成套件，提供多種先進的演算法。為了幫助使用者了解如何在 PETsARD 中整合外部套件，我們額外開發了這個示範，展示如何使用 `custom_method` 方式靈活運用 SDV 的各種合成方法，並完全控制所有參數設定，包括 CPU/GPU 選擇、訓練參數調整等。這個示範不僅展示了 SDV 的使用方式，更重要的是提供了自訂外部方法的完整範例，讓您可以輕鬆整合其他第三方套件或自行開發的演算法。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
    nrows: 100 # 載入前 100 筆資料以加快測試速度
Preprocessor:
  default:
    method: default

Synthesizer:
  # 方法 1: GaussianCopula
  exp1_gaussiancopula:
    method: custom_method
    module_path: sdv-custom-methods.py
    class_name: SDV_GaussianCopula
    # 可選參數：
    # device: cpu                      # 計算設備（預設：cpu）
    # default_distribution: truncnorm  # 數值欄位的預設分布（預設：truncnorm）
    # enforce_min_max_values: true     # 強制最小/最大值限制（預設：true）
    # enforce_rounding: true           # 整數欄位四捨五入（預設：true）
    # numerical_distributions:         # 欄位特定分布（預設：{}）
    #   age: beta
    #   hours-per-week: gamma

  # 方法 2: CTGAN
  exp2_ctgan:
    method: custom_method
    module_path: sdv-custom-methods.py
    class_name: SDV_CTGAN
    epochs: 2                       # 訓練輪數（預設：300）
    batch_size: 50                  # 批次大小（預設：500）⚠️ 重要：必須可被 'pac' 整除（預設 pac=10）
    verbose: true                   # 顯示訓練進度（預設：false）
    generator_dim:                  # 生成器層大小（預設：(256, 256)）
      - 16
      - 16
    discriminator_dim:              # 判別器層大小（預設：(256, 256)）
      - 16
      - 16
    # 可選參數：
    # device: cpu                   # 計算設備（預設：cpu）
    # pac: 10                       # PAC（打包）大小（預設：10）
    # discriminator_steps: 1        # 每次生成器更新的判別器更新次數（預設：1）
    # generator_lr: 0.0002          # 生成器學習率（預設：0.0002）
    # discriminator_lr: 0.0002      # 判別器學習率（預設：0.0002）
    # enforce_rounding: true        # 整數欄位四捨五入（預設：true）

  # 方法 3: CopulaGAN
  exp3_copulagan:
    method: custom_method
    module_path: sdv-custom-methods.py
    class_name: SDV_CopulaGAN
    epochs: 2                       # 訓練輪數（預設：300）
    batch_size: 50                  # 批次大小（預設：500）
                                    # ⚠️ 重要：必須可被 'pac' 整除（預設 pac=10）
                                    # 有效值：10, 20, 30, 40, 50, 60, 70, 80, 90, 100 等
    # pac: 10                       # PAC（打包）大小（預設：10）
                                    # 控制樣本如何打包在一起
                                    # batch_size 必須可被此值整除
    verbose: true                   # 顯示訓練進度（預設：false）
    generator_dim:                  # 生成器層大小（預設：(256, 256)）
      - 16
      - 16
    discriminator_dim:              # 判別器層大小（預設：(256, 256)）
      - 16
      - 16
    # 可選參數：
    # device: cpu                   # 計算設備（預設：cpu）
    # default_distribution: beta    # 數值欄位的預設分布（預設：beta）
    # discriminator_steps: 1        # 每次生成器更新的判別器更新次數（預設：1）
    # generator_lr: 0.0002          # 生成器學習率（預設：0.0002）
    # discriminator_lr: 0.0002      # 判別器學習率（預設：0.0002）
    # enforce_rounding: true        # 整數欄位四捨五入（預設：true）
    # numerical_distributions:      # 欄位特定分布（預設：{}）
    #   age: beta

  # 方法 4: TVAE
  exp4_tvae:
    method: custom_method
    module_path: sdv-custom-methods.py
    class_name: SDV_TVAE
    epochs: 2                       # 訓練輪數（預設：300）
    batch_size: 50                  # 批次大小（預設：500）
                                    # 注意：TVAE 不使用 'pac'，但保持 batch_size=50 以保持一致性
    verbose: true                   # 顯示訓練進度（預設：false）
    encoder_layers:                 # 編碼器層大小（預設：(128, 128)）
      - 16
      - 16
    decoder_layers:                 # 解碼器層大小（預設：(128, 128)）
      - 16
      - 16
    embedding_dim: 32               # 嵌入維度（預設：128）
    # 可選參數：
    # device: cpu                   # 計算設備（預設：cpu）
    # encoder_layers: [128, 128]    # 編碼器層大小（預設：(128, 128)）
    # decoder_layers: [128, 128]    # 解碼器層大小（預設：(128, 128)）
    # enforce_min_max_values: true  # 強制最小/最大值限制（預設：true）
    # enforce_rounding: true        # 整數欄位四捨五入（預設：true）
    # verbose: false                # 顯示訓練進度（預設：false）
    # l2scale: 0.00001              # L2 正則化係數（預設：1e-5）
    # loss_factor: 2                # 重建損失因子（預設：2）

Postprocessor:
  default:
    method: default
Evaluator:
  eval_all_methods:
    method: sdmetrics-qualityreport
Reporter:
  save_comparison:
    method: save_report
    granularity: global
```

## 前置需求

### 1. 安裝 SDV

```bash
pip install sdv
```

### 2. 下載腳本

下載 [`sdv-custom-methods.py`](https://github.com/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/sdv-custom-methods.py) 到與 YAML 檔案相同的目錄。

## 支援的方法

### 1. SDV_GaussianCopula

快速的統計方法，適合大型資料集和快速原型測試。

**特點：**
- 無需訓練迭代，速度最快
- 僅支援 CPU（不使用 GPU）
- 可自訂數值欄位的分布類型

**參數說明：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `device` | `string` | `cpu` | 計算設備（僅支援 `cpu`） |
| `default_distribution` | `string` | `truncnorm` | 數值欄位的預設分布類型 |
| `numerical_distributions` | `dict` | `{}` | 為特定欄位指定分布類型 |
| `enforce_min_max_values` | `bool` | `true` | 強制數值範圍限制 |
| `enforce_rounding` | `bool` | `true` | 整數欄位四捨五入 |

**可用的分布類型：**
- `truncnorm`：截斷常態分布
- `beta`：Beta 分布
- `gamma`：Gamma 分布
- `uniform`：均勻分布
- `norm`：常態分布

**使用範例：**

```yaml
exp_gaussiancopula:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_GaussianCopula
  device: cpu
  default_distribution: truncnorm
  numerical_distributions:
    age: beta
    hours-per-week: gamma
```

### 2. SDV_CTGAN

基於 GAN 的深度學習方法，提供最高品質的合成資料。

**特點：**
- 高品質合成資料
- 支援 GPU 加速
- 可完整調整訓練參數

**參數說明：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `device` | `string` | `cpu` | 計算設備（`cpu` 或 `cuda`） |
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `discriminator_steps` | `int` | `1` | 判別器訓練步數 |
| `generator_lr` | `float` | `0.0002` | 生成器學習率 |
| `discriminator_lr` | `float` | `0.0002` | 判別器學習率 |
| `generator_dim` | `list` | `[256, 256]` | 生成器隱藏層大小 |
| `discriminator_dim` | `list` | `[256, 256]` | 判別器隱藏層大小 |
| `enforce_rounding` | `bool` | `true` | 整數欄位四捨五入 |
| `verbose` | `bool` | `false` | 顯示訓練進度 |

**使用範例：**

```yaml
exp_ctgan:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_CTGAN
  device: cuda        # 使用 GPU 加速
  epochs: 100         # 快速測試用較少輪數
  batch_size: 500
  verbose: true       # 顯示訓練進度
```

### 3. SDV_CopulaGAN

結合統計方法和 GAN 的混合模型。

**特點：**
- 平衡統計準確性和生成品質
- 更好的邊際分布擬合
- 支援 GPU 加速

**參數說明：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `device` | `string` | `cpu` | 計算設備（`cpu` 或 `cuda`） |
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `default_distribution` | `string` | `beta` | 數值欄位的預設分布類型 |
| `numerical_distributions` | `dict` | `{}` | 為特定欄位指定分布類型 |
| `discriminator_steps` | `int` | `1` | 判別器訓練步數 |
| `generator_lr` | `float` | `0.0002` | 生成器學習率 |
| `discriminator_lr` | `float` | `0.0002` | 判別器學習率 |
| `enforce_rounding` | `bool` | `true` | 整數欄位四捨五入 |
| `verbose` | `bool` | `false` | 顯示訓練進度 |

**使用範例：**

```yaml
exp_copulagan:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_CopulaGAN
  device: cpu
  epochs: 200
  default_distribution: beta
```

### 4. SDV_TVAE

基於 VAE 的生成模型，訓練過程穩定。

**特點：**
- 穩定的訓練過程
- 較好的收斂性
- 支援 GPU 加速

**參數說明：**

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `device` | `string` | `cpu` | 計算設備（`cpu` 或 `cuda`） |
| `epochs` | `int` | `300` | 訓練輪數 |
| `batch_size` | `int` | `500` | 批次大小 |
| `encoder_layers` | `list` | `[128, 128]` | 編碼器隱藏層大小 |
| `decoder_layers` | `list` | `[128, 128]` | 解碼器隱藏層大小 |
| `embedding_dim` | `int` | `128` | 嵌入維度大小 |
| `l2scale` | `float` | `0.00001` | L2 正則化係數 |
| `loss_factor` | `int` | `2` | 重建損失因子 |
| `enforce_min_max_values` | `bool` | `true` | 強制數值範圍限制 |
| `enforce_rounding` | `bool` | `true` | 整數欄位四捨五入 |
| `verbose` | `bool` | `false` | 顯示訓練進度 |

**使用範例：**

```yaml
exp_tvae:
  method: custom_method
  module_path: sdv-custom-methods.py
  class_name: SDV_TVAE
  device: cpu
  epochs: 300
  batch_size: 1000
  encoder_layers: [256, 256]
  decoder_layers: [256, 256]
```

## Device 參數詳解

`device` 參數用於指定計算設備，可選擇使用 CPU 或 GPU（CUDA）進行訓練。

### 方法支援情況

| 方法 | CPU | CUDA |
|------|-----|------|
| SDV_GaussianCopula | ✓ | ✗（會發出警告並使用 CPU） |
| SDV_CTGAN | ✓ | ✓ |
| SDV_CopulaGAN | ✓ | ✓ |
| SDV_TVAE | ✓ | ✓ |

## 常見問題

### Q: CTGAN/CopulaGAN/TVAE 訓練很慢怎麼辦？

1. **減少 epochs**：從 300 降到 50-100 進行測試
2. **使用 GPU**：設定 `device: cuda`（如果可用）
3. **增加 batch_size**：可加快每個 epoch 的速度

### Q: GaussianCopula 可以使用 GPU 嗎？

不行，GaussianCopula 是純統計方法，不使用神經網絡，因此不支援 GPU。如果設定 `device: cuda`，系統會發出警告並自動使用 CPU。

### Q: 如何選擇合適的方法？

| 需求 | 推薦方法 |
|------|----------|
| 快速測試 | SDV_GaussianCopula |
| 最高品質 | SDV_CTGAN（需要 GPU） |
| 平衡品質與速度 | SDV_CopulaGAN |
| 訓練穩定性 | SDV_TVAE |
| 無 GPU 環境 | SDV_GaussianCopula 或降低 epochs |