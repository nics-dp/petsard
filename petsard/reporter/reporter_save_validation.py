"""
ReporterSaveValidation - Output Constrainer validation results as CSV
ReporterSaveValidation - 將 Constrainer 驗證結果輸出為 CSV

This Reporter is specifically designed to output Constrainer.validate() validation results as structured CSV reports.
此 Reporter 專門用於將 Constrainer.validate() 的驗證結果輸出為結構化的 CSV 報告。
"""

from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.reporter.reporter_base import BaseReporter


class ReporterSaveValidation(BaseReporter):
    """
    Save Constrainer validation results as CSV report
    將 Constrainer 驗證結果保存為 CSV 報告

    This Reporter outputs validation results as CSV files
    此 Reporter 會將驗證結果輸出為 CSV 檔案
    """

    def __init__(self, config: dict):
        """
        Initialize ReporterSaveValidation
        初始化 ReporterSaveValidation

        Args:
            config (dict): Configuration dictionary / 配置字典
                - method (str): Must be 'SAVE_VALIDATION' / 必須是 'SAVE_VALIDATION'
                - output (str, optional): Output filename prefix, default 'petsard' / 輸出檔名前綴，預設為 'petsard'
                - include_details (bool, optional): Whether to include detailed violation records, default True / 是否包含詳細違規記錄，預設為 True
        """
        super().__init__(config)

        # Whether to include detailed violation records / 是否包含詳細違規記錄
        self.config["include_details"] = self.config.get("include_details", True)

    def create(self, data: dict = None) -> dict[str, Any]:
        """
        Process Constrainer validation result data
        處理 Constrainer 驗證結果資料

        Args:
            data (dict): Input data, should contain Constrainer's validation_result / 輸入資料，應包含 Constrainer 的 validation_result
                Format / 格式: {
                    (tuple): validation_result_dict,
                    ...
                }

        Returns:
            dict[str, Any]: Processed data, containing all validation results / 處理後的資料，包含所有驗證結果
        """
        if not data:
            raise ConfigError("Input data cannot be empty")

        # Process each validation result / 處理每個驗證結果
        processed_results = {}

        for key, validation_result in data.items():
            if not isinstance(validation_result, dict):
                continue

            # Validate input structure / 驗證輸入結構
            if not self._validate_input_structure(validation_result):
                import logging

                logger = logging.getLogger(f"PETsARD.{__name__}")
                logger.warning(f"Skipping invalid validation result for key: {key}")
                continue

            # Process this validation result / 處理這個驗證結果
            processed_result = self._process_validation_result(validation_result, key)
            processed_results[key] = processed_result

        return {"Reporter": processed_results}

    def report(
        self, processed_data: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Save processed validation results as CSV file
        將處理後的驗證結果保存為 CSV 檔案

        Args:
            processed_data (dict[str, Any] | None): Processed data / 處理後的資料

        Returns:
            dict[str, Any] | None: Information about save results / 保存結果的資訊
        """
        if not processed_data or "Reporter" not in processed_data:
            return {}

        reporter_data = processed_data["Reporter"]

        # Generate CSV file for each validation result / 對每個驗證結果生成 CSV 檔案
        for key, result_data in reporter_data.items():
            if not result_data:
                continue

            # Generate filename / 生成檔名
            output_filename = self._generate_filename(key)

            # Save as CSV / 保存為 CSV
            self._save_to_csv(result_data, output_filename)

        return processed_data

    def _validate_input_structure(self, validation_result: dict) -> bool:
        """
        Validate input validation result structure
        驗證輸入的驗證結果結構

        Args:
            validation_result (dict): Validation result / 驗證結果

        Returns:
            bool: Whether structure is valid / 結構是否有效
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
        處理單個驗證結果

        Args:
            validation_result (dict): Validation result / 驗證結果
            key (tuple): Experiment identification key / 實驗識別鍵

        Returns:
            dict[str, Any]: Processed result, containing data for each sheet / 處理後的結果，包含各個 sheet 的資料
        """
        result = {
            "key": key,
            "summary": self._create_summary_dataframe(validation_result),
            "constraint_violations": self._create_violations_dataframe(
                validation_result
            ),
        }

        # If config requires detailed records and data exists / 如果配置要求包含詳細記錄且資料存在
        if self.config["include_details"] and "violation_details" in validation_result:
            violation_details = validation_result["violation_details"]
            if violation_details is not None and not violation_details.empty:
                # Limit each rule to maximum 10 records / 限制每個 rule 最多 10 筆記錄
                # Pass constraint_violations to get correct rule names / 傳遞 constraint_violations 以獲取正確的規則名稱
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
        限制每個 rule 的違規記錄數量並新增條件資訊欄位

        Args:
            violation_details (pd.DataFrame): Complete detailed violation records / 完整的違規詳細記錄
            constraint_violations (dict): Constraint violations info with rule names / 包含規則名稱的條件違規資訊
            max_rows_per_rule (int): Maximum records to keep per rule, default 10 / 每個 rule 最多保留的記錄數，預設為 10

        Returns:
            pd.DataFrame: Limited detailed violation records with constraint info / 限制後的違規詳細記錄（含條件資訊）
        """
        # Identify violation marker columns / 識別違規標記欄位
        violated_columns = [
            col for col in violation_details.columns if col.startswith("__violated_")
        ]

        if not violated_columns:
            return violation_details.head(max_rows_per_rule)

        # Build a mapping from column name to rule name / 建立從欄位名稱到規則名稱的映射
        column_to_rule = {}
        for constraint_type, rules_data in constraint_violations.items():
            if isinstance(rules_data, dict):
                # Check if this is error format / 檢查是否為錯誤格式
                if "error" in rules_data:
                    column_name = f"__violated_{constraint_type}__"
                    column_to_rule[column_name] = {
                        "constraint_type": constraint_type,
                        "rule_name": constraint_type,
                    }
                else:
                    # New format with multiple rules / 新格式包含多條規則
                    rule_idx = 0
                    for rule_name, _rule_stats in rules_data.items():
                        column_name = f"__violated_{constraint_type}_rule{rule_idx}__"
                        column_to_rule[column_name] = {
                            "constraint_type": constraint_type,
                            "rule_name": rule_name,
                        }
                        rule_idx += 1

        # Build result list / 建立結果列表
        result_rows = []

        # For each violation marker column, extract violated rows / 對每個違規標記欄位，提取違規的資料
        for violated_col in violated_columns:
            # Get rows that violated this rule / 取得違反此規則的資料
            mask = violation_details[violated_col] == True
            violated_rows = violation_details[mask].copy()

            if len(violated_rows) == 0:
                continue

            # Get rule info from mapping / 從映射中獲取規則資訊
            rule_info = column_to_rule.get(violated_col)

            if rule_info:
                constraint_type = rule_info["constraint_type"]
                rule_name = rule_info["rule_name"]
            else:
                # Fallback: parse from column name / 備用方案：從欄位名稱解析
                col_name = violated_col.replace("__violated_", "").replace("__", "")
                if "_rule" in col_name:
                    parts = col_name.split("_rule")
                    constraint_type = parts[0]
                    rule_number = parts[1] if len(parts) > 1 else "0"
                    rule_name = f"Rule {int(rule_number) + 1}"
                else:
                    constraint_type = col_name
                    rule_name = constraint_type

            # Limit to max_rows_per_rule / 限制為最多 max_rows_per_rule 筆
            limited_rows = violated_rows.head(max_rows_per_rule).copy()

            # Add constraint info columns / 新增條件資訊欄位
            limited_rows.insert(0, "Violation Index", range(1, len(limited_rows) + 1))
            limited_rows.insert(0, "Rule", rule_name)
            limited_rows.insert(0, "Constraint Type", constraint_type)

            result_rows.append(limited_rows)

        if result_rows:
            # Combine all results / 合併所有結果
            result_df = pd.concat(result_rows, ignore_index=True)

            # Remove internal violation marker columns / 移除內部違規標記欄位
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
        創建摘要資料表

        Args:
            validation_result (dict): Validation result / 驗證結果

        Returns:
            pd.DataFrame: Summary statistics table / 摘要統計表
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
        創建條件違規統計表（包含每條具體規則的統計）

        Args:
            validation_result (dict): Validation result / 驗證結果

        Returns:
            pd.DataFrame: Constraint violation statistics table / 各條件違規統計表
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
            # Check if new format (containing specific rules) or old format (single statistics) / 檢查是否為新格式（包含具體規則）或舊格式（單一統計）
            if isinstance(type_data, dict):
                # Check if error message / 檢查是否為錯誤訊息
                if "error" in type_data and "failed_count" in type_data:
                    # Old format or error format / 舊格式或錯誤格式
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
                    # New format: contains multiple rules / 新格式：包含多條規則
                    for rule_name, rule_stats in type_data.items():
                        if isinstance(rule_stats, dict):
                            # Format violation examples / 格式化違規範例
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
        根據實驗鍵生成檔名

        Args:
            key (tuple): Experiment identification key
                - 單一 source: (Module, experiment_name)
                - 多 source: (Module, experiment_name, source_name)

        Returns:
            str: Generated filename (without extension) / 生成的檔名（不含副檔名）
        """
        output_prefix = self.config["output"]

        # Check if using default output / 檢查是否為預設的 output
        from petsard.reporter.reporter_base import ConfigDefaults

        is_default_output = output_prefix == ConfigDefaults.DEFAULT_OUTPUT_PREFIX

        if is_default_output:
            # When using default output, follow PETsARD naming convention / 使用預設 output 時，遵循 PETsARD 命名慣例
            if isinstance(key, tuple) and len(key) == 3:
                # 多 source 格式: (Module, experiment_name, source_name)
                module = key[0]
                exp_name = key[1]
                source_name = key[2]
                # 格式: {output}[Validation]_Source[來源名稱]_Constrainer[實驗名稱]
                filename = f"{output_prefix}[Validation]_Source[{source_name}]_{module}[{exp_name}]"
            elif isinstance(key, tuple) and len(key) == 2:
                # 單一 source 格式: (Module, experiment_name)
                module = key[0]
                exp_name = key[1]
                filename = f"{output_prefix}[Validation]_{module}[{exp_name}]"
            else:
                # 其他格式（向後相容）
                key_str = (
                    "_".join(str(k) for k in key)
                    if isinstance(key, tuple)
                    else str(key)
                )
                filename = f"{output_prefix}[Validation]_{key_str}"
        else:
            # When using custom output, directly use specified name / 自訂 output 時，直接使用指定的名稱
            filename = output_prefix

        return filename

    def _save_to_csv(self, result_data: dict, output_filename: str) -> None:
        """
        Save results as CSV files (generates 3 separate files)
        將結果保存為 CSV 檔案（產生 3 個獨立檔案）

        Args:
            result_data (dict): Dictionary containing data / 包含資料的字典
            output_filename (str): Output filename (without extension) / 輸出檔名（不含副檔名）
        """
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__}")

        # Save summary data / 保存摘要資料
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

        # Save constraint violation statistics / 保存條件違規統計
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

        # Save detailed violation records (if any) / 保存詳細違規記錄（如果有）
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
