from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from petsard.exceptions import MetadataError
from petsard.metadater.metadata import Attribute, Metadata, Schema


@dataclass
class Field:
    """Single field data abstraction

    Combines pandas Series with Attribute configuration
    """

    data: pd.Series
    attribute: Attribute

    @classmethod
    def create(cls, data: pd.Series, attribute: Attribute | None = None) -> Field:
        """Create Field instance

        Auto-generates attribute from data if not provided
        """
        if attribute is None:
            from petsard.metadater.metadater import AttributeMetadater

            attribute = AttributeMetadater.from_data(data)

        return cls(data=data, attribute=attribute)

    @property
    def name(self) -> str:
        """Field name"""
        return self.attribute.name

    @property
    def dtype(self) -> str:
        """Actual data type"""
        return str(self.data.dtype)

    @property
    def expected_type(self) -> str | None:
        """Expected data type (from Attribute)"""
        return self.attribute.type

    @property
    def logical_type(self) -> str | None:
        """Logical type"""
        return self.attribute.logical_type

    @property
    def null_count(self) -> int:
        """Number of null values"""
        return self.data.isnull().sum()

    @property
    def unique_count(self) -> int:
        """Number of unique values"""
        return self.data.nunique()

    @property
    def is_valid(self) -> bool:
        """Check if data conforms to Attribute definition"""
        from petsard.metadater.metadater import AttributeMetadater

        is_valid, _ = AttributeMetadater.validate(self.attribute, self.data)
        return is_valid

    def get_validation_errors(self) -> list[str]:
        """Get validation errors"""
        from petsard.metadater.metadater import AttributeMetadater

        _, errors = AttributeMetadater.validate(self.attribute, self.data)
        return errors

    def align(self, strategy: dict[str, Any] | None = None) -> pd.Series:
        """Align data"""
        from petsard.metadater.metadater import AttributeMetadater

        return AttributeMetadater.align(self.attribute, self.data, strategy)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
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
    """Single table data abstraction

    Combines pandas DataFrame with Schema configuration
    """

    data: pd.DataFrame
    schema: Schema

    @classmethod
    def create(cls, data: pd.DataFrame, schema: Schema | None = None) -> Table:
        """Create Table instance

        Auto-generates schema from data if not provided
        """
        if schema is None:
            from petsard.metadater.metadater import SchemaMetadater

            schema = SchemaMetadater.from_data(data)

        return cls(data=data, schema=schema)

    @property
    def name(self) -> str:
        """Table name"""
        return self.schema.id

    @property
    def columns(self) -> list[str]:
        """Column list"""
        return list(self.data.columns)

    @property
    def expected_columns(self) -> list[str]:
        """Expected column list (from Schema)"""
        return list(self.schema.attributes.keys())

    @property
    def row_count(self) -> int:
        """Number of rows"""
        return len(self.data)

    @property
    def column_count(self) -> int:
        """Number of columns"""
        return len(self.data.columns)

    def get_field(self, name: str) -> Field:
        """Get specific field"""
        if name not in self.data.columns:
            raise MetadataError(
                f"Column '{name}' not found in table",
                column_name=name,
                available_columns=list(self.data.columns)
            )

        attribute = self.schema.attributes.get(name)
        # Use Field.create() to create Field instance
        return Field.create(data=self.data[name], attribute=attribute)

    def get_fields(self) -> dict[str, Field]:
        """Get all fields"""
        fields = {}
        for col in self.columns:
            fields[col] = self.get_field(col)
        return fields

    def get_missing_columns(self) -> list[str]:
        """Get missing columns (defined in Schema but not in data)"""
        return list(set(self.expected_columns) - set(self.columns))

    def get_extra_columns(self) -> list[str]:
        """Get extra columns (in data but not defined in Schema)"""
        return list(set(self.columns) - set(self.expected_columns))

    def diff(self) -> dict[str, Any]:
        """Compare data with Schema"""
        from petsard.metadater.metadater import SchemaMetadater

        return SchemaMetadater.diff(self.schema, self.data)

    def align(self, strategy: dict[str, Any] | None = None) -> pd.DataFrame:
        """Align data according to Schema"""
        from petsard.metadater.metadater import SchemaMetadater

        return SchemaMetadater.align(self.schema, self.data, strategy)

    def validate(self) -> tuple[bool, dict[str, list[str]]]:
        """Validate all fields"""
        is_valid = True
        errors = {}

        for field_name, field in self.get_fields().items():
            if not field.is_valid:
                is_valid = False
                errors[field_name] = field.get_validation_errors()

        return is_valid, errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
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
    """Multiple tables dataset abstraction

    Combines multiple DataFrames with Metadata configuration
    """

    data: dict[str, pd.DataFrame]
    metadata: Metadata

    @classmethod
    def create(
        cls, data: dict[str, pd.DataFrame], metadata: Metadata | None = None
    ) -> Datasets:
        """Create Datasets instance

        Auto-generates metadata from data if not provided
        """
        if metadata is None:
            from petsard.metadater.metadater import Metadater

            metadata = Metadater.from_data(data)

        return cls(data=data, metadata=metadata)

    @property
    def name(self) -> str:
        """Dataset name"""
        return self.metadata.id

    @property
    def table_names(self) -> list[str]:
        """Table name list"""
        return list(self.data.keys())

    @property
    def expected_tables(self) -> list[str]:
        """Expected table list (from Metadata)"""
        return list(self.metadata.schemas.keys())

    @property
    def table_count(self) -> int:
        """Number of tables"""
        return len(self.data)

    def get_table(self, name: str) -> Table:
        """Get specific table"""
        if name not in self.data:
            raise MetadataError(
                f"Table '{name}' not found in datasets",
                table_name=name,
                available_tables=list(self.data.keys())
            )

        schema = self.metadata.schemas.get(name)
        # Use Table.create() to create Table instance
        return Table.create(data=self.data[name], schema=schema)

    def get_tables(self) -> dict[str, Table]:
        """Get all tables"""
        tables = {}
        for table_name in self.table_names:
            tables[table_name] = self.get_table(table_name)
        return tables

    def get_missing_tables(self) -> list[str]:
        """Get missing tables (defined in Metadata but not in data)"""
        return list(set(self.expected_tables) - set(self.table_names))

    def get_extra_tables(self) -> list[str]:
        """Get extra tables (in data but not defined in Metadata)"""
        return list(set(self.table_names) - set(self.expected_tables))

    def diff(self) -> dict[str, Any]:
        """Compare data with Metadata"""
        from petsard.metadater.metadater import Metadater

        return Metadater.diff(self.metadata, self.data)

    def align(self, strategy: dict[str, Any] | None = None) -> dict[str, pd.DataFrame]:
        """Align data according to Metadata"""
        from petsard.metadater.metadater import Metadater

        return Metadater.align(self.metadata, self.data, strategy)

    def validate(self) -> tuple[bool, dict[str, dict[str, list[str]]]]:
        """Validate all tables"""
        is_valid = True
        errors = {}

        for table_name, table in self.get_tables().items():
            table_valid, table_errors = table.validate()
            if not table_valid:
                is_valid = False
                errors[table_name] = table_errors

        return is_valid, errors

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics"""
        stats = {"name": self.name, "table_count": self.table_count, "tables": {}}

        for table_name, table in self.get_tables().items():
            stats["tables"][table_name] = table.to_dict()

        return stats

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "table_count": self.table_count,
            "table_names": self.table_names,
            "expected_tables": self.expected_tables,
            "missing_tables": self.get_missing_tables(),
            "extra_tables": self.get_extra_tables(),
        }
