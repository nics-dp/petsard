import itertools
from dataclasses import dataclass, field

import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer


@dataclass
class FieldProportionsConfig:
    """
    Configuration class for defining field proportion preservation.

    Attributes:
        field_proportions (list[dict]): List containing field proportion preservation rules. Each rule is a dictionary containing:
            - fields: Field name (str) or field list (list[str])
            - mode: Can be 'all' (all value distribution) or 'missing' (missing values only)
            - tolerance: (Optional) Maximum difference allowed between original and filtered proportions, default 0.1 (10%)

        original_proportions (dict): Stores proportion distribution of each field in original data.
            Calculated and stored during verify_data phase to avoid repeated calculations during checking.

        metadata: Optional Schema object for field type checking

    Methods:
        verify_data(data: pd.DataFrame, target_n_rows: int) -> None:
            Verify if all required fields exist in data, check if configuration is valid, and calculate proportion distribution of original data.

        check_proportions(filtered_data: pd.DataFrame) -> tuple[bool, list[dict]]:
            Check if filtered data maintains proportion requirements for specified fields, and return detailed violation information.
    """

    field_proportions: list[dict] = field(default_factory=list)
    original_proportions: dict = field(default_factory=dict)
    target_n_rows: int = field(default=None, init=False)  # Set internally
    metadata: object = field(default=None)  # Schema object for type checking

    def __post_init__(self):
        """Validate configuration validity"""
        valid_modes: list[str] = ["all", "missing"]
        msgs: list[str] = []
        seen_fields: set = set()

        for i, proportion_rule in enumerate(self.field_proportions):
            # Check if rule is a dictionary
            if not isinstance(proportion_rule, dict):
                msg = f"Error: Rule {i + 1} should be a dictionary: {proportion_rule}"
                msgs.append(msg)
                continue

            # Check required keys
            required_keys = {"fields", "mode"}
            if not required_keys.issubset(proportion_rule.keys()):
                missing_keys = required_keys - set(proportion_rule.keys())
                msg = f"Error: Rule {i + 1} missing required keys: {missing_keys}"
                msgs.append(msg)
                continue

            fields = proportion_rule["fields"]
            mode = proportion_rule["mode"]
            tolerance = proportion_rule.get("tolerance", 0.1)  # Default 0.1 (10%)

            # Check field format
            if isinstance(fields, str):
                # Single field
                field_key = fields
            elif isinstance(fields, list):
                # Field list
                if not fields:
                    msg = f"Error: Rule {i + 1} field list cannot be empty"
                    msgs.append(msg)
                    continue

                # Check if each element in list is a string
                for field in fields:
                    if not isinstance(field, str):
                        msg = f"Error: Elements in rule {i + 1} field list should all be strings: {field}"
                        msgs.append(msg)

                field_key = tuple(fields)
            else:
                msg = f"Error: Fields in rule {i + 1} should be string or string list: {fields}"
                msgs.append(msg)
                continue

            # Check field duplication
            if field_key in seen_fields:
                msg = f"Error: Field {field_key} in rule {i + 1} is duplicated"
                msgs.append(msg)
            else:
                seen_fields.add(field_key)

            # Check if mode is valid
            if mode not in valid_modes:
                msg = f"Error: Mode '{mode}' in rule {i + 1} not in {valid_modes}"
                msgs.append(msg)

            # Check if tolerance is a valid number (if provided)
            if (
                not isinstance(tolerance, (int, float))
                or tolerance < 0
                or tolerance > 1
            ):
                msg = f"Error: Tolerance in rule {i + 1} should be a number between 0 and 1: {tolerance}"
                msgs.append(msg)

        if any(msgs):
            raise ValueError("\n".join(map(str, msgs)))

    def verify_data(self, data: pd.DataFrame, target_n_rows: int) -> None:
        """
        Verify if all required fields exist in data, check if configuration is valid, and calculate proportion distribution of original data.

        Args:
            data (pd.DataFrame): DataFrame to verify.
            target_n_rows (int): Expected number of rows after filtering.

        Raises:
            ValueError: When required fields are missing, field types are unsupported, or configuration is invalid.
        """
        # Set target_n_rows
        if target_n_rows is None or target_n_rows <= 0:
            raise ValueError("target_n_rows must be a positive integer")
        self.target_n_rows = target_n_rows

        # Collect all required field names
        required_fields = set()
        for rule in self.field_proportions:
            fields = rule["fields"]
            if isinstance(fields, str):
                required_fields.add(fields)
            elif isinstance(fields, list):
                required_fields.update(fields)

        # Check if all required fields exist in data
        missing_fields = required_fields - set(data.columns)
        if missing_fields:
            raise ValueError(f"Missing fields in data: {missing_fields}")

        # Check if field types are categorical variables
        # field_proportions only supports categorical variables, not continuous numerical or datetime fields
        unsupported_fields = []
        for field in required_fields:
            # Use metadata for type checking if available
            if self.metadata is not None:
                # Find the attribute in metadata by accessing dict values
                attribute = self.metadata.attributes.get(field)

                if attribute is None:
                    # Field not in metadata, fall back to dtype check
                    dtype = data[field].dtype
                    field_type = self._infer_type_from_dtype(dtype)
                else:
                    # Infer type from attribute properties
                    field_type = self._infer_type_from_attribute(attribute)

                # Reject numeric and datetime types
                if field_type in ["numerical", "datetime"]:
                    unsupported_fields.append(
                        f"{field} (type: {field_type} [from metadata], unsupported)"
                    )
            else:
                # Fall back to DataFrame dtype checking
                dtype = data[field].dtype
                # Reject pure numerical (int, float) and datetime types
                if pd.api.types.is_numeric_dtype(dtype):
                    unsupported_fields.append(
                        f"{field} (type: {dtype}, numerical unsupported)"
                    )
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    unsupported_fields.append(
                        f"{field} (type: {dtype}, datetime unsupported)"
                    )

        if unsupported_fields:
            raise ValueError(
                "field_proportions only supports categorical fields. "
                "The following field types are unsupported:\n  "
                + "\n  ".join(unsupported_fields)
                + "\n\nPlease ensure these fields have their type set to 'category' or other categorical logical types in the schema."
            )

        # Calculate proportion distribution of original data
        self.original_proportions = {}
        self.min_max_counts = {}  # Store min and max sample counts for each condition

        for rule in self.field_proportions:
            fields = rule["fields"]
            mode = rule["mode"]
            tolerance = rule.get("tolerance", 0.1)  # Default 0.1 (10%)

            # Handle single field
            if isinstance(fields, str):
                field = fields
                if field not in data.columns:
                    continue

                key = (field, mode)

                # Calculate 'all' mode - distribution of all values
                if mode == "all" and key not in self.original_proportions:
                    # Calculate original proportions
                    value_counts = (
                        data[field].value_counts(dropna=False, normalize=True).to_dict()
                    )
                    self.original_proportions[key] = value_counts

                    # Calculate min and max sample counts for each value
                    count_bounds = {}
                    for value, prop in value_counts.items():
                        target_count = int(prop * self.target_n_rows)
                        # Min sample count: original proportion minus tolerance, times target rows
                        min_count = int((prop - tolerance) * self.target_n_rows)
                        # Max sample count: original proportion plus tolerance, times target rows
                        max_count = int((prop + tolerance) * self.target_n_rows)
                        count_bounds[value] = {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    self.min_max_counts[key] = count_bounds

                # Calculate 'missing' mode - proportion of missing values only
                elif mode == "missing" and key not in self.original_proportions:
                    missing_prop = data[field].isna().mean()
                    self.original_proportions[key] = missing_prop

                    # Calculate min and max sample counts for missing values
                    target_count = int(missing_prop * self.target_n_rows)
                    min_count = int((missing_prop - tolerance) * self.target_n_rows)
                    max_count = int((missing_prop + tolerance) * self.target_n_rows)
                    self.min_max_counts[key] = {
                        "Missing": {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    }

            # Handle field combinations (list format)
            elif isinstance(fields, list):
                fields_tuple = tuple(fields)
                # Check if all fields exist
                all_fields_exist = all(field in data.columns for field in fields)
                if not all_fields_exist:
                    continue

                key = (fields_tuple, mode)

                # Handle 'missing' mode
                if mode == "missing" and key not in self.original_proportions:
                    # Create combinations indicating whether each field is null
                    missing_patterns = {}
                    count_bounds = {}

                    # Create isna() markers for each field
                    isna_df = pd.DataFrame()
                    for field in fields:
                        isna_df[f"{field}_isna"] = data[field].isna()

                    # Calculate proportion of each missing pattern
                    patterns = list(
                        itertools.product([True, False], repeat=len(fields))
                    )
                    for pattern in patterns:
                        mask = pd.Series(True, index=data.index)
                        for i, field in enumerate(fields):
                            if pattern[i]:
                                mask &= isna_df[f"{field}_isna"]
                            else:
                                mask &= ~isna_df[f"{field}_isna"]

                        pattern_key = pattern
                        pattern_prop = mask.mean()
                        missing_patterns[pattern_key] = pattern_prop

                        target_count = int(pattern_prop * self.target_n_rows)
                        # Calculate min and max sample counts for each pattern
                        min_count = int((pattern_prop - tolerance) * self.target_n_rows)
                        max_count = int((pattern_prop + tolerance) * self.target_n_rows)

                        # Create readable description of pattern
                        pattern_desc = ", ".join(
                            [
                                f"{fields[i]}:{'Missing' if p else 'Not Missing'}"
                                for i, p in enumerate(pattern)
                            ]
                        )

                        count_bounds[pattern_key] = {
                            "desc": pattern_desc,
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }

                    self.original_proportions[key] = missing_patterns
                    self.min_max_counts[key] = count_bounds

                # Handle 'all' mode
                elif mode == "all" and key not in self.original_proportions:
                    # Create combined value for field combinations
                    combined = data[fields].apply(lambda row: tuple(row), axis=1)

                    # Calculate proportion of each combined value
                    value_counts = combined.value_counts(
                        dropna=False, normalize=True
                    ).to_dict()
                    self.original_proportions[key] = value_counts

                    # Calculate min and max sample counts for each combined value
                    count_bounds = {}
                    for value, prop in value_counts.items():
                        target_count = int(prop * self.target_n_rows)
                        min_count = int((prop - tolerance) * self.target_n_rows)
                        max_count = int((prop + tolerance) * self.target_n_rows)
                        count_bounds[value] = {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    self.min_max_counts[key] = count_bounds

        # Final adjustment of min_max: avoid floating point arithmetic issues
        for idx, props in self.min_max_counts.items():
            for value, counts in props.items():
                curr_min: int = counts["min"]
                curr_max: int = counts["max"]
                target: int = counts["target"]

                if target == 0:
                    self.min_max_counts[idx][value]["min"] = 0
                    self.min_max_counts[idx][value]["max"] = 0
                else:
                    self.min_max_counts[idx][value]["min"] = max(1, curr_min)

                if target == self.target_n_rows:
                    self.min_max_counts[idx][value]["min"] = self.target_n_rows
                    self.min_max_counts[idx][value]["max"] = self.target_n_rows
                else:
                    self.min_max_counts[idx][value]["max"] = min(
                        (self.target_n_rows - 1), curr_max
                    )

    def check_proportions(self, filtered_data: pd.DataFrame) -> tuple[bool, list[dict]]:
        """
        Check if filtered data maintains proportion requirements for specified fields

        Args:
            filtered_data (pd.DataFrame): Filtered data

        Returns:
            tuple[bool, list[dict]]:
                - bool: Whether all proportion rules are satisfied
                - list[dict]: List of detailed violation information
        """
        # Ensure original proportions and sample count limits have been calculated
        if not self.original_proportions or not hasattr(self, "min_max_counts"):
            raise ValueError(
                "Original data proportion distribution not yet calculated, please call verify_data method first"
            )

        all_rules_satisfied = True
        violations = []
        filtered_n_rows = len(filtered_data)

        for rule in self.field_proportions:
            fields = rule["fields"]
            mode = rule["mode"]
            tolerance = rule.get("tolerance", 0.1)  # Default 0.1 (10%)

            # Handle single field
            if isinstance(fields, str):
                field = fields
                if field not in filtered_data.columns:
                    continue

                key = (field, mode)

                # Check 'all' mode - distribution of all values
                if (
                    mode == "all"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # Get original data proportions and sample count limits
                    original_counts = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # Calculate actual counts in filtered data
                    value_counts = (
                        filtered_data[field].value_counts(dropna=False).to_dict()
                    )

                    # Check if actual count for each value is within allowed range
                    for value in set(original_counts.keys()):
                        if value not in count_bounds:
                            continue

                        bounds = count_bounds[value]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]
                        actual_count = value_counts.get(value, 0)

                        # Check if constraint is violated
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "Field": field,
                                    "Value": value,
                                    "Original Proportion": original_counts[value],
                                    "Filtered Proportion": actual_count
                                    / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "Actual Count": actual_count,
                                    "Min Count": min_count,
                                    "Max Count": max_count,
                                    "Target Count": target_count,
                                    "Tolerance": tolerance,
                                    "Mode": mode,
                                }
                            )

                # Check 'missing' mode - proportion of missing values only
                elif (
                    mode == "missing"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # Get original data missing proportion and sample count limits
                    orig_missing_prop = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]["Missing"]

                    # Calculate actual missing count in filtered data
                    actual_missing_count = filtered_data[field].isna().sum()

                    min_count = count_bounds["min"]
                    max_count = count_bounds["max"]
                    target_count = count_bounds["target"]

                    # Check if constraint is violated
                    if (
                        actual_missing_count < min_count
                        or actual_missing_count > max_count
                    ):
                        all_rules_satisfied = False
                        violations.append(
                            {
                                "Field": field,
                                "Value": "Missing",
                                "Original Proportion": orig_missing_prop,
                                "Filtered Proportion": actual_missing_count
                                / filtered_n_rows
                                if filtered_n_rows > 0
                                else 0,
                                "Actual Count": actual_missing_count,
                                "Min Count": min_count,
                                "Max Count": max_count,
                                "Target Count": target_count,
                                "Tolerance": tolerance,
                                "Mode": mode,
                            }
                        )

            # Handle field combinations (list format)
            elif isinstance(fields, list):
                fields_tuple = tuple(fields)
                # Check if all fields exist
                all_fields_exist = all(
                    field in filtered_data.columns for field in fields
                )
                if not all_fields_exist:
                    continue

                key = (fields_tuple, mode)

                # Handle 'missing' mode
                if (
                    mode == "missing"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # Get original data missing pattern proportions and sample count limits
                    original_missing_patterns = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # Calculate actual count for each missing pattern in filtered data
                    isna_df = pd.DataFrame()
                    for field in fields:
                        isna_df[f"{field}_isna"] = filtered_data[field].isna()

                    patterns = list(original_missing_patterns.keys())
                    for pattern in patterns:
                        if pattern not in count_bounds:
                            continue

                        bounds = count_bounds[pattern]
                        pattern_desc = bounds["desc"]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]

                        # Calculate actual count
                        mask = pd.Series(True, index=filtered_data.index)
                        for i, field in enumerate(fields):
                            if pattern[i]:
                                mask &= isna_df[f"{field}_isna"]
                            else:
                                mask &= ~isna_df[f"{field}_isna"]

                        actual_count = mask.sum()

                        # Check if constraint is violated
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "Field": fields_tuple,
                                    "Value": pattern_desc,
                                    "Original Proportion": original_missing_patterns[
                                        pattern
                                    ],
                                    "Filtered Proportion": actual_count
                                    / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "Actual Count": actual_count,
                                    "Min Count": min_count,
                                    "Max Count": max_count,
                                    "Target Count": target_count,
                                    "Tolerance": tolerance,
                                    "Mode": mode,
                                }
                            )

                # Handle 'all' mode
                elif (
                    mode == "all"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # Get original data proportions and sample count limits
                    original_counts = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # Calculate actual counts in filtered data
                    combined = filtered_data[fields].apply(
                        lambda row: tuple(row), axis=1
                    )
                    value_counts = combined.value_counts(dropna=False).to_dict()

                    # Check if actual count for each combined value is within allowed range
                    for value in set(original_counts.keys()):
                        if value not in count_bounds:
                            continue

                        bounds = count_bounds[value]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]
                        actual_count = value_counts.get(value, 0)

                        # Check if constraint is violated
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "Field": fields_tuple,
                                    "Value": str(value),
                                    "Original Proportion": original_counts[value],
                                    "Filtered Proportion": actual_count
                                    / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "Actual Count": actual_count,
                                    "Min Count": min_count,
                                    "Max Count": max_count,
                                    "Target Count": target_count,
                                    "Tolerance": tolerance,
                                    "Mode": mode,
                                }
                            )

        return all_rules_satisfied, violations

    def _infer_type_from_dtype(self, dtype) -> str:
        """
        Infer field type from pandas dtype when metadata is not available.

        Args:
            dtype: pandas dtype

        Returns:
            str: 'numerical', 'categorical', or 'datetime'
        """
        if pd.api.types.is_numeric_dtype(dtype):
            return "numerical"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        else:
            return "categorical"

    def _infer_type_from_attribute(self, attribute) -> str:
        """
        Infer field type from Attribute object.

        Args:
            attribute: Attribute object from Schema

        Returns:
            str: 'numerical', 'categorical', or 'datetime'
        """
        data_type_str = str(attribute.type).lower() if attribute.type else "object"

        # Map specific types to categories
        if "int" in data_type_str or "float" in data_type_str:
            return "numerical"
        elif "bool" in data_type_str:
            return "categorical"
        elif data_type_str in ["datetime64", "date", "time", "timestamp"]:
            return "datetime"
        elif attribute.category is True:
            return "categorical"
        else:
            return "categorical"


