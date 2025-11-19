---
title: "Preprocessor YAML"
weight: 130
---

Preprocessor 模組的 YAML 設定檔案格式，用於資料前處理。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor-yaml.ipynb)

### 使用預設前處理

```yaml
Preprocessor:
  demo:
    method: 'default'
```

### 使用自訂處理序列

```yaml
Preprocessor:
  custom:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
```

### 為特定欄位自訂處理器

```yaml
Preprocessor:
  custom_fields:
    method: 'default'
    config:
      missing:
        age: 'missing_mean'
        income: 'missing_median'
      outlier:
        age: 'outlier_zscore'
        income: 'outlier_iqr'
      encoder:
        gender: 'encoder_onehot'
        education: 'encoder_label'
      scaler:
        age: 'scaler_minmax'
        income: 'scaler_standard'
```

## 主要參數

- **method** (`string`, 必要)
  - 前處理方法
  - 可用值：`'default'`（預設處理序列）

- **sequence** (`list`, 選用)
  - 自訂處理序列
  - 可用值：`'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`
  - 預設值：`['missing', 'outlier', 'encoder', 'scaler']`

- **config** (`dict`, 選用)
  - 自訂各欄位的處理器設定
  - 結構：`{處理類型: {欄位名稱: 處理方式}}`

## 處理序列

Preprocessor 支援以下處理步驟，依序執行：

0. **constant**：Constant columns 處理（系統自動執行，無需設定）
1. **[missing]({{< ref "missing-handling" >}})**：缺失值處理
2. **[outlier]({{< ref "outlier-handling" >}})**：離群值處理
3. **[encoder]({{< ref "encoding" >}})**：類別變數編碼
4. **[scaler]({{< ref "scaling" >}})**：數值正規化
5. **[discretizing]({{< ref "discretizing" >}})**：離散化（與 encoder 互斥）

{{< callout type="info" >}}
**Constant Columns 自動處理**：系統會自動偵測並處理所有值都相同的欄位（constant columns）。這類欄位在合成資料生成時可能導致某些演算法（如 Copula）出現錯誤，因此會在前處理時自動移除，並在後處理（Postprocessor）時自動還原。此功能預設啟用且無需額外設定。
{{< /callout >}}

## 預設處理方式

| 處理類型 | 數值型 | 類別型 | 日期時間型 |
|---------|--------|--------|-----------|
| **missing** | `missing_mean` | `missing_drop` | `missing_drop` |
| **outlier** | `outlier_iqr` | 無 | `outlier_iqr` |
| **encoder** | 無 | `encoder_uniform` | 無 |
| **scaler** | `scaler_standard` | 無 | `scaler_standard` |
| **discretizing** | `discretizing_kbins` | `encoder_label` | `discretizing_kbins` |

## 功能文件

詳細的處理器說明請參閱各功能頁面：

- [缺失值處理]({{< ref "missing-handling" >}})
- [離群值處理]({{< ref "outlier-handling" >}})
- [編碼]({{< ref "encoding" >}})
- [縮放]({{< ref "scaling" >}})
- [離散化]({{< ref "discretizing" >}})

## 精度保持

Preprocessor 會自動保持數值欄位的精度：

- **精度保留**：轉換過程中不會改變 schema 中的 `type_attr.precision`
- **自動應用**：轉換完成後自動根據精度進行四捨五入
- **記憶機制**：精度資訊會記錄在 Status 中，供後續模組使用

## 執行說明

- 實驗名稱（第二層）可自由命名，建議使用描述性名稱
- 可定義多個實驗，系統會依序執行
- 前處理的結果會傳遞給 Synthesizer 模組

## 注意事項

- `discretizing` 和 `encoder` 不能同時使用
- `discretizing` 必須是序列中的最後一步
- 某些離群值處理器（如 `outlier_isolationforest`、`outlier_lof`）是全域轉換，會套用到所有欄位
- 自訂 config 會覆蓋預設設定
- 精度會在前處理轉換後自動應用，確保數值一致性
- 詳細的處理器參數設定請參閱各功能頁面和 Processor API 文檔