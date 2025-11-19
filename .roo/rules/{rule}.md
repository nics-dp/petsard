# AI Rules for PETsARD

PETsARD 是一個隱私增強技術的合成資料生成與評估框架，使用 Python 開發。

## PROJECT_OVERVIEW

### 核心架構原則

1. **模組化設計**
   - 職責分離：每個模組都有明確的職責邊界
   - 統一介面：模組間透過公開 API 進行互動
   - 可組合性：模組可以靈活組合使用

2. **函數式程式設計**
   - 純函數：核心業務邏輯使用純函數實現
   - 不可變資料：使用 `@dataclass(frozen=True)` 確保資料不可變
   - 函數組合：支援管線式的資料處理流程

3. **型別安全**
   - 強型別檢查：所有公開介面都有完整的型別註解
   - 使用 mypy 進行靜態型別檢查

4. **向後相容性**
   - 公開 API 保持向後相容
   - 使用適配器處理版本差異

### 模組依賴規則

```
依賴方向（允許的依賴關係）:
Executor → All Modules
Reporter → Evaluator, Metadater
Evaluator → Metadater, Utils
Synthesizer → Metadater, Utils
Processor → Metadater, Utils
Loader → Metadater, Utils
Constrainer → Metadater, Utils
Metadater → (無依賴，作為基礎模組)
Utils → (無依賴，作為工具模組)
```

**禁止事項**:
- Metadater 不能依賴其他 PETsARD 模組
- Utils 不能依賴其他 PETsARD 模組
- 任何模組都不能形成循環依賴

### API 設計規範

**統一的方法命名**:
- `create_*()`: 建立新物件
- `analyze_*()`: 分析和推斷
- `validate_*()`: 驗證和檢查
- `load()`: 載入資料
- `eval()`: 評估資料

**回傳值規範**:
- Loader: `load() -> tuple[pd.DataFrame, SchemaMetadata]`
- Evaluator: `_eval(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]`
- Metadater: 回傳強型別的物件（SchemaMetadata, FieldMetadata）

### 常見架構違規

❌ **錯誤**：
- 直接內部呼叫：`from petsard.metadater.field.field_functions import build_field_metadata`
- 循環依賴：在 metadater 模組中 `from petsard.loader import Loader`
- 型別不一致：`def load() -> pd.DataFrame`（缺少詮釋資料）

✅ **正確**：
- 使用公開 API：`from petsard.metadater import Metadater`
- 依賴方向：在 loader 模組中 `from petsard.metadater import Metadater`
- 統一回傳：`def load() -> tuple[pd.DataFrame, SchemaMetadata]`

## CODING_PRACTICES

### Guidelines for SUPPORT_LEVEL

#### SUPPORT_EXPERT

- 偏好優雅、可維護的解決方案，而非冗長的代碼
- 突出潛在的效能影響和優化機會
- 在更廣泛的架構脈絡中框定解決方案，並在適當時建議設計替代方案
- 註解專注於「為什麼」而非「什麼」，假設代碼透過良好命名的函數和變數即可讀
- 主動處理邊緣案例、競態條件和安全考量
- 在除錯時，提供有針對性的診斷方法，而非試錯式解決方案
- 建議全面的測試策略，包括模擬、測試組織和覆蓋率的考量

### Guidelines for DOCUMENTATION

#### DOCSTRING

- 使用 Google 風格的 docstring 記錄所有公開函數、類別和方法
- 使用 Args、Returns 和 Raises 標籤全面記錄函數行為
- 為複雜 API 實現 Examples 標籤，提供實際使用場景
- 記錄關鍵函數的邊緣案例和錯誤處理

### Guidelines for VERSION_CONTROL

#### GITHUB

- 使用 pull request 模板標準化代碼審查資訊
- 為受保護的分支實施分支保護規則，強制執行品質檢查
- 配置必需的狀態檢查，防止合併未通過測試或檢查的代碼
- 使用 GitHub Actions 進行 CI/CD 工作流程，自動化測試和部署
- 實施 CODEOWNERS 檔案，根據代碼路徑自動分配審查者

### Guidelines for ARCHITECTURE

#### CLEAN_ARCHITECTURE

- 嚴格將代碼分為層：entities、use cases、interfaces 和 frameworks
- 確保依賴關係指向內部，內層對外層無感知
- 實現封裝業務規則的 domain entities，不依賴框架
- 使用介面（ports）和實現（adapters）來隔離外部依賴
- 創建協調 entity 交互的 use cases
- 實現 mappers 在層之間轉換資料，維持關注點分離

