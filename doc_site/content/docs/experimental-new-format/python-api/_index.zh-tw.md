---
title: "Python API"
weight: 300
---

PETsARD 的 Python API 參考。

## 核心模組

- **Loader API** - 資料載入器
- **Metadater API** - 詮釋資料管理器
- **Synthesizer API** - 合成資料生成器
- **Evaluator API** - 品質評估器
- **Writer API** - 資料輸出器

## 設計原則

### 統一介面
所有模組使用一致的方法命名：
- `create()` - 從配置建立
- `eval()` / `synth()` / `write()` - 執行主要功能

### 不可變物件
所有配置類別都是 frozen dataclass，確保資料安全。

### 型別提示
完整的型別標註，提供更好的開發體驗。