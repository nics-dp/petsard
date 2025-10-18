from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from petsard.metadater.stats import DatasetsStats, FieldStats, TableStats


@dataclass
class Attribute:
    """單欄設定檔 Single column configuration (pure data, no methods)"""

    # 基本資訊
    name: str
    description: str | None = None

    # 資料類型
    type: str | None = None
    type_attr: dict[str, Any] | None = None
    category: bool | None = None
    logical_type: str | None = None

    # 配置參數 Configuration parameters (inherit or override)
    enable_optimize_type: bool = True
    enable_null: bool = True
    enable_stats: bool = True  # 新增：是否計算統計資訊

    # 統計資訊
    stats: FieldStats | None = None

    # 資料處理 Data processing
    na_values: list[Any] | None = None
    cast_errors: str = "coerce"
    null_strategy: str = "keep"
    default_value: Any = None

    # 約束條件
    constraints: dict[str, Any] | None = None

    # 時間資訊
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """驗證 Attribute 配置"""
        # 拒絕 type: category
        if self.type == "category":
            raise ValueError(
                f"不允許使用 'type: category'。請使用 'category: true' 參數來標記分類資料。"
                f"\n欄位: {self.name}"
            )

        # 拒絕 logical_type: category
        if self.logical_type == "category":
            raise ValueError(
                f"不允許使用 'logical_type: category'。請使用 'category: true' 參數來標記分類資料。"
                f"\n欄位: {self.name}"
            )


@dataclass
class Schema:
    """單表設定檔 Single table configuration (pure data, no methods)"""

    # 基本資訊 Basic information
    id: str
    name: str | None = None
    description: str | None = None

    # 子物件
    attributes: dict[str, Attribute] = field(default_factory=dict)

    # 表級設定
    primary_key: list[str] | None = None
    foreign_keys: dict[str, str] | None = None
    indexes: list[list[str]] | None = None
    sample_size: int | None = None

    # 合成資料相關
    stage: str | None = None
    parent_schema_id: str | None = None

    # 配置參數（繼承或覆寫）
    enable_optimize_type: bool = True
    enable_null: bool = True
    enable_stats: bool = True  # 新增：是否計算統計資訊

    # 統計資訊
    stats: TableStats | None = None

    # 時間資訊 Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Metadata:
    """多表設定檔 Multiple tables configuration (pure data, no methods)"""

    # 基本資訊 Basic information
    id: str
    name: str | None = None
    description: str | None = None

    # 子物件
    schemas: dict[str, Schema] = field(default_factory=dict)

    # 合成資料流程
    pipeline_stages: list[str] | None = None
    schema_lineage: dict[str, list[str]] | None = None

    # 配置參數 Configuration parameters
    enable_optimize_type: bool = True
    enable_null: bool = True
    enable_relations: bool = True
    enable_stats: bool = True  # 新增：是否計算統計資訊

    # 統計資訊
    stats: DatasetsStats | None = None

    # 關係定義 Relationship definitions
    relations: list[dict[str, Any]] | None = None

    # 差異追蹤 Diff tracking
    # 儲存不同 schema 之間的差異記錄
    # 格式: {timestamp: {module: diff_result, ...}, ...}
    diffs: dict[str, dict[str, Any]] = field(default_factory=dict)

    # 變更歷史 Change history
    # 格式: [{timestamp, module, before_id, after_id, diff}, ...]
    change_history: list[dict[str, Any]] = field(default_factory=list)

    # 時間資訊 Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
