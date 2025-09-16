# Test Suite / 測試套件

## Overview / 概述

PETsARD test suite ensures code quality and reliability through comprehensive testing.

PETsARD 測試套件透過全面的測試確保程式碼品質與可靠性。

## Test Coverage / 測試涵蓋範圍

```
tests/
├── test_loader/         # Data loading functionality / 資料載入功能
├── test_processor/      # Data preprocessing and transformation / 資料前處理與轉換
├── test_synthesizer/    # Synthetic data generation / 合成資料生成
├── test_evaluator/      # Privacy and quality evaluation / 隱私與品質評估
├── test_reporter/       # Report generation and output / 報告生成與輸出
└── test_petsard.py      # End-to-end workflow tests / 端到端工作流程測試
```

### What We Test / 測試內容

- **Loader**: CSV/Excel file loading, benchmark datasets, data validation
- **Processor**: Encoding, scaling, missing value handling, data constraints
- **Synthesizer**: SDV integration, CTGAN, Gaussian Copula, TVAE models
- **Evaluator**: Privacy metrics (anonymeter), quality metrics (SDMetrics)
- **Reporter**: Data saving, report generation, multiple output formats
- **Integration**: Complete PETsARD workflow from config to output

### Test Markers / 測試標記

- `@pytest.mark.stress`: Resource-intensive tests / 資源密集型測試
- `@pytest.mark.excel`: Tests requiring openpyxl / 需要 openpyxl 的測試

## Quick Start / 快速開始

```bash
# Install development dependencies / 安裝開發依賴
pip install -e ".[dev]"

# Run all tests / 執行所有測試
pytest

# Run with coverage / 執行並查看覆蓋率
pytest --cov=petsard --cov-report=html

# Skip stress tests / 跳過壓力測試
pytest -m "not stress"
```

## CI/CD Integration / CI/CD 整合

**Workflow**: `.github/workflows/test-suite.yml`

- **Trigger**: PRs to `dev` and `main` branches
- **Python Versions**: 3.10, 3.11
- **Checks**: 
  - Ruff code quality / 程式碼品質檢查
  - Unit tests with coverage / 單元測試與覆蓋率
  - Functional tests / 功能測試
- **Reports**: Automated PR comments with test results / 自動在 PR 中回報測試結果

## Contributing / 貢獻指南

When adding new features:
新增功能時：

1. Add corresponding tests in appropriate test directory / 在對應的測試目錄新增測試
2. Ensure tests pass locally before PR / PR 前確保本地測試通過
3. Maintain test coverage above 80% / 維持測試覆蓋率 80% 以上
