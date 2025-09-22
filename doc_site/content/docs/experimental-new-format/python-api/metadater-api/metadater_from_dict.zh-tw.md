---
title: "from_dict"
weight: 362
---

從設定字典建立詮釋資料。

## 語法

```python
Metadater.from_dict(config: dict) -> Metadata
```

## 參數

- **config** (`dict`)
  - 詮釋資料設定字典

## 返回值

- **Metadata**
  - 詮釋資料物件

## 範例

```python
from petsard.metadater import Metadater

# 定義結構
config = {
    'tables': {
        'users': {
            'columns': {
                'id': {'type': 'int'},
                'name': {'type': 'str'},
                'age': {'type': 'int'}
            }
        }
    }
}

# 建立詮釋資料
metadata = Metadater.from_dict(config)
```

## 注意事項

- 設定格式請參考 YAML 配置文件中的 Schema 章節
- 支援多表格定義