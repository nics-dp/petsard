---
title: "load_external_module()"
weight: 91
---

**模組**：`petsard.utils`

載入外部 Python 模組並回傳模組實例和類別。

## 語法

```python
load_external_module(module_path, class_name, logger, required_methods=None, search_paths=None)
```

## 參數

| 參數 | 類型 | 必要性 | 預設值 | 說明 |
|------|------|--------|--------|------|
| `module_path` | `str` | 必要 | - | 外部模組路徑（相對或絕對路徑） |
| `class_name` | `str` | 必要 | - | 要從模組載入的類別名稱 |
| `logger` | `logging.Logger` | 必要 | - | 用於記錄訊息的 Logger |
| `required_methods` | `dict[str, list[str]]` | 選填 | `None` | 將方法名稱對應到必要參數名稱的字典 |
| `search_paths` | `list[str]` | 選填 | `None` | 解析模組路徑時嘗試的額外搜尋路徑 |

## 返回值

回傳一個元組 `(module, class)`：
- `module`：載入的模組實例
- `class`：模組中的類別

## 異常

- `FileNotFoundError`：如果模組檔案不存在
- `ConfigError`：如果無法載入模組或模組不包含指定的類別

## 使用範例

**範例 1：載入自訂合成器**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# 載入外部合成器模組
module, CustomSynthesizer = load_external_module(
    module_path='./custom_synthesizer.py',
    class_name='CustomSynthesizer',
    logger=logger,
    required_methods={
        'fit': ['data'],
        'sample': ['num_samples']
    }
)

# 使用載入的類別
synthesizer = CustomSynthesizer()
```

**範例 2：使用搜尋路徑載入模組**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# 從多個可能位置載入模組
module, MyClass = load_external_module(
    module_path='my_module.py',
    class_name='MyClass',
    logger=logger,
    search_paths=[
        './modules',
        './custom_modules',
        '/path/to/shared/modules'
    ]
)
```

**範例 3：不驗證方法載入**

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# 不檢查方法載入模組
module, SimpleClass = load_external_module(
    module_path='./simple_class.py',
    class_name='SimpleClass',
    logger=logger
)
```

## 模組解析

函數按以下順序搜尋模組：

1. 如果 `module_path` 是絕對路徑且存在，直接使用
2. 嘗試使用提供的 `module_path`
3. 嘗試當前工作目錄 + `module_path`
4. 嘗試 `search_paths` 中的每個目錄 + `module_path`

## 方法驗證

當提供 `required_methods` 時，函數會驗證：

1. **方法存在性**：類別中必須存在每個指定的方法
2. **可呼叫檢查**：每個方法必須是可呼叫的
3. **參數檢查**：每個方法必須接受必要的參數

`required_methods` 範例：

```python
required_methods = {
    'fit': ['data', 'metadata'],  # fit() 必須接受 'data' 和 'metadata' 參數
    'sample': ['num_samples'],     # sample() 必須接受 'num_samples' 參數
    'save': []                     # save() 必須存在但不需要參數
}
```

## 注意事項

- **路徑彈性**：支援絕對和相對路徑
- **搜尋策略**：嘗試多個位置尋找模組
- **驗證功能**：可選的方法簽章驗證
- **錯誤處理**：提供詳細的錯誤訊息以利除錯
- **Logger 整合**：使用提供的 logger 記錄所有訊息