---
title: "PETsARD YAML"
weight: 100
---

## PETsARD 為什麼使用 YAML？

PETsARD 採用 YAML 作為主要配置方式，讓您不需要撰寫 Python 程式碼就能完成大部分工作。

1. **無需程式設計**：透過編寫設定檔即可執行完整的合成與評估流程
2. **易於版本控制**：純文字格式，方便追蹤變更和團隊協作
3. **批次處理**：一個設定檔可以定義多個實驗和操作
4. **重複使用**：設定檔可以輕鬆分享和重複使用

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

{{< callout type="info" >}}
**強烈建議的執行順序**

建議按照以下順序配置模組，自行改變順序造成的執行結果恕不負責。
{{< /callout >}}

- **Executor**：執行設定（日誌、工作目錄等）
- **Loader**：資料讀取
- **Splitter**：資料分割
- **Preprocessor**：資料前處理
- **Synthesizer**：資料合成
- **Postprocessor**：資料後處理
- **Constrainer**：資料約束
- **Describer**：資料描述
- **Evaluator**：結果評估
- **Reporter**：報告產生

{{< callout type="warning" >}}
**模組執行限制**

目前限制同一個模組只能執行一次。
{{< /callout >}}

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

## 執行流程

當定義多個實驗時，PETsARD 採用**深度優先**的順序執行所有模組組合：

```
Loader → Splitter → Preprocessor → Synthesizer → Postprocessor → Constrainer → Describer → Evaluator → Reporter
```

{{< callout type="info" >}}
**深度優先（Depth-First）執行順序**

深度優先意味著 PETsARD 會先完整執行第一個實驗組合的所有模組，然後才開始執行第二個實驗組合。這就像是先把一條路走到底，再回頭走另一條路。

**範例**：
```
組合 1: Loader(A) → Synthesizer(method_a) → Evaluator → Reporter
組合 2: Loader(A) → Synthesizer(method_b) → Evaluator → Reporter
組合 3: Loader(B) → Synthesizer(method_a) → Evaluator → Reporter
組合 4: Loader(B) → Synthesizer(method_b) → Evaluator → Reporter
```

**執行樹狀圖**：

{{< mermaid-file file="content/docs/petsard-yaml/depth-first-execution.zh-tw.mermaid" >}}

> **圖例說明：**
> - ① ② ③ ④：執行順序編號
> - 綠色方塊：完整的實驗組合（會執行所有後續模組）
> - 箭頭：資料流向

執行順序：先完成組合 ① 的所有模組 → 再完成組合 ② 的所有模組 → 依此類推

而非廣度優先（Breadth-First）：先執行所有組合的 Loader，再執行所有組合的 Preprocessor...
{{< /callout >}}

### 實驗組合

若在不同模組中定義多個實驗，PETsARD 會產生所有可能的組合。例如：

```yaml
Loader:
  load_a:
    filepath: 'data1.csv'
  load_b:
    filepath: 'data2.csv'
Synthesizer:
  method_a:
    method: 'method-a'
  method_b:
    method: 'method-b'
```

這會產生四種實驗組合：
1. load_a + method_a
2. load_a + method_b
3. load_b + method_a
4. load_b + method_b

每個組合都會完整執行一次完整的流程，讓您可以系統性地比較不同設定的效果。

## 輸出結果

輸出結果需使用 Reporter 模組，請自行參閱 Reporter 模組文件了解詳細設定方式。

## 最佳實踐

遵循這些建議可以讓您的 YAML 設定更易讀、易維護：

1. **使用有意義的實驗名稱**
   - 好：`ctgan_epochs100`、`preprocessing_with_scaling`
   - 避免：`exp1`、`test`、`a`

2. **依模組組織參數**
   - 將相關的參數組織在一起
   - 保持一致的縮排（通常使用 2 或 4 個空格）

3. **為實驗設定加上註解**
   ```yaml
   Synthesizer:
     ctgan:  # 使用 CTGAN 進行表格資料合成
       method: 'sdv-single_table-ctgan'
       epochs: 300  # 增加訓練輪數以提升品質
   ```

4. **執行前驗證 YAML 語法**
   - 確保縮排正確（YAML 對縮排敏感）
   - 檢查冒號後是否有空格
   - 確認引號的配對

5. **善用多實驗比較**
   - 在同一設定檔中定義多個實驗進行比較
   - 使用一致的命名規則方便識別

6. **保持設定檔簡潔**
   - 只設定需要變更的參數
   - 其他參數使用預設值
