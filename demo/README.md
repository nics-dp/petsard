# PETsARD Demo Collection / PETsARD 示例集

Welcome to the PETsARD Demo Collection! This directory contains various practical Jupyter Notebook examples to help you quickly get started with PETsARD's features.

歡迎使用 PETsARD 示例集！這個目錄包含了各種實用的 Jupyter Notebook 示例，幫助您快速上手 PETsARD 的各項功能。

## 📚 Complete Documentation / 完整文件

For detailed API documentation, tutorials, and best practices, please refer to:

如需詳細的 API 文件、教學指南和最佳實務，請參考：

- **📖 [PETsARD Documentation / 文件網站](https://nics-tw.github.io/petsard/)**

## 🗂️ Demo Categories / Demo 分類

### 📚 tutorial/ - Getting Started / 入門教學

**Basic synthesis and evaluation workflows / 基礎合成與評估工作流程**
**use-cases/ - Common Use Cases / 常見使用案例**
**use-cases/data-preprocessing/ - Data Preprocessing / 資料預處理**

### 🏆 best-practices/ - Best Practices / 最佳實踐

**Advanced scenarios and optimizations / 進階場景與優化**

### 🔧 developer-guide/ - Developer Guide / 開發者指南

**Advanced development features / 進階開發功能**

### 📝 petsard-yaml/ - YAML Examples / YAML 範例

**Configuration examples / 設定範例**

## 🚀 Quick Start / 快速開始

### Using in Jupyter Notebook / 在 Jupyter Notebook 中使用

Copy the following code to the beginning of your notebook:

複製以下程式碼到您的 notebook 開頭：

```python
import os, sys
from pathlib import Path

# Load demo_utils and import quick_setup / 載入 demo_utils 並導入 quick_setup
if "COLAB_GPU" in os.environ:
    import urllib.request
    demo_utils_url = "https://raw.githubusercontent.com/nics-tw/petsard/main/demo/demo_utils.py"
    exec(urllib.request.urlopen(demo_utils_url).read().decode('utf-8'))
else:
    # Local: search upward for demo_utils.py / 本地：向上搜尋 demo_utils.py
    for p in [Path.cwd()] + list(Path.cwd().parents)[:10]:
        utils_path = p / "demo_utils.py"
        if utils_path.exists() and "demo" in str(utils_path):
            sys.path.insert(0, str(p))
            exec(open(utils_path).read())
            break

# Use quick_setup / 使用 quick_setup
from demo_utils import quick_setup

is_colab, branch, yaml_path = quick_setup(
    yaml_file="base_loading.yaml",      # YAML configuration file / YAML 設定檔
    benchmark_data=["adult-income"],    # Optional: benchmark datasets / 可選：基準資料集
    petsard_branch="main",              # Optional: specific branch / 可選：指定分支
)
```

### Key Features / 主要特色

**`quick_setup()`** provides one-stop environment configuration for PETsARD notebooks. It automatically detects whether you're running in Google Colab or locally, installs necessary packages, loads benchmark datasets if needed, and locates YAML configuration files intelligently even when notebooks are in subdirectories. The function returns environment information and paths to your YAML files for immediate use.

提供 PETsARD notebook 的一站式環境設定。自動偵測 Google Colab 或本地環境、安裝必要套件、載入基準資料集，並智慧定位 YAML 設定檔案（即使 notebook 在子目錄中）。函數回傳環境資訊和 YAML 檔案路徑供立即使用。

**`display_yaml_info()`** formats and displays YAML configuration files in a clean, readable format. It accepts single or multiple YAML paths and can optionally show or hide the file contents. This function helps you verify your configuration files are correctly loaded and review their settings.

以清晰易讀的格式顯示 YAML 設定檔案。接受單個或多個 YAML 路徑，可選擇顯示或隱藏檔案內容。此函數協助驗證設定檔案是否正確載入並檢視其設定。

**`display_results()`** elegantly formats execution results from PETsARD operations. When displaying DataFrames, it automatically shows only the first few rows to prevent overwhelming output while providing dataset dimensions and column information. The function intelligently handles various data types including dictionaries, lists, and strings, making result inspection clear and concise.

優雅地格式化 PETsARD 操作的執行結果。顯示 DataFrame 時自動只顯示前幾行以避免過長輸出，同時提供資料集維度和欄位資訊。函數智慧處理各種資料類型，讓結果檢視清晰簡潔。

## 🔗 Related Links / 相關連結

- **Documentation / 文件網站**: [https://nics-tw.github.io/petsard/](https://nics-tw.github.io/petsard/)
- **GitHub Repository**: [https://github.com/nics-tw/petsard](https://github.com/nics-tw/petsard)
- **API Reference / API 文件**: [API Documentation](https://nics-tw.github.io/petsard/docs/api/)
- **Tutorials / 教學文件**: [Tutorial Documentation](https://nics-tw.github.io/petsard/docs/tutorial/)

## 📝 Contributing / 貢獻

If you have new examples to share or find any issues, feel free to submit an Issue or Pull Request!

如果您有新的示例想要分享，或發現任何問題，歡迎提交 Issue 或 Pull Request！

---

**Note / 注意**: These examples are for learning and testing purposes only. Please read the relevant documentation thoroughly and test adequately before using in production environments.

這些示例僅供學習和測試使用。在生產環境中使用前，請詳細閱讀相關文件並進行充分測試。
