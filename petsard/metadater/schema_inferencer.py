"""
Schema Inferencer: Infer Schema changes at each stage of the pipeline

This module is responsible for inferring the input and output SchemaMetadata
for each module (Loader → Preprocessor → Synthesizer → Postprocessor → Evaluator)
in the entire pipeline based on YAML configuration during Executor initialization.

Main functions:
1. Track how Processor transforms change field dtypes and attributes
2. Predict input/output Schema for each module
3. Provide dtype consistency validation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from petsard.metadater.metadata import Attribute, Schema


@dataclass
class TransformRule:
    """Single transformation rule

    Describes how a Processor changes field attributes
    """

    processor_type: str  # 'missing', 'outlier', 'encoder', 'scaler', 'discretizing'
    processor_method: str  # Specific method, e.g. 'encoder_onehot', 'scaler_standard'

    # Transform rules
    input_types: list[str] | None = None  # Applicable input types, None means all
    output_type: str | None = None  # Output type, None means keep unchanged
    output_logical_type: str | None = None  # Output logical type

    # Special behaviors
    creates_columns: bool = False  # Whether to create new columns (e.g. OneHot)
    removes_columns: bool = False  # Whether to remove original column
    column_suffix: str | None = None  # Suffix pattern for new columns

    # Attribute changes
    affects_nullable: bool = False  # Whether affects nullability
    nullable_after: bool | None = None  # Nullability after transformation

    context: dict[str, Any] = field(default_factory=dict)  # Additional context


class ProcessorTransformRules:
    """Processor transformation rule repository

    Defines how each Processor changes Schema
    """

    # Define all known transformation rules
    RULES: dict[str, TransformRule] = {
        # === Missing Handlers ===
        "missing_drop": TransformRule(
            processor_type="missing",
            processor_method="missing_drop",
            affects_nullable=True,
            nullable_after=False,
            context={
                "description": "Remove rows containing missing values, field no longer has null"
            },
        ),
        "missing_mean": TransformRule(
            processor_type="missing",
            processor_method="missing_mean",
            input_types=["numerical"],
            affects_nullable=True,
            nullable_after=False,
            context={"description": "Fill with mean, field no longer has null"},
        ),
        "missing_median": TransformRule(
            processor_type="missing",
            processor_method="missing_median",
            input_types=["numerical"],
            affects_nullable=True,
            nullable_after=False,
            context={"description": "Fill with median, field no longer has null"},
        ),
        "missing_mode": TransformRule(
            processor_type="missing",
            processor_method="missing_mode",
            affects_nullable=True,
            nullable_after=False,
            context={"description": "Fill with mode, field no longer has null"},
        ),
        "missing_simple": TransformRule(
            processor_type="missing",
            processor_method="missing_simple",
            affects_nullable=True,
            nullable_after=False,
            context={"description": "Simple fill strategy, field no longer has null"},
        ),
        # === Outlier Handlers ===
        # Outlier handling usually keeps type unchanged, but may remove some rows
        "outlier_iqr": TransformRule(
            processor_type="outlier",
            processor_method="outlier_iqr",
            input_types=["numerical", "datetime"],
            context={"description": "IQR outlier handling, keeps type unchanged"},
        ),
        "outlier_zscore": TransformRule(
            processor_type="outlier",
            processor_method="outlier_zscore",
            input_types=["numerical"],
            context={"description": "Z-Score outlier handling, keeps type unchanged"},
        ),
        "outlier_lof": TransformRule(
            processor_type="outlier",
            processor_method="outlier_lof",
            input_types=["numerical"],
            context={"description": "LOF outlier handling, keeps type unchanged"},
        ),
        "outlier_isolationforest": TransformRule(
            processor_type="outlier",
            processor_method="outlier_isolationforest",
            input_types=["numerical"],
            context={
                "description": "Isolation Forest outlier handling, keeps type unchanged"
            },
        ),
        # === Encoders ===
        "encoder_label": TransformRule(
            processor_type="encoder",
            processor_method="encoder_label",
            input_types=["categorical", "string"],
            output_type="int",
            output_logical_type="encoded_categorical",
            context={"description": "Label encoding, categorical to integer"},
        ),
        "encoder_onehot": TransformRule(
            processor_type="encoder",
            processor_method="encoder_onehot",
            input_types=["categorical", "string"],
            output_type="int",
            output_logical_type="onehot_encoded",
            creates_columns=True,
            removes_columns=True,
            context={
                "description": "One-hot encoding, creates multiple binary columns"
            },
        ),
        "encoder_uniform": TransformRule(
            processor_type="encoder",
            processor_method="encoder_uniform",
            input_types=["categorical", "string"],
            output_type="float",
            output_logical_type="uniform_encoded",
            context={
                "description": "Uniform encoding, categorical to uniformly distributed float"
            },
        ),
        "encoder_datediff": TransformRule(
            processor_type="encoder",
            processor_method="encoder_datediff",
            input_types=["datetime"],
            output_type="int",
            output_logical_type="date_diff_days",
            context={
                "description": "Date diff encoding, calculate days difference from reference date"
            },
        ),
        # === Scalers ===
        "scaler_standard": TransformRule(
            processor_type="scaler",
            processor_method="scaler_standard",
            input_types=["numerical", "datetime"],
            output_type="float",
            output_logical_type="standardized",
            context={
                "description": "Standardization, convert to float with mean 0 and std 1"
            },
        ),
        "scaler_minmax": TransformRule(
            processor_type="scaler",
            processor_method="scaler_minmax",
            input_types=["numerical", "datetime"],
            output_type="float",
            output_logical_type="normalized",
            context={
                "description": "Min-Max normalization, convert to float in [0,1] range"
            },
        ),
        "scaler_log": TransformRule(
            processor_type="scaler",
            processor_method="scaler_log",
            input_types=["numerical"],
            output_type="float",
            output_logical_type="log_transformed",
            context={"description": "Log transformation"},
        ),
        "scaler_log1p": TransformRule(
            processor_type="scaler",
            processor_method="scaler_log1p",
            input_types=["numerical"],
            output_type="float",
            output_logical_type="log1p_transformed",
            context={"description": "Log(1+x) transformation"},
        ),
        "scaler_zerocenter": TransformRule(
            processor_type="scaler",
            processor_method="scaler_zerocenter",
            input_types=["numerical", "datetime"],
            output_type="float",
            output_logical_type="zero_centered",
            context={"description": "Zero centering"},
        ),
        "scaler_timeanchor": TransformRule(
            processor_type="scaler",
            processor_method="scaler_timeanchor",
            input_types=["datetime"],
            output_type="float",
            output_logical_type="time_anchored",
            context={"description": "Time anchor standardization"},
        ),
        # === Discretizing ===
        "discretizing_kbins": TransformRule(
            processor_type="discretizing",
            processor_method="discretizing_kbins",
            input_types=["numerical", "datetime"],
            output_type="int",
            output_logical_type="discretized",
            context={
                "description": "K-Bins discretization, continuous values to discrete intervals"
            },
        ),
    }

    @classmethod
    def get_rule(cls, processor_method: str) -> TransformRule | None:
        """Get transformation rule for specified processor"""
        return cls.RULES.get(processor_method)

    @classmethod
    def apply_rule(cls, attribute: Attribute, rule: TransformRule) -> Attribute:
        """Apply transformation rule to Attribute

        Args:
            attribute: Original Attribute
            rule: Transformation rule

        Returns:
            Transformed Attribute (new instance)
        """
        # Determine if type has changed
        output_type = rule.output_type if rule.output_type else attribute.type
        type_changed = output_type != attribute.type

        # Copy and update type_attr
        type_attr = (attribute.type_attr or {}).copy()

        # Update nullable (if rule affects)
        if rule.affects_nullable:
            type_attr["nullable"] = rule.nullable_after

        # category defaults to unchanged (inherited from original type_attr)

        # Create new Attribute, preserving most original information
        new_attr_dict = {
            "name": attribute.name,
            "description": attribute.description,
            "type": output_type,
            "type_attr": type_attr,
            "logical_type": rule.output_logical_type
            if rule.output_logical_type
            else attribute.logical_type,
            "enable_optimize_type": attribute.enable_optimize_type,
            "enable_stats": attribute.enable_stats,
            "stats": None,  # Statistics change after transformation, temporarily set to None
            "na_values": attribute.na_values,
            "cast_errors": attribute.cast_errors,
            "null_strategy": attribute.null_strategy,
            "default_value": attribute.default_value,
            "constraints": attribute.constraints,
            "created_at": attribute.created_at,
            "updated_at": datetime.now(),
        }

        return Attribute(**new_attr_dict)

    @classmethod
    def apply_transform_info(
        cls, attribute: Attribute, transform_info: dict[str, Any]
    ) -> Attribute:
        """Apply SCHEMA_TRANSFORM information obtained from Processor class

        Args:
            attribute: Original Attribute
            transform_info: Transformation information obtained from Processor.get_schema_transform_info()

        Returns:
            Transformed Attribute (new instance)
        """
        # Determine if type has changed
        output_type = transform_info.get("output_type") or attribute.type
        type_changed = output_type != attribute.type

        # Copy and update type_attr
        type_attr = (attribute.type_attr or {}).copy()

        # Update category (if specified)
        if transform_info.get("output_category") is not None:
            type_attr["category"] = transform_info["output_category"]

        # Update nullable (if rule affects)
        if transform_info.get("affects_nullable"):
            type_attr["nullable"] = transform_info.get("nullable_after", True)

        # Create new Attribute, preserving most original information
        new_attr_dict = {
            "name": attribute.name,
            "description": attribute.description,
            "type": output_type,
            "type_attr": type_attr,
            "logical_type": transform_info.get("output_logical_type")
            or attribute.logical_type,
            "enable_optimize_type": attribute.enable_optimize_type,
            "enable_stats": attribute.enable_stats,
            "stats": None,  # Statistics change after transformation, temporarily set to None
            "na_values": attribute.na_values,
            "cast_errors": attribute.cast_errors,
            "null_strategy": attribute.null_strategy,
            "default_value": attribute.default_value,
            "constraints": attribute.constraints,
            "created_at": attribute.created_at,
            "updated_at": datetime.now(),
        }

        return Attribute(**new_attr_dict)


class SchemaInferencer:
    """Schema Inferencer

    Infer Schema changes based on Processor configuration
    """

    def __init__(self):
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._inference_history: list[dict[str, Any]] = []

    def infer_preprocessor_output(
        self, input_schema: Schema, processor_config: dict[str, dict[str, Any]]
    ) -> Schema:
        """Infer Preprocessor output Schema

        Args:
            input_schema: Input Schema (from Loader)
            processor_config: Processor configuration

        Returns:
            Inferred output Schema
        """
        self.logger.debug(
            f"Inferring Preprocessor output Schema, input fields: {len(input_schema.attributes)}"
        )

        # Check if using 'default' method
        # If so, need to generate complete configuration (simulate Processor._generate_config())
        if self._is_using_default_method(processor_config):
            self.logger.info(
                "Detected using 'default' method, will generate configuration based on DefaultProcessorMap"
            )
            processor_config = self._generate_default_config(input_schema)

        # Deep copy input Schema as base
        output_attributes = {}

        # Track field changes
        inference_record = {
            "timestamp": datetime.now().isoformat(),
            "stage": "preprocessor",
            "changes": [],
        }

        # Iterate through each field and its processor configuration
        for col_name, input_attr in input_schema.attributes.items():
            current_attr = input_attr
            col_changes = []

            # Apply each processor type in order
            for processor_type in [
                "missing",
                "outlier",
                "encoder",
                "scaler",
                "discretizing",
            ]:
                if processor_type not in processor_config:
                    continue

                col_config = processor_config[processor_type].get(col_name)
                if not col_config:
                    continue

                # Get processor method name
                if isinstance(col_config, str):
                    method_name = col_config
                elif isinstance(col_config, dict) and "method" in col_config:
                    method_name = col_config["method"]
                else:
                    continue

                # First try to get dynamic SCHEMA_TRANSFORM from Processor class
                transform_info = self._get_processor_transform_info(
                    processor_type, method_name
                )

                if transform_info:
                    # Use dynamically obtained transformation information
                    # Check if input type and category match
                    if transform_info.get("input_types"):
                        current_type = self._get_data_category(current_attr)
                        if current_type not in transform_info["input_types"]:
                            self.logger.warning(
                                f"Field '{col_name}' type '{current_type}' "
                                f"does not match expected input types {transform_info['input_types']} for '{method_name}'"
                            )
                            continue

                    if transform_info.get("input_category") is not None:
                        current_category = (current_attr.type_attr or {}).get(
                            "category", False
                        )
                        if current_category != transform_info["input_category"]:
                            self.logger.warning(
                                f"Field '{col_name}' category={current_category} "
                                f"does not match expected input_category={transform_info['input_category']} for '{method_name}'"
                            )
                            continue

                    # Apply transformation
                    new_attr = ProcessorTransformRules.apply_transform_info(
                        current_attr, transform_info
                    )
                    # Read category from type_attr
                    category_before = (current_attr.type_attr or {}).get(
                        "category", False
                    )
                    category_after = (new_attr.type_attr or {}).get("category", False)
                    col_changes.append(
                        {
                            "processor": processor_type,
                            "method": method_name,
                            "type_before": current_attr.type,
                            "type_after": new_attr.type,
                            "category_before": category_before,
                            "category_after": category_after,
                            "logical_type_before": current_attr.logical_type,
                            "logical_type_after": new_attr.logical_type,
                        }
                    )
                    current_attr = new_attr

                    self.logger.debug(
                        f"Applied {method_name} to field '{col_name}': "
                        f"type: {col_changes[-1]['type_before']} → {col_changes[-1]['type_after']}, "
                        f"category: {col_changes[-1]['category_before']} → {col_changes[-1]['category_after']}"
                    )
                else:
                    # Fall back to static rules
                    rule = ProcessorTransformRules.get_rule(method_name)
                    if rule:
                        # Check if input type matches
                        if rule.input_types:
                            current_type = self._get_data_category(current_attr)
                            if current_type not in rule.input_types:
                                self.logger.warning(
                                    f"Field '{col_name}' type '{current_type}' "
                                    f"does not match expected input types {rule.input_types} for '{method_name}'"
                                )
                                continue

                        # Apply transformation
                        new_attr = ProcessorTransformRules.apply_rule(
                            current_attr, rule
                        )
                        col_changes.append(
                            {
                                "processor": processor_type,
                                "method": method_name,
                                "type_before": current_attr.type,
                                "type_after": new_attr.type,
                                "logical_type_before": current_attr.logical_type,
                                "logical_type_after": new_attr.logical_type,
                            }
                        )
                        current_attr = new_attr

                        self.logger.debug(
                            f"Applied {method_name} to field '{col_name}': "
                            f"{col_changes[-1]['type_before']} → {col_changes[-1]['type_after']}"
                        )

            output_attributes[col_name] = current_attr
            if col_changes:
                inference_record["changes"].append(
                    {"column": col_name, "transformations": col_changes}
                )

        # Record inference history
        self._inference_history.append(inference_record)

        # Create output Schema
        output_schema = Schema(
            id=f"{input_schema.id}_preprocessed",
            name=f"{input_schema.name} (Preprocessed)",
            description=f"Preprocessed schema from {input_schema.id}",
            attributes=output_attributes,
            primary_key=input_schema.primary_key,
            foreign_keys=input_schema.foreign_keys,
            indexes=input_schema.indexes,
            sample_size=input_schema.sample_size,
            stage="preprocessed",
            parent_schema_id=input_schema.id,
            enable_optimize_type=input_schema.enable_optimize_type,
            enable_stats=False,  # Inferred Schema has no statistics
            stats=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.logger.info(
            f"Inference complete: input {len(input_schema.attributes)} fields → "
            f"output {len(output_attributes)} fields"
        )

        return output_schema

    def _get_processor_transform_info(
        self, processor_type: str, method_name: str
    ) -> dict[str, Any] | None:
        """Dynamically get SCHEMA_TRANSFORM information from Processor class

        Args:
            processor_type: Processor type (encoder, scaler, etc.)
            method_name: Processor method name

        Returns:
            SCHEMA_TRANSFORM dictionary, None if unable to obtain
        """
        try:
            # Dynamically import Processor class
            from petsard.processor.base import ProcessorClassMap

            processor_class = ProcessorClassMap.get_class(method_name)
            if processor_class and hasattr(
                processor_class, "get_schema_transform_info"
            ):
                transform_info = processor_class.get_schema_transform_info()
                self.logger.debug(
                    f"Get SCHEMA_TRANSFORM from {processor_class.__name__}: {transform_info}"
                )
                return transform_info
        except Exception as e:
            self.logger.debug(
                f"Unable to get dynamic SCHEMA_TRANSFORM from {method_name}: {e}"
            )

        return None

    def _get_data_category(self, attribute: Attribute) -> str:
        """Infer data category from Attribute

        Map Attribute's type to categories used by processors:
        numerical, categorical, datetime, object

        Simplified type system: int, float, str, date, datetime
        """
        if not attribute.type:
            return "object"

        type_str = str(attribute.type).lower()

        # Simplified type judgment
        if type_str == "int" or type_str == "float":
            return "numerical"
        elif type_str == "str":
            # str type: check category attribute to determine if categorical
            if attribute.type_attr and attribute.type_attr.get("category") is True:
                return "categorical"
            else:
                return "categorical"  # str defaults to categorical
        elif type_str in ["date", "datetime"]:
            return "datetime"
        elif attribute.type_attr and attribute.type_attr.get("category") is True:
            return "categorical"
        else:
            return "object"

    def get_inference_history(self) -> list[dict[str, Any]]:
        """Get inference history records"""
        return self._inference_history

    def infer_pipeline_schemas(
        self, loader_schema: Schema, pipeline_config: dict[str, Any]
    ) -> dict[str, Schema]:
        """Infer Schema changes across entire pipeline

        Args:
            loader_schema: Schema output by Loader
            pipeline_config: Pipeline configuration (parsed from YAML)

        Returns:
            Dictionary of Schemas for each stage
        """
        schemas = {"Loader": loader_schema}

        # Infer Preprocessor output
        if "Preprocessor" in pipeline_config:
            preprocessor_config = pipeline_config["Preprocessor"]
            schemas["Preprocessor"] = self.infer_preprocessor_output(
                loader_schema, preprocessor_config
            )

        # Synthesizer and Postprocessor usually keep Schema unchanged
        # (unless there are special configurations)
        if "Preprocessor" in schemas:
            schemas["Synthesizer"] = schemas["Preprocessor"]
            schemas["Postprocessor"] = schemas["Preprocessor"]

        return schemas

    def _is_using_default_method(self, processor_config: dict[str, Any]) -> bool:
        """Check if using default method

        Args:
            processor_config: Processor configuration

        Returns:
            True if using default method
        """
        # Check if configuration structure is {"default": {"method": "default"}}
        if len(processor_config) == 1 and "default" in processor_config:
            default_config = processor_config["default"]
            if (
                isinstance(default_config, dict)
                and default_config.get("method") == "default"
            ):
                return True
        return False

    def _generate_default_config(self, schema: Schema) -> dict[str, dict[str, Any]]:
        """Generate default configuration (simulate Processor._generate_config())

        This method copies the logic of Processor._generate_config(),
        assigns processor for each field based on DefaultProcessorMap

        Args:
            schema: Input Schema

        Returns:
            Complete processor configuration
        """
        from petsard.processor.base import DefaultProcessorMap

        field_names = list(schema.attributes.keys())
        config: dict = {
            processor: dict.fromkeys(field_names)
            for processor in DefaultProcessorMap.VALID_TYPES
        }

        for col in field_names:
            # Use same logic as Processor._get_field_infer_dtype()
            infer_dtype = self._get_field_infer_dtype(schema.attributes[col])

            for processor, obj in DefaultProcessorMap.PROCESSOR_MAP.items():
                processor_class = obj[infer_dtype]
                # Convert processor class to method name
                if processor_class is None or (
                    callable(processor_class) and processor_class() is None
                ):
                    config[processor][col] = None
                else:
                    # Derive method name from class name
                    # Example: EncoderUniform → encoder_uniform
                    class_name = processor_class.__name__
                    # Convert to snake_case
                    method_name = self._class_name_to_method_name(class_name)
                    config[processor][col] = method_name

        self.logger.debug(f"Generated default configuration: {config}")
        return config

    def _get_field_infer_dtype(self, attribute: Attribute) -> str:
        """Get field's inferred data type (simulate Processor._get_field_infer_dtype())

        Args:
            attribute: Field attribute

        Returns:
            Inferred data type: 'numerical', 'categorical', 'datetime', 'object'

        Simplified type system: int, float, str, date, datetime
        """
        # Simplified type judgment logic
        data_type_str = str(attribute.type).lower() if attribute.type else "object"

        # Simplified type mapping
        if data_type_str == "int" or data_type_str == "float":
            return "numerical"
        elif data_type_str == "str":
            # str type: check category attribute
            if attribute.type_attr and attribute.type_attr.get("category") is True:
                return "categorical"
            else:
                return "categorical"  # str defaults to categorical
        elif data_type_str in ["date", "datetime"]:
            return "datetime"
        elif attribute.type_attr and attribute.type_attr.get("category") is True:
            return "categorical"
        else:
            return "object"

    def _class_name_to_method_name(self, class_name: str) -> str:
        """Convert class name to method name

        Example: EncoderUniform → encoder_uniform

        Args:
            class_name: Class name

        Returns:
            Method name (snake_case)
        """
        # Convert CamelCase to snake_case
        import re

        # Insert underscore before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        # Handle consecutive uppercase letters
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
