---
title: "編碼"
weight: 3
---

將類別變數轉換為數值格式，以便機器學習演算法處理。

## 背景說明

多數合成演算法僅支援數值型欄位的合成，即使直接支援類別欄位合成，也通常涉及合成器本身內建的前處理與後處理還原轉換。而 CAPE 團隊正是希望控制這些第三方套件不可預期的行為而設計了 PETsARD。

**PETsARD 建議對於任何包含類別變項的欄位，都應主動進行編碼處理**：
- 類別變項：預設使用均勻編碼（Uniform Encoding）
- 技術細節參見 Datacebo 官方文件中的[均勻編碼](https://datacebo.com/blog/improvement-uniform-encoder/)

## 使用範例

請點擊下方按鈕在 Colab 中執行完整範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/getting-started/use-cases/data-preprocessing/encoding-category.ipynb)

### 使用預設編碼

```yaml
Preprocessor:
  demo:
    method: 'default'
    # 類別型欄位：使用均勻編碼
    # 數值型欄位：不編碼
```

### 自訂特定欄位的編碼

```yaml
Preprocessor:
  custom:
    method: 'default'
    config:
      encoder:
        gender: 'encoder_onehot'       # 獨熱編碼
        education: 'encoder_label'     # 標籤編碼
        country: 'encoder_uniform'     # 均勻編碼
        age: None                      # 數值欄位不編碼
```

### 日期編碼

```yaml
Preprocessor:
  date_encoding:
    method: 'default'
    config:
      encoder:
        created_at: 'encoder_date'
        doc_date:
          method: 'encoder_date'
          input_format: '%MinguoY-%m-%d'  # 民國年格式
          date_type: 'date'
```

## 可用的處理器

| 處理器 | 說明 | 適用類型 | 輸出 |
|--------|------|---------|------|
| `encoder_uniform` | 均勻編碼 | 類別型 | 連續值 |
| `encoder_label` | 標籤編碼 | 類別型 | 整數 |
| `encoder_onehot` | 獨熱編碼 | 類別型 | 多欄位（0/1） |
| `encoder_date` | 日期格式轉換 | 日期時間型 | datetime |

## 處理器詳細說明

### encoder_uniform

**均勻編碼**：依照類別出現頻率分配數值範圍。

**特性**：
- 保留類別的頻率資訊
- 輸出為連續值（0.0 到 1.0 之間）
- 高頻類別獲得較大的數值範圍

**範例**：
```yaml
config:
  encoder:
    education: 'encoder_uniform'
```

**編碼示例**：
```
原始資料：['high', 'low', 'medium', 'low', 'low']
頻率：low(60%), medium(20%), high(20%)

編碼結果：
- low → 0.0-0.6 的隨機值
- medium → 0.6-0.8 的隨機值
- high → 0.8-1.0 的隨機值
```

### encoder_label

**標籤編碼**：將類別映射到連續整數。

**特性**：
- 簡單直接的映射
- 輸出為整數（0, 1, 2, ...）
- 不保留類別間的順序關係

**範例**：
```yaml
config:
  encoder:
    gender: 'encoder_label'
```

**編碼示例**：
```
原始資料：['Male', 'Female', 'Male', 'Other']

編碼結果：
- Male → 0
- Female → 1
- Other → 2
```

### encoder_onehot

**獨熱編碼**：為每個類別創建獨立的二元欄位。

**特性**：
- 每個類別變成一個新欄位
- 輸出為多個欄位（0 或 1）
- 不假設類別間有順序關係

**範例**：
```yaml
config:
  encoder:
    color: 'encoder_onehot'
```

**編碼示例**：
```
原始資料：['Red', 'Blue', 'Red', 'Green']

編碼結果（3個新欄位）：
| color_Red | color_Blue | color_Green |
|-----------|------------|-------------|
|     1     |      0     |      0      |
|     0     |      1     |      0      |
|     1     |      0     |      0      |
|     0     |      0     |      1      |
```

### encoder_date

**日期格式轉換**：解析並標準化日期時間資料。

**參數**：
- **input_format** (`str`, 選用)：輸入日期格式
  - 預設：自動偵測
  - 支援民國年：`%MinguoY`
  
