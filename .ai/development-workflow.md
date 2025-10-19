# PETsARD 開發流程與 AI 輔助規範

## 🎯 設計目標

建立一個自動化的開發流程，確保所有開發者在使用 Roo 進行代碼修改時：
1. 在修改代碼時遵循既定的架構設計
2. 保持團隊開發的一致性和架構完整性

## 📁 開發流程配置結構

```
.ai/
├── README.md                           # AI 輔助開發說明
├── development-workflow.md             # 本文件：開發流程規範
└── roo-config/                         # Roo 配置文件
    ├── project-context.md              # 專案上下文配置
    └── architecture-rules.md           # 架構規則
```

## 🔧 Roo 配置整合

### 1. 專案上下文自動載入

創建 `.ai/roo-config/project-context.md`，讓 Roo 在每次啟動時自動載入：

```markdown
# PETsARD 專案上下文

## 核心架構原則
- 模組化設計：每個模組職責清晰分離
- 函數式程式設計：使用純函數和不可變資料結構
- 統一介面：透過公開 API 進行模組間互動
- 向後相容：保持現有 API 穩定性

## 模組架構
- **Loader**: 資料載入和分割
- **Metadater**: 詮釋資料管理核心
- **Processor**: 資料前處理
- **Synthesizer**: 資料合成
- **Evaluator**: 品質評估
- **Reporter**: 結果報告
- **Constrainer**: 約束條件

## 開發規範
1. API 變更時，必須確保向後相容性
2. 所有公開介面都要有完整的型別註解
3. 遵循模組化設計原則
```

### 2. 自動化開發提醒系統

創建 `.ai/roo-config/architecture-rules.md`：

```markdown
# 架構規則與自動提醒

## 代碼修改檢查清單

### 當修改 `petsard/loader/` 時：
- [ ] 確認 API 變更不會破壞向後相容性
- [ ] 驗證與 Metadater 模組的整合是否正常

### 當修改 `petsard/metadater/` 時：
- [ ] 確認三層架構 (Metadata/Schema/Field) 的完整性
- [ ] 驗證函數式設計原則的遵循

### 當修改 `petsard/evaluator/` 時：
- [ ] 確認新的評估器遵循 BaseEvaluator 介面
- [ ] 驗證評估結果格式的一致性

## 自動提醒規則
1. 新增類別或函數時，提醒更新 API 文檔
2. 修改公開介面時，強制檢查向後相容性
```

## 🚀 實施步驟

### 步驟 1: 創建 Roo 專案配置

在專案根目錄創建 `.roo/project.yaml`：

```yaml
name: "PETsARD"
description: "Privacy Enhancing Technologies Synthetic and Real Data"

# 自動載入 AI 輔助配置
context_files:
  - ".ai/roo-config/project-context.md"
  - ".ai/roo-config/architecture-rules.md"
  - ".ai/roo-config/coding-standards.md"

# 開發流程規則
development_rules:
  - name: "api_compatibility_check"
    description: "檢查 API 向後相容性"
    trigger: "public_interface_changed"
    action: "compatibility_review"
```

### 步驟 2: 創建自動化提醒腳本

創建 `.ai/scripts/development-assistant.py`：

```python
#!/usr/bin/env python3
"""
PETsARD 開發助手
協助開發者遵循架構設計原則
"""

import os
import sys
from pathlib import Path
from typing import List

class DevelopmentAssistant:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.ai_dir = self.project_root / ".ai"
    
    def check_modified_files(self, modified_files: List[str]) -> List[str]:
        """檢查修改的文件"""
        python_files = [f for f in modified_files if f.endswith('.py')]
        return python_files
    
    def generate_reminder_message(self, python_files: List[str]) -> str:
        """生成提醒訊息"""
        if not python_files:
            return ""
        
        message = "🔔 開發提醒：您修改了 Python 檔案\n\n"
        message += "請確保：\n"
        message += "1. API 變更保持向後相容性\n"
        message += "2. 所有公開介面有完整型別註解\n"
        message += "3. 遵循模組化設計原則\n\n"
        message += "💡 提醒：遵循架構原則是高品質程式碼的關鍵！"
        return message

if __name__ == "__main__":
    assistant = DevelopmentAssistant(".")
    modified_files = sys.argv[1:] if len(sys.argv) > 1 else []
    python_files = assistant.check_modified_files(modified_files)
    reminder = assistant.generate_reminder_message(python_files)
    if reminder:
        print(reminder)
```

### 步驟 3: Git Hooks 整合

創建 `.ai/scripts/pre-commit-hook.sh`：

```bash
#!/bin/bash
# PETsARD Pre-commit Hook
# 在提交前檢查架構設計原則

echo "🔍 檢查架構設計原則..."

# 獲取修改的 Python 文件
MODIFIED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$MODIFIED_PY_FILES" ]; then
    echo "📝 檢測到 Python 文件修改："
    echo "$MODIFIED_PY_FILES"
    
    # 運行開發助手
    python .ai/scripts/development-assistant.py $MODIFIED_PY_FILES
    
    echo ""
    echo "❓ 您是否已經遵循架構設計原則？ (y/n)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ 請確保遵循架構設計原則後再提交"
        exit 1
    fi
fi

echo "✅ 架構設計原則檢查完成"
```

## 📋 開發者使用指南

### 1. 初始設置

每個開發者在開始工作前：

```bash
# 配置 Roo 載入專案上下文
# 在 Roo 中設置自動載入 .ai/roo-config/ 中的配置文件
```

### 2. 日常開發流程

```bash
# 1. 開始開發前，使用 Roo 進行 AI 輔助開發
roo "我要修改 loader 模組"

# 2. 進行代碼修改
# Roo 會自動提醒遵循架構規則

# 3. 提交變更
git add .
git commit -m "feat: 新增資料載入功能"
```

### 3. Roo 使用範例

```
開發者: "我要在 evaluator 模組新增一個評估器"

Roo:
"根據架構設計原則，新的評估器需要：
1. 繼承 BaseEvaluator 抽象類別
2. 實現 _eval() 方法
3. 遵循統一的評估結果格式
4. 更新 EvaluatorMap 枚舉

請問您要實現什麼類型的評估器？我會幫您遵循現有的架構設計。"
```

## 🔄 持續改進機制

### 1. 架構檢查

定期運行自動化腳本檢查：
- API 文檔的完整性
- 架構設計的遵循程度

### 2. 團隊協作規範

- **代碼審查**: 必須檢查架構設計原則的遵循
- **架構討論**: 重大變更需要團隊討論

### 3. 自動化測試

```python
# 在 CI/CD 中加入架構檢查測試
def test_architecture_compliance():
    """測試代碼是否遵循架構設計原則"""
    # 檢查每個模組的公開 API 是否符合設計原則
    # 檢查模組間的依賴關係是否正確
    pass
```

## 📈 預期效益

1. **架構一致性**: 確保所有開發者遵循統一的架構設計
2. **知識傳承**: 新加入的開發者能快速理解系統架構
3. **品質保證**: 減少架構偏離和設計不一致的問題
4. **協作效率**: 提高團隊協作的效率和品質

這個開發流程確保了 PETsARD 專案在多人協作時能夠保持架構的完整性和一致性，同時讓 AI 輔助開發成為團隊的標準工作流程。