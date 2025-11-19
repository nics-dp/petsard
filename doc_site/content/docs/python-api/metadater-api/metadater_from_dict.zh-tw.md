---
title: "from_dict()"
weight: 322
---

從配置字典建立詮釋資料結構。

## 語法

```python
@staticmethod
def from_dict(config: dict) -> Metadata
```

## 參數

- **config** : dict, required
  - 詮釋資料配置字典
  - 必要參數
  - 需符合 Metadata/Schema/Attribute 的結構規範

## 返回值

- **Metadata**
  - 根據配置建立的詮釋資料物件
  - 包含所有定義的 Schema 和 Attribute

## 說明

`from_dict()` 方法從結構化的配置字典建立 Metadata 物件，適合用於：

1. 從 YAML 配置檔載入後轉換（Loader 內部使用）
2. 程式化定義 schema
3. 動態產生資料結構定義

配置字典的結構應該對應 Metadata、Schema 和 Attribute 的層次關係。

## 基本範例

```python
from petsard.metadater import Metadater

# 定義單一表格的 schema
config = {
    'id': 'my_dataset',
    'name': '使用者資料集',
    'schemas': {
        'users': {
            'id': 'users',
            'name': '使用者表',
            'attributes': {
                'id': {
                    'name': 'id',
                    'type': 'int',
                    'nullable': False
                },
                'name': {
                    'name': 'name',
                    'type': 'str',
                    'nullable': False
                },
                'age': {
                    'name': 'age',
                    'type': 'int',
                    'nullable': True
                }
            }
        }
    }
}

# 建立詮釋資料
metadata = Metadater.from_dict(config)

# 驗證結果
print(f"資料集 ID: {metadata.id}")
print(f"資料集名稱: {metadata.name}")
print(f"包含表格: {list(metadata.schemas.keys())}")
```

## 進階範例

### 多表格定義

```python
from petsard.metadater import Metadater

# 定義包含多個表格的 schema
config = {
    'id': 'ecommerce_db',
    'name': '電商資料庫',
    'description': '包含使用者、訂單和產品資料',
    'schemas': {
        'users': {
            'id': 'users',
            'attributes': {
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'username': {'name': 'username', 'type': 'str', 'nullable': False},
                'email': {'name': 'email', 'type': 'str', 'nullable': False, 'logical_type': 'email'},
                'created_at': {'name': 'created_at', 'type': 'datetime', 'nullable': False}
            }
        },
        'orders': {
            'id': 'orders',
            'attributes': {
                'order_id': {'name': 'order_id', 'type': 'int', 'nullable': False},
                'user_id': {'name': 'user_id', 'type': 'int', 'nullable': False},
                'amount': {'name': 'amount', 'type': 'float', 'nullable': False},
                'status': {'name': 'status', 'type': 'str', 'nullable': False}
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# 檢視各表格結構
for table_name, schema in metadata.schemas.items():
    print(f"\n表格: {table_name}")
    print(f"  欄位數: {len(schema.attributes)}")
    for attr_name in schema.attributes:
        print(f"    - {attr_name}")
```

### 含邏輯型別的定義

```python
from petsard.metadater import Metadater

# 定義含特殊邏輯型別的 schema
config = {
    'id': 'contact_info',
    'schemas': {
        'contacts': {
            'id': 'contacts',
            'attributes': {
                'id': {
                    'name': 'id',
                    'type': 'int',
                    'nullable': False
                },
                'email': {
                    'name': 'email',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'email'  # 標示為電子郵件
                },
                'phone': {
                    'name': 'phone',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'phone_number'  # 標示為電話號碼
                },
                'website': {
                    'name': 'website',
                    'type': 'str',
                    'nullable': True,
                    'logical_type': 'url'  # 標示為 URL
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# 檢視邏輯型別
contacts_schema = metadata.schemas['contacts']
for attr_name, attr in contacts_schema.attributes.items():
    logical_type = attr.logical_type or '(無)'
    print(f"{attr_name}: type={attr.type}, logical_type={logical_type}")
```

### 自訂空值表示

```python
from petsard.metadater import Metadater

# 定義自訂空值表示的 schema
config = {
    'id': 'survey_data',
    'schemas': {
        'responses': {
            'id': 'responses',
            'attributes': {
                'respondent_id': {
                    'name': 'respondent_id',
                    'type': 'int',
                    'nullable': False
                },
                'age': {
                    'name': 'age',
                    'type': 'int',
                    'nullable': True,
                    'na_values': ['unknown', 'N/A', '-1']  # 自訂空值表示
                },
                'income': {
                    'name': 'income',
                    'type': 'float',
                    'nullable': True,
                    'na_values': ['prefer not to say', '-999']
                }
            }
        }
    }
}

metadata = Metadater.from_dict(config)

# 檢視空值設定
responses_schema = metadata.schemas['responses']
for attr_name, attr in responses_schema.attributes.items():
    na_values = getattr(attr, 'na_values', None)
    if na_values:
        print(f"{attr_name}: 自訂空值 = {na_values}")
```

### 從 YAML 讀取後轉換

```python
from petsard.metadater import Metadater
import yaml

# 讀取 YAML 配置檔
with open('schema_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 轉換為 Metadata 物件
metadata = Metadater.from_dict(config)

print(f"從 YAML 載入: {metadata.id}")
```

**schema_config.yaml 範例：**
```yaml
id: example_schema
name: 範例資料結構
schemas:
  users:
    id: users
    attributes:
      user_id:
        name: user_id
        type: int
        nullable: false
      username:
        name: username
        type: str
        nullable: false
```

## 注意事項

- **配置結構**：
  - 必須包含 `id` 和 `schemas` 欄位
  - `schemas` 是字典，鍵為表格名稱
  - 每個 schema 必須包含 `id` 和 `attributes`
  - 每個 attribute 必須包含 `name`, `type`, `nullable`

- **型別支援**：
  - 基本型別：`'int'`, `'float'`, `'str'`, `'bool'`, `'datetime'`
  - 確保型別字串正確，否則可能導致驗證失敗

- **欄位名稱**：
  - `name` 欄位定義實際的欄位名稱
  - 字典的鍵可以與 `name` 不同，但建議保持一致

- **選填欄位**：
  - `name`, `description`: Metadata/Schema 層級的選填欄位
  - `logical_type`: Attribute 層級的選填欄位
  - `na_values`: 自訂空值表示（選填）

- **與 YAML 的關係**：
  - 此方法常用於處理從 YAML 檔案讀取的配置
  - Loader 內部使用此方法處理 `schema` 參數
  - 建議直接使用 YAML 配置而非手動建立字典

- **驗證建議**：
  - 建立後應驗證 metadata 結構是否符合預期
  - 大型配置建議拆分為多個 YAML 檔案管理

- **錯誤處理**：
  - 配置格式錯誤會引發例外
  - 建議使用 try-except 處理配置載入錯誤