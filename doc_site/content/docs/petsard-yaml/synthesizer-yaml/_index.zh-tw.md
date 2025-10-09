---
title: "Synthesizer YAML"
weight: 130
---

Synthesizer 模組負責生成合成資料，支援多種合成方法。

## 主要參數

- **method** (`string`)
  - 合成方式
  - 使用 `method: default` 時，會自動使用 SDV GaussianCopula 方法作為預設合成方法。

### 支援的合成方法

- **SDV 方法**：使用 SDV (Synthetic Data Vault) 套件提供的各種合成演算法
- **自訂合成方法**：整合自行開發的合成演算法
- **外部資料載入**：載入其他工具產生的合成資料進行評測

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/synthesizer-yaml.ipynb)

### 使用預設方法

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  default_synthesis:
    method: default
```

### 多重實驗

可在同一個 YAML 中定義多個合成實驗：

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  default_synthesis:
    method: default

  custom-method:
    method: custom_method
    module_path: custom-synthesis.py
    class_name: MySynthesizer_Shuffle
```

關於 `custom_method` 的設定，請參閱「自訂合成方法」文件。

## 執行流程

1. **接收輸入**：從 Loader 或 Preprocessor 接收資料
2. **生成合成資料**：根據指定方法生成合成資料
3. **保持結構**：維持原始資料的欄位結構
4. **輸出結果**：將合成資料傳遞給後續模組

## 精度處理

當 schema 中指定精度設定時，合成器會自動處理：

- **整數欄位**：維持整數格式
- **小數欄位**：四捨五入到指定位數
- **類別欄位**：保持原有類別
