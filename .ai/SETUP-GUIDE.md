# PETsARD AI 輔助開發設置指南

## 🚀 快速開始

這個指南將幫助您設置 PETsARD 的 AI 輔助開發環境，確保團隊協作時保持架構一致性。

## 📋 前置需求

- Python 3.10+
- Git
- Roo (AI 代碼助手)

## 🔧 設置步驟

### 1. 配置 Roo

在 Roo 中載入專案配置：

```bash
# Roo 會自動讀取 .roo/project.yaml 配置
# 確保以下文件存在：
ls .roo/project.yaml
ls .ai/roo-config/project-context.md
ls .ai/roo-config/architecture-rules.md
```

### 2. 驗證配置

```bash
# 手動運行開發助手
python3 .ai/scripts/development-assistant.py

# 或者修改一個 Python 文件後運行
echo "# test comment" >> petsard/loader/loader.py
python3 .ai/scripts/development-assistant.py
git checkout petsard/loader/loader.py  # 恢復文件
```

## 📖 使用方式

### 日常開發流程

1. **開始開發前**
   - 使用 Roo 進行 AI 輔助開發
   - 了解架構設計原則

2. **進行代碼修改**
   - Roo 會自動提醒遵循架構規則
   - 遵循統一的 API 設計規範

3. **提交代碼**
   ```bash
   git add .
   git commit -m "feat(loader): 新增 CSV 載入功能"
   ```

### Roo 使用範例

#### 修改 Loader 模組
```
開發者: "我要在 loader 模組新增 Excel 載入功能"

Roo:
"根據架構設計原則，新的載入功能需要：
1. 繼承 LoaderBase 抽象類別
2. 實現 load() 方法，回傳 tuple[pd.DataFrame, SchemaMetadata]
3. 使用 Metadater.create_schema() 生成詮釋資料
4. 更新 LoaderConfig 配置

我會幫您遵循現有的架構設計來實現 Excel 載入功能。"
```

#### 修改 Evaluator 模組
```
開發者: "我要新增一個隱私評估器"

Roo:
"根據架構設計原則，新的評估器需要：
1. 繼承 BaseEvaluator 抽象類別
2. 實現 _eval() 方法，回傳 dict[str, pd.DataFrame]
3. 在 EvaluatorMap 中註冊新的評估器
4. 創建對應的配置類別

請問您要實現什麼類型的隱私評估？我會確保遵循統一的評估結果格式。"
```

## 🔍 開發助手功能

### 自動檢查項目

- **架構規則檢查**: 確保遵循模組間依賴規則
- **API 一致性檢查**: 檢查方法命名和回傳格式
- **向後相容性提醒**: API 變更時的相容性檢查

### 生成的提醒範例

```
🔔 PETsARD 開發提醒

您修改了 Python 檔案

請確保：
1. API 變更保持向後相容性
2. 所有公開介面有完整型別註解
3. 遵循模組化設計原則

💡 提醒：遵循架構原則是高品質程式碼的關鍵！
```

## 📁 目錄結構說明

```
.ai/
├── README.md                    # AI 輔助開發總覽
├── SETUP-GUIDE.md              # 本設置指南
├── development-workflow.md      # 詳細開發流程
└── roo-config/                  # Roo 配置文件
    ├── project-context.md       # 專案上下文
    └── architecture-rules.md    # 架構規則

.roo/
└── project.yaml                 # Roo 專案配置
```

## 🎯 最佳實踐

### 1. 開發前準備
- 了解模組的架構原則和 API 規範
- 檢查是否有相關的測試需要更新

### 2. 代碼修改
- 遵循統一的命名規範 (create_*/analyze_*/validate_*)
- 使用完整的型別註解
- 保持函數式設計原則
- 確保不可變資料結構

### 3. 提交前檢查
- 驗證向後相容性
- 執行相關測試
- 確保遵循架構設計原則

## 🆘 常見問題

### Q: Roo 沒有自動載入配置怎麼辦？
A: 確認 `.roo/project.yaml` 文件存在，並重新啟動 Roo。

### Q: 如何確保遵循架構設計原則？
A: 使用 Roo 進行開發時，它會自動提醒架構設計原則。同時參考 `.ai/roo-config/` 中的文件。

## 🔗 相關資源

- [開發流程詳細說明](development-workflow.md)
- [專案上下文配置](roo-config/project-context.md)
- [架構規則說明](roo-config/architecture-rules.md)

## 📞 支援

如果在設置或使用過程中遇到問題，請：
1. 檢查本指南的常見問題部分
2. 查看相關的配置文件是否正確
3. 聯繫團隊技術負責人

---

🎉 **歡迎使用 PETsARD AI 輔助開發環境！**

這個設置將幫助團隊保持程式碼品質和架構一致性，讓協作更加順暢。