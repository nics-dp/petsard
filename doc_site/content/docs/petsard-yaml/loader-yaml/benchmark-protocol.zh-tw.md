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

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/loader-yaml/benchmark-protocol.ipynb)

### 載入基準資料集

```yaml
Loader:
  load_benchmark:
    filepath: benchmark://adult-income
```

### 載入基準資料集與基準資料集詮釋資料

```yaml
Loader:
  load_benchmark_with_schema:
    filepath: benchmark://adult-income
    schema: benchmark://adult-income_schema
```

### 配合本地詮釋資料使用

```yaml
Loader:
  load_with_local_schema:
    filepath: benchmark://adult-income
    schema: benchmark/adult-income_schema.yaml
```

## 可用的基準資料集

### Demographic 資料集

| 資料集名稱 | 協議路徑 | 說明 |
|-----------|---------|------|
| Adult Income | `benchmark://adult-income` | UCI Adult Income 人口普查資料集（48,842 筆，15 欄位） |
| Adult Income Schema | `benchmark://adult-income_schema` | Adult Income 資料集的詮釋資料定義 |
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
