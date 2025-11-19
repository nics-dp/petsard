import logging
import re
from collections import deque
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

import pandas as pd

from petsard.adapter import BaseAdapter
from petsard.exceptions import (
    ConfigError,
    SnapshotError,
    StatusError,
    TimingError,
    UnexecutedError,
)
from petsard.metadater.metadata import Metadata, Schema
from petsard.metadater.metadater import SchemaMetadater
from petsard.metadater.schema_inferencer import SchemaInferencer
from petsard.processor import Processor
from petsard.synthesizer import Synthesizer


@dataclass(frozen=True)
class ExecutionSnapshot:
    """
    Simplified execution snapshot
    """

    snapshot_id: str
    module_name: str
    experiment_name: str
    timestamp: datetime
    metadata_before: Schema | None = None
    metadata_after: Schema | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimingRecord:
    """
    Simplified timing record
    """

    record_id: str
    module_name: str
    experiment_name: str
    step_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def complete(self, end_time: datetime | None = None) -> "TimingRecord":
        """Complete timing record"""
        if end_time is None:
            end_time = datetime.now()

        duration = round((end_time - self.start_time).total_seconds(), 2)

        return TimingRecord(
            record_id=self.record_id,
            module_name=self.module_name,
            experiment_name=self.experiment_name,
            step_name=self.step_name,
            start_time=self.start_time,
            end_time=end_time,
            duration_seconds=duration,
            context=self.context,
        )

    @property
    def formatted_duration(self) -> str:
        """Formatted duration"""
        return f"{self.duration_seconds:.2f}s" if self.duration_seconds else "N/A"


class TimingLogHandler(logging.Handler):
    """
    Simplified timing log handler
    """

    def __init__(self, status_instance):
        super().__init__()
        self.status = status_instance
        self._timing_pattern = re.compile(
            r"TIMING_(\w+)\|([^|]+)\|([^|]+)\|([^|]+)(?:\|([^|]+))?"
        )

    def emit(self, record):
        """Process timing log record"""
        try:
            message = record.getMessage()
            if not message.startswith("TIMING_"):
                return

            match = self._timing_pattern.match(message)
            if not match:
                return

            timing_type, module_name, step_name, timestamp_str, duration_str = (
                match.groups()
            )
            timestamp = float(timestamp_str)
            duration = float(duration_str) if duration_str else None

            expt_name = self.status._current_experiments.get(module_name, "default")

            if timing_type == "START":
                self.status._handle_timing_start(
                    module_name, expt_name, step_name, timestamp
                )
            elif timing_type in ["END", "ERROR"]:
                context = {"status": "error" if timing_type == "ERROR" else "completed"}
                self.status._handle_timing_end(
                    module_name, expt_name, step_name, timestamp, duration, context
                )

        except (ValueError, TypeError, AttributeError):
            pass  # Silently ignore parsing errors


