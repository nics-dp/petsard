
---
title: 測試覆蓋範圍
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide/docker-development
---


## PETsARD 端到端功能測試

### `PETsARD 功能工作流程`

> tests/test_petsard.py

測試完整的 PETsARD 端到端工作流程，使用真實的 YAML 配置。這些測試驗證整個系統從資料載入到合成和評估的正確運作。

#### 核心工作流程測試

**`test_default_synthesis_workflow`**：測試基本資料合成管道
- **YAML 配置**：
  - `Loader`：載入基準 adult-income 資料集
  - `Preprocessor`：使用預設預處理方法
  - `Synthesizer`：使用預設合成方法
  - `Postprocessor`：使用預設後處理方法
  - `Reporter`：將合成資料儲存到輸出目錄
- **預期結果**：
  - 執行成功完成，`is_execution_completed() == True`
  - 合成資料包含所有 15 個預期欄位（age、workclass、fnlwgt、education 等）
  - 輸出資料是有效的 pandas DataFrame，行數 >0
  - 資料維持 adult-income 資料集結構

**`test_data_preprocessing_workflow`**：測試含缺失值處理的資料預處理
- **YAML 配置**：
  - `Loader`：載入含自定義空值（'?'）的 adult-income
  - `Preprocessor`：含缺失值處理和編碼的自定義序列
  - `Synthesizer`：預設合成方法
  - `Postprocessor`：預設後處理
  - `Reporter`：儲存處理後的資料
- **預期結果**：
  - 缺失值在合成前得到適當處理
  - 編碼應用於類別變數
  - 最終合成資料維持資料品質

**`test_data_constraining_workflow`**：測試含資料約束的合成
- **YAML 配置**：
  - `Loader`：標準 adult-income 資料集
  - `Preprocessor`：預設預處理
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Constrainer`：欄位約束（年齡 18-65、每週工時 20-60）和教育欄位比例
  - `Reporter`：儲存約束後的資料
- **預期結果**：
  - 年齡值約束在 18-65 範圍內
  - 每週工時值約束在 20-60 範圍內
  - 教育欄位比例在容忍度內維持
  - 約束正確應用於合成資料

**`test_evaluation_workflow`**：測試含評估指標的合成
- **YAML 配置**：
  - `Loader`：Adult-income 資料集
  - `Splitter`：80/20 訓練/測試分割，1 個樣本
  - `Preprocessor`：預設預處理
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Evaluator`：SDMetrics 品質報告評估
  - `Reporter`：儲存全域粒度的評估報告
- **預期結果**：
  - 資料正確分割以進行評估
  - 品質指標計算完成且可用
  - 時間資訊被捕獲且可存取
  - 評估報告成功生成

**`test_minimal_workflow`**：測試僅含資料載入的最小管道
- **YAML 配置**：
  - `Loader`：僅 Adult-income 資料集
  - `Reporter`：直接儲存載入的資料
- **預期結果**：
  - 資料成功載入，無需處理
  - 原始資料集結構得到保留
  - 展示最小可行的 PETsARD 工作流程

**`test_custom_sequence_preprocessing`**：測試自定義預處理管道
- **YAML 配置**：
  - `Loader`：Adult-income 資料集
  - `Preprocessor`：自定義 4 步序列（missing → outlier → scaler → encoder）
  - `Synthesizer`：預設合成
  - `Postprocessor`：預設後處理
  - `Reporter`：儲存最終處理的資料
- **預期結果**：
  - 所有預處理步驟按正確順序執行
  - 資料轉換依序應用
  - 最終資料準備好進行下游分析

#### 參數化模組執行測試

**`test_workflow_module_execution`**：測試不同工作流程配置
- **測試案例**：
  - `default-synthesis`：完整管道（Loader → Preprocessor → Synthesizer → Postprocessor）
  - `minimal`：基本管道（僅 Loader）
  - `with-splitter`：擴展管道（Loader → Splitter → Preprocessor → Synthesizer → Postprocessor）
- **預期結果**：每個工作流程執行預期的模組並產生有效結果

#### 配置驗證測試

**`test_invalid_yaml_config`**：測試無效配置的錯誤處理
- **YAML 配置**：包含不存在的無效模組（InvalidModule）
- **預期結果**：適當拋出 NameError、ValueError、KeyError 或 AttributeError

**`test_missing_required_config`**：測試空配置的錯誤處理
- **YAML 配置**：空配置檔案
- **預期結果**：對缺少必要組件拋出適當錯誤

#### 主要特色

- **Executor API 整合**：測試使用新的 `is_execution_completed()` 方法檢查執行狀態
- **結果提取**：使用輔助方法 `_extract_module_data()` 處理嵌套結果結構
- **真實資料測試**：使用實際基準資料集（adult-income）進行真實測試
- **配置多樣性**：測試多種 YAML 配置模式和模組組合
- **錯誤處理**：驗證無效配置的適當錯誤處理
- **端到端驗證**：確保從配置到最終輸出的完整工作流程運作

