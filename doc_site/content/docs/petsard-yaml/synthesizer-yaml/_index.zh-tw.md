---
title: "Synthesizer YAML"
weight: 130
---

Synthesizer 模組的 YAML 設定檔案格式。

## 主要參數

- **method** (`string`, 必要)
  - 合成方法名稱
  - 支援的方法：
    - `default`：使用 SDV-GaussianCopula
    - `sdv-single_table-{method}`：使用 SDV 提供的方法
    - `custom_method`：自訂合成方法
    - `custom_data`：載入外部合成資料

## 參數詳細說明

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 合成方法名稱 | `"sdv-single_table-ctgan"` |

### SDV 方法參數

支援的 SDV 方法及其特定參數：

| 方法 | 說明 | 特定參數 |
|------|------|----------|
| `sdv-single_table-gaussiancopula` | 高斯耦合模型 | `default_distribution`, `numerical_distributions` |
| `sdv-single_table-ctgan` | CTGAN 生成模型 | `epochs`, `batch_size`, `discriminator_steps` |
| `sdv-single_table-copulagan` | CopulaGAN 生成模型 | `epochs`, `batch_size`, `discriminator_steps` |
| `sdv-single_table-tvae` | TVAE 生成模型 | `epochs`, `batch_size` |

### 自訂方法參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `module_path` | `string` | 自訂模組路徑 | `"custom_synthesis.py"` |
| `class_name` | `string` | 自訂類別名稱 | `"MySynthesizer"` |

### 外部資料參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `filepath` | `string` | 外部合成資料檔案路徑 | `"synthetic_data.csv"` |

## 使用範例

### 使用預設方法合成

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
Synthesizer:
  default_synthesis:
    method: default
```

### 使用 SDV CTGAN

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
Synthesizer:
  ctgan_synthesis:
    method: sdv-single_table-ctgan
    epochs: 300
    batch_size: 500
    discriminator_steps: 1
```

### 使用 GaussianCopula 與參數

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
Synthesizer:
  gaussian_synthesis:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm
    numerical_distributions:
      age: beta
      income: gamma
```

### 使用自訂合成器

```yaml
Loader:
  load_data:
    filepath: data.csv
Synthesizer:
  custom_synthesis:
    method: custom_method
    module_path: custom_synthesizer.py
    class_name: MyCustomSynthesizer
    # 自訂參數會傳遞給合成器
    custom_param1: value1
    custom_param2: value2
```

### 載入外部合成資料

```yaml
Loader:
  load_original:
    filepath: original_data.csv
Synthesizer:
  external_data:
    method: custom_data
    filepath: external_synthetic.csv
```

## 進階設定

### 多重合成實驗

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
Synthesizer:
  # 實驗 1：GaussianCopula
  exp1_gaussian:
    method: sdv-single_table-gaussiancopula
    default_distribution: truncnorm
  
  # 實驗 2：CTGAN
  exp2_ctgan:
    method: sdv-single_table-ctgan
    epochs: 300
  
  # 實驗 3：TVAE
  exp3_tvae:
    method: sdv-single_table-tvae
    epochs: 500
    batch_size: 1000
```

### 配合 Splitter 使用

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
Splitter:
  split_data:
    num_samples: 3
    train_split_ratio: 0.8
Synthesizer:
  synthesize_splits:
    method: sdv-single_table-ctgan
    epochs: 200
    # 會對每個分割的訓練集進行合成
```

## 預設行為

所有 SDV 合成器都會自動套用以下預設參數：

- **`enforce_rounding=True`**：維持數值欄位的整數精度
- **`enforce_min_max_values=True`**（僅 TVAE 和 GaussianCopula）：強制數值範圍限制

## 精度四捨五入

當 schema 中指定了精度設定時，合成器會自動將生成的數值四捨五入到指定的小數位數。這對金融資料、科學測量等精度敏感的應用特別重要。

## 執行說明

- 可定義多個合成實驗，系統會依序執行
- 每個實驗的結果會儲存供後續評測使用
- 如果使用 Splitter，會對每個分割的訓練集分別進行合成

## 相關說明

- **SDV 整合**：PETsARD 整合了 SDV (Synthetic Data Vault) 套件的多種合成方法
- **自訂合成器**：支援開發者實作自己的合成演算法
- **外部資料**：可載入其他工具產生的合成資料進行評測

## 注意事項

- 深度學習方法（CTGAN、TVAE）需要較長訓練時間和更多計算資源
- 建議根據資料特性選擇適當的合成方法
- 對於大型資料集，考慮調整 `batch_size` 和 `epochs` 參數
- 自訂合成器必須實作必要的介面方法
- 外部合成資料必須與原始資料有相同的欄位結構