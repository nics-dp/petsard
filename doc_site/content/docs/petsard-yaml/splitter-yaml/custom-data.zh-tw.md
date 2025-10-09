---
title: "自訂資料"
weight: 122
---

要使用來自外部來源的預分割資料，請使用 `custom_data` 方法。

`custom_data` 方法允許您提供預先分割的訓練集和驗證集。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/splitter-yaml/custom-data.ipynb)

```yaml
Splitter:
  external_split:
    method: custom_data
    filepath:
      ori: benchmark://adult-income_ori         # Training set
      control: benchmark://adult-income_control # Validation set
    schema:
      ori: benchmark://adult-income_schema
      control: benchmark://adult-income_schema
```

此範例展示 `custom_data` 與其他模組的搭配用法：
- **Splitter**：使用 `custom_data` 載入預分割資料集
- **其他模組**：Loader, Synthesizer 和 Evaluator 搭配使用以完成完整的評測流程

{{< callout type="info" >}}
`filepath` 參數支援所有 Loader 格式，包括 `benchmark://` 協定和一般檔案路徑。
{{< /callout >}}