---
title: "資料有效性診斷"
weight: 1
---

檢查合成資料是否準確反映原始資料的基本特性和結構。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/evaluator-yaml/diagnostic.ipynb)

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori
      control: benchmark://adult-income_control
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
Synthesizer:
  external_data:
    method: custom_data
    filepath: benchmark://adult-income_syn
    schema: benchmark://adult-income_schema
Evaluator:
  validity_check:
    method: sdmetrics-diagnosticreport
```

## 主要參數

- **method** (`string`, 必要參數)
  - 固定值：`sdmetrics-diagnosticreport`

## 評估指標

| 指標 | 說明 | 建議標準 |
|-----|------|---------|
| **Score** | 診斷總分（資料有效性和資料結構的算術平均） | 接近 1.0 |
| **Data Validity** | 資料有效性 | 接近 1.0 |
| - KeyUniqueness | 主鍵唯一性（0-1，獨一無二的比例） | |
| - BoundaryAdherence | 數值邊界一致性（0-1，範圍內的比例） | |
| - CategoryAdherence | 類別基數一致性（0-1，屬於基數的比例） | |
| **Data Structure** | 資料結構 | 1.0 |
| - Column Existence | 欄位存在性 | |
| - Column Type | 欄位型別一致性 | |

## 指標計算說明

### Data Validity（資料有效性）
各欄位有效性分數的算術平均，依欄位特性計算：

- **KeyUniqueness**：主鍵欄位的每筆資料是否獨一無二
- **BoundaryAdherence**：數值或日期欄位是否在原始資料的上下界內
- **CategoryAdherence**：類別或布林欄位的基數是否屬於原始資料的基數集合

### Data Structure（資料結構）
檢查合成資料的欄位名稱與原始資料是否相同。

## 適用情境

- 完成資料合成後的首要檢查項目
- 確認合成過程沒有破壞資料結構
- 驗證資料的基本有效性

## 分數說明與處置

### 理想狀況
- 診斷分數應接近 100%
- 高分表示合成資料成功保留了原始資料的關鍵特性

### 診斷分數未達 1.0 的可能原因

#### Data Validity（資料有效性）未達 1.0

**常見問題**：
- 通常問題出在數值欄位上
- 合成後欄位數值的範圍超過原始範圍

**處置建議**：
- 可視具體資料情境決定是否接受
- 範例：日期欄位
  - 原始資料可能截取到報表日
  - 如果合成資料預測了未來事件，需評估是否合理
  - 並非所有超出範圍的情況都需要否決

#### Data Structure（資料結構）未達 1.0

**常見問題**：
- 合成後的欄位數量減少
- 通常表示前處理流程有誤

**處置建議**：
- 檢查前處理步驟
- 特別注意直接識別欄位的處理：
  - 如果移除直接識別欄位後才訓練合成資料
  - 應該比較「移除直接識別欄位版本」的原始資料
  - 而非比較資料庫版本的原始資料
- 如果是外部合成資料，給定統一的表詮釋資料