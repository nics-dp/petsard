---
title: 深度學習支援檢測
type: docs
weight: 6
prev: docs/installation/package-predownload
next: docs/installation
---

適用於需要使用**深度學習合成器**的環境。

深度學習支援檢測用於確認系統環境是否能充分發揮 PETsARD 的合成資料生成效能。PETsARD 使用 PyTorch 作為深度學習框架，支援 CPU 和 GPU 兩種運算模式。在 CPU 模式下，所有運算都由處理器執行，適用於小規模資料集或測試環境，但處理大型資料集時速度較慢。在 GPU 模式下，運算會利用 NVIDIA 顯示卡的平行運算能力，可大幅提升合成資料生成的速度，特別是在處理數萬筆以上的資料時，效能差異可達數十倍。透過簡單的檢測指令，可以快速確認系統目前使用的運算模式，並判斷是否需要進行 GPU 環境設定。若系統具備 NVIDIA 顯示卡但檢測顯示僅支援 CPU，通常表示需要安裝或更新 CUDA 驅動程式。

> 本文檔專注於 NVIDIA GPU 環境，不考慮 macOS 環境。

## 判斷方式

判斷是否需要深度學習支援：

- **使用深度學習合成器（CTGAN、TVAE 等）**：必須有 GPU 支援
- **使用非深度學習合成器（GaussianCopula 等）**：可在沒有 GPU 支援下運作
- **僅使用評測功能**：可在沒有 GPU 支援下運作

## 步驟 1：檢查 NVIDIA GPU 驅動

若指令執行成功，會顯示 GPU 型號、驅動版本、記憶體使用狀況等資訊。若指令失敗，表示未安裝 NVIDIA 驅動或系統無 NVIDIA 顯示卡。

```bash
# 檢查 NVIDIA GPU 狀態（僅適用於有 NVIDIA 顯示卡的系統）
nvidia-smi
```

## 步驟 2：檢查 PyTorch 與 CUDA 支援

```bash
# 完整檢測指令
python -c "
import torch
print('=== PyTorch 環境資訊 ===')
print(f'PyTorch 版本: {torch.__version__}')
print(f'CUDA 可用: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA 版本: {torch.version.cuda}')
    print(f'GPU 數量: {torch.cuda.device_count()}')
    print(f'GPU 名稱: {torch.cuda.get_device_name(0)}')
else:
    print('目前僅支援 CPU 模式')
"
```

**如何閱讀結果：**

- `CUDA 可用: True` → 可使用 GPU 加速，適合處理大規模資料
- `CUDA 可用: False` → 僅能使用 CPU，適合小規模資料或測試
- `GPU 名稱` → 顯示實際使用的 GPU 型號
