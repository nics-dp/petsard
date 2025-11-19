---
title: "resample_until_satisfy()"
weight: 354
---

重複採樣直到滿足約束條件且達到目標列數。

## 語法

```python
def resample_until_satisfy(
    data: pd.DataFrame,
    target_rows: int,
    synthesizer,
    postprocessor=None,
    max_trials: int = 300,
    sampling_ratio: float = 10.0,
    verbose_step: int = 10
) -> pd.DataFrame
```

## 參數

- **data** : pd.DataFrame, required
    - 要套用約束的輸入資料框
    - 必要參數
    - 如果已有部分符合約束的資料，會作為基礎繼續補充

- **target_rows** : int, required
    - 目標列數
    - 必要參數
    - 最終返回的資料框將包含此數量的列

- **synthesizer** : Synthesizer, required
    - 用於生成合成資料的合成器實例
    - 必要參數
    - 必須是已經透過 `\1` 訓練過的合成器

- **postprocessor** : Postprocessor, optional
    - 資料轉換的後處理器
    - 用於將合成資料轉換回原始格式
    - 預設值：`None`

- **max_trials** : int, optional
    - 最大嘗試次數
    - 達到此次數後即使未滿足目標列數也會停止
    - 預設值：`300`

- **sampling_ratio** : float, optional
    - 每次生成的資料量是目標列數的倍數
    - 用於補償約束過濾造成的資料損失
    - 預設值：`10.0`（生成 10 倍的資料）

- **verbose_step** : int, optional
    - 每隔幾次嘗試顯示進度
    - 設為 `0` 關閉進度顯示
    - 預設值：`10`

## 返回值

- **pd.DataFrame**
    - 滿足所有約束條件且具有目標列數的資料框
    - 若達到 max_trials 仍未滿足，返回已收集的資料（可能少於 target_rows）

## 屬性

執行後會設定以下屬性：

- **resample_trails** : int
    - 達到目標所需的嘗試次數
    - 可用於評估約束條件的嚴格程度

## 說明

`\1` 方法適用於約束條件嚴格、過濾後資料量不足的情況。它會：

1. 先對輸入資料套用約束條件
2. 計算需要補充的資料量
3. 迭代地：
   - 使用合成器生成新的合成資料
   - 套用後處理器（如果有）
   - 套用所有約束條件
   - 累積符合條件的資料
   - 檢查是否達到目標列數
4. 達到目標後，隨機抽取目標數量的列

### 重採樣流程

```
開始
  ↓
套用約束到輸入資料
  ↓
是否足夠? ──是──> 隨機抽樣 target_rows 列 ──> 完成
  ↓ 否
迭代開始 (trials = 0)
  ↓
生成 target_rows × sampling_ratio 列合成資料
  ↓
套用後處理器（如有）
  ↓
套用所有約束條件
  ↓
累積符合條件的資料
  ↓
trials += 1
  ↓
資料是否足夠? ──是──> 隨機抽樣 target_rows 列 ──> 完成
  ↓ 否
trials < max_trials? ──是──> 回到「生成合成資料」
  ↓ 否
返回已收集的資料（警告）
```

## 基本範例

### 簡單重採樣

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# 準備原始資料
df = pd.DataFrame({
    'age': [25, 30, 45, 55, 60],
    'salary': [50000, 60000, 80000, 90000, 95000]
})

# 訓練合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit(df)

# 設定嚴格約束
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",  # 限制年齡範圍
        "salary >= 60000 & salary <= 85000"  # 限制薪資範圍
    ]
}

constrainer = Constrainer(config)

# 重採樣直到達到 100 列
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),  # 從空開始
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50,
    sampling_ratio=20.0  # 每次生成 2000 列
)

print(f"目標列數: 100")
print(f"實際列數: {len(result)}")
print(f"嘗試次數: {constrainer.resample_trails}")
# 目標列數: 100
# 實際列數: 100
# 嘗試次數: 3
```

### 使用後處理器

```python
from petsard import Constrainer, Synthesizer, Preprocessor, Postprocessor
import pandas as pd

# 準備和預處理資料
df = pd.DataFrame({
    'age': [25, 30, 45, 55],
    'category': ['A', 'B', 'A', 'C']
})

preprocessor = Preprocessor('default')
processed_data = preprocessor.fit_transform(df)

# 訓練合成器
synthesizer = Synthesizer(method='default')
synthesizer.create(metadata=schema)
synthesizer.fit(processed_data)

# 創建後處理器
postprocessor = Postprocessor('default')
postprocessor.fit(df)  # 使用原始資料訓練

# 設定約束
config = {
    'field_constraints': [
        "age >= 20 & age <= 50"
    ],
    'field_proportions': [
        {'fields': 'category', 'mode': 'all', 'tolerance': 0.1}
    ]
}

constrainer = Constrainer(config)

# 重採樣（包含後處理）
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=200,
    synthesizer=synthesizer,
    postprocessor=postprocessor,  # 將編碼資料轉回原始格式
    max_trials=100,
    verbose_step=20  # 每 20 次顯示進度
)

