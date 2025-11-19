---
title: 測試覆蓋範圍
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide/docker-development
---

## 測試統計

**當前測試狀態** (2025年11月):
- **總測試數**: 607 個
- **通過率**: 100%
- **執行時間**: ~55 秒

## 測試組織架構

### 測試分類

PETsARD 測試套件按功能模組組織，使用 pytest markers 進行分類：

- **`unit`**: 單元測試，測試獨立組件功能
- **`integration`**: 整合測試，測試模組間互動
- **`stress`**: 壓力測試，測試大型資料集和極端情況
- **`excel`**: Excel 檔案測試，需要 openpyxl 套件

### 測試目錄結構

```
tests/
├── test_petsard.py          # 端到端工作流程測試
├── test_executor.py          # Executor 配置與日誌測試
├── test_adapter.py           # 配置適配器測試
├── loader/                   # 資料載入模組
├── processor/                # 資料處理模組
├── metadater/               # 詮釋資料管理模組
├── synthesizer/             # 合成器模組
├── constrainer/             # 約束器模組
├── evaluator/               # 評估器模組
├── describer/               # 描述器模組
└── reporter/                # 報告器模組
```

## 核心功能測試

### 端到端測試 (`test_petsard.py`)

測試完整的 PETsARD 工作流程：

- **基本工作流程**: 資料載入 → 預處理 → 合成 → 後處理
- **資料預處理**: 缺失值處理、編碼、標準化
- **約束應用**: 數值範圍、欄位比例控制
- **評估指標**: 品質報告、統計比較
- **最小管道**: 僅載入和報告
- **錯誤處理**: 無效配置檢測

### 執行器 (`test_executor.py`)

測試 Executor 配置和執行管理：

- 配置驗證（日誌等級、輸出類型）
- 日誌系統初始化和重新配置
- YAML 配置載入
- 預設值處理

## 資料載入測試

### Loader (`loader/test_loader.py`)

**基礎功能**:
- CSV/Excel 檔案載入
- 自定義空值和標題處理
- 資料-Schema 自動協調（欄位對齊、型別推斷）

**邏輯型態系統**:
- 文字型態：email, url, uuid, categorical, ip_address
- 數值型態：percentage, currency, latitude, longitude
- 識別碼型態：primary_key
- 型態相容性驗證和衝突解決

**Schema 參數系統**:
- 全域參數：compute_stats, optimize_dtypes, sample_size
- 欄位參數：logical_type, leading_zeros
- 參數衝突檢測

**壓力測試** (標記為 `stress`):
- 100MB - 5GB 檔案處理測試
- 記憶體使用監控
- 型別推斷邊界情況

### Benchmarker (`loader/test_benchmarker.py`)

測試基準資料集管理：

- 資料集下載和快取
- SHA-256 完整性驗證（不匹配時警告）
- benchmark:// 協議處理
- LoaderAdapter 整合

### Splitter (`loader/test_splitter.py`)

測試資料分割功能：

- 訓練/測試分割
- 多樣本生成
- 分層抽樣
- 隨機種子控制

## 資料處理測試

### Processor (`processor/`)

**缺失值處理** (`test_missing.py`):
- MissingMean, MissingMedian, MissingSimple, MissingDrop
- pandas 可空整數型別支援
- 銀行家舍入法處理

**異常值處理**:
- IQR、Z-score、Isolation Forest 方法
- 異常值削減或移除
- pandas 陣列相容性

**編碼器**:
- Label、OneHot、Target 編碼
- 自動類型推斷

**標準化器**:
- Standard、MinMax、Robust 標準化
- 數值特徵處理

### Metadater (`metadater/`)

測試三層架構詮釋資料系統：

**三層架構**:
- Metadata 層：多表格管理
- Schema 層：欄位定義
- Attribute 層：欄位屬性

**核心功能**:
- 從資料/配置建立詮釋資料
- 差異比較 (diff)
- 資料對齊 (align)
- 統計計算
- YAML 往返相容性

## 評估與報告測試

### Describer (`describer/`)

**DescriberDescribe** (`test_describer_describe.py`):
- 統計方法：basic, percentile, na, cardinality
- 粒度：全域、欄位級
- 資料類型：數值、類別、混合
- 邊界情況：空資料、極端值、高基數

**DescriberCompare** (`test_describer_compare.py`):
- JS Divergence 計算
- 代碼重用架構（重用 DescriberDescribe）
- NA 值處理
- base/target 參數命名

### Evaluator (`evaluator/`)

**SDMetrics 整合** (`test_sdmetrics.py`):
- 品質報告評估
- 診斷報告生成
- 單表格和多表格場景
- 粒度控制（global/columnwise/pairwise）

**MPUCCS 隱私評估** (`test_mpuccs.py`):
- 成員推論攻擊評估
- 隱私風險指標
- 多類別分類支援

**自定義評估器** (`test_custom_evaluator.py`):
- 評估器註冊機制
- 自定義評估邏輯
- 工廠模式整合

### Constrainer (`constrainer/`)

**約束類型**:
- **NaN 群組約束** (`test_nan_group_constrainer.py`):
  - Delete, Erase, Copy 動作
  - 多欄位處理
- **欄位約束** (`test_field_constrainer.py`):
  - 數值範圍、條件表達式
  - 複雜邏輯組合
  - 字串字面值處理（含運算符）
- **欄位比例** (`test_constrainer.py`):
  - 類別分佈維護
  - 缺失值比例控制
  - 重新採樣機制

### Reporter (`reporter/`)

**ReporterSaveData**:
- CSV/Excel/Pickle 輸出
- 多格式同時儲存
- 自訂輸出路徑

**ReporterSaveSchema** (`test_reporter_save_schema.py`):
- Schema CSV 摘要生成
- YAML 詳細輸出
- 多來源模組支援
- Schema 攤平和結構化

## 配置適配器測試

### Adapter (`test_adapter.py`)

測試 YAML 配置處理：

**三層 YAML 架構**:
- Module 層：模組類型和名稱
- Experiment 層：實驗配置
- Parameters 層：參數細節

**功能測試**:
- benchmark:// 協議處理
- 後處理器精度和四捨五入
- 多重後處理序列
- 管道式資料流驗證