#!/bin/bash
# 測試 benchmark:// 協定修復的命令列指令

echo "=========================================="
echo "測試 Benchmark Schema 載入修復"
echo "=========================================="

# 1. 測試所有 loader 和 benchmarker 相關的測試
echo ""
echo "1. 執行 Loader 和 Benchmarker 測試："
echo "----------------------------------------"
echo "pytest tests/loader/test_loader.py::TestBenchmarkerConfig -v"
echo "pytest tests/loader/test_benchmarker.py -v"

# 2. 測試 LoaderAdapter (包含 benchmark 處理)
echo ""
echo "2. 執行 LoaderAdapter 測試："
echo "----------------------------------------"
echo "pytest tests/ -k 'LoaderAdapter' -v"

# 3. 測試特定的 benchmark 相關測試
echo ""
echo "3. 執行所有 benchmark 相關測試："
echo "----------------------------------------"
echo "pytest tests/ -k 'benchmark' -v"

# 4. 執行單一測試方法
echo ""
echo "4. 執行特定測試方法："
echo "----------------------------------------"
echo "pytest tests/loader/test_loader.py::TestBenchmarkerConfig::test_benchmarker_config_initialization -v"

# 5. 使用詳細輸出和顯示 print 語句
echo ""
echo "5. 執行並顯示詳細輸出："
echo "----------------------------------------"
echo "pytest tests/loader/test_benchmarker.py -v -s"

# 6. 執行並產生覆蓋率報告
echo ""
echo "6. 執行並產生覆蓋率報告："
echo "----------------------------------------"
echo "pytest tests/loader/ --cov=petsard.loader --cov=petsard.adapter --cov-report=term-missing"

# 7. 執行快速測試（排除壓力測試）
echo ""
echo "7. 執行快速測試（排除壓力測試）："
echo "----------------------------------------"
echo "pytest tests/loader/ -m 'not stress' -v"

# 8. 只執行失敗的測試（如果有的話）
echo ""
echo "8. 只重新執行上次失敗的測試："
echo "----------------------------------------"
echo "pytest --lf -v"

# 9. 執行並在第一個失敗時停止
echo ""
echo "9. 在第一個失敗時停止："
echo "----------------------------------------"
echo "pytest tests/loader/ -x -v"

# 10. 平行執行測試（需要 pytest-xdist）
echo ""
echo "10. 平行執行測試（加速）："
echo "----------------------------------------"
echo "pytest tests/loader/ -n auto -v"

echo ""
echo "=========================================="
echo "建議的測試命令："
echo "=========================================="
echo ""
echo "# 快速測試 benchmark 功能："
echo "pytest tests/loader/test_benchmarker.py tests/loader/test_loader.py::TestBenchmarkerConfig -v"
echo ""
echo "# 完整測試 loader 和 adapter："
echo "pytest tests/loader/ tests/ -k 'LoaderAdapter or benchmark' -v --tb=short"
echo ""
echo "# 測試並查看輸出："
echo "pytest tests/loader/test_benchmarker.py -v -s --tb=short"