> **架構說明**：這些測試使用新的 Executor API 與 `is_execution_completed()` 狀態追蹤來驗證完整的 PETsARD 系統。`run()` 方法在當前版本返回 `None`，計劃在 v2.0.0 中返回成功/失敗狀態碼。結果透過 `get_result()` 方法存取，並透過嵌套工作流程結構處理。

### `Executor`

> tests/test_executor.py

測試 Executor 的主要功能：

- `test_default_values`：驗證預設配置值是否正確設定
- `test_update_config`：測試透過 update 方法更新配置值
- `test_validation_log_output_type`：測試日誌輸出類型設定的驗證：
  - 有效值（stdout、file、both）被接受
  - 無效值引發 ConfigError
- `test_validation_log_level`：測試日誌等級的驗證：
  - 有效等級（DEBUG、INFO、WARNING、ERROR、CRITICAL）被接受
  - 無效等級引發 ConfigError
- `test_executor_default_config`：測試使用不含 Executor 部分的 YAML 初始化時使用預設值
- `test_executor_custom_config`：驗證 YAML 中的自定義日誌設定是否正確應用
- `test_logger_setup`：測試日誌初始化的正確性：
  - 日誌等級
  - 多個處理器（檔案和控制台）
  - 處理器類型
- `test_logger_file_creation`：測試日誌檔案是否在指定目錄中創建並正確替換時間戳
- `test_logger_reconfiguration`：測試日誌器能否在初始設置後重新配置
- `test_get_config`：測試從檔案載入 YAML 配置



## 資料讀取

### `Loader`

> tests/loader/test_loader.py

測試 Loader 的主要功能：

- `test_loader_init_no_config`：驗證無配置初始化時會觸發 ConfigError
- `test_loader_init_with_filepath`：測試以檔案路徑初始化，檢查配置路徑和副檔名是否正確設定
- `test_handle_filepath_with_complex_name`：測試各種檔案路徑模式，包含：
  - 含多個點的路徑
  - 相對路徑 (./ 和 ../)
  - 絕對路徑
  - 混合大小寫的副檔名
- `test_loader_init_with_column_types`：驗證欄位型態設定是否正確存入配置
- `test_benchmark_loader`：使用模擬配置測試基準資料集初始化
- `test_load_csv`：測試 CSV 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_load_excel`：測試 Excel 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_benchmark_data_load`：使用模擬數據測試完整的基準資料載入流程
- `test_custom_na_values`：測試自定義空值的處理
- `test_custom_header_names`：測試使用自定義欄位標題載入資料

#### 資料-Schema 自動協調測試

測試資料與 schema 之間的自動協調功能：

- `test_data_schema_reconciliation_extra_columns`：測試資料有額外欄位時的自動處理：
  - 自動將額外欄位加入 schema
  - 使用 `AttributeMetadater.from_data` 推斷欄位類型
  - 驗證 schema 正確更新包含新欄位
- `test_data_schema_reconciliation_missing_columns`：測試 schema 定義但資料缺少欄位時的處理：
  - 使用 `SchemaMetadater.align` 添加缺失欄位
  - 缺失欄位填充預設值（通常為 NA）
  - 驗證對齊策略正確應用

#### 邏輯型態系統測試

測試全面的邏輯型態推斷和驗證系統：

**重新設計的邏輯型態系統（2025 更新）：**
我們的邏輯型態系統已完全重新設計，避免與基本資料型態重疊，並提供清晰的語意意義檢測。

**可用的邏輯型態：**
- **文字型態**：`email`, `url`, `uuid`, `categorical`, `ip_address`（需要字串資料型態）
- **數值型態**：`percentage`, `currency`, `latitude`, `longitude`（需要數值資料型態）
- **識別碼型態**：`primary_key`（需要唯一性驗證）
- **已移除**：`datetime`, `date`, `time`, `duration`, `integer`, `decimal`, `text`, `foreign_key`（避免型態重疊）

**邏輯型態檢測測試（`tests/metadater/field/test_field_functions.py`）：**
- `test_email_logical_type_detection`：測試電子郵件模式檢測與正則表達式驗證（80% 閾值）
- `test_url_logical_type_detection`：測試網址模式檢測與 HTTP/HTTPS 協定驗證（80% 閾值）
- `test_uuid_logical_type_detection`：測試 8-4-4-4-12 十六進位格式的 UUID 格式檢測（95% 閾值）
- `test_ip_address_detection`：測試 IPv4/IPv6 模式識別與全面位址驗證（90% 閾值）
- `test_categorical_detection_via_cardinality`：測試使用動態閾值的 ASPL 基數分析分類檢測
- `test_primary_key_uniqueness_validation`：測試主鍵的 100% 唯一性要求與重複檢測
- `test_percentage_range_validation`：測試百分比值的 0-100 範圍驗證（95% 閾值）
- `test_currency_symbol_detection`：測試貨幣符號檢測與正值驗證的金額值檢測（80% 閾值）
- `test_latitude_longitude_detection`：測試地理座標範圍驗證（緯度 -90/90，經度 -180/180，95% 閾值）

