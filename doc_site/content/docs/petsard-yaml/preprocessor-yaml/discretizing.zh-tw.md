---
title: "離散化"
weight: 5
---

將連續數值資料轉換為離散的類別或區間，與編碼（encoder）互斥使用。

## 使用範例

### 基本使用

```yaml
Preprocessor:
  demo:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # 使用離散化，不使用 encoder
```

### 自訂 K-bins 參數

```yaml
Preprocessor:
  custom:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing
    config:
      discretizing:
        age:
          method: 'discretizing_kbins'
          n_bins: 10                    # 分成10個區間
        income:
          method: 'discretizing_kbins'
          n_bins: 5                     # 分成5個區間
```

## 可用的處理器

| 處理器 | 說明 | 適用類型 | 輸出 |
|--------|------|---------|------|
| `discretizing_kbins` | K-bins 離散化 | 數值型 | 整數標籤 |
| `encoder_label` | 標籤編碼 | 類別型 | 整數標籤 |

**注意**：discretizing 序列中，類別型資料會自動使用 `encoder_label` 進行編碼。

## 處理器詳細說明

### discretizing_kbins

**K-bins 離散化**：將連續數值分割成 k 個等寬區間。

**參數**：
- **n_bins** (`int`, 選用)
  - 區間數量（k值）
  - 預設值：`5`
  - 範例：`n_bins: 10`

**特性**：
- 等寬分箱（equal-width binning）
- 輸出為整數標籤（0, 1, 2, ...）
- 減少資料維度和複雜度

**範例**：
```yaml
config:
  discretizing:
    age:
      method: 'discretizing_kbins'
      n_bins: 5
```

**離散化示例**：
```
原始數值：[18, 25, 35, 45, 55, 65]
n_bins = 5

區間劃分：
[18-27.4) → 0
[27.4-36.8) → 1
[36.8-46.2) → 2
[46.2-55.6) → 3
[55.6-65] → 4

離散化結果：[0, 0, 1, 2, 3, 4]
```

## 處理邏輯

### 數值型資料（discretizing_kbins）

```
訓練階段（fit）：
  計算並儲存區間邊界

轉換階段（transform）：
  依區間邊界將數值映射到整數標籤

還原階段（inverse_transform）：
  將整數標籤還原為區間中點值
```

### 類別型資料（encoder_label）

```
訓練階段（fit）：
  建立類別到整數的映射

轉換階段（transform）：
  依映射將類別轉為整數

還原階段（inverse_transform）：
  依映射將整數還原為類別
```

## 預設行為

當使用 discretizing 序列時的預設處理：

| 資料類型 | 預設處理器 | 說明 |
|---------|-----------|------|
| 數值型 | `discretizing_kbins` | K-bins 離散化（k=5） |
| 類別型 | `encoder_label` | 標籤編碼 |
| 日期時間型 | `discretizing_kbins` | K-bins 離散化（k=5） |

## 與 encoder 的差異

| 特性 | discretizing | encoder |
|-----|-------------|---------|
| **數值輸出** | 離散整數（0, 1, 2, ...） | 連續值或多欄位 |
| **適用場景** | 離散化需求 | 一般編碼需求 |
| **類別處理** | Label 編碼 | 多種編碼（Uniform/Label/OneHot） |
| **與 scaler** | 通常不使用 | 通常配合使用 |
| **序列位置** | 必須是最後一步 | 在 scaler 之前 |

## 使用限制

### 1. 與 encoder 互斥

```yaml
# ❌ 錯誤：不能同時使用
Preprocessor:
  wrong:
    method: 'default'
    sequence:
      - missing
      - encoder       # 錯誤！
      - discretizing  # 與 encoder 互斥
```

```yaml
# ✅ 正確：只使用其中一個
Preprocessor:
  correct:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # 正確
```

### 2. 必須是最後一步

```yaml
# ❌ 錯誤：discretizing 後面還有其他步驟
Preprocessor:
  wrong:
    method: 'default'
    sequence:
      - missing
      - discretizing
      - scaler        # 錯誤！discretizing 必須是最後
```

```yaml
# ✅ 正確：discretizing 是最後一步
Preprocessor:
  correct:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # 正確：最後一步
```

## 完整範例

```yaml
Loader:
  load_data:
    filepath: 'data.csv'
    schema: 'schema.yaml'

Preprocessor:
  discretize_data:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing  # 注意：沒有 encoder 和 scaler
    config:
      # 缺失值處理
      missing:
        age: 'missing_median'
        income: 'missing_mean'
      
      # 離群值處理
      outlier:
        age: 'outlier_iqr'
        income: 'outlier_iqr'
      
      # 離散化配置
      discretizing:
        # 數值型欄位
        age:
          method: 'discretizing_kbins'
          n_bins: 10                    # 年齡分10個區間
        income:
          method: 'discretizing_kbins'
          n_bins: 5                     # 收入分5個區間
        hours_per_week:
          method: 'discretizing_kbins'
          n_bins: 8                     # 工時分8個區間
        
        # 類別型欄位（自動使用 encoder_label）
        gender: 'encoder_label'
        education: 'encoder_label'

Synthesizer:
  synthesize:
    method: 'default'

Postprocessor:
  postprocess:
    method: 'default'
```

## 使用案例

### 1. 簡化資料分布

```yaml
# 將連續分布簡化為離散區間
Preprocessor:
  simplify:
    method: 'default'
    sequence:
      - missing
      - discretizing
    config:
      discretizing:
        salary:
          method: 'discretizing_kbins'
          n_bins: 3  # 低/中/高三個級別
```

### 2. 減少資料維度

```yaml
# 降低數值精度，減少合成難度
Preprocessor:
  reduce_dimension:
    method: 'default'
    sequence:
      - missing
      - outlier
      - discretizing
    config:
      discretizing:
        age:
          method: 'discretizing_kbins'
          n_bins: 5
        score:
          method: 'discretizing_kbins'
          n_bins: 10
```

## 注意事項

- **互斥性**：不能與 encoder 同時使用
- **位置限制**：必須是序列中的最後一步
- **還原精度**：還原時使用區間中點，不會完全還原原值
- **區間數量**：n_bins 應根據資料範圍和需求調整
- **合成器影響**：某些合成器（如 PAC-Synth、DPCTGAN）可能產生浮點數，系統會自動四捨五入
- **適用場景**：適合需要離散化輸出的情況，如某些隱私保護演算法
- **NA 處理**：後處理時會先移除 NA 值再進行還原

## 相關文件

- [Processor API - fit()]({{< ref "/docs/python-api/processor-api/processor_fit" >}})
- [Processor API - transform()]({{< ref "/docs/python-api/processor-api/processor_transform" >}})
- [Processor API - inverse_transform()]({{< ref "/docs/python-api/processor-api/processor_inverse_transform" >}})
- [編碼]({{< ref "encoding" >}})
- [縮放]({{< ref "scaling" >}})