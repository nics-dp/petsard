---
title: 文件
type: docs
weight: 1
prev: docs/developer-guide
next: docs/get-started
---

`PETsARD`（隱私強化技術分析、研究與開發, /pəˈtɑrd/）是一套為了促進資料生成演算法及其評估過程而設計的 Python 程式庫。

其主要功能包括描述資料集、執行各種資料集生成算法，以及對隱私保護和效用進行測量。

## 設計架構

下圖為 `PETsARD` 模組設計與執行流程。

<p align="center"><img src="/petsard/images/PETsARD_design_zhtw.png"></p>

### 系統設計說明

PETsARD 採用模組化設計，透過 YAML 描述資料處理流程。系統整合多種合成演算法，內建隱私評估與品質評估，自動產生視覺化報告。

### 開箱即用

系統提供命令列介面與預設配置範本,支援批次處理與詳細日誌記錄。即使僅具備基礎資料知識的使用者，也能快速上手並有效應用隱私強化技術。

## 使用指南

為方便使用者快速上手，我們準備了完整的[安裝指南](installation)與[最佳實踐](best-practices)，涵蓋環境檢查、資料治理、評測設計與屬性調整。建議循序漸進：安裝前確認環境相容性、資料準備階段遵循治理規範、配置實驗時依用途選定評測策略、執行後透過屬性調整優化效能。

<p align="center"><img src="/petsard/images/best-practice.zh-tw.png"></p>

## 版本紀錄

- [Milestone](https://github.com/nics-dp/PETsARD/releases/latest)
  - 里程碑文件包含了 `PETsARD` 最新版本的詳細資訊。
- [Release Note](https://github.com/nics-dp/petsard/releases)
  - 發佈通知提供 `PETsARD` 每個版本的變更內容。
- [CHANGELOG.md](https://github.com/nics-dp/petsard/blob/main/CHANGELOG.md)
  - 更新日誌提供 `PETsARD` 隨時間演進的所有變更。

## 開源

歡迎提交拉取請求。對於重大變更，請先開啟一個議題來討論您想做的改變。並請確保適當地更新測試。