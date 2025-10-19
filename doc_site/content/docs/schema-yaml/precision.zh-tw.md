---
title: "數值精度"
weight: 203
---

PETsARD 提供自動的數值精度追蹤與保持功能，確保合成資料在整個處理流程中維持原始資料的精度特性。

## 概述

數值精度（precision）是指小數點後的位數。PETsARD 會自動：
1. **推斷精度**：從原始資料中自動偵測每個數值欄位的精度
2. **記錄精度**：在 schema 的 `type_attr` 中儲存精度資訊
3. **保持精度**：在 Loader、Preprocessor、Postprocessor 中自動應用四捨五入

{{< callout type="info" >}}
**自動化處理**：精度追蹤完全自動化，無需手動設定。系統會在資料載入時推斷精度，並在整個 pipeline 中保持。
{{< /callout >}}

## Schema 設定

### 自動推斷

當不提供 schema 時，系統會自動推斷每個數值欄位的精度：

```yaml
# 系統會自動推斷並記錄精度
fields:
  price:
    name: price
    type: float64
    type_attr:
      precision: 2  # 自動推斷：10.12, 20.68 → 精度為 2
  
  amount:
    name: amount
    type: float64
    type_attr:
      precision: 3  # 自動推斷：100.123, 200.988 → 精度為 3
```

### 手動指定

您也可以在 schema 中手動指定精度：

```yaml
fields:
  balance:
    name: balance
    type: float64
    enable_null: false
    type_attr:
      precision: 2  # 手動指定精度為 2（兩位小數）
  
  rate:
    name: rate
    type: float64
    type_attr:
      precision: 4  # 手動指定精度為 4（四位小數）
```

{{< callout type="warning" >}}
**手動指定優先**：當 schema 中已指定精度時，系統不會重新推斷，而是使用指定的精度值。
{{< /callout >}}

## 精度推斷規則

### 數值類型

| 資料類型 | 精度推斷規則 | 範例 |
|---------|-------------|------|
| **整數** | 精度 = 0 | `1, 2, 3` → precision: 0 |
| **浮點數** | 精度 = 最大小數位數 | `1.12, 2.345` → precision: 3 |
| **整數型浮點數** | 精度 = 0 | `1.0, 2.0` → precision: 0 |

### 特殊情況

- **含 null 值**：忽略 null 值，僅從非 null 值推斷精度
- **混合精度**：使用所有值中的最大小數位數
- **非數值型別**：不推斷精度（如字串、布林值）

### 範例

```python
import pandas as pd

# 範例 1：混合精度
df = pd.DataFrame({
    'value': [1.1, 2.22, 3.333, 4.4444]
})
# 推斷結果：precision = 4（最大小數位數）

# 範例 2：含 null 值
df = pd.DataFrame({
    'price': [10.12, None, 20.68, np.nan]
})
# 推斷結果：precision = 2（忽略 null）

# 範例 3：整數型浮點數
df = pd.DataFrame({
    'count': [1.0, 2.0, 3.0]
})
# 推斷結果：precision = 0
```

## 精度應用時機

精度會在以下階段自動應用四捨五入：

### 1. Loader 階段

資料載入後立即應用精度：

```python
from petsard import Loader

# 載入資料（自動應用精度）
loader = Loader(filepath="data.csv")
data, metadata = loader.load()

# data 中的數值欄位已根據推斷的精度進行四捨五入
```

### 2. Preprocessor 階段

前處理轉換後應用精度：

```python
from petsard import Preprocessor

# 前處理（轉換後自動應用精度）
preprocessor = Preprocessor(metadata=metadata)
preprocessor.fit(data)
processed_data = preprocessor.transform(data)

# processed_data 保持原始精度
```

### 3. Postprocessor 階段

後處理還原後應用精度：

```python
from petsard import Postprocessor

# 後處理（還原後自動應用精度）
postprocessor = Postprocessor(metadata=preprocessor_input_schema)
restored_data = postprocessor.transform(synthetic_data)

# restored_data 恢復原始精度
```

{{< callout type="info" >}}
**精度來源**：Postprocessor 使用 `preprocessor_input_schema` 中的精度，確保還原到前處理前的原始精度。
{{< /callout >}}

## 底層實作

### 精度推斷機制

PETsARD 使用 Python 的 `Decimal` 模組進行精確的精度計算：

```python
from decimal import Decimal

def _infer_precision(series: pd.Series) -> int:
    """推斷數值序列的精度（小數位數）"""
    max_precision = 0
    
    for value in series.dropna():
        if pd.notna(value):
            # 使用 Decimal 精確計算小數位數
            decimal_value = Decimal(str(value))
            
            # 取得小數部分
            exponent = decimal_value.as_tuple().exponent
            
            if exponent < 0:
                precision = abs(exponent)
                max_precision = max(max_precision, precision)
    
    return max_precision
```

### 精度應用機制

在每個 adapter 結束時，會調用 `_apply_precision_rounding()` 方法：

