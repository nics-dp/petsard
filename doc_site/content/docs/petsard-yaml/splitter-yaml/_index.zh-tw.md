---
title: "Splitter YAML"
weight: 120
---

Splitter 模組的 YAML 設定檔案格式。

## 主要參數

- **num_samples** (`integer`, 選用)
  - 重複抽樣次數
  - 預設值：1

- **train_split_ratio** (`float`, 選用)
  - 訓練集的資料比例
  - 預設值：0.8

- **max_overlap_ratio** (`float`, 選用)
  - 樣本間允許的最大重疊比率
  - 預設值：1.0（允許完全重疊）

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

## 使用範例

### 基本分割

```yaml
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
```

### 嚴格重疊控制

```yaml
Splitter:
  strict_overlap:
    num_samples: 5
    train_split_ratio: 0.7
    max_overlap_ratio: 0.1  # 最大 10% 重疊
    max_attempts: 50
    random_state: 42
```

### 無重疊分割

```yaml
Splitter:
  no_overlap:
    num_samples: 4
    train_split_ratio: 0.75
    max_overlap_ratio: 0.0  # 完全無重疊
    max_attempts: 100
    random_state: "reproducible"
```

### 完整管線範例

```yaml
# 完整實驗管線
Loader:
  load_data:
    filepath: benchmark/adult-income.csv
    schema: benchmark/adult-income_schema.yaml

Splitter:
  split_data:
    num_samples: 5
    train_split_ratio: 0.8
    max_overlap_ratio: 0.0  # 用於隱私評估的無重疊分割
    random_state: 12345

Synthesizer:
  generate_synthetic:
    method: ctgan
    epochs: 100

Evaluator:
  privacy_evaluation:
    metrics: ["anonymeter"]
  utility_evaluation:
    metrics: ["correlation", "ks_test"]
```

## 使用場景

### 隱私評估

對於 Anonymeter 等隱私評估任務，建議使用無重疊分割：

```yaml
Splitter:
  privacy_split:
    num_samples: 5
    train_split_ratio: 0.8
    max_overlap_ratio: 0.0  # 確保樣本獨立性
    random_state: 12345
```

### 交叉驗證

用於統計驗證的控制重疊：

```yaml
Splitter:
  cross_validation:
    num_samples: 10
    train_split_ratio: 0.7
    max_overlap_ratio: 0.3  # 允許 30% 重疊
    random_state: "cross_val"
```

### 不平衡資料集

處理不平衡資料集時，建議使用較大的樣本數：

```yaml
Splitter:
  imbalanced_data:
    num_samples: 20
    train_split_ratio: 0.85
    max_overlap_ratio: 0.5
    max_attempts: 50
```

## 相關說明

- **拔靴法抽樣**：Splitter 使用拔靴法（bootstrap sampling）生成多個訓練/驗證分割。
- **重疊控制**：透過 `max_overlap_ratio` 參數精確控制樣本間的重疊程度。
- **樣本獨立性**：隱私評估任務通常需要 `max_overlap_ratio: 0.0` 以確保樣本完全獨立。

## 執行說明

- 實驗名稱（第二層）可自由命名，建議使用描述性名稱
- 可定義多個分割實驗，系統會依序執行
- 分割結果會傳遞給下一個模組（如 Synthesizer）使用
- 樣本編號從 1 開始（非 0）

## 注意事項

- `max_overlap_ratio` 設為 0.0 時確保樣本完全無重疊
- 重疊約束過於嚴格可能導致抽樣失敗，請適當調整 `max_attempts`
- 對於小型資料集，建議使用較低的 `max_overlap_ratio` 以確保多樣性
- 始終設定 `random_state` 以確保結果可重現
- 不平衡資料集建議增加 `num_samples` 以獲得更好的代表性