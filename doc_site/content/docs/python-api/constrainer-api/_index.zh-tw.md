---
title: "Constrainer API"
weight: 350
---

合成資料約束處理模組。

## 類別架構

{{< mermaid-file file="content/docs/python-api/constrainer-api/constrainer-class-diagram.zh-tw.mmd" >}}

## 基本使用

```python
from petsard import Constrainer

# 從 YAML 配置初始化
constrainer = Constrainer(config)

# 套用約束
constrained_data = constrainer.apply(synthetic_data)

# 驗證資料
validation_result = constrainer.validate(data)
```

## 建構函式

```python
def __init__(config: dict)
```

**參數**
- `config`: 約束配置字典（通常從 YAML 載入）

**範例**

```python
config = {
    'nan_groups': {...},
    'field_constraints': [...],
    'field_combinations': [...],
    'field_proportions': [...]
}
constrainer = Constrainer(config)
```

## apply()

套用所有約束條件到資料。

```python
def apply(df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame
```

**參數**
- `df`: 輸入資料框
- `target_rows`: 目標列數（可選，供內部使用）

**返回**
- 符合所有約束的資料框

**範例**

```python
result = constrainer.apply(synthetic_data)
```

## validate()

驗證資料是否符合約束，不修改資料。

```python
def validate(
    data: pd.DataFrame,
    return_details: bool = True,
    max_examples_per_rule: int = 6
) -> dict
```

**參數**
- `data`: 要驗證的資料框
- `return_details`: 是否返回詳細違規記錄
- `max_examples_per_rule`: 每條規則的違規範例數上限

**返回**
- 驗證結果字典，包含：
    - `total_rows`: 總列數
    - `passed_rows`: 通過列數
    - `failed_rows`: 失敗列數
    - `pass_rate`: 通過率
    - `is_fully_compliant`: 是否完全符合
    - `constraint_violations`: 違規統計
    - `violation_details`: 違規資料（可選）

**範例**

```python
result = constrainer.validate(data)
print(f"通過率: {result['pass_rate']:.2%}")

if not result['is_fully_compliant']:
    print(result['violation_details'])
```

## resample_until_satisfy()

重複採樣直到滿足約束且達到目標列數。

```python
def resample_until_satisfy(
    data: pd.DataFrame,
    target_rows: int,
    synthesizer,
    postprocessor=None,
    max_trials: int = 300,
    sampling_ratio: float = 10.0,
    verbose_step: int = 10
) -> pd.DataFrame
```

**參數**
- `data`: 初始資料
- `target_rows`: 目標列數
- `synthesizer`: 合成器實例
- `postprocessor`: 後處理器（可選）
- `max_trials`: 最大嘗試次數
- `sampling_ratio`: 每次採樣倍數
- `verbose_step`: 進度顯示間隔

**返回**
- 符合約束且達到目標列數的資料框

**範例**

```python
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=1000,
    synthesizer=synthesizer,
    max_trials=50
)
print(f"嘗試次數: {constrainer.resample_trails}")
```

## register()

註冊自訂約束類型。

```python
@classmethod
def register(cls, name: str, constraint_class: type)
```

**參數**
- `name`: 約束類型名稱
- `constraint_class`: 繼承自 BaseConstrainer 的類別

**範例**

```python
class CustomConstrainer(BaseConstrainer):
    def apply(self, df):
        # 自訂邏輯
        return df

Constrainer.register('custom', CustomConstrainer)
```

## 方法比較

| 方法 | 用途 | 修改資料 |
|------|------|---------|
| apply() | 套用約束並過濾 | ✅ |
| validate() | 驗證資料品質 | ❌ |
| resample_until_satisfy() | 生成符合約束的資料 | ✅ |

## 注意事項

- 約束配置建議使用 YAML 檔案定義
- 約束條件採用嚴格 AND 邏輯組合
- validate() 不會修改資料，僅用於檢查
- resample_until_satisfy() 適用於約束嚴格的情況