---
title: "register()"
weight: 356
---

註冊新的約束條件類型。

## 語法

```python
@classmethod
def register(
    cls,
    name: str,
    constraint_class: type
)
```

## 參數

- **name** : str, required
    - 約束條件類型名稱
    - 必要參數
    - 用於在配置字典中識別此約束類型
    
- **constraint_class** : type, required
    - 實現約束條件的類別
    - 必要參數
    - 必須繼承自 `BaseConstrainer`

## 返回值

無

## 說明

[`register()`](constrainer_register.zh-tw.md) 是類別方法，允許使用者擴充 Constrainer 的功能，註冊自訂的約束類型。

### 內建約束類型

Constrainer 預設註冊了以下約束類型：

- `nan_groups`：[`NaNGroupConstrainer`](../../api/constrainer.zh-tw.md#nan_groups-配置)
- `field_constraints`：[`FieldConstrainer`](../../api/constrainer.zh-tw.md#field_constraints-配置)
- `field_combinations`：[`FieldCombinationConstrainer`](../../api/constrainer.zh-tw.md#field_combinations-配置)
- `field_proportions`：[`FieldProportionsConstrainer`](../../api/constrainer.zh-tw.md#field_proportions-配置)

### 自訂約束類別要求

自訂約束類別必須：

1. 繼承自 `BaseConstrainer` 抽象基類
2. 實作 `validate_config(df: pd.DataFrame) -> bool` 方法
3. 實作 `apply(df: pd.DataFrame) -> pd.DataFrame` 方法
4. 在 `__init__` 中接受配置參數

## 基本範例

### 建立簡單的自訂約束

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class MinRowsConstrainer(BaseConstrainer):
    """確保資料至少有指定列數"""
    
    def __init__(self, config: dict):
        self.min_rows = config.get('min_rows', 10)
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """驗證配置是否有效"""
        return isinstance(self.min_rows, int) and self.min_rows > 0
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """套用約束"""
        if len(df) < self.min_rows:
            raise ValueError(f"資料列數 {len(df)} 小於最小要求 {self.min_rows}")
        return df

# 註冊自訂約束
Constrainer.register('min_rows', MinRowsConstrainer)

# 使用自訂約束
config = {
    'min_rows': {'min_rows': 50},
    'field_constraints': [
        "age >= 18"
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### 建立欄位範圍約束

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class FieldRangeConstrainer(BaseConstrainer):
    """根據百分位數約束欄位範圍"""
    
    def __init__(self, config: dict):
        """
        config: {
            'field_name': {
                'lower_percentile': 5,  # 移除低於 5% 的值
                'upper_percentile': 95  # 移除高於 95% 的值
            }
        }
        """
        self.config = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """驗證配置"""
        for field, params in self.config.items():
            if field not in df.columns:
                return False
            if not (0 <= params.get('lower_percentile', 0) <= 100):
                return False
            if not (0 <= params.get('upper_percentile', 100) <= 100):
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """套用百分位數約束"""
        result = df.copy()
        
        for field, params in self.config.items():
            lower_p = params.get('lower_percentile', 0)
            upper_p = params.get('upper_percentile', 100)
            
            lower_val = result[field].quantile(lower_p / 100)
            upper_val = result[field].quantile(upper_p / 100)
            
            mask = (result[field] >= lower_val) & (result[field] <= upper_val)
            result = result[mask]
        
        return result.reset_index(drop=True)

# 註冊約束
Constrainer.register('field_range', FieldRangeConstrainer)

# 使用
config = {
    'field_range': {
        'salary': {
            'lower_percentile': 10,  # 移除最低 10%
            'upper_percentile': 90   # 移除最高 10%
        },
        'age': {
            'lower_percentile': 5,
            'upper_percentile': 95
        }
    }
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

## 進階範例

### 建立依賴關係約束

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

class DependencyConstrainer(BaseConstrainer):
    """約束欄位間的依賴關係"""
    
    def __init__(self, config: list):
        """
        config: [
            {
                'if': {'field': 'status', 'value': 'active'},
                'then': {'field': 'last_login', 'condition': 'IS NOT pd.NA'}
            }
        ]
        """
        self.rules = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """驗證配置"""
        for rule in self.rules:
            if_field = rule['if']['field']
            then_field = rule['then']['field']
            if if_field not in df.columns or then_field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """套用依賴約束"""
        result = df.copy()
        
        for rule in self.rules:
            if_field = rule['if']['field']
            if_value = rule['if']['value']
            then_field = rule['then']['field']
            then_condition = rule['then']['condition']
            
            # 建立條件遮罩
            if_mask = result[if_field] == if_value
            
            if then_condition == 'IS NOT pd.NA':
                then_mask = result[then_field].notna()
            elif then_condition == 'IS pd.NA':
                then_mask = result[then_field].isna()
            else:
                # 可擴充其他條件
                continue
            
            # 保留滿足 "如果...則..." 規則的列
            result = result[~if_mask | (if_mask & then_mask)]
        
        return result.reset_index(drop=True)

# 註冊約束
Constrainer.register('dependency', DependencyConstrainer)

# 使用
config = {
    'dependency': [
        {
            'if': {'field': 'employed', 'value': 'yes'},
            'then': {'field': 'salary', 'condition': 'IS NOT pd.NA'}
        },
        {
            'if': {'field': 'has_children', 'value': 'yes'},
            'then': {'field': 'num_children', 'condition': 'IS NOT pd.NA'}
        }
    ]
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### 建立統計分布約束

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd
import numpy as np

class OutlierConstrainer(BaseConstrainer):
    """移除統計異常值"""
    
    def __init__(self, config: dict):
        """
        config: {
            'field_name': {
                'method': 'iqr',  # 或 'zscore'
                'threshold': 1.5  # IQR 倍數或 Z-score 閾值
            }
        }
        """
        self.config = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        """驗證配置"""
        for field in self.config.keys():
            if field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """移除異常值"""
        result = df.copy()
        
        for field, params in self.config.items():
            method = params.get('method', 'iqr')
            threshold = params.get('threshold', 1.5)
            
            if method == 'iqr':
                Q1 = result[field].quantile(0.25)
                Q3 = result[field].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                mask = (result[field] >= lower_bound) & (result[field] <= upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs((result[field] - result[field].mean()) / result[field].std())
                mask = z_scores < threshold
            
            else:
                continue
            
            result = result[mask]
        
        return result.reset_index(drop=True)

# 註冊約束
Constrainer.register('outlier', OutlierConstrainer)

# 使用
config = {
    'outlier': {
        'salary': {
            'method': 'iqr',
            'threshold': 1.5
        },
        'age': {
            'method': 'zscore',
            'threshold': 3
        }
    }
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

### 組合使用內建與自訂約束

```python
from petsard import Constrainer
from petsard.constrainer.constrainer_base import BaseConstrainer
import pandas as pd

# 定義自訂約束類別
class UniqueValueConstrainer(BaseConstrainer):
    """確保指定欄位的值唯一"""
    
    def __init__(self, config: list):
        self.unique_fields = config
    
    def validate_config(self, df: pd.DataFrame) -> bool:
        for field in self.unique_fields:
            if field not in df.columns:
                return False
        return True
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for field in self.unique_fields:
            result = result.drop_duplicates(subset=[field])
        return result.reset_index(drop=True)

# 註冊
Constrainer.register('unique_values', UniqueValueConstrainer)

# 組合使用內建與自訂約束
config = {
    # 內建約束
    'nan_groups': {
        'name': 'delete'
    },
    'field_constraints': [
        "age >= 18 & age <= 65"
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [70000, 80000, 90000]}
        )
    ],
    
    # 自訂約束
    'unique_values': ['email', 'id']
}

constrainer = Constrainer(config)
result = constrainer.apply(df)
```

## 注意事項

- **類別方法**：register() 是類別方法（@classmethod），不需要實例即可呼叫
- **繼承要求**：自訂類別必須繼承 `BaseConstrainer`，否則會引發 ValueError
- **全域註冊**：註冊後的約束類型全域可用，影響所有 Constrainer 實例
- **覆蓋內建**：可以註冊相同名稱覆蓋內建約束類型（不建議）
- **執行順序**：自訂約束會按照在 config 中的順序執行
- **錯誤處理**：建議在自訂約束中加入完善的錯誤處理和驗證
- **效能考量**：複雜的自訂約束可能影響整體效能
- **測試建議**：在實際使用前充分測試自訂約束的正確性
- **文件化**：為自訂約束類別編寫清楚的文件字串

## 相關方法

- [`__init__()`](_index.zh-tw.md#建構函式-__init__)：初始化約束設定
- [`apply()`](constrainer_apply.zh-tw.md)：套用約束條件
- [`resample_until_satisfy()`](constrainer_resample_until_satisfy.zh-tw.md)：重複採樣直到滿足約束