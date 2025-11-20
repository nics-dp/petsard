import logging
import warnings

import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer
from petsard.constrainer.field_combination_constrainer import \
    FieldCombinationConstrainer
from petsard.constrainer.field_constrainer import FieldConstrainer
from petsard.constrainer.field_proportions_constrainer import \
    FieldProportionsConstrainer
from petsard.constrainer.nan_group_constrainer import NaNGroupConstrainer


class Constrainer:
    """Factory class for creating and applying constraints"""

    _constraints = {
        "nan_groups": NaNGroupConstrainer,
        "field_constraints": FieldConstrainer,
        "field_combinations": FieldCombinationConstrainer,
        "field_proportions": FieldProportionsConstrainer,
    }

    def __init__(self, config: dict, metadata=None):
        """
        Initialize with full constraint configuration

        Args:
            config: Dictionary containing all constraint configurations
                {
                    'nan_groups': {...},
                    'field_constraints': [...],
                    'field_combinations': [...],
                    'field_proportions': [...]
                }
            metadata: Optional Schema object containing field type information

        Attr.:
            resample_trails (int):
                Number of trials to reach the target number of rows,
                set after calling resample_until_satisfy
            validation_result (dict):
                Validation result from the last validate() call,
                set after calling validate()
            metadata: Schema object for field type checking (optional)
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        self.config = config
        self.metadata = metadata
        self._constrainers = {}
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._setup_constrainers()

        self.resample_trails = None
        self.validation_result = None

    def _setup_constrainers(self):
        """Initialize all constraint instances"""
        for constraint_type, config in self.config.items():
            if constraint_type not in self._constraints:
                warnings.warn(
                    f"Warning: Unknown constraint type '{constraint_type}'",
                    stacklevel=2,
                )
                continue
            else:
                # Pass metadata to constrainers that support it
                constrainer_class = self._constraints[constraint_type]

                # Check if constrainer class accepts metadata parameter
                import inspect

                sig = inspect.signature(constrainer_class.__init__)
                if "metadata" in sig.parameters:
                    self._constrainers[constraint_type] = constrainer_class(
                        config, metadata=self.metadata
                    )
                else:
                    self._constrainers[constraint_type] = constrainer_class(config)

    def apply(self, df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame:
        """
        Apply all constraints in sequence

        Args:
            df: Input DataFrame
            target_rows: Target number of rows (used internally by resample_until_satisfy)

        Returns:
            DataFrame after applying all constraints
        """
        result = df.copy()
        for _constraint_type, constrainer in self._constrainers.items():
            # Set target rows for field proportions constrainer if needed
            if _constraint_type == "field_proportions" and target_rows is not None:
                constrainer._set_target_rows(target_rows)
            result = constrainer.apply(result)
        # Reset index at the end to ensure clean sequential indexing
        return result.reset_index(drop=True)

    @classmethod
    def register(cls, name: str, constraint_class: type):
        """
        Register a new constraint type

        Args:
            name: Constraint type name
            constraint_class: Class implementing the constraint
        """
        if not issubclass(constraint_class, BaseConstrainer):
            raise ValueError("Must inherit from BaseConstrainer")
        cls._constraints[name] = constraint_class

    def resample_until_satisfy(
        self,
        data: pd.DataFrame,
        target_rows: int,
        synthesizer,
        postprocessor=None,
        max_trials: int = 300,
        sampling_ratio: float = 10.0,
        verbose_step: int = 10,
    ) -> pd.DataFrame:
        """
        Resample data until meeting the constraints with target number of rows.

        Args:
            data: Input DataFrame to be constrained
            target_rows: Number of rows to achieve
            synthesizer: Synthesizer instance for generating synthetic data
            postprocessor: Optional postprocessor for data transformation
            max_trials: Maximum number of trials before giving up
            sampling_ratio: Multiple of target_rows to generate in each trial.
                    Default is 10.0, meaning it will generate 10x the target rows
                    to compensate for data loss during constraint filtering.
            verbose_step: Print progress every verbose_step trials. Default is 10.

        Attr:
            resample_trails (int): Number of trials to reach the target number of rows

        Returns:
            DataFrame that satisfies all constraints with target number of rows

        Raises:
            ValueError: If data is empty or synthesizer is None
        """
        # Input validation
        if len(data) == 0:
            raise ValueError("Empty DataFrame is not allowed")
        if synthesizer is None:
            raise ValueError("Synthesizer cannot be None")

        self.resample_trails = 0
        result_df = None
        remain_rows = target_rows - data.shape[0]

        if remain_rows <= 0:
            # Apply constraints to the input data first
            constrained_data = self.apply(data, target_rows)

            if constrained_data.shape[0] >= target_rows:
                # If we have enough rows after applying constraints, sample the target number
                result = constrained_data.sample(
                    n=target_rows, random_state=42
                ).reset_index(drop=True)
                return result
            elif constrained_data.shape[0] > 0:
                # If we have some rows but not enough, continue with resampling
                result_df = constrained_data
                remain_rows = target_rows - constrained_data.shape[0]
            else:
                # If no rows remain after constraints, start fresh with resampling
                result_df = None
                remain_rows = target_rows

        while remain_rows > 0:
            self.resample_trails += 1
            if self.resample_trails >= max_trials:
                warnings.warn(
                    f"Maximum trials ({max_trials}) reached but only got {result_df.shape[0] if result_df is not None else 0} rows",
                    stacklevel=2,
                )
                break

            # Generate new samples
            synthesizer.config.update(
                {
                    "sample_from": "Constrainter",
                    "sample_num_rows": int(target_rows * sampling_ratio),
                }
            )

            new_samples = synthesizer.sample()

            # Apply postprocessor if provided
            if postprocessor is not None:
                new_samples = postprocessor.inverse_transform(new_samples)

            # Apply constraints
            filtered_samples = self.apply(new_samples, target_rows)

            # Combine with existing results
            if result_df is None:
                result_df = filtered_samples
            else:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                        message=".*behavior of DataFrame concatenation with empty or all-NA entries.*",
                    )

                    result_df = (
                        pd.concat(
                            [result_df, filtered_samples],
                            axis=0,
                            ignore_index=True,
                        )
                        .drop_duplicates()
                        .reset_index(drop=True)
                    )

            # Check if we have enough rows
            if result_df.shape[0] >= target_rows:
                # Randomly select target number of rows
                result_df = result_df.sample(
                    n=target_rows, random_state=42
                ).reset_index(drop=True)
                remain_rows = 0
            else:
                remain_rows = target_rows - result_df.shape[0]

            if verbose_step > 0 and self.resample_trails % verbose_step == 0:
                self._logger.info(
                    f"Trial {self.resample_trails}: Got {result_df.shape[0] if result_df is not None else 0} rows, need {remain_rows} more"
                )

        return result_df

    def validate(
        self,
        data: pd.DataFrame,
        return_details: bool = True,
        max_examples_per_rule: int = 6,
    ) -> dict:
        """
        Validate whether data meets all constraints without resampling.

        This method checks if existing data (e.g., loaded from file or custom_data) meets the configured constraints.
        Unlike resample_until_satisfy, this method does not resample but only validates and records violations.

        Args:
            data: DataFrame to validate
            return_details: Whether to return detailed violation records, default is True
            max_examples_per_rule: Maximum number of violation examples per rule, default is 6

        Returns:
            dict: Validation result containing:
                - total_rows (int): Total number of rows
                - passed_rows (int): Number of rows passing all constraints
                - failed_rows (int): Number of rows failing constraints
                - pass_rate (float): Pass rate (0.0 to 1.0)
                - is_fully_compliant (bool): Whether 100% compliant (all data passed)
                - constraint_violations (dict): Violation statistics for each constraint type
                    For each constraint type, contains a dict with:
                        - 'total_failed_count': total violations across all rules
                        - 'total_fail_rate': overall failure rate for this constraint type
                        - 'rules': dict of individual rule violations
                - violation_details (pd.DataFrame, optional): Detailed violation records

        Example:
            >>> constrainer = Constrainer(config)
            >>> result = constrainer.validate(data)
            >>> print(f"Pass rate: {result['pass_rate']:.2%}")
            >>> print(f"Fully compliant: {result['is_fully_compliant']}")
        """
        if len(data) == 0:
            raise ValueError("Empty DataFrame is not allowed")

        total_rows = len(data)
        result = data.copy()
        result["__validation_passed__"] = True  # Track whether each row passes

        # Record violations for each constraint type (including each specific rule)
        constraint_violations = {}

        # Validate each constrainer
        for constraint_type, constrainer in self._constrainers.items():
            # Get configuration for this constraint type
            constraint_config = self.config.get(constraint_type)

            # Handle each specific rule separately based on constraint type
            type_violations = {}

            try:
                if constraint_type == "field_constraints" and isinstance(
                    constraint_config, list
                ):
                    # field_constraints is a list of rules
                    for rule_idx, rule in enumerate(constraint_config):
                        rule_name = f"Rule {rule_idx + 1}: {rule}"

                        # Create temporary constrainer to handle only this rule
                        temp_constrainer = FieldConstrainer([rule])
                        passed_data = temp_constrainer.apply(result.copy())
                        passed_indices = set(passed_data.index)

                        # Calculate number of violations
                        failed_indices = result.index[
                            ~result.index.isin(passed_indices)
                        ]
                        failed_count = len(failed_indices)

                        if failed_count > 0:
                            # Mark violated data
                            column_name = (
                                f"__violated_{constraint_type}_rule{rule_idx}__"
                            )
                            result[column_name] = False
                            result.loc[failed_indices, column_name] = True
                            result.loc[failed_indices, "__validation_passed__"] = False

                            # Collect violation examples (up to max_examples_per_rule)
                            examples = failed_indices[:max_examples_per_rule].tolist()

                            type_violations[rule_name] = {
                                "failed_count": failed_count,
                                "fail_rate": failed_count / total_rows
                                if total_rows > 0
                                else 0.0,
                                "violation_examples": examples,
                            }

                elif constraint_type == "field_combinations" and isinstance(
                    constraint_config, list
                ):
                    # field_combinations is also a list of rules
                    for rule_idx, rule in enumerate(constraint_config):
                        rule_name = f"Rule {rule_idx + 1}: {rule}"

                        # Create temporary constrainer to handle only this rule
                        temp_constrainer = FieldCombinationConstrainer([rule])
                        passed_data = temp_constrainer.apply(result.copy())
                        passed_indices = set(passed_data.index)

                        # Calculate number of violations
                        failed_indices = result.index[
                            ~result.index.isin(passed_indices)
                        ]
                        failed_count = len(failed_indices)

                        if failed_count > 0:
                            # Mark violated data
                            column_name = (
                                f"__violated_{constraint_type}_rule{rule_idx}__"
                            )
                            result[column_name] = False
                            result.loc[failed_indices, column_name] = True
                            result.loc[failed_indices, "__validation_passed__"] = False

                            # Collect violation examples
                            examples = failed_indices[:max_examples_per_rule].tolist()

                            type_violations[rule_name] = {
                                "failed_count": failed_count,
                                "fail_rate": failed_count / total_rows
                                if total_rows > 0
                                else 0.0,
                                "violation_examples": examples,
                            }

                elif constraint_type == "field_proportions" and isinstance(
                    constraint_config, list
                ):
                    # field_proportions is also a list of rules
                    for rule_idx, rule in enumerate(constraint_config):
                        fields = rule.get("fields", "unknown")
                        mode = rule.get("mode", "all")
                        tolerance = rule.get("tolerance", 0.0)
                        rule_name = f"Rule {rule_idx + 1}: {fields} (mode={mode}, tolerance={tolerance})"

                        # Create temporary constrainer to handle only this rule
                        temp_constrainer = FieldProportionsConstrainer([rule])
                        temp_constrainer._set_target_rows(total_rows)
                        passed_data = temp_constrainer.apply(result.copy())
                        passed_indices = set(passed_data.index)

                        # Calculate number of violations
                        failed_indices = result.index[
                            ~result.index.isin(passed_indices)
                        ]
                        failed_count = len(failed_indices)

                        if failed_count > 0:
                            # Mark violated data
                            column_name = (
                                f"__violated_{constraint_type}_rule{rule_idx}__"
                            )
                            result[column_name] = False
                            result.loc[failed_indices, column_name] = True
                            result.loc[failed_indices, "__validation_passed__"] = False

                            # Collect violation examples
                            examples = failed_indices[:max_examples_per_rule].tolist()

                            type_violations[rule_name] = {
                                "failed_count": failed_count,
                                "fail_rate": failed_count / total_rows
                                if total_rows > 0
                                else 0.0,
                                "violation_examples": examples,
                            }

                elif constraint_type == "nan_groups" and isinstance(
                    constraint_config, dict
                ):
                    # nan_groups is a dictionary, each key is a field with its processing rules
                    for field_name, actions in constraint_config.items():
                        # Build rule name
                        if actions == "delete":
                            rule_name = f"{field_name}: delete"
                        elif isinstance(actions, dict):
                            # May have multiple actions, but usually only one
                            action_keys = list(actions.keys())
                            if len(action_keys) == 1:
                                action = action_keys[0]
                                if action == "erase":
                                    target = actions[action]
                                    target_str = (
                                        target
                                        if isinstance(target, str)
                                        else ", ".join(target)
                                    )
                                    rule_name = f"{field_name}: erase -> {target_str}"
                                elif action == "copy":
                                    target = actions[action]
                                    rule_name = f"{field_name}: copy <- {target}"
                                elif action == "nan_if_condition":
                                    conditions = actions[action]
                                    cond_strs = [
                                        f"{k}={v}"
                                        if isinstance(v, str)
                                        else f"{k} in {v}"
                                        for k, v in conditions.items()
                                    ]
                                    rule_name = f"{field_name}: nan_if_condition ({', '.join(cond_strs)})"
                                else:
                                    rule_name = f"{field_name}: {action}"
                            else:
                                rule_name = f"{field_name}: {', '.join(action_keys)}"
                        else:
                            rule_name = f"{field_name}: {actions}"

                        # Create temporary constrainer to handle only this rule
                        temp_constrainer = NaNGroupConstrainer({field_name: actions})
                        passed_data = temp_constrainer.apply(result.copy())
                        passed_indices = set(passed_data.index)

                        # Calculate number of violations
                        failed_indices = result.index[
                            ~result.index.isin(passed_indices)
                        ]
                        failed_count = len(failed_indices)

                        if failed_count > 0:
                            # Mark violated data
                            column_name = f"__violated_{constraint_type}_{field_name}__"
                            result[column_name] = False
                            result.loc[failed_indices, column_name] = True
                            result.loc[failed_indices, "__validation_passed__"] = False

                            # Collect violation examples
                            examples = failed_indices[:max_examples_per_rule].tolist()

                            type_violations[rule_name] = {
                                "failed_count": failed_count,
                                "fail_rate": failed_count / total_rows
                                if total_rows > 0
                                else 0.0,
                                "violation_examples": examples,
                            }

                else:
                    # Other unknown types use original method
                    if constraint_type == "field_proportions":
                        constrainer._set_target_rows(total_rows)

                    passed_data = constrainer.apply(result.copy())
                    passed_indices = set(passed_data.index)

                    # Calculate number of violations
                    failed_indices = result.index[~result.index.isin(passed_indices)]
                    failed_count = len(failed_indices)

                    if failed_count > 0:
                        # Mark violated data
                        column_name = f"__violated_{constraint_type}__"
                        result[column_name] = False
                        result.loc[failed_indices, column_name] = True
                        result.loc[failed_indices, "__validation_passed__"] = False

                        # Collect violation examples
                        examples = failed_indices[:max_examples_per_rule].tolist()

                        type_violations[constraint_type] = {
                            "failed_count": failed_count,
                            "fail_rate": failed_count / total_rows
                            if total_rows > 0
                            else 0.0,
                            "violation_examples": examples,
                        }

                # Only record when there are violations
                if type_violations:
                    constraint_violations[constraint_type] = type_violations

            except Exception as e:
                warnings.warn(
                    f"Warning: Error validating constraint '{constraint_type}': {str(e)}",
                    stacklevel=2,
                )
                # If validation fails, mark as unknown error
                constraint_violations[constraint_type] = {
                    "error": {
                        "failed_count": 0,
                        "fail_rate": 0.0,
                        "error": str(e),
                    }
                }

        # Calculate statistics
        passed_rows = result["__validation_passed__"].sum()
        failed_rows = total_rows - passed_rows
        pass_rate = passed_rows / total_rows if total_rows > 0 else 0.0
        is_fully_compliant = passed_rows == total_rows

        # Build return result
        validation_result = {
            "total_rows": total_rows,
            "passed_rows": int(passed_rows),
            "failed_rows": int(failed_rows),
            "pass_rate": float(pass_rate),
            "is_fully_compliant": bool(is_fully_compliant),
            "constraint_violations": constraint_violations,
        }

        # If detailed information is needed
        if return_details:
            # Only return violated data and their violation markers
            details_df = result[~result["__validation_passed__"]].copy()

            # Remove internal tracking field, keep only violation markers
            if "__validation_passed__" in details_df.columns:
                details_df = details_df.drop(columns=["__validation_passed__"])

            validation_result["violation_details"] = details_df

        # Store validation result for later use
        self.validation_result = validation_result

        return validation_result
