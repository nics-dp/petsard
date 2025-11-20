---
title: 錯誤處理
type: docs
weight: 10
---

# PETsARD 錯誤處理指南

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
└── EXEC_004 (自訂評估器錯誤 / CustomMethodEvaluatorError)

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

## 狀態管理錯誤 (STATUS_*)

### STATUS_001
**名稱**：SnapshotError / 快照錯誤

**常見原因**：嘗試存取不存在的快照或快照資料損壞

**解決方法**：確認快照 ID 正確並檢查資料完整性

### STATUS_002
**名稱**：TimingError / 時間記錄錯誤

**常見原因**：無效的時間資料格式或缺少配對記錄

**解決方法**：檢查時間記錄格式並確認 START/END 記錄完整

## 除錯與協助

若遇到錯誤：
1. 對照本指南確認錯誤代碼的常見原因和解決方法
2. 參考配置指南啟用 DEBUG 日誌，檢查執行流程和 TIMING 記錄
3. 若問題持續，在 GitHub 開立 issue 並附上錯誤代碼、訊息和日誌摘錄