from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from petsard.metadater.metadata import Attribute, Metadata, Schema


@dataclass
class Field:
    """單一欄位的資料抽象 Single field data abstraction

    將 pandas Series 與 Attribute 設定檔結合
    Combines pandas Series with Attribute configuration
    """

    data: pd.Series
    attribute: Attribute

    @classmethod
    def create(cls, data: pd.Series, attribute: Attribute | None = None) -> Field:
        """建立 Field 實例 Create Field instance

        如果未提供 attribute，會從資料自動生成
        Auto-generates attribute from data if not provided
        """
        if attribute is None:
            from petsard.metadater.metadater import AttributeMetadater

            attribute = AttributeMetadater.from_data(data)

        return cls(data=data, attribute=attribute)

    @property
    def name(self) -> str:
        """欄位名稱 Field name"""
        return self.attribute.name

    @property
    def dtype(self) -> str:
        """實際資料類型 Actual data type"""
        return str(self.data.dtype)

    @property
    def expected_type(self) -> str | None:
        """預期的資料類型（來自 Attribute）"""
        return self.attribute.type

    @property
    def logical_type(self) -> str | None:
        """邏輯類型"""
        return self.attribute.logical_type

    @property
    def null_count(self) -> int:
        """空值數量 Number of null values"""
        return self.data.isnull().sum()

    @property
    def unique_count(self) -> int:
        """唯一值數量 Number of unique values"""
        return self.data.nunique()

    @property
    def is_valid(self) -> bool:
        """檢查資料是否符合 Attribute 定義 Check if data conforms to Attribute definition"""
        from petsard.metadater.metadater import AttributeMetadater

        is_valid, _ = AttributeMetadater.validate(self.attribute, self.data)
        return is_valid

    def get_validation_errors(self) -> list[str]:
        """取得驗證錯誤"""
        from petsard.metadater.metadater import AttributeMetadater

        _, errors = AttributeMetadater.validate(self.attribute, self.data)
        return errors

    def align(self, strategy: dict[str, Any] | None = None) -> pd.Series:
        """對齊資料"""
        from petsard.metadater.metadater import AttributeMetadater

        return AttributeMetadater.align(self.attribute, self.data, strategy)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典表示"""
        return {
            "name": self.name,
            "dtype": self.dtype,
            "expected_type": self.expected_type,
            "logical_type": self.logical_type,
            "null_count": self.null_count,
            "unique_count": self.unique_count,
            "is_valid": self.is_valid,
            "row_count": len(self.data),
        }


@dataclass
class Table:
    """單一表格的資料抽象 Single table data abstraction

    將 pandas DataFrame 與 Schema 設定檔結合
    Combines pandas DataFrame with Schema configuration
    """

    data: pd.DataFrame
    schema: Schema

    @classmethod
    def create(cls, data: pd.DataFrame, schema: Schema | None = None) -> Table:
        """建立 Table 實例 Create Table instance

        如果未提供 schema，會從資料自動生成
        Auto-generates schema from data if not provided
        """
        if schema is None:
            from petsard.metadater.metadater import SchemaMetadater

            schema = SchemaMetadater.from_data(data)

        return cls(data=data, schema=schema)

    @property
    def name(self) -> str:
        """表格名稱"""
        return self.schema.id

    @property
    def columns(self) -> list[str]:
        """欄位列表"""
        return list(self.data.columns)

    @property
    def expected_columns(self) -> list[str]:
        """預期的欄位列表（來自 Schema）"""
        return list(self.schema.attributes.keys())

    @property
    def row_count(self) -> int:
        """資料筆數"""
        return len(self.data)

    @property
    def column_count(self) -> int:
        """欄位數量"""
        return len(self.data.columns)

    def get_field(self, name: str) -> Field:
        """取得特定欄位"""
        if name not in self.data.columns:
            raise KeyError(f"Column '{name}' not found in table")

        attribute = self.schema.attributes.get(name)
        # 使用 Field.create() 來建立 Field 實例
        return Field.create(data=self.data[name], attribute=attribute)

    def get_fields(self) -> dict[str, Field]:
        """取得所有欄位"""
        fields = {}
        for col in self.columns:
            fields[col] = self.get_field(col)
        return fields

    def get_missing_columns(self) -> list[str]:
        """取得缺失的欄位（Schema 有定義但資料中沒有）"""
        return list(set(self.expected_columns) - set(self.columns))

    def get_extra_columns(self) -> list[str]:
        """取得額外的欄位（資料中有但 Schema 沒定義）"""
        return list(set(self.columns) - set(self.expected_columns))

    def diff(self) -> dict[str, Any]:
        """比較資料與 Schema 的差異"""
        from petsard.metadater.metadater import SchemaMetadater

        return SchemaMetadater.diff(self.schema, self.data)

    def align(self, strategy: dict[str, Any] | None = None) -> pd.DataFrame:
        """根據 Schema 對齊資料"""
        from petsard.metadater.metadater import SchemaMetadater

        return SchemaMetadater.align(self.schema, self.data, strategy)

    def validate(self) -> tuple[bool, dict[str, list[str]]]:
        """驗證所有欄位"""
        is_valid = True
        errors = {}

        for field_name, field in self.get_fields().items():
            if not field.is_valid:
                is_valid = False
                errors[field_name] = field.get_validation_errors()

        return is_valid, errors

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典表示"""
        return {
            "name": self.name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": self.columns,
            "expected_columns": self.expected_columns,
            "missing_columns": self.get_missing_columns(),
            "extra_columns": self.get_extra_columns(),
        }


