<p align="center"><img width=75% src="https://raw.githubusercontent.com/nics-dp/petsard/main/.github/assets/PETsARD-logo.png"></p>

![Python 3.10](https://img.shields.io/badge/python-v3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-v3.11-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
![PyPI - Status](https://img.shields.io/pypi/status/petsard)

`PETsARD` (Privacy Enhancing Technologies Analysis, Research, and Development, /pəˈtɑrd/) is a Python library for facilitating data generation algorithm and their evaluation processes.

The main functionalities include dataset description, various dataset generation algorithms, and the measurements on privacy protection and utility.

`PETsARD`（隱私強化技術分析、研究與開發）是一套為了促進資料生成演算法及其評估過程而設計的 Python 程式庫。

其主要功能包括描述資料集、執行各種資料集生成算法，以及對隱私保護和效用進行測量。

---

## **✨ Features 主要功能**

- 🔄 **Data Generation 資料生成**: Support for multiple synthetic data generation algorithms including SDV, Faker, and more
  - 支援多種合成資料生成演算法，包括 SDV、Faker 等

- 🔒 **Privacy Evaluation 隱私評估**: Comprehensive privacy risk assessment using anonymeter
  - 使用 anonymeter 進行全面的隱私風險評估

- 📊 **Utility Metrics 效用指標**: Data quality and utility measurements using sdmetrics and custom evaluators
  - 使用 sdmetrics 與自訂評估器進行資料品質與效用測量

- 🎯 **Flexible Configuration 靈活配置**: YAML-based configuration for experiment workflows
  - 基於 YAML 的實驗流程配置

- 📦 **Benchmark Datasets 基準資料集**: Built-in support for loading common benchmark datasets
  - 內建支援載入常見的基準資料集

---

# **📚 Documentation 文件**

## [**🏠 Main Site 主要網站: PETsARD**](https://nics-dp.github.io/petsard/)

Project homepage with overview and foundation information
專案首頁，提供專案概觀與基礎資訊

Website: https://nics-dp.github.io/petsard/

## [**📖 Docs 文件**](https://nics-dp.github.io/petsard/docs/)

The User Guide aims to assist developers in rapidly acquiring the necessary skills for utilising `PETsARD` in data synthesis, evaluating synthesized data, and enhancing the research efficiency in Privacy Enhancing Technologies-related fields.

使用者指南旨在幫助開發者迅速獲得必要的技能，以使用 `PETsARD` 進行資料合成、合成資料的評估，以及提升開發者隱私增強相關領域的研究效率。

### [**📦 Installation 安裝**](https://nics-dp.github.io/petsard/docs/installation/)
- PyPI package installation 從 PyPI 安裝套件
- Docker-based setup Docker 環境建置
- Package pre-download for offline environments 離線環境套件預先下載
- Environment verification 環境檢查

### [**🚀 Getting Started 入門指南**](https://nics-dp.github.io/petsard/docs/getting-started/)
- Default synthesis and evaluation workflow 預設合成與評估流程
- Using external synthetic data 使用外部合成資料

### [**⭐ Best Practices 最佳實踐**](https://nics-dp.github.io/petsard/docs/best-practices/)
- Handling categorical data 處理類別資料
- High-cardinality data techniques 高基數資料技巧
- Multi-timestamp data handling 多時間戳資料處理

### [**⚙️ YAML Configuration YAML 配置**](https://nics-dp.github.io/petsard/docs/petsard-yaml/)
- Executor: Workflow orchestration and execution 工作流程編排與執行
- Loader: Data loading configuration 資料載入配置
- Splitter: Data splitting strategies 資料分割策略
- Preprocessor: Data preprocessing options 資料前處理選項
- Synthesizer: Synthesis methods and parameters 合成方法與參數
- Postprocessor: Data postprocessing options 資料後處理選項
- Evaluator: Privacy and utility evaluation 隱私與效用評估
- Describer: Data description and comparison 資料描述與比較
- Constrainer: Data constraints and validation 資料約束與驗證
- Reporter: Result reporting options 結果報告選項

### [**🐍 Python API 文件**](https://nics-dp.github.io/petsard/docs/python-api/)
Detailed API reference for programmatic usage of PETsARD components

PETsARD 元件程式化使用的詳細 API 參考文件

### [**👨‍💻 Developer Guide 開發者指南**](https://nics-dp.github.io/petsard/docs/developer-guide/)
- Development guidelines 開發指南
- Docker development environment Docker 開發環境
- Test coverage 測試覆蓋率
- Benchmark datasets 基準資料集

### [**📚 Glossary 詞彙表**](https://nics-dp.github.io/petsard/docs/glossary/)
- Key terminology and concepts 關鍵術語與概念
- Technical definitions 技術定義

## [**ℹ️ About 關於**](https://nics-dp.github.io/petsard/about/)

- Project background and license information 專案背景與授權資訊
- Academic citations and related literature 學術引用與相關文獻

---

## **🛠️ Development 開發**

### Requirements 需求

- Python 3.10 or 3.11 (Python 3.12 is not yet supported)
- Python 3.10 或 3.11（尚未支援 Python 3.12）

### Repository Structure 專案結構

```
petsard/
├── petsard/          # Main package source code 主要套件原始碼
├── tests/            # Unit tests 單元測試
├── demo/             # Demo files and examples 展示檔案與範例
├── doc_site/         # Documentation website 文件網站
├── pyproject.toml    # Project configuration 專案配置
├── compose.yml       # Docker Compose configuration Docker Compose 配置
└── README.md         # This file 本檔案
```

### Running Tests 執行測試

```bash
# Install with development dependencies 安裝開發依賴
pip install petsard[dev]

# Run all tests 執行所有測試
pytest

# Run tests with coverage 執行測試並生成覆蓋率報告
pytest --cov=petsard --cov-report=html
```

### Building Documentation 建構文件

The documentation site is built using Hugo. To run it locally:

文件網站使用 Hugo 建構。本地執行方式：

```bash
cd doc_site
hugo server
```

---

## **🤝 Contributing 貢獻**

Contributions are welcome! Please feel free to submit a Pull Request.

歡迎貢獻！請隨時提交 Pull Request。

For major changes, please open an issue first to discuss what you would like to change.

對於重大更改，請先開啟 issue 討論您想要更改的內容。

---

## **🔒 Security 安全**

For security vulnerabilities, please refer to our [Security Policy](SECURITY.md).

如有安全漏洞，請參閱我們的[安全政策](SECURITY.md)。

---

## **📄 License 授權**

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

本專案依據 [LICENSE](LICENSE) 檔案中指定的條款授權。

---

## **🔗 Links 連結**

- **GitHub Repository 程式碼倉庫**: https://github.com/nics-dp/petsard
- **Documentation 文件**: https://nics-dp.github.io/petsard/
- **PyPI Package PyPI 套件**: https://pypi.org/project/petsard/
- **Test PyPI Package 測試 PyPI 套件**: https://test.pypi.org/project/petsard/
- **Issue Tracker 問題追蹤**: https://github.com/nics-dp/petsard/issues

---

## **📧 Contact 聯絡**

For questions or support, please:
- Open an issue on GitHub 在 GitHub 開啟 issue
- Check the documentation 查看文件
- Visit the project website 造訪專案網站

如有問題或需要支援，請：
- 在 GitHub 開啟 issue
- 查看文件
- 造訪專案網站