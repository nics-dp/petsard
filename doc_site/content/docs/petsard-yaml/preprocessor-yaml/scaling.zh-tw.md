---
title: "縮放"
weight: 4
---

將數值資料正規化到特定範圍或分布，以改善機器學習演算法的效能。

## 使用範例

### 自訂特定欄位的縮放

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  scaling-specific:
    sequence:
      - scaler
    config:
      scaler:
        age: 'scaler_minmax'          # 最小-最大縮放
        fnlwgt: 'scaler_standard'     # 標準化
        educational-num: 'scaler_log' # 對數轉換
        capital-loss: None            # 類別欄位不縮放

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

### 時間錨點縮放

```yaml
---
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema

Preprocessor:
  time_scaling:
    sequence:
      - scaler
    config:
      scaler:
        created_at:
          method: 'scaler_timeanchor'
          reference: 'event_time'    # 參考時間欄位
          unit: 'D'                  # 單位：天

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

| 處理器 | 說明 | 適用類型 | 輸出範圍 |
|--------|------|---------|---------|
| `scaler_standard` | 標準化 | 數值型 | 均值0，標準差1 |
| `scaler_minmax` | 最小-最大縮放 | 數值型 | [0, 1] |
| `scaler_zerocenter` | 零中心化 | 數值型 | 均值0 |
| `scaler_log` | 對數轉換 | 正數值 | log(x) |
| `scaler_log1p` | log(1+x) 轉換 | 非負數值 | log(1+x) |
| `scaler_timeanchor` | 時間錨點縮放 | 日期時間型 | 時間差 |

## 處理器詳細說明

### scaler_standard

**標準化**：轉換為均值0、標準差1的分布。

**公式**：
```
x' = (x - μ) / σ
```

**特性**：
- 保留資料分布形狀
- 消除量綱影響
- 適合大多數機器學習演算法

### scaler_minmax

**最小-最大縮放**：線性縮放到 [0, 1] 範圍。

**公式**：
```
x' = (x - min) / (max - min)
```

**特性**：
- 保留資料分布形狀
- 輸出範圍固定
- 對離群值敏感

### scaler_zerocenter

**零中心化**：將均值調整為0，但保留原始標準差。

**公式**：
```
x' = x - μ
```

**特性**：
- 只調整位置，不調整尺度
- 保留原始資料的變異程度
- 適合需要保持原始尺度的情況

### scaler_log

**對數轉換**：對數值進行對數轉換。

**公式**：
```
x' = log(x)
```

**特性**：
- 只適用於正數
- 壓縮大數值，擴展小數值
- 適合處理偏態分布

**注意**：資料必須為正數，否則會產生錯誤。

### scaler_log1p

**log(1+x) 轉換**：對數轉換的變體，適合包含零的資料。

**公式**：
```
x' = log(1 + x)
```

**特性**：
- 適用於非負數（包含0）
- 數值穩定性更好
- 還原時使用 exp(x') - 1

### scaler_timeanchor

**時間錨點縮放**：計算與參考時間的時間差。

**參數**：
- **reference** (`str` 或 `list[str]`, 必要)：參考時間欄位名稱
  - **單一參考** (`str`)：轉換錨點欄位為與參考欄位的時間差
  - **多個參考** (`list[str]`)：保持錨點為日期，轉換所有參考欄位為與錨點的時間差
- **unit** (`str`, 選用)：時間差單位
  - `'D'`：天（預設）
  - `'S'`：秒

**特性**：
- 將絕對時間轉為相對時間
- 支援一對一或一對多的時間關係
- 適合處理多時間點資料（如：公司成立日 vs 多個申請/核准日期）

**使用模式**：

1. **單一參考模式**（一個參考欄位）
```yaml
scaler:
  created_at:
    method: 'scaler_timeanchor'
    reference: 'event_time'  # 單一參考欄位
    unit: 'D'
```
結果：`created_at` 被轉換為與 `event_time` 的天數差異（數值），`event_time` 保持為日期

2. **多參考模式**（多個參考欄位）
```yaml
scaler:
  established_date:
    method: 'scaler_timeanchor'
    reference:  # 多個參考欄位（列表）
      - 'first_apply_date'
      - 'approval_date'
      - 'tracking_date'
    unit: 'D'
```
結果：`established_date` 保持為日期（錨點），三個參考欄位被轉換為與錨點的天數差異（數值）

## 處理邏輯

### 統計縮放（Standard/MinMax/ZeroCenter）

- **訓練階段（fit）**：計算統計參數（均值、標準差、最小值、最大值）
- **轉換階段（transform）**：使用統計參數縮放資料
- **還原階段（inverse_transform）**：使用統計參數反縮放

### 對數轉換（Log/Log1p）

- **訓練階段（fit）**：無需訓練
- **轉換階段（transform）**：套用對數函數
- **還原階段（inverse_transform）**：套用指數函數

### 時間錨點（TimeAnchor）

- **訓練階段（fit）**：記錄參考欄位
- **轉換階段（transform）**：計算與參考時間的差值
- **還原階段（inverse_transform）**：加回參考時間，還原為絕對時間

## 預設行為

不同資料類型的預設縮放：

| 資料類型 | 預設處理器 | 說明 |
|---------|-----------|------|
| 數值型 | `scaler_standard` | 標準化 |
| 類別型 | 無 | 不縮放 |
| 日期時間型 | `scaler_standard` | 標準化（時間戳） |

## 縮放方法比較

| 方法 | 優點 | 缺點 | 適用場景 |
|-----|------|------|---------|
| **Standard** | 通用性強<br/>保留分布 | 無固定範圍 | 大多數情況<br/>神經網路 |
| **MinMax** | 範圍固定<br/>易於理解 | 對離群值敏感 | 需要固定範圍<br/>圖像處理 |
| **ZeroCenter** | 保留尺度<br/>簡單 | 不改變尺度 | 需保留原始尺度 |
| **Log** | 處理偏態<br/>壓縮大值 | 只適用正數 | 收入、人口等<br/>右偏分布 |
| **Log1p** | 允許零值<br/>穩定 | 輕微壓縮 | 計數資料<br/>非負數 |
| **TimeAnchor** | 相對時間<br/>易處理 | 需參考欄位 | 時間序列<br/>事件時間 |

## 完整範例

```yaml
Loader:
  load_data:
    filepath: 'data.csv'
    schema: 'schema.yaml'

Preprocessor:
  scale_data:
    method: 'default'
    sequence:
      - missing
      - outlier
      - encoder
      - scaler
    config:
      scaler:
        # 數值欄位使用不同縮放方法
        age: 'scaler_minmax'              # 年齡：0-1範圍
        income: 'scaler_log1p'            # 收入：對數轉換
        hours_per_week: 'scaler_standard' # 工時：標準化
        
        # 時間欄位
        created_at:
          method: 'scaler_timeanchor'
          reference: 'birth_date'
          unit: 'D'
        
        # 類別欄位不縮放
        gender: None
        education: None
```

## 注意事項

- **處理順序**：縮放通常是最後的前處理步驟（編碼之後）
- **Log 限制**：scaler_log 只能用於正數，否則會產生 NaN
- **離群值影響**：MinMax 對離群值敏感，建議先處理離群值
- **參考欄位**：TimeAnchor 的參考欄位必須存在且為日期時間型
- **還原精確度**：所有縮放方法都可精確還原（在數值精度範圍內）
- **合成資料**：合成資料的縮放值可能略微超出訓練資料範圍
- **與 discretizing 配合**：如果使用 discretizing，通常不需要 scaler