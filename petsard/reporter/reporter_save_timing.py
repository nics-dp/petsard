"""
Pure functional ReporterSaveTiming
Completely stateless design, focused on business logic
"""

import pandas as pd

from petsard.reporter.reporter_base import BaseReporter


class ReporterSaveTiming(BaseReporter):
    """
    Pure functional timing reporter
    Completely stateless, focused on business logic
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'petsard'.
                - module (str or list, optional): Module name(s) to filter timing data.
                - time_unit (str, optional): Time unit for reporting ('seconds', 'minutes', 'hours', 'days').
                    Default is 'seconds'.
        """
        super().__init__(config)

        # Handle module filtering
        module = self.config.get("module", [])
        if isinstance(module, str):
            module = [module]
        elif module is None:
            module = []
        self.config["modules"] = module

        # Handle time unit
        time_unit = self.config.get("time_unit", "seconds")
        valid_units = ["days", "hours", "minutes", "seconds"]
        if time_unit not in valid_units:
            time_unit = "seconds"
        self.config["time_unit"] = time_unit

    def create(self, data: dict = None) -> pd.DataFrame | None:
        """
        Pure function: Process timing data and return result

        Args:
            data (dict): The data used for creating the timing report.
                - timing_data (pd.DataFrame): The timing data DataFrame.

        Returns:
            pd.DataFrame | None: Processed timing data, returns None if no data
        """
        if data is None:
            data = {}

        timing_data = data.get("timing_data")

        # Handle empty or missing timing data
        if timing_data is None or (
            isinstance(timing_data, pd.DataFrame) and timing_data.empty
        ):
            return None

        return self._process_timing_data(timing_data)

    def report(self, processed_data: pd.DataFrame | None = None) -> pd.DataFrame | None:
        """
        Pure function: Generate and save report

        Args:
            processed_data (pd.DataFrame | None): Processed timing data

        Returns:
            pd.DataFrame | None: Generated report data
        """
        # Handle empty data situation
        if processed_data is None:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__.split('.')[-1]}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return None

        if processed_data.empty:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__.split('.')[-1]}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return None

        # Save report
        full_output: str = f"{self.config['output']}_[Timing]"
        self._save(data=processed_data, full_output=full_output)

        return processed_data

    def _process_timing_data(self, timing_data: pd.DataFrame) -> pd.DataFrame:
        """
        Core logic for processing timing data

        Args:
            timing_data (pd.DataFrame): Raw timing data

        Returns:
            pd.DataFrame: Processed timing data
        """
        # Copy data to avoid modifying original data
        timing_data = timing_data.copy()

        # Filter by modules if specified
        if self.config["modules"]:
            timing_data = timing_data[
                timing_data["module_name"].isin(self.config["modules"])
            ]

        # Handle time unit conversion
        time_unit = self.config["time_unit"]
        if time_unit != "seconds":
            # Create new column with converted time
            duration_col = f"duration_{time_unit}"
            if time_unit == "minutes":
                timing_data[duration_col] = timing_data["duration_seconds"] / 60
            elif time_unit == "hours":
                timing_data[duration_col] = timing_data["duration_seconds"] / 3600
            elif time_unit == "days":
                timing_data[duration_col] = timing_data["duration_seconds"] / 86400

            # Remove the original duration_seconds column
            timing_data = timing_data.drop(columns=["duration_seconds"])

            # Reorder columns to put the new duration column in the right place
            cols = list(timing_data.columns)
            if duration_col in cols:
                cols.remove(duration_col)
                # Insert after 'end_time' if it exists
                if "end_time" in cols:
                    insert_idx = cols.index("end_time") + 1
                    cols.insert(insert_idx, duration_col)
                else:
                    cols.append(duration_col)
                timing_data = timing_data[cols]

        return timing_data
