---
title: "自訂資料"
weight: 132
---

要評測由外部工具生成的合成資料，請使用 `custom_data` 方法。

`custom_data` 方法讓 Evaluator 能正確辨識外部檔案為合成結果並進行評測。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/custom-data.ipynb)

```yaml
Synthesizer:
  external_data:
    method: custom_data
    filepath: path/to/your-synthetic-data.csv
```

此範例展示 `custom_data` 與其他模組的搭配用法：
- **Synthesizer**：使用 `custom_data` 匯入外部合成資料
- **其他模組**：Loader 和 Evaluator 搭配使用以完成完整的評測流程

{{< callout type="info" >}}
使用 `custom_data` 時，`filepath` 參數支援所有 Loader 格式，包括 `benchmark://` 協定和一般檔案路徑。
{{< /callout >}}