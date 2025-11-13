"""
Pure functional ReporterSaveData
Completely stateless design, focused on business logic
"""

from typing import Any

from petsard.exceptions import ConfigError
from petsard.reporter.reporter_base import (
    BaseReporter,
    RegexPatterns,
    convert_full_expt_tuple_to_name,
)


class ReporterSaveData(BaseReporter):
    """
    Pure functional data saving reporter
    Completely stateless, focused on business logic
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - source (str | List[str]): The source of the data.
                - output (str, optional):
                    The output filename prefix for the report.
                    Default is 'petsard'.

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
        """
        super().__init__(config)

        # source should be string or list of string: Union[str, List[str]]
        if "source" not in self.config:
            raise ConfigError
        elif not isinstance(self.config["source"], str | list) or (
            isinstance(self.config["source"], list)
            and not all(isinstance(item, str) for item in self.config["source"])
        ):
            raise ConfigError

        # convert source to list if it is string
        if isinstance(self.config["source"], str):
            self.config["source"] = [self.config["source"]]

    def create(self, data: dict) -> dict[str, Any]:
        """
        Pure function: Process data and return result

        Args:
            data (dict): The data dictionary.
                Generating by ReporterOperator.set_input()
                See BaseReporter._verify_create_input() for format requirement.

        Returns:
            dict[str, Any]: Processed data dictionary

        Raises:
            ConfigError: If the index tuple is not an even number.
        """
        # verify input data
        self._verify_create_input(data)

        processed_data = {}

        # last 1 of index should remove postfix "_[xxx]" to match source
        for full_expt_tuple, df in data.items():
            # check if last 2 element of index in source
            last_module_expt_name = [
                full_expt_tuple[-2],
                RegexPatterns.POSTFIX_REMOVAL.sub("", full_expt_tuple[-1]),
            ]
            if any(item in self.config["source"] for item in last_module_expt_name):
                full_expt_name = convert_full_expt_tuple_to_name(full_expt_tuple)
                processed_data[full_expt_name] = df

        return processed_data

    def report(self, processed_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Pure function: Generate and save report

        Args:
            processed_data (dict[str, Any] | None): Processed data

        Returns:
            dict[str, Any]: Generated report data

        Notes:
            Some of the data may be None, such as Evaluator.get_global/columnwise/pairwise. These will be skipped.
        """
        if not processed_data:
            return {}

        saved_data = {}
        for expt_name, df in processed_data.items():
            # Some of the data may be None.
            #   e.g. Evaluator.get_global/columnwise/pairwise
            #   just skip it
            if df is None:
                continue

            # petsard_{expt_name}
            full_output = f"{self.config['output']}_{expt_name}"
            self._save(data=df, full_output=full_output)
            saved_data[expt_name] = df

        return saved_data