class FieldProportionsConstrainer(BaseConstrainer):
    """Field proportions constrainer for maintaining data distribution proportions"""

    def __init__(self, config: dict, metadata=None):
        """
        Initialize field proportions constrainer

        Args:
            config: Dictionary containing field proportions configuration
                {
                    'field_proportions': [...]
                }
            metadata: Optional Schema object for field type checking
        """
        super().__init__(config)
        self.metadata = metadata
        self.proportions_config = None
        self._setup_config()

    def _setup_config(self):
        """Setup the field proportions configuration"""
        try:
            # Handle different config formats
            if isinstance(self.config, list):
                # Direct list format: [{'fields': 'category', 'mode': 'all', 'tolerance': 0.1}, ...]
                config_dict = {"field_proportions": self.config}
            elif isinstance(self.config, dict):
                if "field_proportions" in self.config and isinstance(
                    self.config["field_proportions"], list
                ):
                    # New simplified format: {'field_proportions': [...]}
                    config_dict = {
                        "field_proportions": self.config["field_proportions"]
                    }
                else:
                    # Fallback: assume the whole config is the field proportions config
                    config_dict = self.config
            else:
                raise ValueError(f"Invalid config format: {type(self.config)}")

            # Pass metadata to FieldProportionsConfig
            config_dict["metadata"] = self.metadata
            self.proportions_config = FieldProportionsConfig(**config_dict)
        except Exception as e:
            raise ValueError(f"Invalid field proportions configuration: {e}") from e

    def _set_target_rows(self, target_rows: int):
        """Internal method to set target rows from Constrainer"""
        self.target_rows = target_rows

    def validate_config(self) -> bool:
        """Validate if the configuration is legal"""
        try:
            # Configuration validation is done in FieldProportionsConfig.__post_init__
            return self.proportions_config is not None
        except Exception:
            return False

    def apply(self, df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame:
        """
        Apply field proportions constraint to the data

        Args:
            df: Input DataFrame
            target_rows: Target number of rows (provided by Constrainer)

        Returns:
            DataFrame after applying field proportions constraint
        """
        if df.empty:
            return df

        # Set target rows if provided
        if target_rows is not None:
            self._set_target_rows(target_rows)

        # Verify data and setup proportions if not already done
        if not self.proportions_config.original_proportions:
            if not hasattr(self, "target_rows") or self.target_rows is None:
                raise ValueError("target_rows must be provided")
            self.proportions_config.verify_data(df, self.target_rows)

        # Apply the constraint filtering
        result_df, ops_df = self._constraint_filter_field_proportions(
            df, self.proportions_config
        )

        return result_df

    def _constraint_filter_field_proportions(
        self,
        data: pd.DataFrame,
        config: FieldProportionsConfig = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filter DataFrame based on given field proportion preservation conditions, ensuring field value distribution counts remain within acceptable range.

        Args:
            data (pd.DataFrame): Data to filter
            config (FieldProportionsConfig): Configuration class containing field proportion preservation settings

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]:
                - Filtered data with reset index
                - Operation log DataFrame containing filter actions, conditions, affected row counts, etc.
        """
        if (
            config is None
            or not hasattr(config, "original_proportions")
            or not config.original_proportions
            or not hasattr(config, "min_max_counts")
            or not config.min_max_counts
        ):
            return data, pd.DataFrame()

        # Copy data to avoid modifying original
        data_result = data.copy()
        # initial_rows = len(data_result)  # Currently unused, commented for future use

        # Create operation log list
        ops_records = []

        # Set max iterations to avoid infinite loop
        max_iterations = 50
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check if all conditions are satisfied
            proportions_satisfied, violations = config.check_proportions(data_result)

            # If no proportion requirements violated, return directly
            if proportions_satisfied:
                break

            # Classify violations by type
            overflow_violations = []  # Violations with excessive counts
            underflow_violations = []  # Violations with insufficient counts

            for violation in violations:
                actual_count = violation["Actual Count"]
                min_count = violation["Min Count"]
                max_count = violation["Max Count"]

                if actual_count > max_count:
                    overflow_violations.append(violation)
                elif actual_count < min_count:
                    underflow_violations.append(violation)

            # If no overflow violations and only underflow violations, we may not be able to adjust further
            if not overflow_violations:
                break

            # 1. First mark all data that needs protection (conditions with insufficient counts)
            # protect_mask = pd.Series(False, index=data_result.index)  # Currently unused

            # 2. Find first overflow violation condition and handle it
            found_overflow = False

            for violation in overflow_violations:
                field_name = violation["Field"]
                value = violation["Value"]
                actual_count = violation["Actual Count"]
                max_count = violation["Max Count"]
                mode = violation["Mode"]

                # Calculate number of rows to remove
                remove_needed = actual_count - max_count

                # Build filter condition mask
                if isinstance(field_name, str):
                    # Single field
                    if mode == "all":
                        # Find data with specific value
                        if pd.isna(value):
                            value_mask = data_result[field_name].isna()
                        else:
                            value_mask = data_result[field_name] == value
                        condition_desc = f"Field {field_name} with value {value}"
                    else:  # mode == 'missing'
                        # Find data with missing values
                        value_mask = data_result[field_name].isna()
                        condition_desc = f"Field {field_name} with missing values"
                else:
                    # Field combination
                    fields = (
                        field_name if isinstance(field_name, tuple) else [field_name]
                    )
                    if mode == "all":
                        # Handle specific values in field combinations
                        if (
                            isinstance(value, str)
                            and value.startswith("(")
                            and value.endswith(")")
                        ):
                            # Parse string form of tuple
                            import ast

                            try:
                                parsed_value = ast.literal_eval(value)
                                if isinstance(parsed_value, tuple):
                                    value_mask = pd.Series(
                                        True, index=data_result.index
                                    )
                                    for i, field in enumerate(fields):
                                        if i < len(parsed_value):
                                            if pd.isna(parsed_value[i]):
                                                value_mask &= data_result[field].isna()
                                            else:
                                                value_mask &= (
                                                    data_result[field]
                                                    == parsed_value[i]
                                                )
                                else:
                                    # Capture loop variable to avoid B023
                                    def check_value(row, target_value=value):
                                        return str(tuple(row)) == target_value

                                    value_mask = data_result[list(fields)].apply(
                                        check_value, axis=1
                                    )
                            except Exception:  # Avoid bare except E722
                                # Capture loop variable to avoid B023
                                def check_value_fallback(row, target_value=value):
                                    return str(tuple(row)) == target_value

                                value_mask = data_result[list(fields)].apply(
                                    check_value_fallback, axis=1
                                )
                        else:
                            # Capture loop variable to avoid B023
                            def check_value_str(row, target_value=value):
                                return str(tuple(row)) == str(target_value)

                            value_mask = data_result[list(fields)].apply(
                                check_value_str, axis=1
                            )
                        condition_desc = (
                            f"Field combination {field_name} with value {value}"
                        )
                    else:  # mode == 'missing'
                        # Handle missing patterns in field combinations - simplified handling
                        value_mask = pd.Series(False, index=data_result.index)
                        condition_desc = f"Field combination {field_name} with {value}"

                # If there is available data to remove
                available_count = value_mask.sum()
                if available_count > 0:
                    # Decide how many rows to remove
                    remove_count = min(remove_needed, available_count)

                    # Randomly select indices to remove
                    indices_to_remove = (
                        data_result[value_mask]
                        .sample(n=remove_count, random_state=42)
                        .index
                    )

                    # Log operation
                    detailed_record = {
                        "Iteration": iteration,
                        "Remove Condition": condition_desc,
                        "Remove Reason": "Excessive count",
                        "Current Count": actual_count,
                        "Max Count": max_count,
                        "Needed Removal": remove_needed,
                        "Actual Removal": remove_count,
                        "Remaining Rows": len(data_result) - remove_count,
                    }

                    ops_records.append(detailed_record)

                    # Filter data
                    data_result = data_result.drop(indices_to_remove)

                    found_overflow = True
                    break  # After handling one condition, break and re-evaluate all conditions

            # If all overflow conditions cannot be handled, exit loop
            if not found_overflow:
                break

        # Final check
        final_proportions_satisfied, final_violations = config.check_proportions(
            data_result
        )
        if not final_proportions_satisfied:
            import logging

            logger = logging.getLogger("PETsARD.FieldProportionsConstrainer")
            logger.warning(
                f"⚠ field_proportions constraint: After {iteration} iterations, {len(final_violations)} conditions still not fully satisfied. "
                f"This may be due to insufficient data, overly strict tolerance settings, or conflicts between conditions."
            )
            # Log detailed violation information
            for i, violation in enumerate(final_violations[:3], 1):  # Show only first 3
                logger.debug(
                    f"  Violation {i}: Field={violation['Field']}, Value={violation['Value']}, "
                    f"Actual Count={violation['Actual Count']}, "
                    f"Expected Range=[{violation['Min Count']}, {violation['Max Count']}]"
                )
            if len(final_violations) > 3:
                logger.debug(
                    f"  ... {len(final_violations) - 3} more violations not shown"
                )

        # Create operation log DataFrame
        ops_df = (
            pd.DataFrame(ops_records)
            if ops_records
            else pd.DataFrame(
                columns=[
                    "Iteration",
                    "Remove Condition",
                    "Remove Reason",
                    "Current Count",
                    "Max Count",
                    "Needed Removal",
                    "Actual Removal",
                    "Remaining Rows",
                ]
            )
        )

        return data_result, ops_df
