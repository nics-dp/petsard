---
title: "load"
weight: 312
---

載入資料並返回 DataFrame 與 SchemaMetadata。

## 語法

```python
def load() -> tuple[pd.DataFrame, SchemaMetadata]
```

## 參數

無

## 返回值

- **tuple[pd.DataFrame, SchemaMetadata]**
    - 包含兩個元素的元組：
        - `data` (`pd.DataFrame`): 載入的資料表
        - `schema` (`SchemaMetadata`): 資料結構詮釋資料

## 說明

`load()` 方法用於實際載入資料。必須在 `__init__()` 之後呼叫此方法。

此方法會根據初始化時的配置，執行以下操作：
1. 讀取資料檔案或下載 benchmark 資料集
2. 處理資料格式
3. 推論或載入資料 schema
4. 返回處理後的 DataFrame 與 SchemaMetadata

## 基本範例

```python
from petsard import Loader

# 初始化載入器
loader = Loader('data.csv')

# 載入資料
data, schema = loader.load()

# 查看結果
print(f"資料形狀: {data.shape}")
print(f"欄位類型: {schema.column_types}")
```

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 必須先呼叫 `__init__()` 初始化載入器
- 返回格式的詳細說明請參考 YAML 配置文件中的 Loader 章節
- 大型檔案建議使用適當的參數以節省記憶體
- 返回的 DataFrame 是複製而非參照，修改不會影響原始檔案