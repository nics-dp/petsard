---
title: "from_dict"
weight: 2
---

從設定字典建立詮釋資料。

## 語法

```python
Metadater.from_dict(config: dict) -> Metadata
```

## 參數

- **config** (`dict`)
  - 詮釋資料設定字典
  - 必須包含 `id` 和 `schemas` 欄位

## 返回值

- **Metadata**
  - 根據設定建立的詮釋資料物件

## 範例

```python
from petsard.metadater import Metadater

# 定義設定
config = {
    'id': 'my_dataset',
    'schemas': {
        'users': {
            'id': 'users',
            'fields': {
                'id': {
                    'type': 'int64',
                    'nullable': False
                },
                'email': {
                    'type': 'object',
                    'nullable': True,
                    'logical_type': 'email'
                }
            }
        }
    }
}

# 建立詮釋資料
metadata = Metadater.from_dict(config)
```

## 設定結構

```yaml
id: <metadata_id>
schemas:
  <table_name>:
    id: <schema_id>
    fields:
      <field_name>:
        type: <data_type>
        nullable: <boolean>
        logical_type: <type>  # 選填
```

## 注意事項

- 設定字典通常來自 YAML 檔案解析
- 欄位名稱作為 key，不需要額外的 name 屬性
- 內部會將 `fields` 轉換為 `attributes`