print(f"最終列數: {len(result)}")
print(f"嘗試次數: {constrainer.resample_trails}")
print("\n類別分布:")
print(result['category'].value_counts())
```

## 進階範例

### 從現有資料擴充

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# 已有部分符合約束的資料
existing_data = pd.DataFrame({
    'age': [28, 35, 42],
    'performance': [5, 5, 4],
    'education': ['PhD', 'Master', 'PhD']
})

# 設定約束
config = {
    'field_constraints': [
        "age >= 25 & age <= 50",
        "performance >= 4"
    ],
    'field_combinations': [
        (
            {'education': 'performance'},
            {'PhD': [4, 5], 'Master': [4, 5]}
        )
    ]
}

constrainer = Constrainer(config)

# 從現有資料擴充到 100 列
result = constrainer.resample_until_satisfy(
    data=existing_data,  # 使用現有資料作為基礎
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50
)

print(f"原始資料: {len(existing_data)} 列")
print(f"最終資料: {len(result)} 列")
print(f"新增資料: {len(result) - len(existing_data)} 列")
```

### 監控重採樣過程

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# 設定非常嚴格的約束
config = {
    'field_constraints': [
        "age >= 30 & age <= 35",  # 很窄的範圍
        "salary >= 70000 & salary <= 75000",
        "performance == 5"  # 必須是最高分
    ],
    'field_combinations': [
        (
            {'education': 'salary'},
            {'PhD': [70000, 75000]}  # 只允許 PhD
        )
    ]
}

constrainer = Constrainer(config)

# 重採樣並監控過程
print("開始重採樣...")
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=50,
    synthesizer=synthesizer,
    max_trials=200,
    sampling_ratio=50.0,  # 因為約束嚴格，增加採樣比例
    verbose_step=10  # 每 10 次顯示進度
)
# Trial 10: Got 15 rows, need 35 more
# Trial 20: Got 28 rows, need 22 more
# Trial 30: Got 41 rows, need 9 more
# Trial 40: Got 50 rows, need 0 more

print(f"\n完成！")
print(f"目標列數: 50")
print(f"實際列數: {len(result)}")
print(f"總嘗試次數: {constrainer.resample_trails}")
print(f"平均每次有效資料: {len(result) / constrainer.resample_trails:.2f} 列")
```

### 處理採樣失敗

```python
from petsard import Constrainer, Synthesizer
import pandas as pd

# 設定幾乎不可能滿足的約束
config = {
    'field_constraints': [
        "age == 25 & salary == 100000"  # 極度特定的條件
    ]
}

constrainer = Constrainer(config)

# 嘗試重採樣
result = constrainer.resample_until_satisfy(
    data=pd.DataFrame(),
    target_rows=100,
    synthesizer=synthesizer,
    max_trials=50,
    sampling_ratio=100.0,
    verbose_step=10
)

if len(result) < 100:
    print(f"警告：只收集到 {len(result)} 列資料（目標 100 列）")
    print(f"嘗試次數已達上限: {constrainer.resample_trails}")
    print("建議：放寬約束條件或增加 max_trials/sampling_ratio")
else:
    print(f"成功收集到 {len(result)} 列資料")
```

### 優化採樣參數

```python
from petsard import Constrainer, Synthesizer
import pandas as pd
import time

config = {
    'field_constraints': [
        "age >= 25 & age <= 45"
    ]
}

constrainer = Constrainer(config)

# 測試不同的 sampling_ratio
for ratio in [5.0, 10.0, 20.0, 50.0]:
    start_time = time.time()

    result = constrainer.resample_until_satisfy(
        data=pd.DataFrame(),
        target_rows=100,
        synthesizer=synthesizer,
        sampling_ratio=ratio,
        verbose_step=0  # 關閉進度顯示
    )

    elapsed = time.time() - start_time

    print(f"Sampling Ratio: {ratio}")
    print(f"  嘗試次數: {constrainer.resample_trails}")
    print(f"  執行時間: {elapsed:.2f} 秒")
    print(f"  成功率: {len(result) / (constrainer.resample_trails * 100 * ratio) * 100:.2f}%")
    print()
```

## 注意事項

- **合成器狀態**：synthesizer 必須已經透過 `\1` 訓練
- **資料累積**：會自動去除重複列，確保資料多樣性
- **記憶體使用**：大 sampling_ratio 和多次迭代會消耗較多記憶體
- **參數調整**：
    - 約束嚴格時，增加 sampling_ratio
    - 合成器品質差時，增加 max_trials
    - 快速測試時，減少 target_rows
- **失敗處理**：達到 max_trials 會發出警告但仍返回已收集的資料
- **隨機性**：最終抽樣使用固定種子（random_state=42）確保可重現性
- **效能考量**：每次迭代都會完整套用所有約束，大型資料集可能較慢
- **進度顯示**：設定 verbose_step=0 可關閉進度輸出
- **比例維護**：field_proportions 會自動使用 target_rows 作為目標
- **初始資料**：提供初始 data 可加速收集過程

## 相關方法

- `\1`：初始化約束設定
- `\1`：單次套用約束
- `\1`：註冊自訂約束類型