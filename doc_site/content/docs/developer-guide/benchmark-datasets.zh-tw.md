---
title: 基準資料集維護
type: docs
weight: 82
prev: docs/developer-guide/development-guidelines
next: docs/developer-guide/anonymeter
---

本文件說明如何維護 PETsARD 的基準資料集。

## 儲存位置

所有基準資料集儲存於：
- **服務**：AWS S3
- **組織**：NICS-RA（國家資通安全研究院）
- **儲存桶**：`petsard-benchmark`

## 檔案校驗

### SHA-256 校驗碼（僅供參考）

每個資料集都有 SHA-256 校驗碼用於檔案完整性驗證：

```python
from petsard.loader.benchmarker import digest_sha256

hasher = digest_sha256(filepath)
hash_value = hasher.hexdigest()
```

系統會驗證 SHA-256 雜湊值的前七個字元。如果驗證失敗，會拋出錯誤。

## 維護流程

### 新增資料集

1. 上傳資料集檔案到 S3 儲存桶
2. 計算並記錄 SHA-256 校驗碼
3. 更新 `petsard/loader/benchmark_datasets.yaml`，包含：
   - 資料集名稱
   - 檔案名稱
   - SHA-256 雜湊值（前 7 個字元）

### 更新現有資料集

1. 替換 S3 中的檔案
2. 重新計算 SHA-256 校驗碼
3. 更新 `benchmark_datasets.yaml` 中的雜湊值

## 設定檔

`benchmark_datasets.yaml` 檔案包含資料集登錄及用於驗證的 SHA-256 校驗碼。