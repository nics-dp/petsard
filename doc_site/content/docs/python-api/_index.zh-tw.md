---
title: "Python API"
type: docs
weight: 1000
prev: docs/glossary
next: docs/developer-guide
---

PETsARD 的 Python API 文件。

{{< callout type="warning" >}}
**重要說明**：本套件期望使用者僅使用 Executor 執行 YAML 做調控，使用者不被預期直接使用內部模組做操作。本段文件僅供開發團隊內部註記使用，任何對於這些模組功能的改動將不會被列為重大變更 (BREAKING CHANGE) 也不保證向後相容。
{{< /callout >}}

## 設計原則

### 適配器模式 (Adapter Pattern)
採用適配器設計模式，透過 Adapter 層統一各模組的介面，讓 Executor 能以一致的方式執行所有組件：
- `create()` - 建立實例
- `fit_sample()` / `eval()` / `report()` - 執行方法（訓練與生成 / 執行評估 / 輸出報告）

每個模組都透過 Adapter 包裝，確保對外提供標準化的介面。

### 不可變物件
所有配置類別都是 frozen dataclass，確保資料安全。

### 型別提示
完整的型別標註，提供更好的開發體驗。

## 配置與執行

| 模組 | 功能 |
|------|------|
| Executor | 實驗管線的主要介面，負責協調整個資料合成和評估流程 |

## 資料管理

| 模組 | 功能 |
|------|------|
| Metadater | 資料集架構和詮釋資料管理，處理資料型別定義和驗證 |

## 管線組件

| 模組 | 功能 |
|------|------|
| Benchmarker | 基準資料集管理，自動下載和處理基準測試資料 |
| Loader | 資料載入和處理，支援多種檔案格式 |
| Splitter | 實驗資料分割，支援訓練/測試集分割 |
| Processor | 資料前處理和後處理，包含編碼和正規化 |
| Synthesizer | 合成資料生成，支援多種合成演算法 |
| Constrainer | 合成資料的資料約束處理器，確保資料符合業務規則 |
| Evaluator | 隱私、保真度和效用評估，提供多維度品質評估 |
| Describer | 描述性資料摘要，提供資料統計分析 |
| Reporter | 結果匯出和報告，支援多種輸出格式 |

## 系統組件

| 模組 | 功能 |
|------|------|
| Adapter | 所有模組的標準化執行包裝器 |
| Config | 實驗配置管理，處理 YAML 配置檔案 |
| Status | 管線狀態和進度追蹤，提供執行監控 |
| Utils | 核心工具函式和外部模組載入 |
