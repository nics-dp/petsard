---
title: 快速入門
type: docs
weight: 2
---

PETsARD 的目標客群為任何資料使用者，這代表我們不預期使用者需要具備工程知識，特別是 Python 程式能力。使用者僅需要使用以下三行 Python 程式碼，便可專注於設定檔的編寫：

```python
from petsard import Executor


exec = Executor(config=yaml_path)
exec.run()
```

我們唯一的公開類別只有 `Executor`，使用者透過 YAML 設定檔與 PETsARD 交流。所需的設定檔包括：

1. **PETsARD YAML**：一個合成執行對應一個設定檔
2. **Schema YAML**：一個資料表對應一個 Schema 設定
3. **Constraints YAML**（可選）：一個資料表對應一個約束條件設定

## 什麼是 YAML？

YAML（YAML Ain't Markup Language）是一種人類可讀的資料序列化格式，PETsARD 使用它來進行實驗設定。

- **易讀易寫**：使用縮排和簡潔的語法，不需要程式設計背景也能理解
- **結構清晰**：透過縮排表達層級關係，視覺上一目了然
- **支援多種資料型別**：字串、數字、布林值、列表、物件等

以下情境可以幫助您選擇合適的 YAML 設定方式：

1. **[基本使用：以預設參數做資料合成](default-synthesis)**

  - 當您只需要基本的資料合成時
  - 用於簡單的隱私強化合成資料生成

2. **[基本使用與評測：以預設參數做資料合成與資料評測](default-synthesis-default-evaluation)**

  - 當您需要合成與完整評測時
  - 包含保護力、保真度與實用性評估

3. **[評測外部合成資料：以外部合成資料做預設評測](external-synthesis-default-evaluation)**

  - 當您想評估其他解決方案的合成資料時
  - 使用我們的評測指標來評估外部合成的資料

只要選擇符合您需求的情境，準備對應的 YAML 設定，即可執行上述程式碼。