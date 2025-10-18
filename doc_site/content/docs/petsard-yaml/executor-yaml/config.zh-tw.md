---
title: "Config 配置"
weight: 51
---

Config 負責解析和管理 YAML 配置檔案，將宣告式配置轉換為可執行的模組序列。

## 配置結構

YAML 配置檔案採用階層式結構，每個模組包含一個或多個實驗配置：

```yaml
ModuleName:
  experiment_name:
    parameter1: value1
    parameter2: value2
```

## 完整配置範例

```yaml
# 資料載入
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
  load_custom:
    filepath: ./data/custom.csv

# 資料前處理
Preprocessor:
  preprocess:
    method: default

# 資料分割
Splitter:
  split_train_test:
    train_split_ratio: 0.8
    num_samples: 3

# 資料合成
Synthesizer:
  sdv_gaussian:
    method: sdv
    model: GaussianCopula
  sdv_ctgan:
    method: sdv
    model: CTGAN

# 資料評測
Evaluator:
  evaluate_quality:
    method: sdmetrics-qualityreport
  evaluate_privacy:
    method: anonymeter-singlingout

# 結果報告
Reporter:
  save_synthetic:
    method: save_data
    source: Synthesizer
  generate_report:
    method: save_report
    granularity: global
```

## 模組執行順序

Config 會自動按照以下順序安排模組執行：

1. **Loader** - 資料載入
2. **Preprocessor** - 資料前處理（選填）
3. **Splitter** - 資料分割（選填）
4. **Synthesizer** - 資料合成
5. **Postprocessor** - 資料後處理（選填）
6. **Constrainer** - 約束條件（選填）
7. **Evaluator** - 資料評測（選填）
8. **Reporter** - 結果報告（選填）

## 實驗命名規則

### 基本規則

- 實驗名稱必須在同一模組內唯一
- 可使用英文、數字、底線和連字號
- 不能以 `_[xxx]` 模式結尾（保留給系統內部使用）

### 有效的實驗名稱

```yaml
Loader:
  load_data:           # ✓ 有效
    filepath: data.csv
  
  load-benchmark:      # ✓ 有效
    filepath: benchmark://adult-income
  
  load_custom_v2:      # ✓ 有效
    filepath: custom.csv
```

### 無效的實驗名稱

```yaml
Loader:
  load_data_[1]:       # ✗ 無效：保留模式
    filepath: data.csv
  
  load_[test]:         # ✗ 無效：保留模式
    filepath: test.csv
```

## Splitter 特殊處理

當 Splitter 配置包含 `num_samples > 1` 時，Config 會自動展開為多個實驗：

### 原始配置

```yaml
Splitter:
  split_data:
    train_split_ratio: 0.8
    num_samples: 3
```

### 自動展開後

```yaml
Splitter:
  split_data_[3-1]:
    train_split_ratio: 0.8
    num_samples: 1
  split_data_[3-2]:
    train_split_ratio: 0.8
    num_samples: 1
  split_data_[3-3]:
    train_split_ratio: 0.8
    num_samples: 1
```

這個展開過程是自動的，使用者只需要在配置中指定 `num_samples` 參數。

## 多實驗配置

### 笛卡爾積執行

當多個模組都包含多個實驗時，Config 會產生笛卡爾積的執行組合：

```yaml
Loader:
  load_v1:
    filepath: data_v1.csv
  load_v2:
    filepath: data_v2.csv

Synthesizer:
  method_a:
    method: sdv
    model: GaussianCopula
  method_b:
    method: sdv
    model: CTGAN
```

執行組合：
1. `load_v1` → `method_a`
2. `load_v1` → `method_b`
3. `load_v2` → `method_a`
4. `load_v2` → `method_b`

### 結果命名

每個執行組合的結果會以組合名稱儲存：

```
Loader[load_v1]_Synthesizer[method_a]
Loader[load_v1]_Synthesizer[method_b]
Loader[load_v2]_Synthesizer[method_a]
Loader[load_v2]_Synthesizer[method_b]
```

## 配置驗證

Config 在初始化時會執行以下驗證：

### 1. 結構驗證
- 檢查配置是否為有效的字典結構
- 確認模組名稱是否正確

### 2. 命名驗證
- 檢查實驗名稱是否使用保留模式
- 確認實驗名稱在模組內唯一

### 3. 參數驗證
- 由各模組的 Adapter 執行參數檢查
- 在建立 Adapter 實例時進行驗證

## 錯誤處理

### ConfigError

當配置不符合規則時會拋出 `ConfigError`：

```python
from petsard.exceptions import ConfigError

try:
    config = Config(config_dict)
except ConfigError as e:
    print(f"配置錯誤：{e}")
```

常見錯誤：
- 使用保留的實驗命名模式
- 配置結構不正確
- 缺少必要參數

## 注意事項

- **執行順序**：Config 會自動安排正確的模組執行順序，不需手動指定
- **實驗組合**：多實驗配置會產生笛卡爾積，注意執行時間
- **命名規範**：遵守實驗命名規則，避免使用保留模式
- **Splitter 展開**：`num_samples` 參數會自動展開，不需手動設定多個實驗
- **參數驗證**：建議先用小規模測試配置，確認參數正確後再執行完整流程