**型態相容性系統測試：**
- `test_compatible_type_logical_combinations`：測試有效組合：
  - `string` + `email`, `url`, `uuid`, `categorical`, `ip_address` ✅
  - `numeric` + `percentage`, `currency`, `latitude`, `longitude` ✅
  - `int/string` + `primary_key` ✅
- `test_incompatible_type_logical_combinations`：測試觸發警告的無效組合：
  - `numeric` + `email`, `url`, `uuid`, `ip_address` ❌
  - `string` + `percentage`, `currency`, `latitude`, `longitude` ❌
- `test_logical_type_fallback_on_conflict`：測試型態衝突時自動回退到推斷
- `test_logical_type_priority_handling`：測試優先級系統（資料型態約束 > 邏輯型態提示）

**邏輯型態配置測試：**
- `test_logical_type_never_mode`：測試使用 "never" 設定停用邏輯型態推斷
- `test_logical_type_infer_mode`：測試使用 "infer" 設定的自動推斷
- `test_logical_type_explicit_specification`：測試透過配置強制指定特定邏輯型態與相容性驗證
- `test_logical_type_validation_thresholds`：測試信心閾值（文字模式 80%，數值範圍 90-95%）

**模式匹配和驗證測試：**
- `test_regex_pattern_validation`：測試更新的電子郵件、網址、UUID、IP 位址檢測正則表達式模式
- `test_numeric_range_validation`：測試緯度、經度、百分比值的範圍驗證
- `test_special_validator_functions`：測試地理座標的自定義驗證函數
- `test_pattern_confidence_scoring`：測試信心評分和基於閾值的分類
- `test_primary_key_duplicate_detection`：測試主鍵驗證的重複檢測機制

**錯誤處理和衝突解決測試：**
- `test_compatibility_warning_generation`：測試不相容 type/logical_type 組合的警告產生
- `test_automatic_fallback_mechanism`：測試衝突發生時的自動回退機制
- `test_logging_incompatibility_messages`：測試不相容原因的詳細記錄

> **重新設計的邏輯型態系統**：我們的專有邏輯型態推斷系統已重新設計，專注於語意意義檢測而不與基本資料型態重疊。系統使用模式識別、統計分析和驗證函數，具有嚴格的型態相容性規則和完整的衝突解決機制。

#### Schema 參數測試

測試 schema 參數系統的全面功能：

**全域參數測試（`TestSchemaGlobalParameters`）：**
- `test_compute_stats_parameter`：測試 `compute_stats` 全域參數的布林值驗證
- `test_optimize_dtypes_parameter`：測試 `optimize_dtypes` 全域參數的布林值驗證
- `test_sample_size_parameter`：測試 `sample_size` 全域參數的正整數驗證
- `test_sample_size_null`：測試 `sample_size` 參數接受 null 值
- `test_leading_zeros_parameter`：測試 `leading_zeros` 全域參數的有效值（"never", "num-auto", "leading_n"）
- `test_leading_zeros_invalid`：測試 `leading_zeros` 參數的無效值處理
- `test_nullable_int_parameter`：測試 `nullable_int` 全域參數的布林值驗證
- `test_nullable_int_invalid`：測試 `nullable_int` 參數的無效值處理
- `test_infer_logical_types_parameter`：測試 `infer_logical_types` 全域參數的布林值驗證
- `test_descriptive_parameters`：測試描述性參數（`title`, `description`, `version`）的字串驗證

**欄位參數測試（`TestSchemaFieldParameters`）：**
- `test_logical_type_parameter`：測試欄位層級 `logical_type` 參數的有效值驗證
- `test_leading_zeros_field_level`：測試欄位層級 `leading_zeros` 參數覆蓋全域設定
- `test_leading_zeros_field_invalid`：測試欄位層級 `leading_zeros` 參數的無效值處理

**參數衝突測試（`TestSchemaParameterConflicts`）：**
- `test_infer_logical_types_conflict`：測試 `infer_logical_types=true` 與欄位層級 `logical_type` 的衝突檢測

**Loader Schema 參數測試（`tests/loader/test_loader.py`）：**
- `TestLoaderSchemaParameters`：測試 Loader 中全域 schema 參數
- `TestLoaderSchemaFieldParameters`：測試 Loader 中欄位層級 schema 參數
- `TestLoaderSchemaParameterConflicts`：測試 Loader 中參數衝突檢測
- `TestLoaderSchemaEdgeCases`：測試 Loader 中 schema 邊界情況

**SchemaConfig 驗證測試（`tests/metadater/test_schema_types.py`）：**
- `test_schema_config_with_parameters`：測試 SchemaConfig 使用參數的初始化
- `test_schema_config_invalid_leading_zeros`：測試 SchemaConfig 無效 `leading_zeros` 值的錯誤處理
- `test_schema_config_invalid_nullable_int`：測試 SchemaConfig 無效 `nullable_int` 值的錯誤處理
- `test_schema_config_logical_type_conflict`：測試 SchemaConfig 中邏輯類型衝突的檢測

