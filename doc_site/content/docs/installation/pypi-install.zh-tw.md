---
title: PyPI 安裝
type: docs
weight: 220
prev: docs/installation/docker-prebuilt
next: docs/installation/docker-prebuilt
---

適用於**有網路連線**但**不支援 Docker** 的環境。

## 可用的依賴群組

PETsARD 提供不同的依賴群組供各種使用情境：

| 群組 | 包含功能 |
|------|----------|
| **預設** | 配置、讀檔、合成、評測、基準資料集下載的基本功能（pyyaml、pandas、anonymeter、sdmetrics、sdv、torch、requests 等） |
| **資料科學** (`ds`) | 基本功能 + Jupyter Notebook 支援（適用於 Docker 環境中使用 Jupyter） |
| **完整** (`all`) | 資料科學功能 + xlsx 檔案支援 |
| **開發** (`dev`) | 完整功能 + 開發與測試工具（pytest、ruff、coverage 等） |

## 方式 1：PyPI 安裝（推薦）

PETsARD 已發布至 [PyPI](https://pypi.org/project/petsard/)。

### 方式 1-a：使用 uv（最快，推薦）

[uv](https://github.com/astral-sh/uv) 是快速的 Python 套件安裝工具。

**步驟 1：安裝 uv**（如已安裝可跳過）

```bash
# macOS 和 Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip 安裝
pip install uv
```

**步驟 2：安裝 PETsARD**

```bash
# 基本安裝（推薦給大多數使用者）
uv pip install petsard

# 使用依賴群組
uv pip install petsard[ds]   # 適用於 Docker 環境中使用 Jupyter
uv pip install petsard[all]  # 包含 xlsx 檔案支援
uv pip install petsard[dev]  # 用於開發
```

### 方式 1-b：使用 pip

**現代化 pip（>= 25.0）支援 dependency-groups：**

```bash
# 基本安裝（推薦給大多數使用者）
pip install petsard

# 使用依賴群組
pip install --group ds petsard    # 適用於 Docker 環境中使用 Jupyter
pip install --group all petsard   # 包含 xlsx 檔案支援
pip install --group dev petsard   # 用於開發
```

**舊版 pip（< 25.0）- 向後相容語法：**

```bash
pip install petsard[ds]   # 適用於 Docker 環境中使用 Jupyter
pip install petsard[all]  # 包含 xlsx 檔案支援
pip install petsard[dev]  # 用於開發
```

### 方式 1-c：從 TestPyPI 安裝（測試用）

若要從 [TestPyPI](https://test.pypi.org/) 安裝預發布或測試版本：

```bash
# 使用 uv
uv pip install --index-url https://test.pypi.org/simple/ petsard

# 使用 pip
pip install --index-url https://test.pypi.org/simple/ petsard

# 使用依賴群組（可能需要額外的 --extra-index-url 以安裝依賴）
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --group ds petsard
```

**注意：** TestPyPI 用於測試套件發布。生產環境請從主要 PyPI 安裝（方式 1-a 或 1-b）。

#### 受限網域環境安裝

如果您在受限的網路環境中安裝（例如：企業防火牆後或透過代理伺服器），可能會遇到 SSL 憑證驗證問題。此時可以使用 `--trusted-host` 參數來略過憑證驗證：

```bash
# 現代化 pip（>= 25.0）
pip install --group ds petsard \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org

# 舊版 pip（< 25.0）
pip install petsard[ds] \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org
```

**Jupyter Notebook 使用者**，語法相同：

```python
# 現代化 pip（>= 25.0）
%pip install --group ds petsard \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org

# 舊版 pip（< 25.0）
%pip install petsard[ds] \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org
```

**了解 `--trusted-host` 參數：**

- `--trusted-host pypi.org` - 信任 PyPI 主索引伺服器
- `--trusted-host files.pythonhosted.org` - 信任 PyPI 的套件檔案儲存伺服器

這些參數會告訴 pip 跳過指定主機的 SSL 憑證驗證。適用於以下情況：
- 企業網路為了安全檢查而攔截 SSL/TLS 流量
- 使用自簽憑證
- 因代理伺服器設定導致憑證驗證失敗

**注意：** 僅在可信任的網路環境中使用 `--trusted-host`，因為它會降低安全性（停用憑證驗證）。生產環境建議配置正確的 SSL 憑證或使用私有 PyPI 鏡像。

## 方式 2：原始碼安裝

適用於開發或自訂建置。

### 方式 2-a：使用 Git（推薦）

```bash
# 複製儲存庫
git clone https://github.com/nics-dp/petsard.git
cd petsard

# 使用現代化 pip（>= 25.0）搭配 dependency-groups
pip install --group all -e .   # 完整功能
pip install --group ds -e .    # 資料科學功能
pip install --group dev -e .   # 開發工具

# 使用舊版 pip（< 25.0）- 向後相容
pip install -e .[all]  # 完整功能
pip install -e .[ds]   # 資料科學功能
pip install -e .[dev]  # 開發工具

# 或使用 uv（推薦用於開發）
uv sync --group all    # 完整功能
uv sync --group dev    # 開發環境
```

### 方式 2-b：手動下載（無需 Git）

如果您的環境沒有安裝 Git，可以直接下載原始碼 ZIP 檔案：

**步驟 1：下載原始碼**

前往 [PETsARD GitHub Releases](https://github.com/nics-dp/petsard/releases) 或直接下載：
- 最新穩定版本：https://github.com/nics-dp/petsard/archive/refs/heads/main.zip
- 或從 Releases 頁面選擇特定版本

**步驟 2：解壓縮並安裝**

```bash
# 解壓縮下載的檔案
unzip petsard-main.zip
cd petsard-main

# 使用現代化 pip（>= 25.0）搭配 dependency-groups
pip install --group all -e .   # 完整功能
pip install --group ds -e .    # 資料科學功能
pip install --group dev -e .   # 開發工具

# 使用舊版 pip（< 25.0）- 向後相容
pip install -e .[all]  # 完整功能
pip install -e .[ds]   # 資料科學功能
pip install -e .[dev]  # 開發工具

# 或使用 uv（推薦用於開發）
uv sync --group all    # 完整功能
uv sync --group dev    # 開發環境
```

**Windows 使用者**可使用檔案總管直接解壓縮，然後在該資料夾開啟命令提示字元或 PowerShell 執行安裝指令。

**開發推薦工具：**
* `pyenv` - Python 版本管理
* `uv` - 套件管理
