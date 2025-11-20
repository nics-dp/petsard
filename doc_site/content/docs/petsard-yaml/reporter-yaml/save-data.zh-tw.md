---
title: "儲存資料"
type: docs
weight: 701
prev: docs/petsard-yaml/reporter-yaml
next: docs/petsard-yaml/reporter-yaml/save-report
---

使用 `save_data` 方法將合成資料或其他模組的輸出儲存為 CSV 檔案。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/reporter-yaml/reporter_save-data.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Splitter:
  basic_split:
    num_samples: 3
    train_split_ratio: 0.8
Preprocessor:
  default:
    method: default

Synthesizer:
  default:
    method: default

  petsard-gaussian-copula:
    method: petsard-gaussian-copula

Postprocessor:
  default:
    method: default
Reporter:
  save_all_step:
    method: save_data  # 必要：固定使用 save_data 方法
    source:            # 必要：指定要儲存的資料來源
      - Splitter.ori          # 儲存分割器的原始資料
      - Splitter.control      # 儲存分割器的控制組資料
      - Preprocessor          # 儲存預處理後的資料
      - Synthesizer.default   # 儲存 default 合成器的結果
      - Synthesizer.petsard-gaussian-copula  # 儲存 petsard-gaussian-copula 合成器的結果
      - Postprocessor         # 儲存後處理的資料
    # output: petsard  # 選用：輸出檔案名稱前綴（預設：petsard）
    # naming_strategy: traditional  # 選用：檔名命名策略，可選 traditional 或 compact（預設：traditional）
```

## 主要參數

### 必要參數

| 參數 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `method` | `string` | 固定為 `save_data` | `save_data` |
| `source` | `string` 或 `list` | 目標模組或實驗名稱 | `Synthesizer` 或 `["Synthesizer", "Loader"]` |

#### source 參數詳細說明

`source` 參數用於指定要儲存的資料來源，支援以下格式：

1. **單一模組**：儲存該模組的所有輸出
   ```yaml
   source: Synthesizer
   ```

2. **特定實驗**：儲存特定實驗的輸出
   ```yaml
   source: Synthesizer.petsard-gaussian-copula
   ```

3. **多個來源**：儲存多個模組或實驗的輸出
   ```yaml
   source:
     - Splitter.ori
     - Preprocessor
     - Synthesizer.default
   ```

**引用注意事項**：

- **Splitter 的特殊輸出**：可用 `.ori`（原始完整資料）、`.control`（控制組資料）、`.train`（訓練集）、`.test`（測試集）指定子集
- **實驗名稱匹配**：引用實驗時，名稱必須與 YAML 中定義的實驗名稱完全一致
- **依賴關係**：只能引用在當前 Reporter 之前執行的模組

**重要提示**：當引用 `Postprocessor` 時，會自動包含所有上游合成器的後處理結果。例如範例中有兩個合成器（`default` 和 `petsard-gaussian-copula`），引用 `Postprocessor` 會自動儲存兩個合成器的後處理結果。

### 選用參數

| 參數 | 類型 | 預設值 | 說明 | 範例 |
|------|------|--------|------|------|
| `output` | `string` | `petsard` | 輸出檔案名稱前綴 | `my_experiment` |
| `naming_strategy` | `string` | `traditional` | 檔名命名策略，詳見主頁面說明 | `compact` |

## 輸出格式

所有資料會儲存為 CSV 格式，檔案命名遵循主頁面說明的命名策略。

**CSV 檔案內容：**
- 原始資料的所有欄位
- 保持資料類型和結構
- 使用 UTF-8 編碼
- 包含標題列

## 常見問題

### Q: 如何避免檔案被覆寫？

**A:** 使用不同的 `output` 前綴或實驗名稱

### Q: 可以指定儲存路徑嗎？

**A:** 有兩種方式：

1. **使用 output 參數指定相對路徑**：檔案會儲存在當前工作目錄下的指定路徑

2. **使用不同的實驗名稱**：在 YAML 中為實驗定義有意義的名稱，會自動反映在輸出檔名中

## 注意事項

- **檔案覆寫**：同名檔案會被覆寫，請使用不同的 `output` 前綴
- **記憶體限制**：大型資料集可能需要較多記憶體
- **編碼格式**：所有檔案使用 UTF-8 編碼
- **資料完整性**：儲存時會保留所有欄位和資料類型
- **實驗追蹤**：建議使用有意義的實驗名稱和輸出前綴

