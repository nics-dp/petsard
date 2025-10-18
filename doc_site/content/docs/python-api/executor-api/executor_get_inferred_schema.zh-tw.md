---
title: "get_inferred_schema()"
weight: 55
---

獲取指定模組的推論 Schema。

## 語法

```python
def get_inferred_schema(module: str) -> Schema | None
```

## 參數

- **module** : str, required
    - 模組名稱
    - 通常為 `'Preprocessor'`

## 返回值

- **Schema | None**
    - 推論的 Schema 物件
    - 若不存在則返回 `None`

## 說明

`get_inferred_schema()` 方法用於獲取特定模組的推論 Schema。此功能主要用於 Preprocessor 模組，可在 Loader 執行後獲取 Preprocessor 處理後的 Schema 資訊。

Schema 推論流程：
1. Executor 初始化時讀取 Preprocessor 配置
2. Loader 執行後，根據載入的資料 Schema 推論
3. 結合 Preprocessor 配置推論處理後的 Schema
4. 可透過此方法獲取推論結果

## 基本範例

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 獲取推論的 Preprocessor Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')

if inferred_schema:
    print(f"Schema ID: {inferred_schema.id}")
    print(f"屬性數量: {len(inferred_schema.attributes)}")
else:
    print("無推論 Schema")
```

## 進階範例

### 檢查 Schema 變化

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 獲取原始 Schema（來自 Loader）
original_schema = exec.status.get_metadata('Loader')

# 獲取推論的 Preprocessor Schema
preprocessed_schema = exec.get_inferred_schema('Preprocessor')

if preprocessed_schema:
    print("Schema 變化：")
    print(f"原始欄位數：{len(original_schema.attributes)}")
    print(f"處理後欄位數：{len(preprocessed_schema.attributes)}")
    
    # 比較欄位類型變化
    for attr_name in original_schema.attributes:
        if attr_name in preprocessed_schema.attributes:
            orig_type = original_schema.attributes[attr_name].type
            proc_type = preprocessed_schema.attributes[attr_name].type
            if orig_type != proc_type:
                print(f"  {attr_name}: {orig_type} → {proc_type}")
```

### 驗證 Schema 推論

```python
from petsard import Executor

# 配置包含 Preprocessor
exec = Executor('config_with_preprocessor.yaml')
exec.run()

# 檢查 Schema 是否成功推論
inferred_schema = exec.get_inferred_schema('Preprocessor')

if inferred_schema is None:
    print("警告：Schema 推論失敗")
    print("可能原因：")
    print("1. 配置中沒有 Preprocessor")
    print("2. Loader 尚未執行")
    print("3. Schema 推論過程發生錯誤")
else:
    print("Schema 推論成功")
    print(f"推論的 Schema: {inferred_schema.id}")
```

### 使用推論 Schema 進行驗證

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 獲取推論 Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')

if inferred_schema:
    # 檢查特定欄位的類型
    expected_types = {
        'age': 'numerical',
        'education': 'categorical',
        'income': 'numerical'
    }
    
    for field_name, expected_type in expected_types.items():
        if field_name in inferred_schema.attributes:
            actual_type = inferred_schema.attributes[field_name].type
            if actual_type == expected_type:
                print(f"✓ {field_name}: {actual_type}")
            else:
                print(f"✗ {field_name}: 期望 {expected_type}, 實際 {actual_type}")
```

### 存取推論歷史

```python
from petsard import Executor

exec = Executor('config.yaml')
exec.run()

# 獲取推論 Schema
inferred_schema = exec.get_inferred_schema('Preprocessor')

if inferred_schema:
    # 存取推論歷史（透過 Status 的 SchemaInferencer）
    inference_history = exec.status.schema_inferencer.get_inference_history()
    
    if inference_history:
        print("Schema 推論歷史：")
        for i, record in enumerate(inference_history, 1):
            print(f"\n推論 {i}:")
            print(f"  時間：{record.get('timestamp', 'N/A')}")
            print(f"  變更數：{len(record.get('changes', []))}")
            
            # 顯示變更詳情
            for change in record.get('changes', []):
                print(f"    {change.get('field')}: "
                      f"{change.get('from_type')} → {change.get('to_type')}")
```

## 推論機制

### 何時推論

Schema 推論在以下時機執行：

1. **Executor 初始化時**：
   - 檢查配置中是否有 Preprocessor
   - 準備推論配置

2. **Loader 執行後**：
   - 獲取實際的資料 Schema
   - 執行推論邏輯

3. **Splitter 執行後**：
   - 確保資料分割後 Schema 保持一致

### 推論內容

推論會考慮以下 Preprocessor 操作：

- **Scaling**：不改變欄位類型
- **Encoding**：可能改變欄位類型（如 onehot 會增加欄位）
- **Discretizing**：數值 → 類別
- **Missing Handling**：不改變欄位類型
- **Outlier Handling**：不改變欄位類型

## 使用場景

### 1. Synthesizer 配置驗證

確認 Synthesizer 使用正確的 Schema：

```python
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    # 驗證 Schema 符合 Synthesizer 需求
    validate_schema_for_synthesizer(inferred_schema)
```

### 2. 除錯 Schema 變化

檢查資料處理後的 Schema 變化：

```python
original = exec.status.get_metadata('Loader')
processed = exec.get_inferred_schema('Preprocessor')
compare_schemas(original, processed)
```

### 3. 文檔生成

為處理後的資料生成 Schema 文檔：

```python
inferred_schema = exec.get_inferred_schema('Preprocessor')
if inferred_schema:
    generate_schema_documentation(inferred_schema)
```

## 注意事項

- **執行時機**：必須在 `run()` 執行且 Loader 完成後才能獲取有效結果
- **模組限制**：目前主要用於 `'Preprocessor'` 模組
- **推論準確性**：推論基於配置，實際處理可能有差異
- **None 返回**：返回 `None` 表示推論不可用或失敗
- **Schema 一致性**：推論 Schema 應與實際處理後的資料一致
- **配置依賴**：推論結果依賴 Preprocessor 配置的正確性
- **進階功能**：這是進階功能，一般使用不需要直接調用
- **建議作法**：使用 YAML 配置檔而非直接使用 Python API