```python
def _apply_precision_rounding(
    self, 
    data: pd.DataFrame, 
    schema: Schema, 
    context: str
) -> pd.DataFrame:
    """對數值欄位應用精度四捨五入"""
    
    for col_name, attribute in schema.attributes.items():
        # 檢查是否有精度資訊
        if (attribute.type_attr and 
            'precision' in attribute.type_attr and
            col_name in data.columns):
            
            precision = attribute.type_attr['precision']
            
            # 應用四捨五入
            data[col_name] = data[col_name].apply(
                lambda x: safe_round(x, precision) if pd.notna(x) else x
            )
    
    return data
```

### Schema 轉換時的精度保留

在 `SchemaInferencer` 中，轉換規則會保留 `type_attr`（包含精度）：

```python
class ProcessorTransformRules:
    @staticmethod
    def apply_rule(...):
        # 保留原始 type_attr（包含精度資訊）
        if base_attribute and base_attribute.type_attr:
            target_attribute.type_attr = base_attribute.type_attr.copy()
```

### 精度記憶機制

在 `Status` 類別中記憶 preprocessor 的輸入 schema：

```python
# 在 PreprocessorAdapter 中記憶
status.put(
    module='Preprocessor',
    preprocessor_input_schema=input_metadata
)

# 在 PostprocessorAdapter 中取得
preprocessor_input_schema = status.get_preprocessor_input_schema()
```

## 實際應用範例

### 完整 Pipeline

```python
from petsard import Loader, Preprocessor, Synthesizer, Postprocessor

# 1. 載入資料（自動推斷並應用精度）
loader = Loader(filepath="financial_data.csv")
data, schema = loader.load()
# 假設 'amount' 欄位推斷為 precision: 2

# 2. 前處理（保持精度）
preprocessor = Preprocessor(metadata=schema)
preprocessor.fit(data)
processed = preprocessor.transform(data)
# 轉換後的資料保持 precision: 2

# 3. 合成
synthesizer = Synthesizer(metadata=preprocessor.metadata)
synthesizer.fit(processed)
synthetic = synthesizer.sample(n=1000)

# 4. 後處理（恢復原始精度）
postprocessor = Postprocessor(metadata=preprocessor.metadata)
restored = postprocessor.transform(synthetic)
# restored 中的 'amount' 恢復為 precision: 2

# 結果：合成資料的精度與原始資料一致
```

### 自訂 Schema

```python
from petsard import Loader
from petsard.metadater import Schema, Attribute

# 定義帶有精度的 schema
custom_schema = Schema(
    id="financial_schema",
    attributes={
        "balance": Attribute(
            name="balance",
            type="float64",
            enable_null=False,
            type_attr={"precision": 2}  # 指定精度
        ),
        "interest_rate": Attribute(
            name="interest_rate",
            type="float64",
            enable_null=False,
            type_attr={"precision": 4}  # 更高精度
        )
    }
)

# 使用自訂 schema 載入
loader = Loader(filepath="data.csv", schema=custom_schema)
data, schema = loader.load()
# 資料會根據指定的精度進行四捨五入
```

## 最佳實踐

### 1. 讓系統自動推斷

對於大多數情況，建議讓系統自動推斷精度：

```python
# ✅ 推薦：自動推斷
loader = Loader(filepath="data.csv")
data, schema = loader.load()
```

### 2. 特殊需求時手動指定

僅在有特殊需求時才手動指定：

```python
# 範例：金融資料要求統一為 2 位小數
schema = Schema(
    attributes={
        "amount": Attribute(
            type="float64",
            type_attr={"precision": 2}
        )
    }
)
```

### 3. 檢查推斷結果

可以檢查系統推斷的精度：

```python
# 查看推斷的精度
for name, attr in schema.attributes.items():
    if attr.type_attr and 'precision' in attr.type_attr:
        print(f"{name}: precision = {attr.type_attr['precision']}")
```

## 常見問題

### Q: 如何停用精度追蹤？

A: 精度追蹤是可選的。如果 schema 中沒有 `type_attr.precision`，則不會應用四捨五入。

### Q: 精度會影響合成資料的品質嗎？

A: 不會。精度僅在最終輸出時應用，不影響模型訓練和資料合成的過程。

### Q: 可以為不同欄位設定不同精度嗎？

A: 可以。每個欄位獨立記錄和應用精度。

### Q: Preprocessor 轉換後精度會丟失嗎？

A: 不會。`SchemaInferencer` 會在轉換時保留 `type_attr`，確保精度資訊不丟失。

## 技術細節

### 四捨五入函數

PETsARD 使用 `safe_round()` 函數進行安全的四捨五入：

```python
from petsard.utils import safe_round

# 處理各種情況
safe_round(10.12345, 2)  # → 10.12
safe_round(None, 2)      # → None
safe_round(np.nan, 2)    # → np.nan
```

### 精度儲存位置

```yaml
fields:
  price:
    name: price
    type: float64
    type_attr:
      precision: 2  # 儲存在這裡
```

### 相關類別與方法

- **AttributeMetadater.from_data()**: 推斷精度
- **AttributeMetadater._infer_precision()**: 精度推斷邏輯
- **SchemaInferencer**: 保留 type_attr
- **BaseAdapter._apply_precision_rounding()**: 應用精度
- **Status.get_preprocessor_input_schema()**: 取得原始 schema

## 相關文檔

- [資料型別](../data-types) - 了解支援的資料型別
- [Schema 架構](../architecture) - 了解 Schema 的整體架構