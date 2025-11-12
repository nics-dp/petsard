---
title: Docker 離線部署
type: docs
weight: 4
prev: docs/installation/pypi-install
next: docs/installation/package-predownload
---

適用於**無網路連線**但**支援 Docker** 的環境。

此方式需要在有網路的環境中先建置或拉取 Docker 映像，然後匯出為檔案，最後在離線環境中匯入使用。

> 如果您的環境**有網路連線**，請直接參閱 [Docker 預建](../docker-prebuilt) 方式，無需匯出/匯入步驟。

## 步驟 1：在有網路的環境中準備 Docker 映像

### 方式 A：匯出預建映像（推薦）

先拉取預建映像（詳見 [Docker 預建](../docker-prebuilt)），然後匯出：

```bash
# 拉取最新版本（如已完成可跳過）
docker pull ghcr.io/nics-dp/petsard:latest

# 匯出映像為檔案
docker save ghcr.io/nics-dp/petsard:latest -o petsard-latest.tar
```

### 方式 B：建置並匯出映像

如果需要自訂或修改容器，可以建置自己的映像：

```bash
# 複製儲存庫
git clone https://github.com/nics-dp/petsard.git
cd petsard

# 建置標準版本（預設 - 不含 Jupyter）
docker build -t petsard:latest .

# 匯出映像為檔案
docker save petsard:latest -o petsard-latest.tar
```

### 建置包含 Jupyter Lab 的版本

```bash
# 建置並運行包含 Jupyter Lab 的版本
docker build --build-arg INCLUDE_JUPYTER=true -t petsard:jupyter .

# 匯出映像
docker save petsard:jupyter -o petsard-jupyter.tar
```

## 步驟 2：傳輸映像檔案

將匯出的 `.tar` 檔案（例如 `petsard-latest.tar`）透過 USB 隨身碟、內部網路或其他方式傳輸到離線環境。

## 步驟 3：在離線環境中匯入映像

```bash
# 匯入 Docker 映像
docker load -i petsard-latest.tar

# 驗證映像已成功匯入
docker images | grep petsard
```
