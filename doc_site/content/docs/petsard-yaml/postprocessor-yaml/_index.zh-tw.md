---
title: "Postprocessor YAML（更新中）"
weight: 150
---

Postprocessor 模組的 YAML 設定檔案格式，用於資料後處理（還原轉換）。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/postprocessor-yaml/postprocessor-yaml.ipynb)

### 使用預設後處理

```yaml
Postprocessor:
  demo:
    method: 'default'
```

### 搭配 Preprocessor 使用

```yaml
Preprocessor:
  demo:
    method: 'default'
    
Synthesizer:
  demo:
    method: 'default'
    
Postprocessor:
  demo:
    method: 'default'  # 自動還原 Preprocessor 的轉換
```

## 主要參數

- **method** (`string`, 必要)
  - 後處理方法
  - 可用值：`'default'`（自動還原前處理）

## 工作原理

Postprocessor 會自動執行 Preprocessor 的逆向操作，將合成資料還原到原始格式：

1. **自動偵測**：讀取對應的 Preprocessor 配置
2. **逆序執行**：按相反順序執行還原操作
3. **資料還原**：
   - 反縮放（scaler → inverse scaler）
   - 反編碼（encoder → inverse encoder）
   - 反離散化（discretizing → inverse discretizing）
   - 恢復缺失值（missing → restore NA）

## 還原序列

假設 Preprocessor 的序列為 `['missing', 'outlier', 'encoder', 'scaler']`，  
Postprocessor 的還原序列為 `['scaler', 'encoder', 'missing']`

**注意**：
- `outlier` 不會被還原（離群值處理無法逆向）
- 序列自動反轉
- 缺失值會依原始資料的比例重新插入

## 還原流程圖

```
合成資料（已編碼）
  ↓
反縮放（Scaler inverse）
  ↓
反編碼（Encoder inverse）
  ↓
插入缺失值（Missing restore）
  ↓
原始格式資料
```

## 執行說明

- Postprocessor 必須在 Synthesizer 之後執行
- 系統會自動讀取前面的 Preprocessor 配置
- 如果沒有對應的 Preprocessor，Postprocessor 將不執行任何操作
- 實驗名稱（第二層）可自由命名

## 注意事項

- Postprocessor 會自動偵測並使用對應的 Preprocessor 配置
- 離群值處理無法還原，資料範圍可能與原始資料略有差異
- 缺失值會按照原始比例隨機插入（位置可能不同）
- 資料類型會自動對齊到原始 schema 定義
- 詳細的還原機制請參閱 Postprocessor API 文檔

## 與 Preprocessor 的對應關係

| Preprocessor 步驟 | Postprocessor 對應 | 說明 |
|------------------|-------------------|------|
| `missing` | `restore_missing` | 依比例重新插入缺失值 |
| `outlier` | ❌ 不還原 | 離群值處理無法逆向 |
| `encoder` | `inverse_encoder` | 類別變數解碼 |
| `scaler` | `inverse_scaler` | 數值反縮放 |
| `discretizing` | `inverse_discretizing` | 連續化 |

## 完整範例

```yaml
Loader:
  load_data:
    filepath: 'benchmark/adult-income.csv'
    schema: 'benchmark/adult-income_schema.yaml'

Preprocessor:
  preprocess:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
    config:
      missing:
        age: 'missing_mean'
      encoder:
        gender: 'encoder_onehot'

Synthesizer:
  synthesize:
    method: 'default'

Postprocessor:
  postprocess:
    method: 'default'
    # 會自動執行：
    # 1. inverse scaler
    # 2. inverse encoder (gender 會從 one-hot 還原)
    # 3. restore missing (age 會插入適當比例的 NA)

Reporter:
  save:
    method: 'save_data'
    source: 'Postprocessor'