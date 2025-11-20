---
title: "Splitter API"
type: docs
weight: 1070
---

資料分割模組，用於建立訓練集和驗證集，具備重疊控制功能。

## 類別架構

{{< mermaid-file file="content/docs/python-api/splitter-api/splitter-class-diagram.zh-tw.mmd" >}}

> **圖例說明：**
> - 藍色方塊：主要類別
> - 橘色方塊：子類別實作
> - 淺紫色方塊：設定與資料類別
> - `<|--`：繼承關係
> - `*--`：組合關係
> - `..>`：相依關係

## 基本使用

```python
from petsard import Splitter

# 基本分割
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# 嚴格重疊控制
splitter = Splitter(
    num_samples=5,
    train_split_ratio=0.7,
    max_overlap_ratio=0.1  # 最大 10% 重疊
)
```

## 建構函式 (__init__)

初始化資料分割器實例。

### 語法

```python
def __init__(
    num_samples: int = 1,
    train_split_ratio: float = 0.8,
    random_state: int | float | str = None,
    max_overlap_ratio: float = 1.0,
    max_attempts: int = 30
)
```

### 參數

- **num_samples** : int, optional
    - 重複抽樣次數
    - 預設值：`1`
    - 必須為正整數

- **train_split_ratio** : float, optional
    - 訓練集的資料比例
    - 預設值：`0.8`
    - 範圍：`0.0` 到 `1.0`

- **random_state** : int | float | str, optional
    - 用於重現結果的隨機種子
    - 預設值：`None`
    - 可以是整數、浮點數或字串

- **max_overlap_ratio** : float, optional
    - 樣本間允許的最大重疊比率
    - 預設值：`1.0`（100% - 允許完全重疊）
    - 範圍：`0.0` 到 `1.0`
    - 設為 `0.0` 表示樣本間無重疊

- **max_attempts** : int, optional
    - 重疊控制的最大抽樣嘗試次數
    - 預設值：`30`
    - 當重疊控制啟用時使用

### 返回值

- **Splitter**
    - 初始化的分割器實例

### 使用範例

```python
from petsard import Splitter

# 使用預設設定的基本分割器
splitter = Splitter()

# 多重樣本與重現性
splitter = Splitter(
    num_samples=5,
    train_split_ratio=0.8,
    random_state=42
)

# 嚴格重疊控制
splitter = Splitter(
    num_samples=3,
    max_overlap_ratio=0.1,  # 最大 10% 重疊
    max_attempts=50
)

# 樣本間無重疊
splitter = Splitter(
    num_samples=5,
    max_overlap_ratio=0.0,  # 完全無重疊
    random_state="experiment_v1"
)
```

## 注意事項

- 函數式 API 直接從 `split()` 方法回傳元組
- 使用函數式程式設計模式與不可變資料結構
- 詳細的 split 方法用法請參考 split() 文件
- 建議使用 YAML 設定進行複雜實驗
- 內部使用拔靴法抽樣產生多個樣本