**FieldConfig 驗證測試（`tests/metadater/field/test_field_types.py`）：**
- `test_field_config_with_parameters`：測試 FieldConfig 使用參數的初始化
- `test_field_config_invalid_logical_type`：測試 FieldConfig 無效 `logical_type` 值的錯誤處理
- `test_field_config_invalid_leading_zeros`：測試 FieldConfig 無效 `leading_zeros` 值的錯誤處理
- `test_field_config_invalid_category_method`：測試 FieldConfig 無效 `category_method` 值的錯誤處理
- `test_field_config_invalid_datetime_precision`：測試 FieldConfig 無效 `datetime_precision` 值的錯誤處理

**邊界情況測試（`TestEdgeCases`）：**
- `test_empty_schema`：測試空 schema 的處理
- `test_schema_with_only_global_params`：測試僅含全域參數的 schema
- `test_invalid_global_parameter`：測試無效全域參數的錯誤處理
- `test_invalid_field_parameter`：測試無效欄位參數的錯誤處理
- `test_mixed_legacy_and_schema`：測試混合舊版和 schema 語法的相容性

**主要特色：**
- **兩層架構驗證**：測試全域參數與欄位參數的分層結構
- **參數衝突檢測**：自動檢測並報告邏輯衝突（如 `infer_logical_types` 與欄位 `logical_type`）
- **向後相容性**：確保參數系統與舊版 schema 語法完全相容
- **全面驗證**：涵蓋參數值範圍、型別、邏輯一致性檢查
- **邊界情況覆蓋**：測試空 schema、混合語法、無效參數組合等極端情況

> **Schema 參數系統**：實現了基於兩層架構的 schema 參數系統，提供全域參數（如 `compute_stats`, `optimize_dtypes`, `sample_size`）和欄位層級參數（如 `logical_type`, `leading_zeros`）的靈活配置，同時具備完整的參數衝突檢測和向後相容性保證。

#### 容易誤判資料類型處理功能

測試處理容易誤判、型別判斷模糊的資料：

- `test_preserve_raw_data_feature`：測試 preserve_raw_data 功能阻止 pandas 自動類型推斷：
  - 驗證當 preserve_raw_data=True 時使用 dtype=object
  - 測試與其他容易誤判資料處理功能的整合
  - 驗證原始資料保留的資料載入流程
- `test_leading_zero_detection_config`：測試 auto_detect_leading_zeros 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_nullable_integer_config`：測試 force_nullable_integers 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_ambiguous_data_config_combination`：測試所有容易誤判資料處理配置的組合：
  - preserve_raw_data + auto_detect_leading_zeros + force_nullable_integers
  - 驗證所有設定能正確協同運作
- `test_backward_compatibility`：測試新功能不會破壞現有功能：
  - 驗證新參數的預設值
  - 測試功能停用時的正常載入行為

#### 壓力測試

測試大型檔案處理和邊緣情況型別推斷：

**TestLoaderStress** - 逐步檔案大小測試，包含超時機制：
- `test_small_file_100mb`：測試 100MB 檔案（30秒超時）
- `test_medium_file_1gb`：測試 1GB 檔案（120秒超時）
- `test_large_file_3gb`：測試 3GB 檔案（300秒超時）  
- `test_xlarge_file_5gb`：測試 5GB 檔案（600秒超時）

**TestLoaderTypeInference** - 邊緣情況型別推斷，99.9% 正常資料，0.1% 例外在最後：
- `test_int_with_string_exception`：測試整數資料含字串例外
- `test_float_with_null_exception`：測試浮點數資料含空值例外
- `test_string_with_numeric_exception`：測試字串資料含數值例外

**主要特色：**
- **記憶體監控**：使用 psutil 進行即時記憶體使用追蹤
- **超時保護**：載入超過時間限制時自動測試失敗
- **型別推斷驗證**：確保 99.9% 正常資料，0.1% 例外放置在檔案末尾
- **效能指標**：處理速度測量（MB/秒）和記憶體效率追蹤

**使用方式：**
```bash
# 執行所有壓力測試
pytest tests/loader/ -m stress -v

# 執行特定壓力測試類別
pytest tests/loader/test_loader.py::TestLoaderStress -v
pytest tests/loader/test_loader.py::TestLoaderTypeInference -v

# 執行壓力測試示範
python -c "from tests.loader.test_loader import run_stress_demo; run_stress_demo()"
```

### `Benchmarker`

> tests/loader/test_benchmarker.py

測試基準資料集處理與錯誤處理：

#### 基礎功能測試

- `test_basebenchmarker_init`：驗證 BaseBenchmarker 作為抽象類別無法被實例化
- `test_benchmarker_requests_init`：使用模擬的檔案系統操作測試 BenchmarkerRequests 初始化
- `test_download_success`：測試成功下載的情境，包含：
  - 模擬 HTTP 請求
  - 模擬檔案操作
  - SHA256 驗證記錄
