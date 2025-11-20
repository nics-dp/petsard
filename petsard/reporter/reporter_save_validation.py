"""
ReporterSaveValidation - Output Constrainer validation results as CSV

This Reporter is specifically designed to output Constrainer.validate() validation results as structured CSV reports.
"""

from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.reporter.reporter_base import BaseReporter


class ReporterSaveValidation(BaseReporter):
    """
    Save Constrainer validation results as CSV report

    This Reporter outputs validation results as CSV files
    """

    def __init__(self, config: dict):
        """
        Initialize ReporterSaveValidation

        Args:
            config (dict): Configuration dictionary
                - method (str): Must be 'SAVE_VALIDATION'
                - output (str, optional): Output filename prefix, default 'petsard'
                - include_details (bool, optional): Whether to include detailed violation records, default True
        """
        super().__init__(config)

        # Whether to include detailed violation records
        self.config["include_details"] = self.config.get("include_details", True)

    def create(self, data: dict = None) -> dict[str, Any]:
        """
        Process Constrainer validation result data

        Args:
            data (dict): Input data, should contain Constrainer's validation_result
                Format: {
                    (tuple): validation_result_dict,
                    ...
                }

        Returns:
            dict[str, Any]: Processed data, containing all validation results
        """
        if not data:
            raise ConfigError("Input data cannot be empty")

        # Process each validation result
        processed_results = {}

        for key, validation_result in data.items():
            if not isinstance(validation_result, dict):
                continue

            # Validate input structure
            if not self._validate_input_structure(validation_result):
                import logging

                logger = logging.getLogger(f"PETsARD.{__name__.split('.')[-1]}")
                logger.warning(f"Skipping invalid validation result for key: {key}")
                continue

            # Process this validation result
            processed_result = self._process_validation_result(validation_result, key)
            processed_results[key] = processed_result

        return {"Reporter": processed_results}

    def report(
        self, processed_data: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Save processed validation results as CSV file

        Args:
            processed_data (dict[str, Any] | None): Processed data

        Returns:
            dict[str, Any] | None: Information about save results
        """
        if not processed_data or "Reporter" not in processed_data:
            return {}

        reporter_data = processed_data["Reporter"]

        # Generate CSV file for each validation result
        for key, result_data in reporter_data.items():
            if not result_data:
                continue

            # Generate filename
            output_filename = self._generate_filename(key)

            # Save as CSV
            self._save_to_csv(result_data, output_filename)

        return processed_data

    def _validate_input_structure(self, validation_result: dict) -> bool:
        """
        Validate input validation result structure

        Args:
            validation_result (dict): Validation result

        Returns:
            bool: Whether structure is valid
        """
        required_keys = [
            "total_rows",
            "passed_rows",
            "failed_rows",
            "pass_rate",
            "is_fully_compliant",
            "constraint_violations",
        ]

        return all(key in validation_result for key in required_keys)

    def _process_validation_result(
        self, validation_result: dict, key: tuple
    ) -> dict[str, Any]:
        """
        Process single validation result

        Args:
            validation_result (dict): Validation result
            key (tuple): Experiment identification key

        Returns:
            dict[str, Any]: Processed result, containing data for each sheet
        """
        result = {
            "key": key,
            "summary": self._create_summary_dataframe(validation_result),
            "constraint_violations": self._create_violations_dataframe(
                validation_result
            ),
        }

        # If config requires detailed records and data exists
        if self.config["include_details"] and "violation_details" in validation_result:
            violation_details = validation_result["violation_details"]
            if violation_details is not None and not violation_details.empty:
                # Limit each rule to maximum 10 records
                # Pass constraint_violations to get correct rule names
                result["violation_details"] = self._limit_violation_details(
                    violation_details, validation_result["constraint_violations"]
                )

        return result

    def _limit_violation_details(
        self,
        violation_details: pd.DataFrame,
        constraint_violations: dict,
        max_rows_per_rule: int = 10,
    ) -> pd.DataFrame:
        """
        Limit number of violation records per rule and add constraint info columns

        Args:
            violation_details (pd.DataFrame): Complete detailed violation records
            constraint_violations (dict): Constraint violations info with rule names
            max_rows_per_rule (int): Maximum records to keep per rule, default 10

        Returns:
            pd.DataFrame: Limited detailed violation records with constraint info
        """
        # Identify violation marker columns
        violated_columns = [
            col for col in violation_details.columns if col.startswith("__violated_")
        ]

        if not violated_columns:
            return violation_details.head(max_rows_per_rule)

        # Build a mapping from column name to rule name
        column_to_rule = {}
        for constraint_type, rules_data in constraint_violations.items():
            if isinstance(rules_data, dict):
                # Check if this is error format
                if "error" in rules_data:
                    column_name = f"__violated_{constraint_type}__"
                    column_to_rule[column_name] = {
                        "constraint_type": constraint_type,
                        "rule_name": constraint_type,
                    }
                else:
                    # New format with multiple rules
                    rule_idx = 0
                    for rule_name, _rule_stats in rules_data.items():
                        column_name = f"__violated_{constraint_type}_rule{rule_idx}__"
                        column_to_rule[column_name] = {
                            "constraint_type": constraint_type,
                            "rule_name": rule_name,
                        }
                        rule_idx += 1

        # Build result list
        result_rows = []

        # For each violation marker column, extract violated rows
        for violated_col in violated_columns:
            # Get rows that violated this rule
            mask = violation_details[violated_col] == True
            violated_rows = violation_details[mask].copy()

            if len(violated_rows) == 0:
                continue

            # Get rule info from mapping
            rule_info = column_to_rule.get(violated_col)

            if rule_info:
                constraint_type = rule_info["constraint_type"]
                rule_name = rule_info["rule_name"]
            else:
                # Fallback: parse from column name
                col_name = violated_col.replace("__violated_", "").replace("__", "")
                if "_rule" in col_name:
                    parts = col_name.split("_rule")
                    constraint_type = parts[0]
                    rule_number = parts[1] if len(parts) > 1 else "0"
                    rule_name = f"Rule {int(rule_number) + 1}"
                else:
                    constraint_type = col_name
                    rule_name = constraint_type

            # Limit to max_rows_per_rule
            limited_rows = violated_rows.head(max_rows_per_rule).copy()

            # Add constraint info columns
            limited_rows.insert(0, "Violation Index", range(1, len(limited_rows) + 1))
            limited_rows.insert(0, "Rule", rule_name)
            limited_rows.insert(0, "Constraint Type", constraint_type)

            result_rows.append(limited_rows)

        if result_rows:
            # Combine all results
            result_df = pd.concat(result_rows, ignore_index=True)

            # Remove internal violation marker columns
            cols_to_drop = [
                col for col in result_df.columns if col.startswith("__violated_")
            ]
            result_df = result_df.drop(columns=cols_to_drop)

            return result_df
        else:
            return pd.DataFrame()

    def _create_summary_dataframe(self, validation_result: dict) -> pd.DataFrame:
        """
        Create summary data table

        Args:
            validation_result (dict): Validation result

        Returns:
            pd.DataFrame: Summary statistics table
        """
        summary_data = {
            "Metric": [
                "total_rows",
                "passed_rows",
                "failed_rows",
                "pass_rate",
                "is_fully_compliant",
            ],
            "Value": [
                validation_result["total_rows"],
                validation_result["passed_rows"],
                validation_result["failed_rows"],
                f"{validation_result['pass_rate']:.6f}",
                validation_result["is_fully_compliant"],
            ],
        }

        return pd.DataFrame(summary_data)

    def _create_violations_dataframe(self, validation_result: dict) -> pd.DataFrame:
        """
        Create constraint violation statistics table (including statistics for each specific rule)

        Args:
            validation_result (dict): Validation result

        Returns:
            pd.DataFrame: Constraint violation statistics table
        """
        violations = validation_result["constraint_violations"]

        if not violations:
            return pd.DataFrame(
                {
                    "Constraint Type": [],
                    "Rule": [],
                    "Failed Count": [],
                    "Fail Rate": [],
                    "Violation Examples": [],
                    "Error Message": [],
                }
            )

        rows = []
        for constraint_type, type_data in violations.items():
            # Check if new format (containing specific rules) or old format (single statistics)
            if isinstance(type_data, dict):
                # Check if error message
                if "error" in type_data and "failed_count" in type_data:
                    # Old format or error format
                    row = {
                        "Constraint Type": constraint_type,
                        "Rule": "-",
                        "Failed Count": type_data.get("failed_count", 0),
                        "Fail Rate": f"{type_data.get('fail_rate', 0):.6f}",
                        "Violation Examples": "",
                        "Error Message": type_data.get("error", ""),
                    }
                    rows.append(row)
                else:
                    # New format: contains multiple rules
                    for rule_name, rule_stats in type_data.items():
                        if isinstance(rule_stats, dict):
                            # Format violation examples
                            examples = rule_stats.get("violation_examples", [])
                            examples_str = (
                                ", ".join(str(idx) for idx in examples)
                                if examples
                                else "-"
                            )

                            row = {
                                "Constraint Type": constraint_type,
                                "Rule": rule_name,
                                "Failed Count": rule_stats.get("failed_count", 0),
                                "Fail Rate": f"{rule_stats.get('fail_rate', 0):.6f}",
                                "Violation Examples": examples_str,
                                "Error Message": rule_stats.get("error", ""),
                            }
                            rows.append(row)

        return pd.DataFrame(rows)

    def _generate_filename(self, key: tuple) -> str:
        """
        Generate filename based on experiment key

        Args:
            key (tuple): Experiment identification key
                - Single source: (Module, experiment_name)
                - Multiple sources: (Module, experiment_name, source_name)

        Returns:
            str: Generated filename (without extension)
        """
        output_prefix = self.config["output"]

        # Check if using default output
        from petsard.reporter.reporter_base import ConfigDefaults

        is_default_output = output_prefix == ConfigDefaults.DEFAULT_OUTPUT_PREFIX

        if is_default_output:
            # When using default output, follow PETsARD naming convention
            if isinstance(key, tuple) and len(key) == 3:
                # Multiple source format: (Module, experiment_name, source_name)
                module = key[0]
                exp_name = key[1]
                source_name = key[2]
                # Format: {output}_[Validation]_Source[source_name]_Constrainer[experiment_name]
                filename = f"{output_prefix}_[Validation]_Source[{source_name}]_{module}[{exp_name}]"
            elif isinstance(key, tuple) and len(key) == 2:
                # Single source format: (Module, experiment_name)
                module = key[0]
                exp_name = key[1]
                filename = f"{output_prefix}_[Validation]_{module}[{exp_name}]"
            else:
                # Other formats (backward compatibility)
                key_str = (
                    "_".join(str(k) for k in key)
                    if isinstance(key, tuple)
                    else str(key)
                )
                filename = f"{output_prefix}_[Validation]_{key_str}"
        else:
            # When using custom output, directly use specified name
            filename = output_prefix

        return filename

    def _save_to_csv(self, result_data: dict, output_filename: str) -> None:
        """
        Save results as CSV files (generates 3 separate files)

        Args:
            result_data (dict): Dictionary containing data
            output_filename (str): Output filename (without extension)
        """
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__.split('.')[-1]}")

        # Save summary data
        if "summary" in result_data:
            summary_df = result_data["summary"]
            summary_file = f"{output_filename}_summary"
            logger.info(f"Saving summary report to {summary_file}.csv")
            try:
                self._save(data=summary_df, full_output=summary_file)
                logger.info("Successfully saved summary report")
            except Exception as e:
                logger.error(f"Failed to save summary CSV file: {str(e)}")
                raise

        # Save constraint violation statistics
        if "constraint_violations" in result_data:
            violations_df = result_data["constraint_violations"]
            violations_file = f"{output_filename}_violations"
            logger.info(f"Saving violations report to {violations_file}.csv")
            try:
                self._save(data=violations_df, full_output=violations_file)
                logger.info("Successfully saved violations report")
            except Exception as e:
                logger.error(f"Failed to save violations CSV file: {str(e)}")
                raise

        # Save detailed violation records (if any)
        if "violation_details" in result_data:
            details_df = result_data["violation_details"]
            details_file = f"{output_filename}_details"
            logger.info(f"Saving details report to {details_file}.csv")
            try:
                self._save(data=details_df, full_output=details_file)
                logger.info("Successfully saved details report")
            except Exception as e:
                logger.error(f"Failed to save details CSV file: {str(e)}")
                raise
