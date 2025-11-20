---
title: 錯誤處理
type: docs
weight: 800
prev: docs/schema-yaml
next: docs/glossary
---

PETsARD 使用結構化的錯誤代碼系統。所有錯誤提供錯誤代碼、上下文和解決建議。

## 錯誤訊息結構

每個錯誤提供：
- **錯誤代碼**：結構化識別碼（如 `CONFIG_001`）
- **錯誤訊息**：清楚描述問題
- **上下文**：相關資訊（檔案路徑、欄位名稱等）
- **建議**：解決指引

## 錯誤代碼階層

```
配置錯誤 (CONFIG_*)
├── CONFIG_001 (缺少配置 / NoConfigError)
└── CONFIG_002 (配置錯誤 / ConfigError)

資料處理錯誤 (DATA_*)
├── DATA_001 (無法載入 / UnableToLoadError)
├── DATA_002 (詮釋資料錯誤 / MetadataError)
├── DATA_003 (無法遵循詮釋資料 / UnableToFollowMetadataError)
└── DATA_004 (基準資料集錯誤 / BenchmarkDatasetsError)

操作狀態錯誤 (STATE_*)
├── STATE_001 (尚未建立 / UncreatedError)
├── STATE_002 (尚未擬合 / UnfittedError)
└── STATE_003 (尚未執行 / UnexecutedError)

執行錯誤 (EXEC_*)
├── EXEC_001 (無法合成 / UnableToSynthesizeError)
├── EXEC_002 (無法評估 / UnableToEvaluateError)
├── EXEC_003 (不支援的方法 / UnsupportedMethodError)
├── EXEC_004 (自訂評估器錯誤 / CustomMethodEvaluatorError)
└── EXEC_005 (缺少依賴 / MissingDependencyError)

狀態管理錯誤 (STATUS_*)
├── STATUS_001 (快照錯誤 / SnapshotError)
└── STATUS_002 (時間記錄錯誤 / TimingError)
```

## 配置錯誤 (CONFIG_*)

### CONFIG_001
**名稱**：NoConfigError / 缺少配置

**常見原因**：未提供配置檔案或配置字串為空

**解決方法**：提供有效的配置檔案路徑或 YAML 字串

### CONFIG_002
**名稱**：ConfigError / 配置錯誤

**常見原因**：YAML 語法錯誤或欄位值超出有效範圍

**解決方法**：驗證 YAML 語法並確認欄位值正確

## 資料處理錯誤 (DATA_*)

### DATA_001
**名稱**：UnableToLoadError / 無法載入

**常見原因**：檔案不存在或格式不支援

**解決方法**：確認檔案路徑正確且格式受支援（CSV、Excel、Parquet）

### DATA_002
**名稱**：MetadataError / 詮釋資料錯誤

**常見原因**：詮釋資料格式不正確或與實際資料不符

**解決方法**：確認詮釋資料格式與資料結構相符

### DATA_003
**名稱**：UnableToFollowMetadataError / 無法遵循詮釋資料

**常見原因**：詮釋資料綱要與資料結構不符

**解決方法**：確認詮釋資料欄位名稱與資料欄位相符

### DATA_004
**名稱**：BenchmarkDatasetsError / 基準資料集錯誤

**常見原因**：網路連線問題或基準名稱錯誤

**解決方法**：檢查網路連線並確認基準名稱正確

## 操作狀態錯誤 (STATE_*)

### STATE_001
**名稱**：UncreatedError / 尚未建立

**常見原因**：在呼叫 create() 方法前使用物件

**解決方法**：先呼叫 create() 方法再使用物件

### STATE_002
**名稱**：UnfittedError / 尚未擬合

**常見原因**：在呼叫 fit() 方法前使用模型

**解決方法**：先呼叫 fit() 方法訓練模型

### STATE_003
**名稱**：UnexecutedError / 尚未執行

**常見原因**：在工作流程執行前存取結果

**解決方法**：先執行工作流程再存取結果

## 執行錯誤 (EXEC_*)

### EXEC_001
**名稱**：UnableToSynthesizeError / 無法合成

**常見原因**：詮釋資料不完整或資料品質問題

**解決方法**：確認詮釋資料完整性並檢查資料品質

### EXEC_002
**名稱**：UnableToEvaluateError / 無法評估

**常見原因**：缺少必要的資料集或資料格式不一致

**解決方法**：確認所有必要資料集存在且格式一致

### EXEC_003
**名稱**：UnsupportedMethodError / 不支援的方法

**常見原因**：方法名稱錯誤或未安裝必要依賴

**解決方法**：確認方法名稱拼寫正確並安裝必要依賴

### EXEC_004
**名稱**：CustomMethodEvaluatorError / 自訂評估器錯誤

**常見原因**：自訂評估器實作錯誤

