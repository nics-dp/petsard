---
title: Docker 建立
type: docs
weight: 2
prev: docs/installation
---

# Docker 建立

適用於**有網路連線**且**支援 Docker** 的環境。

## 方式：使用預建 Docker 容器

PETsARD 提供預先建置的 Docker 容器，無需本地 Python 環境設定即可使用。

```bash
# 拉取最新版本
docker pull ghcr.io/nics-dp/petsard:latest

# 運行互動式容器
docker run -it --rm ghcr.io/nics-dp/petsard:latest
```

**可用標籤：**
- `latest` - 最新穩定版本（來自 main 分支）
- `dev` - 開發版本（來自 dev 分支）

## 下一步

安裝完成後，您可以：

* 查看[快速入門](../getting-started)以獲取詳細範例
* 查看 PETsARD YAML 文件了解設定方式
* 探索基準資料集進行測試
* 在 GitHub 儲存庫中檢視範例設定