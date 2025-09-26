---
title: "benchmark://"
weight: 112
---

Loader 支援使用 `benchmark://` 協議自動下載並載入基準資料集。

## 協議格式

```yaml
Loader:
  experiment_name:
    filepath: benchmark://dataset-name
```

## 使用範例

### 載入 Adult Income 資料集

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
```

### 配合 Schema 使用

```yaml
Loader:
  load_with_schema:
    filepath: benchmark://adult-income
    schema: schemas/adult-income.yaml
```

## 可用的基準資料集

### Demographic 資料集

| 資料集名稱 | 協議路徑 | 說明 |
|-----------|---------|------|
| Adult Income | `benchmark://adult-income` | UCI Adult Income 人口普查資料集（48,842 筆，15 欄位） |
| Adult Income (Original) | `benchmark://adult-income_ori` | 原始訓練資料（用於 demo） |
| Adult Income (Control) | `benchmark://adult-income_control` | 控制組資料（用於 demo） |
| Adult Income (Synthetic) | `benchmark://adult-income_syn` | SDV Gaussian Copula 合成資料（用於 demo） |

### Best Practices 範例資料集

| 資料集名稱 | 協議路徑 | 說明 |
|-----------|---------|------|
| Multi-table Companies | `benchmark://best-practices_multi-table_companies` | 多表格範例 - 公司資料 |
| Multi-table Applications | `benchmark://best-practices_multi-table_applications` | 多表格範例 - 申請資料 |
| Multi-table Tracking | `benchmark://best-practices_multi-table_tracking` | 多表格範例 - 追蹤資料 |
| Multi-timestamp | `benchmark://best-practices_multi-table` | 多時間戳範例資料 |
| Categorical & High-cardinality | `benchmark://best-practices_categorical_high-cardinality` | 類別型與高基數範例資料 |

## 完整管線範例

```yaml
---
Loader:
  # 使用基準資料集
  benchmark:
    filepath: benchmark://adult-income
    
Preprocessor:
  preprocess:
    method: default
    
Synthesizer:
  synthesize:
    method: sdv-single-table
    model: gaussian_copula
    
Postprocessor:
  postprocess:
    method: default
    
Evaluator:
  quality_report:
    method: sdmetrics-qualityreport
    
Reporter:
  save_synthetic:
    method: save_data
    output_path: output/synthetic_adult.csv
  save_report:
    method: save_report
    granularity: global
...
```

## 工作原理

1. **協議偵測**：Loader 偵測到 `benchmark://` 協議
2. **自動下載**：從 AWS S3 儲存區下載資料集
3. **驗證檢查**：使用 SHA256 驗證資料完整性
4. **本地快取**：資料儲存在 `benchmark/` 目錄
5. **載入資料**：使用本地路徑載入資料

## 使用時機

基準資料集適合用於：

- **測試新演算法**：在已知特性的資料上測試
- **參數調校**：比較不同參數設定的效果
- **效能基準**：與學術研究結果比較
- **教學示範**：提供標準化的範例資料

## 注意事項

- 首次使用需要網路連線下載資料
- 資料集會快取在本地 `benchmark/` 目錄
- 大型資料集下載可能需要較長時間
- 協議名稱不區分大小寫（但建議使用小寫）
- 所有資料集都經過 SHA256 驗證確保完整性