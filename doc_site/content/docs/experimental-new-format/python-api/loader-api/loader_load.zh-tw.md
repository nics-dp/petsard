---
title: "Loader.load()"
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
2. 處理資料格式（標題、分隔符號、編碼等）
3. 推論或載入資料 schema
4. 返回處理後的 DataFrame 與 SchemaMetadata

## 返回格式詳解

### DataFrame 結構

返回的 `pd.DataFrame` 包含：
- 所有資料列與欄位
- 適當的資料類型（根據 schema 或自動推論）
- 處理後的缺失值
- 解析後的日期時間欄位（如有指定）

### SchemaMetadata 結構

返回的 `SchemaMetadata` 物件包含：

```python
class SchemaMetadata:
    column_types: dict         # 欄位類型定義
    primary_key: str | None    # 主鍵欄位
    relationships: list        # 資料關聯
    constraints: dict          # 資料約束條件
    
    # 欄位類型格式
    column_types = {
        'column_name': {
            'type': 'numerical' | 'categorical' | 'datetime' | 'text',
            'subtype': str,    # 更細分的類型（可選）
            'min': float,      # 數值最小值（數值型）
            'max': float,      # 數值最大值（數值型）
            'values': list,    # 可能的值（類別型）
            'format': str      # 格式（日期時間型）
        }
    }
```

## 範例

### 基本使用

```python
from petsard import Loader
import pandas as pd

# 初始化載入器
loader = Loader('data.csv')

# 載入資料
data, schema = loader.load()

# 查看資料
print(data.head())
print(f"資料形狀: {data.shape}")
print(f"欄位: {data.columns.tolist()}")

# 查看 schema
print(f"欄位類型: {schema.column_types}")
print(f"主鍵: {schema.primary_key}")
```

### CSV 檔案載入

```python
# 基本 CSV 載入
loader = Loader('sales_data.csv')
data, schema = loader.load()

# 含特殊設定的 CSV
loader = Loader(
    filepath='sales_data.csv',
    sep=';',
    encoding='latin-1',
    parse_dates=['order_date', 'ship_date']
)
data, schema = loader.load()

# 無標題列的 CSV
loader = Loader(
    filepath='no_header.csv',
    header_names=['id', 'name', 'value']
)
data, schema = loader.load()
```

### Excel 檔案載入

```python
# 載入第一個工作表
loader = Loader('report.xlsx')
data, schema = loader.load()

# 載入特定工作表
loader = Loader('report.xlsx', sheet_name='Summary')
data, schema = loader.load()

# 載入多個工作表（返回字典）
loader = Loader('report.xlsx', sheet_name=None)
all_sheets = {}
for sheet_name in ['Sheet1', 'Sheet2']:
    loader = Loader('report.xlsx', sheet_name=sheet_name)
    data, schema = loader.load()
    all_sheets[sheet_name] = (data, schema)
```

### Parquet 檔案載入

```python
# 基本 Parquet 載入
loader = Loader('data.parquet')
data, schema = loader.load()

# 選擇特定欄位
loader = Loader(
    filepath='large_data.parquet',
    columns=['id', 'feature1', 'target']
)
data, schema = loader.load()

# 使用篩選條件
loader = Loader(
    filepath='data.parquet',
    filters=[('age', '>', 18), ('city', '==', 'Taipei')]
)
data, schema = loader.load()
```

### Benchmark 資料集載入

```python
# 載入 Adult Income 基準資料集
loader = Loader('benchmark://adult-income')
data, schema = loader.load()

print(f"Adult Income 資料集 (美國人口普查局):")
print(f"  - 資料筆數: {len(data)}")  # 48,842
print(f"  - 欄位數: {len(data.columns)}")  # 15
print(f"  - 特性: 混合數值與類別型特徵，包含敏感資訊（收入）")
print(f"  - 類別欄位: {[k for k, v in schema.column_types.items() if v['type'] == 'categorical']}")
print(f"  - 數值欄位: {[k for k, v in schema.column_types.items() if v['type'] == 'numerical']}")

# 強制重新下載（如果需要更新快取）
loader = Loader(
    filepath='benchmark://adult-income',
    force_download=True
)
data, schema = loader.load()
```

### 使用 Schema 配置

```python
# 從 YAML 檔案載入 schema
loader = Loader(
    filepath='customers.csv',
    schema='customers_schema.yaml'
)
data, schema = loader.load()

# Schema 會影響資料類型
print("根據 Schema 設定的資料類型:")
for col, dtype in data.dtypes.items():
    schema_type = schema.column_types.get(col, {}).get('type', 'unknown')
    print(f"  {col}: {dtype} (schema: {schema_type})")
```

### 處理大型檔案

