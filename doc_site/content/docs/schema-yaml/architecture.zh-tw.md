---
title: "架構說明"
weight: 1
---

Schema 採用三層架構來描述資料結構。

## 三層架構

| 層級 | 對應資料 | 說明 |
|------|---------|------|
| **Metadata** | Datasets | 管理多個表格 |
| **Schema** | Table | 定義單一表格 |
| **欄位屬性（Attribute）** | Field | 描述單一欄位 |

## 架構關係

```
Metadata (資料集)
├── Schema (表格 1)
│   ├── 欄位屬性 (欄位 1)
│   ├── 欄位屬性 (欄位 2)
│   └── 欄位屬性 (欄位 3)
├── Schema (表格 2)
│   ├── 欄位屬性 (欄位 1)
│   └── 欄位屬性 (欄位 2)
└── Schema (表格 3)
    └── 欄位屬性 (...)
```

## 實際資料對應

| Schema 層級 | Python 資料型別 | 範例 |
|------------|----------------|------|
| Metadata | `dict[str, DataFrame]` | `{'users': df1, 'orders': df2}` |
| Schema | `pd.DataFrame` | `pd.DataFrame(...)` |
| 欄位屬性 | `pd.Series` | `df['user_id']` |

## 使用說明

### 單表格場景（常見）

大多數情況下只包含一個表格：

```yaml
id: my_dataset
schemas:
  users:              # 單一表格
    id: users
    attributes:
      user_id:
        type: int
      name:
        type: str
```

### 多表格場景

當資料集包含多個相關表格：

```yaml
id: ecommerce
schemas:
  users:              # 第一個表格
    id: users
    attributes: {...}
  orders:             # 第二個表格
    id: orders
    attributes: {...}
  products:           # 第三個表格
    id: products
    attributes: {...}
```

## 注意事項

- 實際使用時通常只需定義 Schema 和欄位屬性
- Metadata 層級在單表格場景下由系統自動建立
- 詳細的配置參數請參閱欄位屬性參數文檔