- **date_type** (`str`, 選用)：輸出類型
  - `'date'`：僅日期
  - `'datetime'`：日期和時間（預設）
  - `'datetime_tz'`：含時區

- **tz** (`str`, 選用)：時區
  - 範例：`'Asia/Taipei'`

- **numeric_convert** (`bool`, 選用)：是否轉換數值時間戳
  - 預設：`False`

- **invalid_handling** (`str`, 選用)：無效日期處理
  - `'error'`：拋出錯誤（預設）
  - `'erase'`：設為 NA
  - `'replace'`：使用替換規則

**範例**：
```yaml
config:
  encoder:
    # 基本使用
    created_at: 'encoder_date'
    
    # 民國年格式
    doc_date:
      method: 'encoder_date'
      input_format: '%MinguoY-%m-%d'
      date_type: 'date'
    
    # 含時區
    event_time:
      method: 'encoder_date'
      date_type: 'datetime_tz'
      tz: 'Asia/Taipei'
      invalid_handling: 'erase'
```

## 處理邏輯

### 類別編碼（Uniform/Label/OneHot）

```
訓練階段（fit）：
  學習類別映射規則

轉換階段（transform）：
  依映射規則將類別轉為數值

還原階段（inverse_transform）：
  依映射規則將數值還原為類別
```

### 日期編碼（Date）

```
訓練階段（fit）：
  無需訓練

轉換階段（transform）：
  解析並轉換為標準日期格式

還原階段（inverse_transform）：
  保持日期格式或轉為日期字串
```

## 預設行為

不同資料類型的預設編碼：

| 資料類型 | 預設處理器 | 說明 |
|---------|-----------|------|
| 數值型 | 無 | 不編碼 |
| 類別型 | `encoder_uniform` | 均勻編碼 |
| 日期時間型 | 無 | 不編碼 |

## 編碼方法比較

| 方法 | 優點 | 缺點 | 適用場景 |
|-----|------|------|---------|
| **Uniform** | 保留頻率資訊<br/>連續值利於合成 | 需要足夠樣本數 | 預設選擇<br/>合成資料 |
| **Label** | 簡單高效<br/>節省空間 | 暗示順序關係 | 有序類別<br/>離散化前處理 |
| **OneHot** | 不假設順序<br/>清晰表達 | 高基數時產生大量欄位 | 低基數類別<br/>獨立類別 |
| **Date** | 標準化日期格式<br/>支援多種輸入 | 需要正確格式設定 | 日期時間資料 |

## 完整範例

```yaml
Loader:
  load_data:
    filepath: 'data.csv'
    schema: 'schema.yaml'

Preprocessor:
  encode_data:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
    config:
      encoder:
        # 使用不同編碼方法
        gender: 'encoder_onehot'           # 二元類別：One-Hot
        education: 'encoder_label'         # 有序類別：Label
        occupation: 'encoder_uniform'      # 多類別：Uniform
        
        # 日期處理
        birth_date:
          method: 'encoder_date'
          input_format: '%MinguoY/%m/%d'
          date_type: 'date'
        
        # 數值欄位不編碼
        age: None
        income: None
```

## 注意事項

- **OneHot 欄位數量**：會依類別數量產生多個新欄位
- **高基數問題**：類別數量過多時避免使用 OneHot
- **編碼順序**：建議在離群值處理之後、縮放之前執行
- **民國年支援**：使用 `%MinguoY` 格式標記
- **時區處理**：datetime_tz 類型會保留時區資訊
- **還原精確度**：Uniform 編碼還原時可能有輕微誤差
- **與 discretizing 互斥**：不能同時使用 encoder 和 discretizing

## 相關文件

- [Processor API - fit()]({{< ref "/docs/python-api/processor-api/processor_fit" >}})
- [Processor API - transform()]({{< ref "/docs/python-api/processor-api/processor_transform" >}})
- [Processor API - inverse_transform()]({{< ref "/docs/python-api/processor-api/processor_inverse_transform" >}})
- [縮放]({{< ref "scaling" >}})
- [離散化]({{< ref "discretizing" >}})