---
title: "align()"
weight: 324
---

根據詮釋資料定義對齊資料結構。

## 語法

```python
@staticmethod
def align(
    metadata: Metadata,
    data: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]
```

## 參數

- **metadata** : Metadata, required
  - 詮釋資料定義（目標結構）
  - 必要參數
  - 定義期望的資料結構、欄位順序、型別等
  
- **data** : dict[str, pd.DataFrame], required
  - 待對齊的資料，鍵為表格名稱，值為 DataFrame
  - 必要參數

## 返回值

- **dict[str, pd.DataFrame]**
  - 對齊後的資料字典
  - 結構、欄位順序、型別符合 metadata 定義
  - 缺失欄位會補充為 NaN
  - 額外欄位會被保留

## 說明

`align()` 方法根據 Metadata 定義調整實際資料的結構，確保資料符合預期格式。此方法執行以下操作：

1. **欄位順序調整**：按 metadata 定義的順序重新排列欄位
2. **補充缺失欄位**：為 metadata 中定義但資料中缺失的欄位添加 NaN 值
3. **保留額外欄位**：資料中存在但 metadata 未定義的欄位會被保留在最後
4. **型別轉換**：嘗試將欄位轉換為 metadata 定義的型別（如果可能）
5. **空值處理**：根據 nullable 設定處理空值

## 基本範例

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義期望的結構
config = {
    'id': 'target_schema',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'age': {'name': 'age', 'type': 'int', 'nullable': True},
                'email': {'name': 'email', 'type': 'str', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 實際資料（欄位順序不同、缺少某些欄位）
raw_data = {
    'users': pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],  # 順序不同
        'id': [1, 2, 3],
        'phone': ['123-456', '234-567', '345-678']  # 額外欄位
        # 缺少 'age' 和 'email' 欄位
    })
}

# 對齊資料結構
aligned_data = Metadater.align(metadata, raw_data)

# 檢視對齊結果
print("對齊後的欄位順序：", list(aligned_data['users'].columns))
# 輸出: ['id', 'name', 'age', 'email', 'phone']

print("\n對齊後的資料：")
print(aligned_data['users'])
# id    name     age  email       phone
# 1     Alice    NaN  NaN         123-456
# 2     Bob      NaN  NaN         234-567
# 3     Charlie  NaN  NaN         345-678
```

## 進階範例

### 處理欄位順序差異

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義標準欄位順序
config = {
    'id': 'standard_order',
    'schemas': {
        'products': {
            'id': 'products',
            'attributes': {
                'product_id': {'name': 'product_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'price': {'name': 'price', 'type': 'float', 'nullable': False},
                'category': {'name': 'category', 'type': 'str', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 資料欄位順序混亂
messy_data = {
    'products': pd.DataFrame({
        'category': ['Electronics', 'Books', 'Clothing'],
        'product_id': [101, 102, 103],
        'price': [299.99, 19.99, 49.99],
        'name': ['Laptop', 'Novel', 'T-Shirt']
    })
}

# 對齊資料
aligned_data = Metadater.align(metadata, messy_data)

print("對齊前順序:", list(messy_data['products'].columns))
print("對齊後順序:", list(aligned_data['products'].columns))
# 對齊前順序: ['category', 'product_id', 'price', 'name']
# 對齊後順序: ['product_id', 'name', 'price', 'category']
```

