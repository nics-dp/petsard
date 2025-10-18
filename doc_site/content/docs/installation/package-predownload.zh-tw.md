---
title: 套件預下載
type: docs
weight: 5
prev: docs/installation/docker-offline-deployment
next: docs/installation
---

適用於**無網路連線**且**不支援 Docker** 的環境。

此方式需要在有網路的環境中先下載所有依賴套件，然後傳輸到離線環境中進行安裝。

## 步驟 1：在有網路的環境中下載套件

我們提供了輪子下載工具來預先準備所有依賴套件：

### 下載核心依賴套件

```bash
# 下載 Linux 環境的套件
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# 下載 Windows 環境的套件
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os windows

# 下載 macOS Intel 環境的套件
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os macos

# 下載 macOS Apple Silicon 環境的套件
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os macos-arm
```

### 下載額外的依賴群組

```bash
# 下載資料科學相關套件
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds

# 下載完整套件（包含所有功能）
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds all

# 下載開發工具
python demo/installation/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups dev
```

**參數說明：**

| 參數 | 說明 | 範例 |
|------|------|------|
| `--branch` | Git 分支名稱 | `main`, `dev` |
| `--python-version` | Python 版本 | `3.10`, `3.11`, `3.11.5` |
| `--os` | 目標作業系統 | `linux`, `windows`, `macos`, `macos-arm` |
| `--groups` | 可選的依賴群組 | `ds`, `all`, `dev`（可用空格分隔指定多個） |

**作業系統支援：**
- `linux`：Linux 64位元
- `windows`：Windows 64位元
- `macos`：macOS Intel
- `macos-arm`：macOS Apple Silicon

**依賴群組說明：**
- **預設**（無需指定）：配置、讀檔、合成、評測的基本功能
- `ds`：資料科學功能 + Jupyter Notebook 支援
- `all`：完整功能 + 延伸支援（基準資料集下載、Excel 檔案支援）
- `dev`：測試與開發工具

### 下載位置

下載的套件預設會儲存在 `wheels/` 目錄中，結構如下：

```
wheels/
├── petsard-x.y.z-py3-none-any.whl
├── pandas-x.y.z-cp311-cp311-linux_x86_64.whl
├── numpy-x.y.z-cp311-cp311-linux_x86_64.whl
└── ... (其他依賴套件)
```

## 步驟 2：傳輸套件檔案

將整個 `wheels/` 目錄透過 USB 隨身碟、內部網路或其他方式傳輸到離線環境。

## 步驟 3：在離線環境中安裝

### 方式 A：使用 pip 直接安裝（推薦）

```bash
# 切換到 wheels 目錄
cd wheels/

# 安裝所有套件
pip install *.whl

# 或安裝 PETsARD 及其依賴
pip install --no-index --find-links=. petsard
```

### 方式 B：使用 pip 指定本地目錄

```bash
# 從 wheels 目錄安裝
pip install --no-index --find-links=./wheels petsard

# 安裝特定群組的套件
pip install --no-index --find-links=./wheels petsard[ds]
```

### 驗證安裝

```bash
# 檢查 PETsARD 是否正確安裝
python -c "import petsard; print('✅ PETsARD 已安裝，版本:', petsard.__version__)"

# 檢查 Executor 是否可用
python -c "from petsard.executor import Executor; print('✅ Executor 可用')"
```

## 疑難排解

### 找不到符合的套件版本

**問題：** 安裝時提示找不到符合的套件版本

**解決方法：**
1. 確認下載時使用的 Python 版本與離線環境一致
2. 確認下載時使用的作業系統與離線環境一致
3. 重新下載正確版本的套件

### 依賴衝突

**問題：** 安裝時提示套件依賴衝突

**解決方法：**
```bash
# 強制安裝，忽略依賴檢查（謹慎使用）
pip install --no-deps --no-index --find-links=./wheels petsard

# 然後手動安裝缺少的依賴
pip install --no-index --find-links=./wheels <缺少的套件名稱>
```

### 權限問題

**問題：** 沒有權限安裝到系統 Python

**解決方法：**
```bash
# 安裝到使用者目錄
pip install --user --no-index --find-links=./wheels petsard

# 或使用虛擬環境（推薦）
python -m venv petsard-env
source petsard-env/bin/activate  # Linux/macOS
# 或
petsard-env\Scripts\activate  # Windows

pip install --no-index --find-links=./wheels petsard
```

## 進階使用

### 下載特定版本的 PETsARD

```bash
# 下載特定分支的套件
python demo/petsard_wheel_downloader.py --branch v1.0.0 --python-version 3.11 --os linux

# 下載開發版本
python demo/petsard_wheel_downloader.py --branch dev --python-version 3.11 --os linux
```

### 批次下載多個平台的套件

```bash
# 為多個平台下載套件
for os in linux windows macos macos-arm; do
    python demo/petsard_wheel_downloader.py \
        --branch main \
        --python-version 3.11 \
        --os $os \
        --groups ds
done
```

## 下一步

安裝完成後，您可以：

* 查看[快速入門](../getting-started)以獲取詳細範例
* 查看 PETsARD YAML 文件了解設定方式
* 探索基準資料集進行測試
* 在 GitHub 儲存庫中檢視範例設定