- `test_download_request_fails`：測試下載請求失敗（HTTP 404 等）的處理方式
- `test_file_already_exists_hash_match`：測試檔案已存在且哈希值匹配的情境，確認直接使用本地檔案
- `test_init_file_exists_hash_match`：測試初始化時檔案存在且哈希值匹配的處理邏輯

#### SHA-256 驗證測試（更新於 2025/9）

- `test_verify_file_mismatch_logs_warning`：測試 SHA256 驗證失敗時記錄警告而非拋出錯誤：
  - 驗證警告訊息包含預期和實際的 SHA-256 值
  - 確認程式繼續執行而不中斷
- `test_verify_file_match`：測試 SHA256 驗證成功時的記錄訊息
- `test_file_content_change`：測試檔案內容變更後的哈希驗證機制：
  - 正確檢測變更並記錄警告
  - 允許使用修改後的本地檔案

#### LoaderAdapter 整合測試

- `test_loaderadapter_benchmark_download_success`：測試 LoaderAdapter 成功下載 benchmark 檔案
- `test_loaderadapter_benchmark_download_failure`：測試 LoaderAdapter 處理 benchmark 下載失敗：
  - 驗證錯誤訊息包含詳細的失敗原因
  - 確認拋出 BenchmarkDatasetsError
- `test_loaderadapter_schema_benchmark_download_failure`：測試 LoaderAdapter 處理 schema benchmark 下載失敗
- `test_loaderadapter_benchmark_protocol_case_insensitive`：測試 benchmark:// 協議大小寫不敏感
- `test_loaderadapter_unsupported_benchmark`：測試不支援的 benchmark 資料集錯誤處理
- `test_loaderadapter_sha256_mismatch_warning`：測試 SHA-256 不匹配時的警告處理：
  - 確認程式繼續執行
  - 驗證警告訊息正確記錄

> **重要更新**：從 2025 年 9 月起，SHA-256 驗證失敗改為記錄警告而非拋出錯誤，允許開發者使用修改過的本地 benchmark 檔案進行測試。這個改變提升了開發體驗，同時仍保留完整性檢查的資訊記錄。

#### `BenchmarkerConfig`

> tests/loader/test_loader.py::TestBenchmarkerConfig

測試管理基準資料集配置的 BenchmarkerConfig 類別：

- `test_benchmarker_config_requires_benchmark_name`：測試初始化時需要 benchmark_name 參數
- `test_benchmarker_config_initialization`：測試 BenchmarkerConfig 初始化與正確的屬性設定：
  - 基準名稱、檔案名稱、存取類型
  - 區域名稱、儲存桶名稱、SHA256 雜湊值
  - 與基準 YAML 配置載入的整合
- `test_benchmarker_config_get_benchmarker_config`：測試 get_benchmarker_config 方法：
  - 為 BenchmarkerRequests 返回正確的字典格式
  - 包含所有必要的鍵值（benchmark_filename、benchmark_bucket_name、benchmark_sha256、filepath）
  - 構建正確的本地基準檔案路徑
- `test_benchmarker_config_unsupported_benchmark`：測試不支援的基準資料集的錯誤處理
- `test_benchmarker_config_private_access_unsupported`：測試私有基準存取嘗試的錯誤處理

> **架構重構**：BenchmarkerConfig 已從 LoaderConfig 中提取出來，提供清晰的關注點分離。LoaderConfig 現在包含一個可選的 benchmarker_config 屬性，允許兩種不同的狀態：有或沒有基準功能。這種重構提高了程式碼的可維護性，並遵循單一職責原則。

## 資料處理

### `Processor`

#### 缺失值處理器

> tests/processor/test_missing.py

測試缺失值處理的全面類型相容性：

**MissingMean 測試（4 個測試）：**
- `test_mean_no_missing_values`：測試無缺失值的平均值填補
- `test_mean_with_missing_values`：測試有缺失值的平均值填補
- `test_mean_with_integer_dtype`：測試 pandas 可空整數類型（Int32、Int64）的平均值填補：
  - 驗證整數資料類型的正確處理，不會出現 TypeError
  - 測試平均值的自動四捨五入以符合整數相容性
  - 驗證轉換後的資料類型保持
- `test_mean_with_integer_dtype_fractional_mean`：測試平均值有小數部分時的填補：
  - 測試整數類型的銀行家舍入法（20.5 → 20）
  - 確保小數平均值的正確類型轉換

**MissingMedian 測試（4 個測試）：**
- `test_median_no_missing_values`：測試無缺失值的中位數填補
- `test_median_with_missing_values`：測試有缺失值的中位數填補
- `test_median_with_integer_dtype`：測試 pandas 可空整數類型（Int32、Int64）的中位數填補：
  - 驗證整數資料類型的正確處理，不會出現 TypeError
  - 測試中位數的自動四捨五入以符合整數相容性
  - 驗證轉換後的資料類型保持
- `test_median_with_integer_dtype_fractional_median`：測試中位數有小數部分時的填補：
  - 測試整數類型的銀行家舍入法（20.5 → 20）
  - 確保小數中位數的正確類型轉換