### 補充缺失欄位

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義完整的 schema
config = {
    'id': 'complete_schema',
    'schemas': {
        'employees': {
            'id': 'employees',
            'attributes': {
                'emp_id': {'name': 'emp_id', 'type': 'int', 'nullable': False},
                'name': {'name': 'name', 'type': 'str', 'nullable': False},
                'department': {'name': 'department', 'type': 'str', 'nullable': True},
                'salary': {'name': 'salary', 'type': 'float', 'nullable': True},
                'hire_date': {'name': 'hire_date', 'type': 'datetime', 'nullable': True}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 資料只有部分欄位
incomplete_data = {
    'employees': pd.DataFrame({
        'emp_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
        # 缺少 department, salary, hire_date
    })
}

# 對齊並補充缺失欄位
aligned_data = Metadater.align(metadata, incomplete_data)

print("對齊後的欄位:", list(aligned_data['employees'].columns))
print("\n缺失欄位已補充為 NaN:")
print(aligned_data['employees'])
#    emp_id     name  department  salary hire_date
# 0       1    Alice         NaN     NaN       NaT
# 1       2      Bob         NaN     NaN       NaT
# 2       3  Charlie         NaN     NaN       NaT
```

### 多表格對齊

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義多表格 schema
config = {
    'id': 'multi_table',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False}
            }
        },
        'orders': {
            'id': 'orders',
            'attributes': {
                'order_id': {'name': 'order_id', 'type': 'int', 'nullable': False},
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'amount': {'name': 'amount', 'type': 'float', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 多個表格的資料
raw_data = {
    'users': pd.DataFrame({
        'username': ['alice', 'bob'],  # 順序不同
        'user_id': [1, 2]
    }),
    'orders': pd.DataFrame({
        'amount': [100.0, 200.0],  # 順序不同
        'user_id': [1, 2],
        'order_id': [101, 102]
    })
}

# 對齊所有表格
aligned_data = Metadater.align(metadata, raw_data)

print("Users 表格對齊後:", list(aligned_data['users'].columns))
print("Orders 表格對齊後:", list(aligned_data['orders'].columns))
```

### Loader 內部使用情境

```python
from petsard.metadater import Metadater
import pandas as pd

# 模擬 Loader 的內部流程
def load_data_with_schema(filepath, schema_config):
    """模擬 Loader 如何使用 Metadater.align()"""
    
    # 1. 從配置建立 metadata
    metadata = Metadater.from_dict(schema_config)
    
    # 2. 讀取原始資料
    raw_data = {'data': pd.read_csv(filepath)}
    
    # 3. 對齊資料結構
    aligned_data = Metadater.align(metadata, raw_data)
    
    return aligned_data['data'], metadata

# 使用範例
schema_config = {
    'id': 'my_schema',
    'schemas': {
        'data': {
            'id': 'data',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': True}
            }
        }
    }
}

# data, schema = load_data_with_schema('data.csv', schema_config)
```

### 處理型別轉換

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義嚴格的型別 schema
config = {
    'id': 'typed_schema',
    'schemas': {
        'measurements': {
            'id': 'measurements',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': False},
                'is_valid': {'name': 'is_valid', 'type': 'bool', 'nullable': False}
            }
        }
    }
}
metadata = Metadater.from_dict(config)

# 資料型別可能不完全正確
raw_data = {
    'measurements': pd.DataFrame({
        'id': ['1', '2', '3'],  # 字串型 int
        'value': [1, 2, 3],  # int 型 float
        'is_valid': [1, 0, 1]  # int 型 bool
    })
}

# 對齊會嘗試轉換型別
aligned_data = Metadater.align(metadata, raw_data)

print("對齊後的資料型別:")
print(aligned_data['measurements'].dtypes)
# id           int64
# value      float64
# is_valid      bool
```

### 資料管線中的使用

```python
from petsard.metadater import Metadater
import pandas as pd

# 定義標準化流程
class DataPipeline:
    def __init__(self, schema_config):
        self.metadata = Metadater.from_dict(schema_config)
    
    def process(self, raw_data):
        """標準化資料處理流程"""
        # 1. 對齊資料結構
        aligned = Metadater.align(self.metadata, raw_data)
        
        # 2. 檢查差異
        diff = Metadater.diff(self.metadata, aligned)
        if diff:
            print("警告：資料結構仍有差異", diff)
        
        # 3. 返回標準化的資料
        return aligned

# 使用管線
schema_config = {
    'id': 'standard',
    'schemas': {
        'data': {
            'id': 'data',
            'attributes': {
                'id': {'name': 'id', 'type': 'int', 'nullable': False},
                'value': {'name': 'value', 'type': 'float', 'nullable': True}
            }
        }
    }
}

pipeline = DataPipeline(schema_config)

# 處理不同來源的資料
sources = [
    {'data': pd.DataFrame({'value': [1.5, 2.5], 'id': [1, 2]})},
    {'data': pd.DataFrame({'id': [3, 4], 'value': [3.5, 4.5]})},
]

standardized_data = [pipeline.process(source) for source in sources]
```

## 注意事項

- **對齊操作**：
  - 欄位順序會按 metadata 定義重新排列
  - 缺失欄位會補充為 NaN（或對應型別的空值）
  - 額外欄位會保留在最後（metadata 未定義的欄位）
  - 型別轉換會盡力執行，但不保證所有轉換都能成功
  
- **非破壞性操作**：
  - 不會修改原始輸入資料
  - 返回新的 DataFrame 副本
  - 額外欄位不會被移除
  
- **型別轉換**：
  - 自動嘗試轉換為定義的型別
  - 轉換失敗時可能保留原型別或引發錯誤
  - 日期時間型別轉換需要格式正確
  
- **空值處理**：
  - 補充的欄位會使用 NaN（數值）或 None（物件）
  - 日期時間型別使用 NaT (Not a Time)
  - nullable 設定不影響對齊過程，只影響驗證
  
- **效能考量**：
  - 大型資料集的對齊可能較耗時
  - 頻繁的型別轉換會影響效能
  - 建議在資料載入階段一次性對齊
  
- **使用時機**：
  - 資料載入後的標準化
  - 合併不同來源的資料前
  - 確保資料符合下游模組要求
  - 資料管線中的標準化步驟
  
- **與其他方法的關係**：
  - 通常在 `diff()` 之後使用
  - Loader 內部自動呼叫此方法
  - 配合 `from_dict()` 或 `from_data()` 建立 metadata
  
- **錯誤處理**：
  - 型別轉換失敗可能引發例外
  - 建議使用 try-except 處理可能的錯誤
  - 對齊前可先用 `diff()` 檢查差異程度
  
- **最佳實踐**：
  - 在資料管線早期階段對齊資料
  - 對齊後驗證結果是否符合預期
  - 記錄對齊過程中的警告和錯誤
  - 考慮將對齊操作封裝為獨立函數