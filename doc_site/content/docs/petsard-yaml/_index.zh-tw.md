---
title: "PETsARD YAML"
weight: 100
---

<!--
文件編寫原則（給 roo code 參考）：

### YAML 優先文件
- 以 **YAML 使用者**為主要對象
- 詳細說明所有可在 YAML 中設定的選項
- 提供完整的 YAML 配置範例
- **使用者應優先查閱 YAML 文件**

### 文件撰寫規範

#### 避免交叉連結
- **不要使用內部連結**：避免頁面間的相互連結，因為文件結構可能變動
- **自給自足**：每個頁面應包含完整資訊，不依賴其他頁面

#### 使用列點而非多層標題
- **簡化層級**：參數說明使用列點格式，避免過多的標題層級
- **提升可讀性**：使用列點和縮排來表達結構，讓文件更簡潔易懂
- **減少空白**：避免每個參數都是獨立標題造成的大量空白

#### 選項說明原則
- **YAML 優先**：所有配置選項和詳細說明都在 YAML 文件中
- **完整說明**：每個參數都應包含型別、預設值、範例
- **避免重複**：詳細說明只在 YAML 文件維護，Python API 不重複

#### 結構化資訊
- **由淺入深**：從基本用法到進階選項逐步說明
- **完整範例**：提供從簡單到複雜的多個範例
- **實用導向**：以實際使用情境為出發點
-->

## 什麼是 YAML？

YAML（YAML Ain't Markup Language）是一種人類可讀的資料序列化格式，PETsARD 使用它來進行實驗設定。本文件說明如何有效地組織您的 YAML 設定。

- **易讀易寫**：使用縮排和簡潔的語法，不需要程式設計背景也能理解
- **結構清晰**：透過縮排表達層級關係，視覺上一目了然
- **支援多種資料型別**：字串、數字、布林值、列表、物件等

## PETsARD 為什麼使用 YAML？

PETsARD 採用 YAML 作為主要配置方式，讓您不需要撰寫 Python 程式碼就能完成大部分工作。

1. **無需程式設計**：透過編寫設定檔即可執行完整的合成與評估流程
2. **易於版本控制**：純文字格式，方便追蹤變更和團隊協作
3. **批次處理**：一個設定檔可以定義多個實驗和操作
4. **重複使用**：設定檔可以輕鬆分享和重複使用
<!-- 5. **環境變數支援**：敏感資訊（如 API 金鑰）可以使用環境變數保護 -->

## PETsARD YAML 基本結構

PETsARD 的 YAML 設定採用三層架構：

```yaml
模組名稱:             # 第一層：模組
    實驗名稱:         # 第二層：實驗
        參數1: 數值   # 第三層：參數
        參數2: 數值
```

### 模組層級

最上層定義了按執行順序排列的處理模組：

- **Executor**：執行設定（日誌、工作目錄等）
- **Loader**：資料讀取
- **Splitter**：資料分割
- **Preprocessor**：資料前處理
- **Synthesizer**：資料合成
- **Postprocessor**：資料後處理
- **Constrainer**：資料約束
- **Evaluator**：結果評估
- **Reporter**：報告產生

### 實驗層級

每個模組可以有多個實驗設定。實驗名稱自訂，可根據用途命名：

```yaml
Synthesizer:
    gaussian-copula:   # 使用高斯 Copula 方法
        method: 'sdv-single_table-gaussiancopula'
    ctgan:             # 使用 CTGAN 方法
        method: 'sdv-single_table-ctgan'
    tvae:              # 使用 TVAE 方法
        method: 'sdv-single_table-tvae'
```

同一模組中的多個實驗會依序執行，讓您可以：
- 比較不同方法的效果
- 測試不同參數設定
- 進行批次處理

### 參數層級

每個實驗包含具體的參數設定。不同的方法有不同的參數需求。

## 完整範例

```yaml
# 一個完整的 PETsARD 設定範例
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  gaussian-copula:
    method: 'sdv-single_table-gaussiancopula'
  ctgan:
    method: 'sdv-single_table-ctgan'
  tvae:
    method: 'sdv-single_table-tvae'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  quality-report:
    method: 'sdmetrics-qualityreport'
Reporter:
  save-data:
    method: 'save_data'
    source: 'Synthesizer'
```

這個範例展示了：
1. 載入資料（Loader）
2. 預設的資料前處理（Preprocessor）
3. 使用兩種不同方法合成資料（Synthesizer）
4. 資料後處理（Postprocessor）
5. 評估合成資料品質（Evaluator）
6. 儲存結果（Reporter）