@dataclass
class Datasets:
    """多表資料集的抽象 Multiple tables dataset abstraction

    將多個 DataFrame 與 Metadata 設定檔結合
    Combines multiple DataFrames with Metadata configuration
    """

    data: dict[str, pd.DataFrame]
    metadata: Metadata

    @classmethod
    def create(
        cls, data: dict[str, pd.DataFrame], metadata: Metadata | None = None
    ) -> Datasets:
        """建立 Datasets 實例 Create Datasets instance

        如果未提供 metadata，會從資料自動生成
        Auto-generates metadata from data if not provided
        """
        if metadata is None:
            from petsard.metadater.metadater import Metadater

            metadata = Metadater.from_data(data)

        return cls(data=data, metadata=metadata)

    @property
    def name(self) -> str:
        """資料集名稱"""
        return self.metadata.id

    @property
    def table_names(self) -> list[str]:
        """表格名稱列表"""
        return list(self.data.keys())

    @property
    def expected_tables(self) -> list[str]:
        """預期的表格列表（來自 Metadata）"""
        return list(self.metadata.schemas.keys())

    @property
    def table_count(self) -> int:
        """表格數量"""
        return len(self.data)

    def get_table(self, name: str) -> Table:
        """取得特定表格"""
        if name not in self.data:
            raise KeyError(f"Table '{name}' not found in datasets")

        schema = self.metadata.schemas.get(name)
        # 使用 Table.create() 來建立 Table 實例
        return Table.create(data=self.data[name], schema=schema)

    def get_tables(self) -> dict[str, Table]:
        """取得所有表格"""
        tables = {}
        for table_name in self.table_names:
            tables[table_name] = self.get_table(table_name)
        return tables

    def get_missing_tables(self) -> list[str]:
        """取得缺失的表格（Metadata 有定義但資料中沒有）"""
        return list(set(self.expected_tables) - set(self.table_names))

    def get_extra_tables(self) -> list[str]:
        """取得額外的表格（資料中有但 Metadata 沒定義）"""
        return list(set(self.table_names) - set(self.expected_tables))

    def diff(self) -> dict[str, Any]:
        """比較資料與 Metadata 的差異"""
        from petsard.metadater.metadater import Metadater

        return Metadater.diff(self.metadata, self.data)

    def align(self, strategy: dict[str, Any] | None = None) -> dict[str, pd.DataFrame]:
        """根據 Metadata 對齊資料"""
        from petsard.metadater.metadater import Metadater

        return Metadater.align(self.metadata, self.data, strategy)

    def validate(self) -> tuple[bool, dict[str, dict[str, list[str]]]]:
        """驗證所有表格"""
        is_valid = True
        errors = {}

        for table_name, table in self.get_tables().items():
            table_valid, table_errors = table.validate()
            if not table_valid:
                is_valid = False
                errors[table_name] = table_errors

        return is_valid, errors

    def get_statistics(self) -> dict[str, Any]:
        """取得統計資訊"""
        stats = {"name": self.name, "table_count": self.table_count, "tables": {}}

        for table_name, table in self.get_tables().items():
            stats["tables"][table_name] = table.to_dict()

        return stats

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典表示"""
        return {
            "name": self.name,
            "table_count": self.table_count,
            "table_names": self.table_names,
            "expected_tables": self.expected_tables,
            "missing_tables": self.get_missing_tables(),
            "extra_tables": self.get_extra_tables(),
        }
