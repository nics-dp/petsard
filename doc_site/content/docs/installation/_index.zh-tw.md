---
title: 安裝指引
type: docs
weight: 1
prev: docs
next: docs/getting-started
---

## 執行環境檢查

{{< mermaid-file file="content/docs/installation/environment-check-flow.zh-tw.mmd" >}}

**圖例說明：**

- 淡藍色框：流程起點
- 淡紫色框：條件判斷節點
- 淡綠色框：執行操作節點

## 安裝方式選擇

根據您的環境條件，請選擇適合的安裝方式：

### 有網路連線的環境

- **[Docker 建立](docker-build)** - 支援 Docker 的環境（推薦）
  - 無需本地 Python 環境設定
  - 快速部署，環境一致性高

- **[PyPI 安裝](pypi-install)** - 不支援 Docker 的環境
  - 直接安裝到本地 Python 環境
  - 支援多種依賴群組選擇
  - 推薦使用 uv 進行安裝

### 無網路連線的環境

- **[Docker 匯出](docker-export)** - 支援 Docker 的環境
  - 先在有網路環境建置/拉取映像
  - 匯出後傳輸到離線環境使用

- **[套件預下載](package-predownload)** - 不支援 Docker 的環境
  - 預先下載所有依賴套件
  - 傳輸到離線環境進行安裝

## 快速開始

### 使用 Docker（推薦）

驗證 Docker 映像是否正常運作：

```bash
# 拉取最新版本
docker pull ghcr.io/nics-dp/petsard:latest

# 驗證安裝
docker run --rm ghcr.io/nics-dp/petsard:latest python -c "
import petsard
print('✅ PETsARD 安裝成功！')
"
```

- 互動式開發

```bash
# 啟動互動式 Python 會話
docker run -it --entrypoint /opt/venv/bin/python3 \
  -v $(pwd):/app/data \
  ghcr.io/nics-dp/petsard:latest

# 在容器內，您可以運行：
# from petsard import Executor
# print('PETsARD 已準備就緒！')
```

### 使用 PyPI 安裝

驗證本地安裝是否成功：

```bash
# 安裝 PETsARD（推薦使用 uv，也可使用 pip）
uv pip install petsard
# 或
pip install petsard

# 驗證安裝
python -c "
import petsard
print('✅ PETsARD 安裝成功！')
"
```

### 下一步

完成安裝驗證後，您可以：

1. 查看[快速入門](../getting-started)以獲取詳細使用範例
2. 建立 YAML 設定檔開始使用 PETsARD
3. 探索 PETsARD YAML 文件了解設定方式