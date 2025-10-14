---
title: "PETsARD 高斯耦合"
weight: 1
math: true
---

使用 Numba JIT 與 PyTorch 實現的高效高斯耦合合成器，支援 CPU/GPU 混合運算與智能設備選擇。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/synthesizer-yaml/petsard-gaussian-copula.ipynb)

```yaml
Synthesizer:
  petsard-gaussian-copula:
    method: petsard-gaussian-copula
    sample_num_rows: 1000  # 生成列數，預設為訓練資料列數
    use_gpu: auto          # 設備選擇，預設 auto（自動）
    gpu_threshold: 50000   # auto 模式閾值，預設 50,000
```

## 參數說明

- **method** (`string`, 必要) - 固定值：`petsard-gaussian-copula`
- **sample_num_rows** (`integer`, 選填) - 生成的合成資料列數，若未指定則使用訓練資料列數
- **use_gpu** (`string` 或 `boolean`, 選填，預設 `"auto"`) - 設備選擇模式：
  - `"auto"` (預設)：根據資料量自動選擇，超過 `gpu_threshold` 且 GPU 可用時使用 GPU，否則使用 CPU
  - `true`：強制使用 GPU，若 GPU 不可用則報錯
  - `false`：強制使用 CPU
- **gpu_threshold** (`integer`, 選填，預設 `50,000`) - 當 `use_gpu="auto"` 時，資料超過此列數才使用 GPU

## 演算法原理

高斯耦合（Gaussian Copula）透過以下步驟分離邊際分佈與相關性結構：

1. **邊際轉換** - 使用經驗累積分佈函數轉為均勻分佈：$u_i = F_i(X_i) = \frac{\text{rank}(X_i)}{n}$
2. **高斯化** - 使用標準常態分位數函數：$z_i = \Phi^{-1}(u_i)$
3. **相關性學習** - 在高斯空間學習相關矩陣：$\Sigma = \text{corr}(\mathbf{Z})$
4. **聯合抽樣** - 從多變量常態分佈抽樣：$\mathbf{Z}^* \sim \mathcal{N}(\mathbf{0}, \Sigma)$
5. **反向轉換** - 轉回原始分佈空間：$u_i^* = \Phi(z_i^*), \quad X_i^* = F_i^{-1}(u_i^*)$

數學表示：$H(\mathbf{X}) = \Phi_{\Sigma}\left(\Phi^{-1}(F_1(X_1)), \ldots, \Phi^{-1}(F_D(X_D))\right)$

## 實作特色

### 混合計算架構

PETsARD 採用 **NumPy + Numba JIT + PyTorch** 架構，各階段使用最適合的工具：

| 階段 | 使用工具 | 加速效果 |
|------|---------|---------|
| Transform | NumPy + Numba JIT | JIT 編譯後 ~700x |
| Correlation | NumPy | 快速穩定 |
| Regularization | NumPy (Ledoit-Wolf) | 避免特徵值分解 |
| Sampling | NumPy | 比 PyTorch CPU 快 ~100x |
| Inverse Transform | NumPy + Numba JIT | JIT 編譯線性插值 |
| GPU Operations | PyTorch | 大資料集加速 |

### 核心優化技術

- **Numba JIT 編譯** - 自訂 rank 計算與線性插值，比標準實作快 2-3x，編譯後再快 10-100x
- **智能設備選擇** - 小資料（< 5萬列）用 CPU 避免傳輸開銷，大資料用 GPU 加速
- **Identity 快速路徑** - 檢測到變數獨立時使用超快的獨立抽樣
- **Ledoit-Wolf 正則化** - 使用 $\Sigma_{\text{reg}} = (1 - \lambda)\Sigma + \lambda I$，只在必要時做特徵值分解

### 與其他實作的差異

**相同**：標準高斯耦合演算法，使用相同的統計方法

**不同**：PETsARD 加入 Numba JIT 加速、PyTorch GPU 支援、智能設備選擇等工程優化

## 資料要求

- ✅ 類別變數已編碼為整數 (0, 1, 2, ...)
- ✅ 所有欄位為數值型態（int, float, datetime）
- ❌ 不接受 string/object 型態

生成過程使用 float64，完成後自動還原原始型態（整數四捨五入、時間型態轉換等）。

## 效能與限制

### 效能參考

- **小型資料**（< 1萬列）：訓練 ~1s，生成 ~0.5s
- **中型資料**（1-5萬列）：訓練 ~2-3s，生成 ~1s
- **大型資料**（> 5萬列）：自動切換 GPU，速度提升 2-5 倍

{{< callout type="info" >}}
首次執行 Numba JIT 需編譯（~2s），之後執行會快很多。
{{< /callout >}}

### 限制

- 主要捕捉**線性相關性**（Pearson 相關係數），非線性關係可能無法完全重現
- 複雜條件依賴會被簡化為聯合高斯分佈
- 相關矩陣大小為 O(n²)，超過 1000 欄位需大量記憶體

## 參考文獻

- Nelsen, R. B. (2006). An Introduction to Copulas (2nd ed.). Springer. https://doi.org/10.1007/0-387-28678-0