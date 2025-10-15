---
title: "自訂合成方法"
weight: 3
---

要建立自己的合成器，需要實作一個含有三個必要方法的 Python 類別，並設定 YAML 檔案來使用它。

## 必要實作

您的 Python 類別必須包含：

```python
class YourSynthesizer:
    def __init__(self, config: dict, metadata):
        """初始化合成器"""
        pass

    def fit(self, data: pd.DataFrame):
        """從輸入資料學習"""
        pass

    def sample(self) -> pd.DataFrame:
        """生成並回傳合成資料"""
        pass
```

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/custom-synthesis.ipynb)

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
Synthesizer:
  your-custom-method:
    method: custom_method
    module_path: custom-synthesis.py  # Python 檔案名稱
    class_name: MySynthesizer_Shuffle # 檔案中的類別名稱
```

### 範例：Shuffle 合成器

我們的範例 `custom-synthesis.py` 實作了一個簡單的合成器：
1. **儲存**：在 `fit()` 時儲存每個欄位的值
2. **打亂**：獨立打亂每個欄位以破壞相關性
3. **回傳**：在 `sample()` 時回傳打亂後的資料

這種方法保留了每個欄位的分布，同時移除欄位間的關聯性 - 適用於簡單的匿名化或作為基準方法。

{{< callout type="info" >}}
Python 檔案應放在與您的 notebook 或 YAML 檔案相同的目錄中。
{{< /callout >}}