class Status:
    """
    Status manager centered on Metadater

    Provides complete progress snapshot mechanism, tracking metadata changes before and after each module execution.
    Maintains compatibility with original Status interface.
    """

    def __init__(
        self,
        config,
        max_snapshots: int = 1000,
        max_changes: int = 5000,
        max_timings: int = 10000,
    ):
        """
        Initialize status manager

        Args:
            config: Configuration object
            max_snapshots: Maximum number of snapshots, prevents memory leak
            max_changes: Maximum number of change records
            max_timings: Maximum number of timing records
        """
        self.config = config
        self.sequence: list = config.sequence
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

        # Core Metadata instance - stores all change history
        self.metadata_obj = Metadata(
            id="status_metadata",
            name="Status Metadata",
            description="Metadata tracking for Status module",
        )

        # State storage - maintain compatibility with original interface
        self.status: dict = {}
        self.metadata: dict[str, Schema] = {}

        # Schema inferencer - used to infer Schema at each stage of pipeline
        self.schema_inferencer = SchemaInferencer()
        self.inferred_schemas: dict[str, Schema] = {}  # Store inferred Schema

        # Preprocessor input metadata memory - used for Postprocessor's many-to-one conversion restoration
        # Store Preprocessor's input Schema so Postprocessor knows the original dtype
        self.preprocessor_input_schema: Schema | None = None

        # Optimized snapshot functionality - use deque to limit size
        self.max_snapshots = max_snapshots
        self.max_timings = max_timings

        self.snapshots: deque[ExecutionSnapshot] = deque(maxlen=max_snapshots)
        self._snapshot_counter = 0

        # Snapshot index, use weak reference dict to avoid memory leak
        self._snapshot_index: dict[str, ExecutionSnapshot] = {}

        # Optimized time recording functionality
        self.timing_records: deque[TimingRecord] = deque(maxlen=max_timings)
        self._timing_counter = 0
        self._active_timings: dict[str, TimingRecord] = {}  # Track active timing

        # Compatibility support for original features
        if "Splitter" in self.sequence:
            self.exist_train_indices: list[set] = []
        if "Reporter" in self.sequence:
            self.report: dict = {}

        # Validation result storage - used for Constrainer validate mode
        self._validation_results: dict[str, dict] = {}

        # Set up logging handler to capture timing information
        self._timing_handler = TimingLogHandler(self)
        self._timing_handler.setLevel(logging.INFO)

        # Add handler to PETsARD's root logger
        petsard_logger = logging.getLogger("PETsARD")
        petsard_logger.addHandler(self._timing_handler)

        # Store mapping of current experiment names
        self._current_experiments: dict[str, str] = {}

    def _generate_id(self, prefix: str, counter_attr: str) -> str:
        """
        Unified ID generation method, avoid code duplication

        Args:
            prefix: ID prefix (e.g., 'snapshot', 'change', 'timing')
            counter_attr: Counter attribute name (e.g., '_snapshot_counter')

        Returns:
            str: Generated unique ID
        """
        current_counter = getattr(self, counter_attr)
        setattr(self, counter_attr, current_counter + 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{current_counter + 1:06d}_{timestamp}"

    def _generate_snapshot_id(self) -> str:
        """Generate snapshot ID"""
        return self._generate_id("snapshot", "_snapshot_counter")

    def _generate_timing_id(self) -> str:
        """Generate timing ID"""
        return self._generate_id("timing", "_timing_counter")

    def _merge_context(
        self, base_context: dict[str, Any], new_context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        Merge two context dictionaries.

        Args:
            base_context: Base context dictionary
            new_context: New context to merge, can be None

        Returns:
            dict[str, Any]: Merged context dictionary
        """
        if new_context:
            merged = base_context.copy()
            merged.update(new_context)
            return merged
        return base_context

    def _create_snapshot(
        self,
        module: str,
        expt: str,
        metadata_before: Schema | None = None,
        metadata_after: Schema | None = None,
        context: dict[str, Any] | None = None,
    ) -> ExecutionSnapshot:
        """
        Create execution snapshot

        Args:
            module: Module name
            expt: Experiment name
            metadata_before: Metadata before execution
            metadata_after: Metadata after execution
            context: Execution context

        Returns:
            ExecutionSnapshot: Created snapshot
        """
        snapshot = ExecutionSnapshot(
            snapshot_id=self._generate_snapshot_id(),
            module_name=module,
            experiment_name=expt,
            timestamp=datetime.now(),
            metadata_before=metadata_before,
            metadata_after=metadata_after,
            context=context or {},
        )

        self.snapshots.append(snapshot)
        # Update index
        self._snapshot_index[snapshot.snapshot_id] = snapshot
        # If limit exceeded, clean up old index entries
        if (
            len(self.snapshots) == self.max_snapshots
            and len(self._snapshot_index) > self.max_snapshots
        ):
            # Clean up index entries not in deque
            valid_ids = {s.snapshot_id for s in self.snapshots}
            self._snapshot_index = {
                k: v for k, v in self._snapshot_index.items() if k in valid_ids
            }

        self._logger.debug(
            f"Created snapshot: {snapshot.snapshot_id} for {module}[{expt}]"
        )
        return snapshot

    def start_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Start timing

        Args:
            module: Module name
            expt: Experiment name
            step: Step name
            context: Additional context information

        Returns:
            str: Timing record ID
        """
        timing_id = self._generate_timing_id()
        timing_key = f"{module}_{expt}_{step}"

        timing_record = TimingRecord(
            record_id=timing_id,
            module_name=module,
            experiment_name=expt,
            step_name=step,
            start_time=datetime.now(),
            context=context or {},
        )

        self._active_timings[timing_key] = timing_record
        self._logger.debug(f"Start timing: {timing_key} - {timing_id}")

        return timing_id

    def end_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: dict[str, Any] | None = None,
    ) -> TimingRecord | None:
        """
        End timing

        Args:
            module: Module name
            expt: Experiment name
            step: Step name
            context: Additional context information

        Returns:
            Optional[TimingRecord]: Completed timing record, returns None if no corresponding start record found
        """
        timing_key = f"{module}_{expt}_{step}"

        if timing_key not in self._active_timings:
            self._logger.warning(
                f"Cannot find corresponding start timing record: {timing_key}"
            )
            return None

        active_timing = self._active_timings.pop(timing_key)

        # Merge additional context information
        merged_context = self._merge_context(active_timing.context, context)

        completed_timing = active_timing.complete()
        # Update context
        completed_timing = TimingRecord(
            record_id=completed_timing.record_id,
            module_name=completed_timing.module_name,
            experiment_name=completed_timing.experiment_name,
            step_name=completed_timing.step_name,
            start_time=completed_timing.start_time,
            end_time=completed_timing.end_time,
            duration_seconds=completed_timing.duration_seconds,
            context=merged_context,
        )

        self.timing_records.append(completed_timing)

        self._logger.debug(
            f"End timing: {timing_key} - Duration: {completed_timing.formatted_duration}"
        )

        return completed_timing

    def _create_timing_record(
        self,
        timing_id: str,
        module: str,
        expt: str,
        step: str,
        start_time: datetime,
        end_time: datetime | None = None,
        duration_seconds: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> TimingRecord:
        """
        Unified timing record creation method, avoid code duplication

        Args:
            timing_id: Timing record ID
            module: Module name
            expt: Experiment name
            step: Step name
            start_time: Start time
            end_time: End time
            duration_seconds: Duration in seconds
            context: Context information

        Returns:
            TimingRecord: Created timing record
        """
        return TimingRecord(
            record_id=timing_id,
            module_name=module,
            experiment_name=expt,
            step_name=step,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            context=context or {},
        )

    def _handle_timing_start(self, module: str, expt: str, step: str, timestamp: float):
        """
        Process start timing information parsed from logging

        Args:
            module: Module name
            expt: Experiment name
            step: Step name
            timestamp: Timestamp
        """
        try:
            timing_id = self._generate_timing_id()
            timing_key = f"{module}_{expt}_{step}"
            start_time = datetime.fromtimestamp(timestamp)

            timing_record = self._create_timing_record(
                timing_id=timing_id,
                module=module,
                expt=expt,
                step=step,
                start_time=start_time,
                context={"source": "logging"},
            )

            self._active_timings[timing_key] = timing_record
            self._logger.debug(f"Start timing from logging: {timing_key} - {timing_id}")

        except (ValueError, OSError) as e:
            raise TimingError(f"Unable to process timing start event: {e}") from e

    def _handle_timing_end(
        self,
        module: str,
        expt: str,
        step: str,
        timestamp: float,
        duration: float | None,
        context: dict[str, Any],
    ):
        """
        Process end timing information parsed from logging

        Args:
            module: Module name
            expt: Experiment name
            step: Step name
            timestamp: End timestamp
            duration: Duration in seconds
            context: Context information
        """
        try:
            timing_key = f"{module}_{expt}_{step}"
            end_time = datetime.fromtimestamp(timestamp)
            rounded_duration = round(duration, 2) if duration is not None else None

            if timing_key in self._active_timings:
                # Has corresponding start record
                active_timing = self._active_timings.pop(timing_key)
                merged_context = self._merge_context(active_timing.context, context)

                completed_timing = self._create_timing_record(
                    timing_id=active_timing.record_id,
                    module=module,
                    expt=expt,
                    step=step,
                    start_time=active_timing.start_time,
                    end_time=end_time,
                    duration_seconds=rounded_duration,
                    context=merged_context,
                )
            else:
                # No corresponding start record, create orphaned record
                timing_id = self._generate_timing_id()
                start_time = datetime.fromtimestamp(timestamp - (duration or 0))
                orphaned_context = {**context, "source": "logging", "orphaned": True}

                completed_timing = self._create_timing_record(
                    timing_id=timing_id,
                    module=module,
                    expt=expt,
                    step=step,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=rounded_duration,
                    context=orphaned_context,
                )

            self.timing_records.append(completed_timing)

            self._logger.debug(
                f"End timing from logging: {timing_key} - Duration: {completed_timing.formatted_duration}"
            )

        except (ValueError, OSError) as e:
            raise TimingError(f"Unable to process timing end event: {e}") from e

    def put(self, module: str, expt: str, operator: BaseAdapter):
        """
        Add module status and operator to status dictionary

        This is the core method, integrating Metadater's snapshot functionality

        Args:
            module: Current module name
            expt: Current experiment name
            operator: Current operator
        """
        # Record current module's experiment name for logging handler use
        self._current_experiments[module] = expt
        # Get metadata state before execution
        metadata_before = self.metadata.get(module) if module in self.metadata else None

        # State update logic (maintain original logic)
        if module in self.status:
            module_seq_idx = self.sequence.index(module)
            module_to_keep = set(self.sequence[: module_seq_idx + 1])
            keys_to_remove = [key for key in self.status if key not in module_to_keep]
            for exist_module in keys_to_remove:
                del self.status[exist_module]

        # Use Metadater to manage metadata
        if module in ["Loader", "Splitter", "Preprocessor"]:
            new_metadata = operator.get_metadata()

            # CRITICAL: For Preprocessor, remember its input schema for Postprocessor use
            # This solves the reversibility problem of many-to-one transformations (e.g., int64/float64 → float64)
            if module == "Preprocessor":
                # Store Preprocessor's input Schema (from Loader or Splitter)
                pre_module = self.get_pre_module("Preprocessor")
                if pre_module and pre_module in self.metadata:
                    self.preprocessor_input_schema = self.metadata[pre_module]
                    self._logger.info(
                        f"Remember Preprocessor input Schema (from {pre_module})"
                    )

                # CRITICAL FIX: Use Preprocessor's actual output Schema, not inferred Schema
                # After Preprocessor execution, its output Schema is the real data structure (e.g., after EncoderUniform it's float64, category=False)
                # Inferred Schema is only for prediction, should not override actual execution results
                #
                # Before fix: Use inferred Schema (category=True, type=string) → CTGAN misidentifies as high cardinality category
                # After fix: Use actual Schema (category=False, type=float64) → CTGAN correctly processes as numeric
                self._logger.info(
                    f"Using Preprocessor actual output Schema ({len(new_metadata.attributes)} fields)"
                )
                # new_metadata is already Preprocessor's actual output, use directly

            # Use SchemaMetadater.diff to track changes
            if metadata_before is not None and hasattr(operator, "get_data"):
                # Calculate differences
                diff_result = SchemaMetadater.diff(metadata_before, operator.get_data())

                # Record changes to Metadata
                timestamp = datetime.now().isoformat()
                change_record = {
                    "timestamp": timestamp,
                    "module": f"{module}[{expt}]",
                    "before_id": metadata_before.id,
                    "after_id": new_metadata.id,
                    "diff": diff_result,
                }

                # Update Metadata's change_history and diffs
                # Since Metadata is frozen, need to rebuild
                updated_change_history = list(self.metadata_obj.change_history)
                updated_change_history.append(change_record)

                updated_diffs = dict(self.metadata_obj.diffs)
                if timestamp not in updated_diffs:
                    updated_diffs[timestamp] = {}
                updated_diffs[timestamp][module] = diff_result

                self.metadata_obj = replace(
                    self.metadata_obj,
                    change_history=updated_change_history,
                    diffs=updated_diffs,
                    updated_at=datetime.now(),
                )

            self.set_metadata(module, new_metadata)

        # Reporter processing
        if module == "Reporter":
            self.set_report(report=operator.get_result())

        # Splitter processing - update exist_train_indices
        if module == "Splitter" and hasattr(operator, "get_train_indices"):
            train_indices = operator.get_train_indices()
            self.update_exist_train_indices(train_indices)

        # Constrainer processing - store validation results
        if module == "Constrainer" and hasattr(operator, "get_validation_result"):
            validation_result = operator.get_validation_result()
            if validation_result is not None:
                self.put_validation_result(module, validation_result)
                self._logger.info(f"Stored validation result for {module}[{expt}]")

        # Create execution snapshot
        metadata_after = self.metadata.get(module)
        self._create_snapshot(
            module=module,
            expt=expt,
            metadata_before=metadata_before,
            metadata_after=metadata_after,
            context={
                "operator_type": type(operator).__name__,
                "sequence_position": self.sequence.index(module)
                if module in self.sequence
                else -1,
            },
        )

        # Update status dictionary (maintain original format)
        temp = {}
        temp["expt"] = expt
        temp["operator"] = operator
        self.status[module] = temp

        self._logger.info(
            f"Status updated: {module}[{expt}] - Snapshot count: {len(self.snapshots)}"
        )

    # === Original interface methods (maintain compatibility) ===

    def set_report(self, report: dict) -> None:
        """Add report data to report dictionary"""
        if not hasattr(self, "report"):
            raise UnexecutedError

        for eval_expt_name, report_data in report.items():
            self.report[eval_expt_name] = report_data.copy()

    def get_pre_module(self, curr_module: str) -> str:
        """Get the previous module in the sequence"""
        module_idx = self.sequence.index(curr_module)
        if module_idx == 0:
            return None
        else:
            return self.sequence[module_idx - 1]

    def get_result(self, module: str) -> dict | pd.DataFrame:
        """Get the result of a specific module"""
        return self.status[module]["operator"].get_result()

    def get_full_expt(self, module: str = None) -> dict:
        """Get dictionary of module names and corresponding experiment names"""
        if module is None:
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in self.sequence
                if seq_module in self.status
            }
        else:
            if module not in self.sequence:
                raise ConfigError

            module_idx = self.sequence.index(module) + 1
            sub_sequence = self.sequence[:module_idx]
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in sub_sequence
            }

    def get_exist_train_indices(self) -> list[set]:
        """Get the list of unique training index sets generated by the Splitter module"""
        return self.exist_train_indices

    def update_exist_train_indices(self, new_indices: list[set]) -> None:
        """
        Update exist_train_indices by adding new training indices to the set list

        Args:
            new_indices: New training index set list[set]
        """
        if not hasattr(self, "exist_train_indices"):
            self.exist_train_indices = []

        for index_set in new_indices:
            self.exist_train_indices.append(index_set)

    def set_metadata(self, module: str, metadata: Schema) -> None:
        """Set metadata for the given module"""
        self.metadata[module] = metadata

    def get_metadata(self, module: str = "Loader") -> Schema:
        """Get metadata of the dataset"""
        if module not in self.metadata:
            raise UnexecutedError
        return self.metadata[module]

    def get_preprocessor_input_schema(self) -> Schema | None:
        """
        Get Preprocessor's input Schema

        This is used for Postprocessor's many-to-one transformation restoration,
        e.g., int64 → scaler → float64 → inverse → int64

        Returns:
            Preprocessor's input Schema, returns None if not exists
        """
        return self.preprocessor_input_schema

    def get_synthesizer(self) -> Synthesizer:
        """Get synthesizer instance"""
        if "Synthesizer" in self.status:
            return self.status["Synthesizer"]["operator"].synthesizer
        else:
            raise UnexecutedError

    def get_processor(self) -> Processor:
        """Get the dataset processor"""
        if "Preprocessor" in self.status:
            return self.status["Preprocessor"]["operator"].processor
        else:
            raise UnexecutedError

    def get_report(self) -> dict:
        """Get report data generated by Reporter module"""
        if not hasattr(self, "report"):
            raise UnexecutedError
        return self.report

    def put_validation_result(self, module: str, validation_result: dict) -> None:
        """
        Store Constrainer's validation result

        Args:
            module: Module name (usually "Constrainer")
            validation_result: Validation result dictionary containing:
                - total_rows (int): Total number of data rows
                - passed_rows (int): Number of rows passing all conditions
                - failed_rows (int): Number of rows failing conditions
                - pass_rate (float): Pass rate (0.0 to 1.0)
                - is_fully_compliant (bool): Whether 100% compliant
                - constraint_violations (dict): Violation statistics for each condition
                - violation_details (pd.DataFrame, optional): Detailed violation records
        """
        if not hasattr(self, "_validation_results"):
            self._validation_results = {}

        self._validation_results[module] = validation_result
        self._logger.debug(f"Store validation result: {module}")

    def get_validation_result(self, module: str = None) -> dict | None:
        """
        Get Constrainer's validation result

        Args:
            module: Module name, returns all validation results if None

        Returns:
            dict: Validation result dictionary, returns None if not exists
        """
        if not hasattr(self, "_validation_results"):
            return None

        if module is None:
            # Return all validation results
            return self._validation_results.copy() if self._validation_results else None

        return self._validation_results.get(module)

    # === New snapshot and change tracking methods ===

    def get_snapshots(self, module: str = None) -> list[ExecutionSnapshot]:
        """
        Get snapshot list

        Args:
            module: Optional module name filter

        Returns:
            List[ExecutionSnapshot]: Snapshot list
        """
        if module is None:
            return self.snapshots.copy()
        else:
            return [s for s in self.snapshots if s.module_name == module]

    def get_snapshot_by_id(self, snapshot_id: str) -> ExecutionSnapshot | None:
        """
        Get specific snapshot by ID - optimized version using index

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Optional[ExecutionSnapshot]: Snapshot object or None
        """
        return self._snapshot_index.get(snapshot_id)

    def get_change_history(self, module: str = None) -> list[dict[str, Any]]:
        """
        Get change history

        Args:
            module: Optional module name filter

        Returns:
            List[dict]: Change record list
        """
        if module is None:
            return self.metadata_obj.change_history
        else:
            return [
                ch
                for ch in self.metadata_obj.change_history
                if module in ch.get("module", "")
            ]

    def get_metadata_evolution(self, module: str = "Loader") -> list[Schema]:
        """
        Get metadata evolution history for specific module - optimized version avoiding duplicates

        Args:
            module: Module name

        Returns:
            List[Schema]: Metadata evolution list
        """
        evolution = []
        seen_ids = set()

        for snapshot in self.snapshots:
            if snapshot.module_name == module:
                if (
                    snapshot.metadata_before
                    and snapshot.metadata_before.schema_id not in seen_ids
                ):
                    evolution.append(snapshot.metadata_before)
                    seen_ids.add(snapshot.metadata_before.schema_id)
                if (
                    snapshot.metadata_after
                    and snapshot.metadata_after.schema_id not in seen_ids
                ):
                    evolution.append(snapshot.metadata_after)
                    seen_ids.add(snapshot.metadata_after.schema_id)
        return evolution

    def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore state from snapshot (basic implementation)

        Args:
            snapshot_id: Snapshot ID

        Returns:
            bool: Whether restoration was successful
        """
        snapshot = self.get_snapshot_by_id(snapshot_id)
        if snapshot is None:
            self._logger.error(f"Cannot find snapshot: {snapshot_id}")
            return False

        try:
            # Validate snapshot integrity
            if not snapshot.metadata_after:
                raise SnapshotError(
                    f"Snapshot {snapshot_id} has no recoverable metadata"
                )

            if not hasattr(snapshot.metadata_after, "schema_id"):
                raise SnapshotError(
                    f"Snapshot {snapshot_id} has invalid metadata format"
                )

            # Restore metadata state
            self.metadata[snapshot.module_name] = snapshot.metadata_after
            self._logger.info(
                f"Restored {snapshot.module_name} metadata from snapshot {snapshot_id}"
            )
            return True

        except SnapshotError as e:
            self._logger.error(f"Snapshot restoration failed: {e}")
            return False
        except (AttributeError, KeyError) as e:
            self._logger.error(f"Snapshot data access error: {e}")
            return False
        except Exception as e:
            self._logger.error(
                f"Unexpected snapshot restoration error: {e}", exc_info=True
            )
            raise StatusError(
                f"Unexpected error during snapshot restoration: {e}"
            ) from e

    def get_status_summary(self) -> dict[str, Any]:
        """
        Get status summary information

        Returns:
            Dict[str, Any]: Status summary
        """
        # Calculate change statistics
        total_changes = len(self.metadata_obj.change_history)
        last_change = (
            self.metadata_obj.change_history[-1]
            if self.metadata_obj.change_history
            else None
        )

        return {
            "sequence": self.sequence,
            "active_modules": list(self.status.keys()),
            "metadata_modules": list(self.metadata.keys()),
            "total_snapshots": len(self.snapshots),
            "total_changes": total_changes,
            "total_diffs": len(self.metadata_obj.diffs),
            "last_snapshot": self.snapshots[-1].snapshot_id if self.snapshots else None,
            "last_change": last_change,
        }

    def get_timing_records(self, module: str = None) -> list[TimingRecord]:
        """
        Get timing records for specific module

        Args:
            module: Optional module name filter, returns all records if None

        Returns:
            List[TimingRecord]: Timing record list
        """
        if module is None:
            return self.timing_records.copy()
        else:
            return [r for r in self.timing_records if r.module_name == module]

    def get_timing_report_data(self) -> pd.DataFrame:
        """
        Get timing record data suitable for Reporter use - optimized version

        Returns:
            pd.DataFrame: DataFrame of timing records
        """
        if not self.timing_records:
            return pd.DataFrame()

        # Use list comprehension and pre-allocation to improve performance
        data = [
            {
                "record_id": record.record_id,
                "module_name": record.module_name,
                "experiment_name": record.experiment_name,
                "step_name": record.step_name,
                "start_time": record.start_time.isoformat(),
                "end_time": record.end_time.isoformat() if record.end_time else None,
                "duration_seconds": record.duration_seconds,
                **record.context,  # Expand extra information from context
            }
            for record in self.timing_records
        ]

        return pd.DataFrame(data)

    def get_data_by_module(self, modules: str | list[str]) -> dict[str, pd.DataFrame]:
        """
        Get data by module name
        Designed specifically for Describer and Reporter, uses only module names

        Args:
            modules: Module name or list of names
                - 'Loader', 'Splitter', 'Preprocessor', 'Synthesizer', 'Postprocessor', 'Constrainer'
                - 'Evaluator', 'Describer', etc.

        Returns:
            dict[str, pd.DataFrame]: key is module name, value is data
        """
        if isinstance(modules, str):
            modules = [modules]

        data_sources = {}

        for module_name in modules:
            if module_name not in self.status:
                continue

            result = self.get_result(module_name)

            if isinstance(result, pd.DataFrame):
                data_sources[module_name] = result
            elif isinstance(result, dict):
                # If dictionary (like Splitter's result), expand to module_key format
                for key, value in result.items():
                    if isinstance(value, pd.DataFrame):
                        data_sources[f"{module_name}_{key}"] = value

        return data_sources