**MissingSimple 測試（2 個測試）：**
- `test_simple_no_missing_values`：測試無缺失值的簡單值填補
- `test_simple_with_missing_values`：測試有缺失值的簡單值填補

**MissingDrop 測試（2 個測試）：**
- `test_drop_no_missing_values`：測試無缺失值的刪除策略
- `test_drop_with_missing_values`：測試有缺失值的刪除策略

> **整數類型相容性**：增強的缺失值處理器現在正確支援 pandas 可空整數類型（Int8、Int16、Int32、Int64），透過自動將浮點填補值四捨五入為整數，防止 fillna 操作期間的 TypeError。這確保與 schema 指定的整數類型無縫整合，同時維持資料完整性。

#### 異常值檢測處理器

增強異常值檢測，具有 pandas 可空整數陣列相容性：

**OutlierHandler 基礎類別：**
- 增強 `fit()` 和 `transform()` 方法，使用 `np.asarray()` 轉換
- 正確處理 pandas 可空整數陣列，防止廣播錯誤
- 維持與異常值檢測演算法中 numpy 操作的相容性

> **Pandas 陣列相容性**：異常值處理器現在使用 `np.asarray()` 而非 `.values`，確保 pandas 可空整數陣列正確轉換為 numpy 陣列，防止異常值檢測演算法中邏輯操作期間的 ValueError。

### `Metadater`

> tests/metadater/test_metadater.py

測試 Metadater 三層架構的完整功能（700+ 行測試）：

#### 三層架構測試

**Metadata 層測試：**
- `test_metadata_from_data`：測試從資料建立 Metadata
- `test_metadata_from_metadata`：測試從配置建立 Metadata
- `test_metadata_get`：測試取得 Schema 物件
- `test_metadata_add`：測試新增 Schema
- `test_metadata_update`：測試更新 Schema
- `test_metadata_remove`：測試移除 Schema
- `test_metadata_diff`：測試 Metadata 層級差異比較
- `test_metadata_align`：測試 Metadata 層級資料對齊

**Schema 層測試：**
- `test_schema_from_data`：測試從 DataFrame 建立 Schema
- `test_schema_from_metadata`：測試從配置建立 Schema
- `test_schema_get`：測試取得 Attribute 物件
- `test_schema_add`：測試新增 Attribute
- `test_schema_update`：測試更新 Attribute
- `test_schema_remove`：測試移除 Attribute
- `test_schema_diff`：測試 Schema 層級差異比較
- `test_schema_align`：測試 Schema 層級資料對齊

**Attribute 層測試：**
- `test_attribute_from_data`：測試從 Series 建立 Attribute
- `test_attribute_from_metadata`：測試從配置建立 Attribute
- `test_attribute_diff`：測試 Attribute 層級差異比較
- `test_attribute_align`：測試 Attribute 層級資料對齊

#### 統計功能測試

- `test_metadater_with_stats`：測試啟用統計的 Metadater 功能
- `test_schema_metadater_with_stats`：測試 Schema 層級統計計算
- `test_attribute_metadater_with_stats`：測試 Attribute 層級統計計算
- `test_stats_calculation_accuracy`：測試統計計算準確性：
  - 均值、中位數、標準差
  - 唯一值計數、空值計數
  - 最小值、最大值、四分位數

#### YAML 相容性測試

- `test_yaml_fields_compatibility`：測試 YAML 中 'fields' 到內部 'attributes' 的對應
- `test_schema_to_dict_with_fields`：測試 Schema 輸出為字典時使用 'fields' 鍵名
- `test_metadater_yaml_roundtrip`：測試 YAML 配置的完整往返：
  - 從 YAML 載入
  - 處理和修改
  - 輸出回 YAML 格式

#### 進階功能測試

- `test_multi_table_operations`：測試多表格操作：
  - 同時處理多個表格
  - 跨表格的差異比較
  - 批次對齊操作
- `test_nested_diff_operations`：測試嵌套差異操作：
  - Metadata 層級調用 Schema.diff()
  - Schema 層級調用 Attribute.diff()
  - 差異結果的層級標示
- `test_strategy_based_align`：測試策略導向的對齊：
  - 自動 diff 模式
  - 指定策略模式
  - 自定義對齊規則

#### 邊界情況測試

- `test_empty_data_handling`：測試空資料處理
- `test_missing_table_handling`：測試缺失表格處理
- `test_invalid_configuration`：測試無效配置的錯誤處理
- `test_type_mismatch_handling`：測試型別不匹配處理

#### 效能測試

- `test_large_dataset_performance`：測試大型資料集效能
- `test_memory_efficiency`：測試記憶體使用效率
- `test_concurrent_operations`：測試並行操作安全性

> **架構重構說明**：Metadater 測試已完全重構，整合了原有的 test_metadater_v2.py 和 test_metadater_functional.py，形成單一全面的測試套件。新測試涵蓋三層架構（Metadata → Schema → Attribute）的所有功能，包含統計計算、差異比較、資料對齊、YAML 相容性等完整功能。

## 資料評測

### `Describer` (2025年10月更新)