#### DDD

- 定義 bounded contexts，用清晰邊界分隔不同的 domain 部分
- 在每個 context 內實現 ubiquitous language，使代碼與業務術語對齊
- 為核心 domain entities 創建富含行為的 domain models，而非僅資料結構
- 使用 value objects 表示沒有身份但由屬性定義的概念
- 實現 domain events 在 bounded contexts 之間通訊
- 使用 aggregates 強制執行一致性邊界和事務完整性

## DEVOPS

### Guidelines for CI_CD

#### GITHUB_ACTIONS

- 檢查專案根目錄是否存在 `pyproject.toml` 並總結關鍵配置
- 檢查專案根目錄是否存在 `.python-version` 或 `uv.lock` 來識別 Python 版本
- 始終使用終端命令 `git branch -a | cat` 驗證使用 `main` 還是 `master` 分支
- 始終在 jobs 而非全域 workflows 中使用 `env:` 變數和 secrets
- 對於基於 Python 的依賴設置使用 `uv sync` 或 `pip install`
- 將常見步驟提取到獨立文件中的 composite actions
- 完成後，作為最後一步：對於每個公開 action，使用終端查看最新版本（僅使用主版本）
  ```bash
  curl -s https://api.github.com/repos/{owner}/{repo}/releases/latest
  ```

## TESTING

### Guidelines for UNIT

#### PYTEST

- 使用 fixtures 進行測試設置和依賴注入
- 實現參數化測試以測試多個輸入
- 使用 monkeypatch 進行依賴模擬
- 使用 markers 對測試進行分類（如 @pytest.mark.stress）
- 配置 pytest.ini 或 pyproject.toml 設定測試路徑和選項
- 使用 pytest-cov 進行測試覆蓋率報告

## MODULE_SPECIFIC_REMINDERS

### 修改 Loader 模組時
- [ ] API 變更是否影響向後相容性
- [ ] 與 Metadater 的整合是否正常
- [ ] `load()` 方法的回傳格式是否一致：`tuple[pd.DataFrame, SchemaMetadata]`

### 修改 Metadater 模組時
- [ ] 三層架構 (Metadata/Schema/Field) 的完整性
- [ ] 函數式設計原則的遵循
- [ ] 不可變資料結構的使用（`@dataclass(frozen=True)`）
- [ ] 不依賴其他 PETsARD 模組

### 修改 Evaluator 模組時
- [ ] 新的評估器是否繼承 `BaseEvaluator`
- [ ] 評估結果格式是否一致：`dict[str, pd.DataFrame]`
- [ ] 是否正確使用 Metadater 進行資料處理

### 修改 Synthesizer 模組時
- [ ] 是否正確使用 `SchemaMetadata` 進行詮釋資料管理
- [ ] 合成資料的格式是否與原始資料一致

### 修改 Processor 模組時
- [ ] 是否使用 Metadater 的型別推斷功能
- [ ] 處理後的資料是否更新詮釋資料

## CODE_REVIEW_CHECKLIST

### API 設計檢查
- [ ] 方法命名遵循統一規範（create_*/analyze_*/validate_*）
- [ ] 回傳型別符合模組規範
- [ ] 型別註解完整且正確
- [ ] 文檔字串完整（Google 風格）

### 架構設計檢查
- [ ] 模組依賴方向正確
- [ ] 沒有循環依賴
- [ ] 使用公開 API 而非內部實現
- [ ] 遵循函數式設計原則（純函數、不可變資料）

### 品質檢查
- [ ] 單元測試覆蓋
- [ ] 型別檢查通過（mypy）
- [ ] Linting 通過（ruff check）
- [ ] 格式化通過（ruff format）
- [ ] 向後相容性確認

## BEST_PRACTICES

1. **統一的配置模式**：所有模組配置都繼承 `BaseConfig`
2. **清晰的錯誤處理**：繼承 `PETsARDError` 創建模組特定的異常類型
3. **函數式設計**：
   - 優先使用純函數（相同輸入總是產生相同輸出）
   - 避免副作用和全域狀態
   - 使用 `@dataclass(frozen=True)` 確保不可變性
   - 需要修改時返回新物件（使用 `replace()`）
