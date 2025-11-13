from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from petsard.metadater.stats import DatasetsStats, FieldStats, TableStats


@dataclass
class Attribute:
    """Single column configuration (pure data, no methods)"""

    # Basic information
    name: str
    description: str | None = None

    # Data type
    type: str | None = None
    type_attr: dict[str, Any] | None = None
    logical_type: str | None = None

    # Configuration parameters (inherit or override)
    enable_optimize_type: bool = True
    enable_stats: bool = True

    # Statistics
    stats: FieldStats | None = None

    # Data processing
    na_values: list[Any] | None = None
    cast_errors: str = "coerce"
    null_strategy: str = "keep"
    default_value: Any = None

    # Constraints
    constraints: dict[str, Any] | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Syntactic sugar parameters (only for initialization, will be moved to type_attr)
    category: bool | None = None
    nullable: bool | None = None
    precision: int | None = None

    def __post_init__(self):
        """Validate and process Attribute configuration"""
        # Initialize type_attr
        if self.type_attr is None:
            self.type_attr = {}

        # Syntactic sugar processing: move flat parameters to type_attr
        # category
        if self.category is not None:
            if "category" in self.type_attr:
                raise ValueError(
                    f"Field '{self.name}' has category defined in both top-level and type_attr. "
                    f"Please define it in only one place."
                )
            self.type_attr["category"] = self.category
        # Ensure category has default value
        if "category" not in self.type_attr:
            self.type_attr["category"] = False

        # nullable
        if self.nullable is not None:
            if "nullable" in self.type_attr:
                raise ValueError(
                    f"Field '{self.name}' has nullable defined in both top-level and type_attr. "
                    f"Please define it in only one place."
                )
            self.type_attr["nullable"] = self.nullable
        # Ensure nullable has default value
        if "nullable" not in self.type_attr:
            self.type_attr["nullable"] = True

        # precision (existing, but also add check)
        if self.precision is not None:
            if "precision" in self.type_attr:
                raise ValueError(
                    f"Field '{self.name}' has precision defined in both top-level and type_attr. "
                    f"Please define it in only one place."
                )
            self.type_attr["precision"] = self.precision

        # Remove syntactic sugar attributes (maintain internal consistency)
        del self.category
        del self.nullable
        del self.precision

        # Reject type: category
        if self.type == "category":
            raise ValueError(
                f"'type: category' is not allowed. Use 'category: true' or 'type_attr.category: true' to mark categorical data. "
                f"\nField: {self.name}"
            )

        # Reject logical_type: category
        if self.logical_type == "category":
            raise ValueError(
                f"'logical_type: category' is not allowed. Use 'category: true' or 'type_attr.category: true' to mark categorical data. "
                f"\nField: {self.name}"
            )


@dataclass
class Schema:
    """Single table configuration (pure data, no methods)"""

    # Basic information
    id: str
    name: str | None = None
    description: str | None = None

    # Child objects
    attributes: dict[str, Attribute] = field(default_factory=dict)

    # Table-level settings
    primary_key: list[str] | None = None
    foreign_keys: dict[str, str] | None = None
    indexes: list[list[str]] | None = None
    sample_size: int | None = None

    # Synthetic data related
    stage: str | None = None
    parent_schema_id: str | None = None

    # Configuration parameters (inherit or override)
    enable_optimize_type: bool = True
    enable_null: bool = True
    enable_stats: bool = True  # Added: whether to calculate statistics

    # Statistics
    stats: TableStats | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Metadata:
    """Multiple tables configuration (pure data, no methods)"""

    # Basic information
    id: str
    name: str | None = None
    description: str | None = None

    # Child objects
    schemas: dict[str, Schema] = field(default_factory=dict)

    # Synthetic data pipeline
    pipeline_stages: list[str] | None = None
    schema_lineage: dict[str, list[str]] | None = None

    # Configuration parameters
    enable_optimize_type: bool = True
    enable_null: bool = True
    enable_relations: bool = True
    enable_stats: bool = True  # Added: whether to calculate statistics

    # Statistics
    stats: DatasetsStats | None = None

    # Relationship definitions
    relations: list[dict[str, Any]] | None = None

    # Diff tracking
    # Store diff records between different schemas
    # Format: {timestamp: {module: diff_result, ...}, ...}
    diffs: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Change history
    # Format: [{timestamp, module, before_id, after_id, diff}, ...]
    change_history: list[dict[str, Any]] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