**解決方法**：檢查自訂評估器實作並確認繼承正確的基礎類別

### EXEC_005
**名稱**：MissingDependencyError / 缺少依賴

**常見原因**：使用的方法需要選用依賴套件但未安裝

**解決方法**：安裝所需套件（例如：`pip install sdv`）

**範例**：
```python
try:
    synthesizer = Synthesizer(method="sdv-single_table-gaussiancopula")
except MissingDependencyError as e:
    print(f"缺少依賴: {e}")
    print(f"安裝指令: {e.context.get('install_command')}")
```

## 狀態管理錯誤 (STATUS_*)

### STATUS_001
**名稱**：SnapshotError / 快照錯誤

**常見原因**：嘗試存取不存在的快照或快照資料損壞

**解決方法**：確認快照 ID 正確並檢查資料完整性

### STATUS_002
**名稱**：TimingError / 時間記錄錯誤

**常見原因**：無效的時間資料格式或缺少配對記錄

**解決方法**：檢查時間記錄格式並確認 START/END 記錄完整

## 最佳實踐

### 開發者指引

在開發 PETsARD 或擴充功能時，請遵循以下原則：

#### 1. 使用適當的自訂錯誤

**❌ 錯誤做法**：
```python
except Exception as e:
    print(f"Error: {e}")
    return None
```

**✅ 正確做法**：
```python
from petsard.exceptions import DataProcessingError
import logging

logger = logging.getLogger(__name__)

try:
    # 處理資料
    data = process_data()
except ValueError as e:
    logger.error(f"數值轉換失敗: {e}")
    raise DataProcessingError(
        message="無法處理資料",
        error_code="DATA_002",
        field_name=field_name,
        suggestion="請檢查資料格式是否正確"
    ) from e
```

#### 2. 使用 logging 而非 print

**❌ 錯誤做法**：
```python
print(f"Processing column: {col}")
print(f"Error occurred: {e}")
```

**✅ 正確做法**：
```python
import logging

logger = logging.getLogger(__name__)

logger.debug(f"處理欄位: {col}")
logger.error(f"發生錯誤: {e}")
logger.warning(f"跳過無效欄位: {col}")
```

#### 3. 捕獲具體的異常類型

**❌ 錯誤做法**：
```python
try:
    result = risky_operation()
except Exception as e:  # 太廣泛
    handle_error(e)
```

**✅ 正確做法**：
```python
try:
    result = risky_operation()
except (ValueError, KeyError, TypeError) as e:  # 具體類型
    logger.warning(f"操作失敗: {e}")
    handle_error(e)
except FileNotFoundError as e:  # 檔案相關
    raise UnableToLoadError(
        message="無法載入檔案",
        filepath=filepath
    ) from e
```

#### 4. 提供有用的錯誤上下文

**❌ 錯誤做法**：
```python
raise ConfigError("Invalid config")
```

**✅ 正確做法**：
```python
raise ConfigError(
    message="配置中的欄位值無效",
    config_section="synthesizer",
    invalid_field="sample_size",
    provided_value=-100,
    valid_values=["正整數"],
    suggestion="sample_size 必須是正整數"
)
```

#### 5. 從原始異常鏈接

使用 `from e` 保留原始錯誤堆疊：

```python
try:
    data = pd.read_csv(filepath)
except FileNotFoundError as e:
    raise UnableToLoadError(
        message=f"找不到檔案: {filepath}",
        filepath=filepath
    ) from e  # 保留原始錯誤資訊
```

### 日誌層級使用指引

- **DEBUG**：詳細的診斷資訊（變數值、執行流程）
- **INFO**：一般資訊訊息（操作完成、階段進度）
- **WARNING**：警告訊息（可恢復的錯誤、降級處理）
- **ERROR**：錯誤訊息（操作失敗但不影響整體）
- **CRITICAL**：嚴重錯誤（系統無法繼續執行）

### 錯誤訊息撰寫原則

1. **清楚描述問題**：說明發生什麼錯誤
2. **提供上下文**：包含相關的值、檔案路徑、欄位名稱
3. **建議解決方案**：告訴使用者如何修正
4. **使用錯誤代碼**：便於查詢文檔和追蹤問題

## 除錯與協助

若遇到錯誤：
1. **查看錯誤代碼**：對照本指南確認錯誤代碼的常見原因和解決方法
2. **檢查日誌**：參考配置指南啟用 DEBUG 日誌，檢查執行流程和 TIMING 記錄
3. **尋求協助**：若問題持續，在 [GitHub](https://github.com/nics-tw/PETsARD/issues) 開立 issue 並附上：
   - 錯誤代碼和完整錯誤訊息
   - 相關的配置檔案或程式碼片段
   - 日誌摘錄（DEBUG 層級）
   - Python 版本和 PETsARD 版本