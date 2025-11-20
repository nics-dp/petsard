---
title: "SDV 合成方法"
type: docs
weight: 655
prev: docs/petsard-yaml/synthesizer-yaml/sdv-custom-methods
next: docs/petsard-yaml/synthesizer-yaml
---

PETsARD 整合 [SDV (Synthetic Data Vault)](https://sdv.dev/) 套件，提供多種先進的合成資料生成演算法。

{{< callout type="warning" >}}
**重要通知**：內建的 SDV 整合方法未來有計劃下架。建議使用 [SDV Custom Methods](../sdv-custom-methods) 以獲得更好的靈活性和長期支援。
{{< /callout >}}

{{< callout type="info" >}}
**注意**：本文件僅提供 YAML 配置範例，不提供 Jupyter notebook 範例。
{{< /callout >}}

## 使用範例

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Synthesizer:
  gaussian:
    method: sdv-single_table-gaussiancopula

  ctgan:
    method: sdv-single_table-ctgan

  copulagan:
    method: sdv-single_table-copulagan

  tvae:
    method: sdv-single_table-tvae
```

## 方法一覽

| 方法 | method 設定值 | 特點 | GPU |
|------|--------------|------|-----|
| GaussianCopula | `default` 或 `sdv-single_table-gaussiancopula` | 快速、適合大型資料 | ✗ |
| CTGAN | `sdv-single_table-ctgan` | 高品質、複雜模式 | ✓ |
| CopulaGAN | `sdv-single_table-copulagan` | 平衡統計與深度學習 | ✓ |
| TVAE | `sdv-single_table-tvae` | 訓練穩定、收斂快 | ✓ |

## 方法說明

### GaussianCopula

基於統計分布的經典方法，執行速度快，適合快速原型測試。

**特點**：
- ✓ 速度快，適合大型資料
- ✓ 低計算需求
- ✗ 主要捕捉線性相關性

### CTGAN

基於 GAN 的深度學習方法，生成品質最佳。

**特點**：
- ✓ 高品質合成資料
- ✓ 適合複雜資料模式
- ✗ 訓練時間較長

**預設參數**：
- `epochs`: 300
- `batch_size`: 500
- `generator_lr`: 0.0002
- `discriminator_lr`: 0.0002

### CopulaGAN

結合 Copula 統計與 GAN，適合混合型資料。

**特點**：
- ✓ 平衡統計與深度學習優點
- ✓ 更好的邊際分布模擬
- ✓ 適合連續與離散混合資料

**預設參數**：
- `epochs`: 300
- `batch_size`: 500
- `default_distribution`: beta

### TVAE

基於 VAE 的生成模型，訓練過程穩定。

**特點**：
- ✓ 穩定的訓練過程
- ✓ 較好的收斂性
- ✓ 適合中等規模資料

**預設參數**：
- `epochs`: 300
- `batch_size`: 500
- `encoder_layers`: [128, 128]
- `decoder_layers`: [128, 128]

## 自動功能

### Schema 轉換

PETsARD 自動將內部 Schema 轉換為 SDV Metadata

### 自動參數

所有方法自動啟用：
- `enforce_rounding`: 整數四捨五入
- `enforce_min_max_values`: 數值範圍限制（GaussianCopula、TVAE）

### GPU 偵測

深度學習方法（CTGAN、CopulaGAN、TVAE）自動偵測並使用 GPU。

## 選擇建議

| 情境 | 建議方法 |
|------|----------|
| 快速測試 | GaussianCopula |
| 高品質需求 | CTGAN |
| 混合型資料 | CopulaGAN |
| 中型資料 | TVAE |
| 大型資料 | GaussianCopula |

## 可用分布

GaussianCopula 與 CopulaGAN 支援：

- `norm`：常態分布
- `truncnorm`：截斷常態分布（預設）
- `beta`：Beta 分布
- `gamma`：Gamma 分布
- `uniform`：均勻分布
- `gaussian_kde`：核密度估計

## 限制

### 內建整合限制

- ✗ 無法調整訓練參數（epochs、batch_size 等）
- ✗ 無法指定分布類型
- ✗ 無法手動選擇 CPU/GPU

## 注意事項

1. 深度學習方法在 GPU 上訓練更快
2. 預設 300 epochs，CPU 訓練可能耗時
3. 大型資料配合深度學習需大量記憶體
4. 內建整合參數固定，無法調整
