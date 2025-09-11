---
title: "YAML 教學"
weight: 200
---

使用 YAML 設定檔配置 PETsARD 模組。

## 概述

PETsARD 支援使用 YAML 設定檔來配置各個模組，提供宣告式的配置方式，不需要撰寫程式碼即可完成大部分工作。

## YAML 設定優勢

### 1. 宣告式配置
不需要撰寫程式碼，只需要編寫設定檔：
<!-- ```yaml
loader:
  type: csv
  source: data/users.csv
  config:
    encoding: utf-8
``` -->

### 2. 易於版本控制
純文字格式，方便追蹤變更和協作。

### 3. 環境變數支援
敏感資訊可以使用環境變數：
<!-- ```yaml
database:
  connection: ${DATABASE_URL}
  password: ${DB_PASSWORD}
``` -->

### 4. 批次處理
一個設定檔可以定義多個操作：
<!-- ```yaml
loaders:
  - name: users
    type: csv
    source: users.csv
  - name: orders
    type: excel
    source: orders.xlsx
``` -->

<!-- ## 使用方式

### Python 整合
```python
from petsard import PETsARD

# 載入 YAML 設定
petsard = PETsARD.from_yaml('config.yaml')

# 執行處理
result = petsard.run()
```

### 命令列工具
```bash
# 使用 YAML 設定執行
petsard run --config config.yaml

# 驗證設定檔
petsard validate --config config.yaml -->