#### `DescriberDescribe`

> tests/describer/test_describer_describe.py

測試 **DescriberDescribe 統計描述功能** 的全面實現（19 個測試）：

**初始化測試 (4 個測試):**
- `test_initialization`: 測試 DescriberDescribe 初始化與配置驗證
- `test_initialization_invalid_stats_method`: 測試無效統計方法的錯誤處理
- `test_initialization_invalid_granularity`: 測試無效粒度參數的錯誤處理
- `test_initialization_with_all_parameters`: 測試完整參數配置的初始化

**統計方法測試 (4 個測試):**
- `test_basic_stats`: 測試基本統計方法（mean, median, std）的計算
- `test_percentile_stats`: 測試百分位數統計（p25, p50, p75）的計算
- `test_na_stats`: 測試 NA 值統計（na_count, na_rate）的計算
- `test_cardinality_stats`: 測試基數統計（distinct, count）的計算

**粒度測試 (2 個測試):**
- `test_global_granularity`: 測試全域粒度統計輸出格式與結構
- `test_columnwise_granularity`: 測試欄位粒度統計的詳細輸出

**邊界情況測試 (6 個測試):**
- `test_empty_dataframe`: 測試空 DataFrame 的處理
- `test_single_row_dataframe`: 測試單行 DataFrame 的統計計算
- `test_all_na_column`: 測試全 NA 欄位的統計處理
- `test_extreme_values`: 測試極端值的統計準確性
- `test_high_cardinality`: 測試高基數資料的效能
- `test_percentile_with_insufficient_data`: 測試資料不足時的百分位數計算

**資料類型測試 (3 個測試):**
- `test_numeric_types`: 測試數值型資料（int, float）的統計
- `test_categorical_types`: 測試類別型資料的統計處理
- `test_mixed_types`: 測試混合資料類型的處理

> **測試特色**：此測試套件涵蓋 DescriberDescribe 的完整功能，包括多種統計方法、不同粒度的輸出、各種邊界情況，以及對不同資料類型的支援。測試確保統計計算的準確性和穩健性。

#### `DescriberCompare`

> tests/describer/test_describer_compare.py

測試 **重構後的 DescriberCompare** 實現（6 個測試，1 個跳過）：

#### DescriberCompare 重構測試

**核心功能測試：**
- `test_js_divergence_type_validation`：測試 JS Divergence 資料類型驗證
  - 驗證數值型和類別型資料都能正確計算 JS Divergence
  - 確認類型檢查已正確擴展以接受所有有效資料類型
  
- `test_describer_compare_initialization`：測試 DescriberCompare 初始化
  - 驗證內部創建 ori_describer 和 syn_describer 實例
  - 確認兩個 DescriberDescribe 實例都被正確配置
  - 測試 jsdivergence 從統計方法中正確過濾（僅用於比較）

- `test_na_value_handling`：測試 NA 值處理（已修復）
  - 測試包含 pandas.NA 值的資料處理
  - 驗證欄位名稱從 `ori`/`syn` 改為 `base`/`target`
  - 確認 FutureWarning 已通過適當的 pandas 選項修復

**重構架構測試：**
- `test_code_reuse`：驗證 DescriberCompare 重用 DescriberDescribe
  - 確認 DescriberCompare 內部使用 DescriberDescribe 實例
  - 測試統計計算委派給 DescriberDescribe
  - 驗證代碼重用而非重複實現

- `test_separation_of_concerns`：測試關注點分離
  - DescriberDescribe 負責統計計算（`_eval` 方法）
  - DescriberCompare 負責比較邏輯（`_apply_comparison`、`_calculate_jsdivergence`）
  - 比較方法映射（`COMPARE_METHOD_MAP`）正確實現

**整合測試（跳過）：**
- `test_full_yaml_execution`：完整 YAML 執行測試（標記為 integration，需要完整環境）

> **架構改進（2025年10月）**：DescriberCompare 已完全重構以重用 DescriberDescribe 的功能，遵循「compare 是 describe 的擴展」原則。這消除了代碼重複，提高了可維護性，並確保統計計算的一致性。參數命名也從 `ori`/`syn` 改為 `base`/`target` 以提供更好的語意清晰度。

### `Evaluator`

### `Constrainer`

> tests/constrainer/test_constrainer.py

測試主要的 Constrainer 工廠類別功能（18 個測試）：

- `test_basic_initialization`：測試基本 constrainer 初始化和配置儲存
- `test_nan_groups_constraints`：測試 NaN 群組約束：
  - Delete 動作實現
  - Erase 動作含多個目標
  - Copy 動作含類型檢查
- `test_field_constraints`：測試欄位層級約束：
  - 數值範圍條件
  - 多條件組合
- `test_field_combinations`：測試欄位組合規則：
  - 教育-績效對應
  - 多值組合
- `test_all_constraints_together`：測試所有約束協同運作：
  - 約束互動
  - 複雜過濾場景
- `test_resample_functionality`：測試重新採樣直到滿足：
  - 目標行數達成
  - 合成資料生成
  - 約束滿足
