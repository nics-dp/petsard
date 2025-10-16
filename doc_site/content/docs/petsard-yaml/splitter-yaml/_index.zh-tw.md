---
title: "Splitter YAML"
weight: 120
---

Splitter 模組的 YAML 設定檔案格式。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/splitter-yaml/splitter-yaml.ipynb)

### 基本分割

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
```

### 控制重疊比例

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  controlled_overlap:
    num_samples: 10
    train_split_ratio: 0.8
    max_overlap_ratio: 0.8  # 允許 80% 重疊
    max_attempts: 500
    random_state: 42
```

### 無重疊分割

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  no_overlap:
    num_samples: 2
    train_split_ratio: 0.01
    max_overlap_ratio: 0.0  # 完全不重疊
    max_attempts: 100000
    random_state: 42
```

{{< callout type="warning" >}}
**注意**：此範例僅示範無重疊設定。由於本套件採用隨機抽樣後比較的演算法，實現完全無重疊（`max_overlap_ratio: 0.0`）極為困難。此功能旨在提供抽樣多樣性，實務上建議保留適度重疊（如 `max_overlap_ratio: 0.8`）以確保執行效率。
{{< /callout >}}

## 主要參數

- **num_samples** (`integer`, 選用)
  - 重複抽樣次數
  - 預設值：1

- **train_split_ratio** (`float`, 選用)
  - 訓練集的資料比例
  - 預設值：0.8

## 參數詳細說明

### 必要參數

Splitter 沒有必要參數，所有參數皆為選用。

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `num_samples` | `integer` | `1` | 重複抽樣次數 | `5` |
| `train_split_ratio` | `float` | `0.8` | 訓練集的資料比例（0.0 到 1.0） | `0.7` |
| `random_state` | `integer\|string` | `null` | 用於重現結果的隨機種子 | `42` 或 `"exp_v1"` |
| `max_overlap_ratio` | `float` | `1.0` | 樣本間允許的最大重疊比率（0.0 到 1.0） | `0.1` |
| `max_attempts` | `integer` | `30` | 重疊控制的最大抽樣嘗試次數 | `50` |

## 使用場景

Splitter 模組主要是為了配合 Evaluator 評測需求而設計，用於將資料集拆分為訓練集和測試集。詳細的分割後評測設定，請參考 Evaluator YAML 說明文件。

## 相關說明

- **拔靴法抽樣**：Splitter 使用拔靴法（bootstrap sampling）生成多個訓練/驗證分割。
- **重疊控制**：透過 `max_overlap_ratio` 參數精確控制樣本間的重疊程度。
- **樣本獨立性**：如需更完整的實驗拆分測試，可根據 `train_split_ratio` 設定 `max_overlap_ratio`（例如 `train_split_ratio: 0.8` 可設定 `max_overlap_ratio: 0.8`）。

## 執行說明

- 可定義多個分割實驗，系統會依序執行
- 分割結果會傳遞給下一個模組（如 Synthesizer）使用
- 樣本編號從 1 開始（非 0）

## 注意事項

- 重疊約束過於嚴格可能導致抽樣失敗，請適當調整 `max_attempts`
- 設定 `random_state` 以確保結果可重現