```python
# 只載入部分資料
loader = Loader(
    filepath='huge_dataset.csv',
    nrows=10000  # 只載入前 10,000 筆
)
data, schema = loader.load()

# 只載入特定欄位
loader = Loader(
    filepath='wide_dataset.csv',
    usecols=['id', 'feature1', 'feature2', 'target']
)
data, schema = loader.load()

# 分批載入（使用 chunksize）
loader = Loader(
    filepath='huge_dataset.csv',
    chunksize=5000  # 每批 5,000 筆
)

# 注意：使用 chunksize 時，load() 會返回 iterator
chunk_iterator = loader.load()
for i, (chunk_data, chunk_schema) in enumerate(chunk_iterator):
    print(f"處理第 {i+1} 批資料: {chunk_data.shape}")
    # 處理每批資料...
```

### 完整工作流程

```python
from petsard import Loader, Synthesizer, Evaluator

# 1. 載入原始資料
loader = Loader('original_data.csv', schema='data_schema.yaml')
original_data, schema = loader.load()

print(f"載入完成: {original_data.shape}")
print(f"Schema 包含 {len(schema.column_types)} 個欄位定義")

# 2. 生成合成資料
synthesizer = Synthesizer(method='ctgan')
synthesizer.fit(original_data, schema)
synthetic_data = synthesizer.sample(n=len(original_data))

# 3. 評估合成資料品質
evaluator = Evaluator('sdmetrics-qualityreport')
evaluator.create()
result = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})

print(f"資料品質分數: {result['global']['Score'].values[0]:.2f}")
```

## 錯誤處理

### 檔案不存在

```python
try:
    loader = Loader('non_existent.csv')
    data, schema = loader.load()
except FileNotFoundError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：File not found: non_existent.csv
```

### 不支援的檔案格式

```python
try:
    loader = Loader('data.unknown')
    data, schema = loader.load()
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Unsupported file format: .unknown
```

### 編碼錯誤

```python
try:
    loader = Loader('data.csv', encoding='utf-8')
    data, schema = loader.load()
except UnicodeDecodeError as e:
    print(f"編碼錯誤，嘗試其他編碼...")
    loader = Loader('data.csv', encoding='latin-1')
    data, schema = loader.load()
```

### Schema 不符

```python
try:
    loader = Loader('data.csv', schema='wrong_schema.yaml')
    data, schema = loader.load()
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Schema mismatch: column 'unknown_col' not found in data
```

### Benchmark 下載失敗

```python
try:
    loader = Loader('benchmark://invalid-dataset')
    data, schema = loader.load()
except ValueError as e:
    print(f"錯誤：{e}")
    # 輸出：錯誤：Unknown benchmark dataset: invalid-dataset
    # 目前只支援 'adult-income'
```

## 效能優化建議

### 記憶體管理

```python
# 對於大型檔案，使用適當的資料類型
loader = Loader(
    filepath='large_data.csv',
    dtype={
        'id': 'int32',          # 使用較小的整數類型
        'category': 'category',  # 使用 category 類型節省記憶體
        'value': 'float32'       # 使用較小的浮點數類型
    }
)
data, schema = loader.load()
```

### 平行處理

```python
# 某些格式支援平行讀取
loader = Loader(
    filepath='data.parquet',
    engine='pyarrow'  # PyArrow 支援多執行緒
)
data, schema = loader.load()
```

### 快取機制

```python
# Adult Income 基準資料集會自動快取
loader = Loader('benchmark://adult-income')
# 第一次載入會下載（約 3.8 MB）
data1, schema1 = loader.load()

# 第二次載入從快取讀取（更快）
data2, schema2 = loader.load()
```

## 內部運作

`load()` 方法的內部運作流程：

1. **檔案驗證**：檢查檔案是否存在、格式是否支援
2. **載入器選擇**：根據副檔名或方法選擇適當的載入器
3. **資料讀取**：使用對應的 pandas 函數讀取資料
4. **資料處理**：處理標題、缺失值、資料類型轉換
5. **Schema 處理**：載入或推論 schema 資訊
6. **驗證檢查**：確保資料與 schema 一致
7. **返回結果**：打包 DataFrame 與 SchemaMetadata

## 注意事項

- 必須先呼叫 `__init__()` 初始化載入器
- 大型檔案建議使用 `nrows`、`usecols` 或 `chunksize` 參數
- Schema 不符時會拋出例外，請確保 schema 與資料一致
- Benchmark 資料集首次載入需要網路連線
- 日期時間欄位建議使用 `parse_dates` 參數自動解析
- 類別型資料使用 `category` dtype 可大幅節省記憶體
- 返回的 DataFrame 是複製而非參照，修改不會影響原始檔案