- `test_error_handling`：測試錯誤情況：
  - 無效配置格式
  - 缺失欄位
- `test_edge_cases`：測試邊界條件：
  - 空 DataFrame
  - 所有 NaN 值
- `test_empty_config`：測試空配置的 constrainer
- `test_unknown_constraint_type_warning`：測試未知約束類型的警告
- `test_resample_trails_attribute`：測試重新採樣追蹤功能
- `test_register_custom_constraint`：測試自定義約束註冊
- `test_register_invalid_constraint_class`：測試無效約束類別的錯誤處理

**欄位比例整合測試（5 個測試）：**
- `test_field_proportions_integration`：測試欄位比例 constrainer 與新架構的整合：
  - 含更新配置格式的單一欄位比例
  - 缺失值比例維護
  - 欄位組合比例處理
- `test_field_proportions_with_other_constraints`：測試欄位比例與其他約束類型協同運作：
  - 結合欄位比例和欄位約束
  - 多約束互動驗證
- `test_field_proportions_comprehensive_integration`：測試基於真實場景的全面欄位比例整合：
  - 教育、收入和工作類別資料分佈維護
  - 多種約束模式（all、missing、field combinations）
  - 含 `target_rows` 參數的新架構驗證
- `test_field_proportions_multiple_modes`：測試含多種約束模式的欄位比例：
  - 類別比例（'all' 模式）
  - 缺失值比例（'missing' 模式）
  - 區域比例驗證
- `test_field_proportions_edge_cases_integration`：測試欄位比例邊界情況：
  - 小型資料集處理
  - 目標行數大於可用資料
  - 空欄位比例列表處理

#### `NaNGroupConstrainer`

> tests/constrainer/test_nan_group_constrainer.py

測試 NaN 值處理約束（18 個測試）：

- `test_invalid_config_initialization`：測試無效配置處理：
  - 非字典輸入
  - 無效動作類型
  - 無效目標規格
  - Delete 動作與其他動作組合
- `test_valid_config_initialization`：測試有效配置：
  - 獨立 Delete 動作
  - Erase 動作的多個目標
  - Copy 動作的單一目標
  - 不同目標格式
- `test_erase_action`：測試 erase 動作功能：
  - 當來源欄位為 NaN 時將目標欄位設為 NaN
  - 處理多個目標欄位
- `test_copy_action_compatible_types`：測試相容類型之間的值複製
- `test_copy_action_incompatible_types`：測試不相容類型複製的處理
- `test_multiple_constraints`：測試多個約束協同運作
- `test_delete_action_edge_case`：測試含邊界情況的 delete 動作
- `test_erase_action_multiple_targets`：測試含多個目標欄位的 erase 動作
- `test_copy_action_type_validation`：測試含類型驗證的 copy 動作
- `test_invalid_action_type`：測試無效動作類型的處理
- `test_invalid_target_specification`：測試無效目標欄位規格
- `test_empty_config_handling`：測試空配置處理
- `test_mixed_action_validation`：測試混合動作配置的驗證

#### `FieldConstrainer`

> tests/constrainer/test_field_constrainer.py

測試欄位層級約束（14 個測試）：

- `test_invalid_config_structure`：測試配置驗證：
  - 非列表輸入
  - 無效約束格式
  - 空約束
- `test_invalid_constraint_syntax`：測試語法驗證：
  - 不匹配的括號
  - 無效運算符
  - 缺少運算符
- `test_field_extraction`：測試欄位名稱提取：
  - 加法運算
  - 括號表達式
  - NULL 檢查
  - 日期運算
- `test_string_literals_with_operators`：測試包含運算符的字串字面值提取和驗證：
  - 驗證像 `'<=50K'` 或 `'>50K'` 這類字串被正確處理為字面值
  - 測試修正後的 issue：字串內的運算符曾被錯誤解析為比較運算符
  - 確保 `_extract_fields()` 方法在提取欄位名之前先移除引號內的字串
- `test_apply_string_literals_with_operators`：測試套用包含運算符的字串字面值約束：
  - 驗證像 `"income == '<=50K'"` 這類約束能正確運作
  - 測試實際資料過濾功能與字串字面值的正確匹配
- `test_complex_expression_validation`：測試複雜約束組合
- `test_empty_constraint_list`：測試空約束列表處理
- `test_null_check_operations`：測試 NULL 值檢查運算
- `test_date_operation_constraints`：測試基於日期的約束運算
- `test_parentheses_validation`：測試括號匹配驗證
- `test_operator_validation`：測試運算符語法驗證

> **字串字面值處理修正（2025年10月）**：`FieldConstrainer` 的 `_extract_fields()` 方法已修正，能正確處理包含運算符的字串字面值（如 `'<=50K'`、`'>50K'`）。修正前，這些字串內的運算符會被錯誤地解析為比較運算符，導致 `50K` 被誤認為欄位名。現在方法會在提取欄位名之前先移除所有單引號和雙引號內的內容，確保字串字面值被正確識別。

#### `