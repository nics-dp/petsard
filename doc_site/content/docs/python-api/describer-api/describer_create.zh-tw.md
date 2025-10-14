---
title: "create()"
weight: 1
---

初始化並準備評估器進行資料描述。

## 語法

```python
def create() -> None
```

## 參數

此方法不接受參數。

## 返回值

- **None**
    - 此方法不返回值

## 說明

`create()` 方法根據設定的模式和參數初始化內部評估器實作。在使用 `eval()` 執行評估之前，必須先呼叫此方法。

初始化過程包括：
- 建立適當的評估器類別（DataDescriber 或 Stats）
- 根據模式設定統計方法
- 若為比較模式，設定比較參數
- 準備評估所需的內部資料結構

## 基本範例

### Describe 模式

```python
from petsard.evaluator import Describer

# 初始化描述器
describer = Describer(
    method='describe',
    describe_method=['mean', 'median', 'std', 'corr']
)

# 建立評估器
describer.create()

# 現在可以評估資料
results = describer.eval(data={'data': df})
```

### Compare 模式

```python
from petsard.evaluator import Describer

# 初始化比較模式
describer = Describer(
    method='describe',
    mode='compare',
    stats_method=['mean', 'std', 'jsdivergence'],
    compare_method='pct_change'
)

# 建立評估器
describer.create()

# 現在可以比較資料集
results = describer.eval(data={'ori': ori_df, 'syn': syn_df})
```

### 使用自訂參數

```python
from petsard.evaluator import Describer

# 使用自訂參數初始化
describer = Describer(
    method='describe',
    describe_method=['mean', 'std', 'min', 'max', 'corr'],
    percentile=0.95  # 計算第 95 百分位數
)

# 建立評估器
describer.create()

# 評估資料
results = describer.eval(data={'data': df})
```

## 注意事項

- **必要步驟**：在 `eval()` 之前必須呼叫 `create()`
- **一次性初始化**：每個 Describer 實例只需呼叫一次
- **模式特定**：建立的評估器取決於設定的模式
- **效能**：建立過程輕量，實際計算發生在 `eval()` 中
- **錯誤處理**：若設定無效會引發錯誤
- **狀態管理**：建立的內部狀態會在多次 `eval()` 呼叫間保持