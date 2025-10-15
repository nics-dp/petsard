---
title: "load()"
weight: 342
---

載入資料並返回 DataFrame 與 Schema。

## 語法

```python
def load() -> tuple[pd.DataFrame, Schema]
```

## 參數

無

## 返回值

- **tuple[pd.DataFrame, Schema]**
    - 包含兩個元素的元組：
        - `data` (`pd.DataFrame`): 載入的資料表
        - `schema` (`Schema`): 資料結構元資料

## 說明

`load()` 方法用於實際載入資料。必須在 `__init__()` 之後呼叫此方法。

此方法會根據初始化時的配置，執行以下操作：
1. 合併舊版參數到 schema
2. 使用 pandas reader 模組讀取資料
3. 透過 metadater 處理並驗證 schema
4. 返回處理後的 DataFrame 與 Schema

## 基本範例

```python
from petsard import Loader

# 初始化載入器
loader = Loader('data.csv')

# 載入資料
data, schema = loader.load()

# 查看結果
print(f"資料形狀: {data.shape}")
print(f"Schema ID: {schema.id}")
print(f"屬性數量: {len(schema.attributes)}")
```

## 進階範例

### 快速測試大型檔案

對於大型資料檔案，可以使用 `nrows` 參數只載入部分資料進行測試：

```python
from petsard import Loader

# 只載入前 1000 列進行快速測試
loader = Loader('large_dataset.csv', nrows=1000)
data, schema = loader.load()

print(f"測試資料形狀: {data.shape}")
print(f"快速驗證 schema 結構...")
```

這在以下情況特別有用：
- 🚀 快速驗證資料格式和 schema
- 💾 減少記憶體使用
- 🔬 原型開發和實驗
- ⚡ 加速開發迭代

## 注意事項

- 建議使用 YAML 配置檔而非直接使用 Python API
- 必須先呼叫 `__init__()` 初始化載入器
- 返回的 Schema 詳細說明請參考 Metadater API 文檔
- 大型檔案建議使用 `nrows` 參數以節省記憶體
- 返回的 DataFrame 是複製而非參照，修改不會影響原始檔案
- Excel 格式需要安裝 `openpyxl` 套件