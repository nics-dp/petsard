---
title: "編碼"
type: docs
weight: 643
prev: docs/petsard-yaml/preprocessor-yaml/outlier-handling
next: docs/petsard-yaml/preprocessor-yaml/scaling
---

將類別變數轉換為數值格式，以便機器學習演算法處理。

## 背景說明

多數合成演算法僅支援數值型欄位的合成，即使直接支援類別欄位合成，也通常涉及合成器本身內建的前處理與後處理還原轉換。而 CAPE 團隊正是希望控制這些第三方套件不可預期的行為而設計了 PETsARD。

**PETsARD 建議對於任何包含類別變項的欄位，都應主動進行編碼處理**：
- 類別變項：預設使用均勻編碼（Uniform Encoding）
- 技術細節參見 Datacebo 官方文件中的[均勻編碼](https://datacebo.com/blog/improvement-uniform-encoder/)

## 使用範例

請點擊下方按鈕在 Colab 中執行完整範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/preprocessor-yaml/preprocessor_encoder.ipynb)

### 自訂特定欄位的編碼

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  encoding-specific:
    sequence:
      - encoder
    config:
      encoder:
        gender: 'encoder_onehot'          # 獨熱編碼
        education: 'encoder_label'        # 標籤編碼
        native-country: 'encoder_uniform' # 均勻編碼
        income: None                      # 不編碼

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

### 時間編碼：日期差異計算

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://best-practices_multi-table

Preprocessor:
  date_diff:
    sequence:
      - encoder
    config:
      encoder:
        first_apply_apply_date:
          method: 'encoder_datediff'
          baseline_date: 'established_date' # 基準日期欄位
          diff_unit: 'days'                 # 差異單位：days/weeks/months/years

Reporter:
  save_data:
    method: save_data
    source:
      - Preprocessor
  save_schema:
    method: save_schema
    source:
      - Loader
      - Preprocessor
...
```

## 可用的處理器

| 處理器 | 說明 | 適用類型 | 輸出 |
|--------|------|---------|------|
| `encoder_uniform` | 均勻編碼 | 類別型 | 連續值 |
| `encoder_label` | 標籤編碼 | 類別型 | 整數 |
| `encoder_onehot` | 獨熱編碼 | 類別型 | 多欄位（0/1） |
| `encoder_datediff` | 日期差異計算 | 日期時間型 | 數值（時間差） |

## 處理器詳細說明

### encoder_uniform

**均勻編碼**：依照類別出現頻率分配數值範圍。

**特性**：
- 保留類別的頻率資訊
- 輸出為連續值（0.0 到 1.0 之間）
- 高頻類別獲得較大的數值範圍

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

### encoder_datediff

**日期差異計算**：計算目標日期與基準日期的時間差。

**參數**：
- **baseline_date** (`str`, 必要)：基準日期欄位名稱
- **diff_unit** (`str`, 選用)：時間差單位
  - `'days'`：天（預設）
  - `'weeks'`：週
  - `'months'`：月
  - `'years'`：年
- **absolute_value** (`bool`, 選用)：是否取絕對值
  - 預設：`False`

**特性**：
- 將絕對時間轉為相對時間
- 適合處理時間序列資料
- 需要指定基準日期欄位

## 處理邏輯

### 類別編碼（Uniform/Label/OneHot）

- **訓練階段（fit）**：學習類別映射規則
- **轉換階段（transform）**：依映射規則將類別轉為數值
- **還原階段（inverse_transform）**：依映射規則將數值還原為類別

### 日期差異計算（DateDiff）

- **訓練階段（fit）**：記錄基準日期欄位
- **轉換階段（transform）**：計算與基準日期的差值
- **還原階段（inverse_transform）**：從差值還原為絕對日期

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
| **DateDiff** | 相對時間易處理<br/>適合時間序列 | 需要基準日期 | 事件時間<br/>時間序列 |

## 注意事項

- **OneHot 欄位數量**：會依類別數量產生多個新欄位
- **高基數問題**：類別數量過多時避免使用 OneHot
- **編碼順序**：建議在離群值處理之後、縮放之前執行
- **時間錨點**：encoder_datediff 適合處理相對時間關係
- **還原精確度**：Uniform 編碼還原時可能有輕微誤差
- **與 discretizing 互斥**：不能同時使用 encoder 和 discretizing