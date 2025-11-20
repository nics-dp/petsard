---
title: 安裝指引：執行環境檢查
type: docs
weight: 200
prev: docs/getting-started
next: docs/data-preparation
---

根據網路連線狀態與 Docker 支援情況選擇適合的安裝方式。推薦使用 Docker 預建方案，可確保環境一致性並簡化部署流程。若需深度學習功能，請確認 CUDA 支援。

{{< mermaid-file file="content/docs/installation/environment-check-flow.zh-tw.mmd" >}}

**圖例說明：**

- 淡藍色框：流程起點
- 淡紫色框：條件判斷節點
- 淡綠色框：執行操作節點

## 安裝方式選擇

根據您的環境條件，請選擇適合的安裝方式：

### 有網路連線的環境

- **[Docker 預建](docker-prebuilt)** - 支援 Docker 的環境（推薦）
  - 無需本地 Python 環境設定
  - 快速部署，環境一致性高

- **[PyPI 安裝](pypi-install)** - 不支援 Docker 的環境
  - 直接安裝到本地 Python 環境
  - 支援多種依賴群組選擇
  - 推薦使用 uv 進行安裝

### 無網路連線的環境

- **[Docker 離線部署](docker-offline-deployment)** - 支援 Docker 的環境
  - 先在有網路環境建置/拉取映像
  - 匯出後傳輸到離線環境使用

- **[套件預下載](package-predownload)** - 不支援 Docker 的環境
  - 預先下載所有依賴套件
  - 傳輸到離線環境進行安裝

### 深度學習支援

- **[深度學習支援檢測](dl-support-check)** - 使用深度學習合成器的環境
  - 檢查 NVIDIA GPU 驅動狀態
  - 驗證 PyTorch 與 CUDA 支援
  - 確認系統運算模式（CPU/GPU）

### 下一步

完成安裝驗證後，您可以：

1. 查看[快速入門](../getting-started)以獲取詳細使用範例
2. 建立 YAML 設定檔開始使用 PETsARD
3. 探索 PETsARD YAML 文件了解設定方式