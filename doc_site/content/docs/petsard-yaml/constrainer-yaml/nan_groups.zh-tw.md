---
title: "空值處理"
type: docs
weight: 671
prev: docs/petsard-yaml/constrainer-yaml
next: docs/petsard-yaml/constrainer-yaml/field_constraints
---

定義當特定欄位為空值時的處理方式。

## 使用範例

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/petsard-yaml/constrainer-yaml/constrainer_nan_groups.ipynb)
> **注意**：使用 Colab 請參考[執行環境設定](/petsard/docs/#colab-執行說明)。

```yaml
nan_groups:
  # 必要欄位：為空則刪除整列
  workclass: 'delete'

  # 關聯欄位：occupation 為空時，income 也應為空
  occupation:
    erase: 'income'

  # 補充欄位：age 為空時，可用 educational-num 補充
  age:
    copy: 'educational-num'

  # 條件式空值：workclass 從未工作則無 capital-gain
  capital-gain:
    nan_if_condition:
      workclass: 'Never-worked'
```

## 支援的動作

### delete - 刪除整列

當指定欄位為 NA 時，刪除整列資料。

**語法格式：**
```yaml
main_field_name: 'delete'
```

---

### erase - 清除其他欄位

當主欄位為 NA 時，將其他指定欄位設為 NA。支援單一或多個目標欄位。

**語法格式：**
```yaml
main_field_name:
  erase: 'target_field_name'
```
或
```yaml
main_field_name:
  erase:
    - 'target_field_name1'
    - 'target_field_name2'
```

---

### copy - 複製值

當主欄位有值且目標欄位為 NA 時，將主欄位的值複製到目標欄位。

**語法格式：**
```yaml
main_field_name:
  copy: 'target_field_name'
```

---

### nan_if_condition - 條件式設為空值

當條件欄位符合特定條件時，將主欄位設為 NA。

**語法格式：**
```yaml
main_field_name:
  nan_if_condition:
    condition_field_name: 'value'
```
或
```yaml
main_field_name:
  nan_if_condition:
    condition_field_name:
      - 'value1'
      - 'value2'
```

## 注意事項

- **不可逆**：delete 操作會永久移除資料列
- **謹慎使用 copy**：確保兩個欄位的值域相容
- **條件檢查**：nan_if_condition 會檢查目標欄位的值是否符合條件
- **大小寫敏感**：條件值的比對是大小寫敏感的
