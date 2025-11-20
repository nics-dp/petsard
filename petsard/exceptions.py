"""
PETsARD Exception Hierarchy

This module defines a structured exception hierarchy for the PETsARD framework,
providing detailed error information with error codes, context, and suggestions.
"""

from typing import Any


class PETsARDError(Exception):
    """
    Base class for all PETsARD exceptions.

    Provides structured error information including error codes, context,
    and resolution suggestions.

    Attributes:
        message: Error message
        error_code: Error code (e.g., "CONFIG_001")
        context: Additional error context information

    Example:
        ```python
        try:
            # Some operation
            pass
        except PETsARDError as e:
            print(f"Error: {e.message}")
            print(f"Code: {e.error_code}")
            print(f"Suggestion: {e.get_suggestion()}")
        ```
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        **context: Any
    ):
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        self.context = context

        # Construct full error message
        full_message = f"[{self.error_code}] {message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items() if k != "suggestion")
            if context_str:
                full_message += f" ({context_str})"

        super().__init__(full_message)

    def get_suggestion(self) -> str:
        """Get resolution suggestion for this error."""
        return self.context.get("suggestion", "Please check documentation or contact support")


# ===== Configuration Errors =====

class ConfigurationError(PETsARDError):
    """
    Base class for configuration-related errors.

    This category includes errors related to:
    - Missing or invalid configuration files
    - Invalid configuration format
    - Missing required configuration fields
    - Invalid configuration values
    """


class NoConfigError(ConfigurationError):
    """
    Raised when required configuration is missing.

    Common causes:
    - No configuration file or string provided
    - Configuration file path does not exist
    - Configuration string is empty

    Resolution:
    1. Verify configuration file path is correct
    2. Check file permissions
    3. Ensure configuration string is valid YAML

    Used in:
    - petsard/executor.py: When config parameter is missing
    - petsard/config.py: When required config sections are missing

    Example:
        ```python
        try:
            executor = Executor(config=None)
        except NoConfigError as e:
            print(f"Configuration error: {e}")
            print(f"Suggestion: {e.get_suggestion()}")
        ```
    """

    def __init__(self, message: str = "No configuration provided", config_path: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIG_001",
            config_path=config_path,
            suggestion="Provide a valid configuration file path or YAML string",
            **kwargs
        )


class ConfigError(ConfigurationError):
    """
    Raised when configuration format or content is invalid.

    Common causes:
    - Invalid YAML format
    - Missing required fields
    - Field values out of valid range
    - Type mismatch in configuration values

    Resolution:
    1. Validate YAML syntax
    2. Check all required fields are present
    3. Verify field values are within valid ranges
    4. Ensure correct data types

    Used in:
    - petsard/executor.py: YAML parsing errors, invalid log settings
    - petsard/config_base.py: Config validation failures
    - petsard/adapter.py: Invalid module configurations
    - petsard/loader/loader.py: Invalid loader configurations
    - petsard/reporter/*.py: Invalid reporter configurations

    Example:
        ```python
        try:
            config = {"log_level": "INVALID"}  # Invalid log level
            executor = Executor(config=yaml.dump(config))
        except ConfigError as e:
            print(f"Invalid configuration: {e}")
            print(f"Valid values: {e.context.get('valid_values')}")
        ```
    """

    def __init__(
        self,
        message: str = "Invalid configuration",
        config_section: str = None,
        invalid_field: str = None,
        provided_value: Any = None,
        valid_values: list = None,
        **kwargs
    ):
        suggestion = "Check configuration format and required fields"
        if valid_values:
            suggestion = f"Valid values are: {', '.join(map(str, valid_values))}"

        super().__init__(
            message=message,
            error_code="CONFIG_002",
            config_section=config_section,
            invalid_field=invalid_field,
            provided_value=provided_value,
            valid_values=valid_values,
            suggestion=suggestion,
            **kwargs
        )


# ===== Data Processing Errors =====

class DataProcessingError(PETsARDError):
    """
    Base class for data processing errors.

    This category includes errors related to:
    - Data loading failures
    - Metadata processing issues
    - Schema mismatches
    - Data format problems
    """


class UnableToLoadError(DataProcessingError):
    """
    Raised when data loading fails.

    Common causes:
    - File does not exist or cannot be accessed
    - Unsupported file format
    - Corrupted data content
    - Missing required dependencies (e.g., openpyxl for Excel)

    Resolution:
    1. Verify file path is correct
    2. Check file permissions
    3. Ensure file format is supported
    4. Install required dependencies

    Used in:
    - petsard/loader/loader_pandas.py: File reading failures

    Example:
        ```python
        try:
            loader = Loader(method="csv", path="missing_file.csv")
            data, schema = loader.load()
        except UnableToLoadError as e:
            print(f"Load failed: {e}")
            print(f"File: {e.context.get('filepath')}")
        ```
    """

    def __init__(self, message: str = "Unable to load data", filepath: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DATA_001",
            filepath=filepath,
            suggestion="Check file path, format, and permissions",
            **kwargs
        )


class MetadataError(DataProcessingError):
    """
    Raised for metadata-related errors.

    Common causes:
    - Metadata format is incorrect
    - Metadata doesn't match actual data
    - Missing required metadata information
    - Invalid schema definitions

    Resolution:
    1. Verify metadata format matches specification
    2. Check metadata fields match data columns
    3. Ensure all required metadata is present
    4. Validate type definitions

    Used in:
    - petsard/metadater/metadater.py: Type casting errors, schema validation
    - petsard/metadater/metadata.py: Invalid field definitions

    Example:
        ```python
        try:
            schema = SchemaMetadata(attributes=[...])
        except MetadataError as e:
            print(f"Metadata error: {e}")
        ```
    """

    def __init__(self, message: str = "Metadata error", **kwargs):
        super().__init__(
            message=message,
            error_code="DATA_002",
            suggestion="Verify metadata format and content match data structure",
            **kwargs
        )


class UnableToFollowMetadataError(DataProcessingError):
    """
    Raised when unable to follow specified metadata schema.

    Common causes:
    - Metadata schema doesn't match data structure
    - Required transformations cannot be applied
    - Type conversions fail

    Resolution:
    1. Verify metadata schema matches data
    2. Check column names and types
    3. Ensure transformations are applicable

    Used in:
    - petsard/loader/loader.py: Schema following failures

    Example:
        ```python
        try:
            loader.load()  # With metadata that doesn't match data
        except UnableToFollowMetadataError as e:
            print(f"Cannot follow metadata: {e}")
        ```
    """

    def __init__(self, message: str = "Unable to follow metadata", **kwargs):
        super().__init__(
            message=message,
            error_code="DATA_003",
            suggestion="Ensure metadata schema matches actual data structure",
            **kwargs
        )


class BenchmarkDatasetsError(DataProcessingError):
    """
    Raised for benchmark dataset-related errors.

    Common causes:
    - Benchmark dataset not found
    - Download failure
    - Corrupted benchmark data
    - Missing required benchmark dependencies

    Resolution:
    1. Check internet connection
    2. Verify benchmark name is correct
    3. Check disk space
    4. Clear cache and retry

    Used in:
    - petsard/adapter.py: Benchmark download/load failures
    - petsard/loader/benchmarker.py: Benchmark processing errors

    Example:
        ```python
        try:
            loader = Loader(method="adult")
        except BenchmarkDatasetsError as e:
            print(f"Benchmark error: {e}")
        ```
    """

    def __init__(self, message: str = "Benchmark dataset error", dataset_name: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DATA_004",
            dataset_name=dataset_name,
            suggestion="Check benchmark name and internet connection",
            **kwargs
        )


# ===== Operation State Errors =====

class OperationStateError(PETsARDError):
    """
    Base class for operation state errors.

    This category includes errors related to:
    - Objects not properly initialized
    - Missing required pre-conditions
    - Invalid operation sequences
    """


class UncreatedError(OperationStateError):
    """
    Raised when attempting to use an object that hasn't been created.

    Common causes:
    - Using object before calling create() method
    - Creation process failed
    - Object initialization incomplete

    Resolution:
    1. Call create() method before using the object
    2. Verify creation succeeded
    3. Check for errors during creation

    Used in:
    - petsard/synthesizer/synthesizer.py: Synthesizer not created
    - petsard/evaluator/evaluator.py: Evaluator not created

    Example:
        ```python
        try:
            synthesizer = Synthesizer(method="gaussian_copula")
            synthesizer.sample(n=100)  # Error: not created yet
        except UncreatedError as e:
            print(f"Object not created: {e}")
            print(f"Call {e.context.get('object_type')}.create() first")
        ```
    """

    def __init__(self, message: str = "Object not created", object_type: str = None, **kwargs):
        suggestion = "Call create() method first"
        if object_type:
            suggestion = f"Call {object_type}.create() method before using it"

        super().__init__(
            message=message,
            error_code="STATE_001",
            object_type=object_type,
            suggestion=suggestion,
            **kwargs
        )


class UnfittedError(OperationStateError):
    """
    Raised when attempting to use a model that hasn't been fitted.

    Common causes:
    - Using model before calling fit() method
    - Fitting process failed
    - Model training incomplete

    Resolution:
    1. Call fit() method with training data
    2. Verify fitting succeeded
    3. Check training data validity

    Used in:
    - petsard/processor/base.py: Processor not fitted
    - petsard/processor/discretizing.py: Discretizer not fitted
    - petsard/processor/scaler.py: Scaler not fitted
    - petsard/processor/encoder.py: Encoder not fitted
    - petsard/processor/missing.py: Missing value handler not fitted
    - petsard/processor/constant.py: Constant processor not fitted
    - petsard/synthesizer/synthesizer_base.py: Synthesizer not fitted

    Example:
        ```python
        try:
            processor = Processor()
            processor.transform(data)  # Error: not fitted yet
        except UnfittedError as e:
            print(f"Model not fitted: {e}")
            print(f"Call {e.context.get('model_type')}.fit() first")
        ```
    """

    def __init__(self, message: str = "Model not fitted", model_type: str = None, **kwargs):
        suggestion = "Call fit() method with training data first"
        if model_type:
            suggestion = f"Call {model_type}.fit() method before using it"

        super().__init__(
            message=message,
            error_code="STATE_002",
            model_type=model_type,
            suggestion=suggestion,
            **kwargs
        )


class UnexecutedError(OperationStateError):
    """
    Raised when attempting to access results before execution.

    Common causes:
    - Accessing results before workflow execution
    - Execution failed or incomplete
    - Accessing data from unexecuted modules

    Resolution:
    1. Execute the workflow first
    2. Check execution completed successfully
    3. Verify all required modules were executed

    Used in:
    - petsard/status.py: Accessing report/metadata before execution
    - petsard/reporter/reporter_save_report.py: Accessing unexecuted results

    Example:
        ```python
        try:
            status = Status()
            report = status.get_report()  # Error: not executed yet
        except UnexecutedError as e:
            print(f"Workflow not executed: {e}")
        ```
    """

    def __init__(self, message: str = "Workflow not executed", **kwargs):
        super().__init__(
            message=message,
            error_code="STATE_003",
            suggestion="Execute the workflow before accessing results",
            **kwargs
        )


# ===== Execution Errors =====

class ExecutionError(PETsARDError):
    """
    Base class for execution-time errors.

    This category includes errors related to:
    - Synthesis failures
    - Evaluation failures
    - Transformation errors
    - Runtime processing issues
    """


class UnableToSynthesizeError(ExecutionError):
    """
    Raised when data synthesis fails.

    Common causes:
    - Incomplete metadata
    - Synthesis method doesn't support data type
    - Data quality issues
    - Insufficient training data

    Resolution:
    1. Check metadata completeness
    2. Verify data types are supported
    3. Review data quality
    4. Try different synthesis method

    Used in:
    - petsard/synthesizer/sdv.py: SDV synthesis failures

    Example:
        ```python
        try:
            synthesizer.create(data, schema)
            syn_data = synthesizer.sample(n=1000)
        except UnableToSynthesizeError as e:
            print(f"Synthesis failed: {e}")
            print(f"Method: {e.context.get('synthesizer_method')}")
        ```
    """

    def __init__(self, message: str = "Unable to synthesize data", synthesizer_method: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXEC_001",
            synthesizer_method=synthesizer_method,
            suggestion="Check metadata completeness and data quality",
            **kwargs
        )


class UnableToEvaluateError(ExecutionError):
    """
    Raised when evaluation fails.

    Common causes:
    - Missing required datasets (ori/syn/control)
    - Inconsistent data formats
    - Evaluation method doesn't support data type
    - Invalid evaluation configuration

    Resolution:
    1. Verify all required datasets are present
    2. Check data format consistency
    3. Review evaluation method requirements
    4. Validate evaluation configuration

    Used in:
    - Currently not explicitly used (placeholder for future use)

    Example:
        ```python
        try:
            evaluator.eval(data={"ori": ori_data})  # Missing syn data
        except UnableToEvaluateError as e:
            print(f"Evaluation failed: {e}")
            print(f"Method: {e.context.get('evaluator_method')}")
        ```
    """

    def __init__(self, message: str = "Unable to evaluate data", evaluator_method: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXEC_002",
            evaluator_method=evaluator_method,
            suggestion="Check all required datasets are present and formats are consistent",
            **kwargs
        )


class UnsupportedMethodError(ExecutionError):
    """
    Raised when an unsupported method is specified.

    Common causes:
    - Invalid synthesizer method name
    - Invalid evaluator method name
    - Method not available in current environment
    - Required dependencies not installed

    Resolution:
    1. Check method name spelling
    2. Verify method is supported
    3. Install required dependencies
    4. Check documentation for valid methods

    Used in:
    - petsard/loader/loader.py: Invalid loader method
    - petsard/loader/benchmarker.py: Invalid benchmark name
    - petsard/synthesizer/synthesizer.py: Invalid synthesizer method
    - petsard/synthesizer/sdv.py: Unsupported SDV model
    - petsard/evaluator/*.py: Invalid evaluation methods
    - petsard/reporter/reporter_base.py: Invalid reporter method

    Example:
        ```python
        try:
            synthesizer = Synthesizer(method="invalid_method")
        except UnsupportedMethodError as e:
            print(f"Unsupported method: {e}")
            print(f"Valid methods: {e.context.get('valid_methods')}")
        ```
    """

    def __init__(
        self,
        message: str = "Unsupported method",
        method_name: str = None,
        valid_methods: list = None,
        **kwargs
    ):
        suggestion = "Check documentation for valid methods"
        if valid_methods:
            suggestion = f"Valid methods are: {', '.join(valid_methods)}"

        super().__init__(
            message=message,
            error_code="EXEC_003",
            method_name=method_name,
            valid_methods=valid_methods,
            suggestion=suggestion,
            **kwargs
        )


class MissingDependencyError(ExecutionError):
    """
    Raised when a required optional dependency is not installed.

    Common causes:
    - Using a method that requires optional dependencies
    - Optional package not installed
    - Package version incompatible

    Resolution:
    1. Install the required package (e.g., pip install sdv)
    2. Check package version compatibility
    3. Use alternative methods that don't require the dependency

    Used in:
    - petsard/synthesizer/synthesizer.py: SDV synthesizer requires sdv package

    Example:
        ```python
        try:
            synthesizer = Synthesizer(method="sdv-single_table-gaussiancopula")
        except MissingDependencyError as e:
            print(f"Missing dependency: {e}")
            print(f"Install: {e.context.get('install_command')}")
        ```
    """

    def __init__(
        self,
        message: str = "Required dependency not installed",
        package_name: str = None,
        install_command: str = None,
        **kwargs
    ):
        suggestion = "Install the required package"
        if install_command:
            suggestion = f"Install with: {install_command}"
        elif package_name:
            suggestion = f"Install with: pip install {package_name}"

        super().__init__(
            message=message,
            error_code="EXEC_005",
            package_name=package_name,
            install_command=install_command,
            suggestion=suggestion,
            **kwargs
        )


class CustomMethodEvaluatorError(ExecutionError):
    """
    Raised when custom evaluator method encounters an error.

    Common causes:
    - Custom evaluator implementation error
    - Invalid custom evaluator configuration
    - Custom evaluator missing required methods

    Resolution:
    1. Review custom evaluator implementation
    2. Check evaluator inherits from correct base class
    3. Verify all required methods are implemented
    4. Test custom evaluator separately

    Used in:
    - petsard/evaluator/customer_evaluator.py: Custom evaluator errors

    Example:
        ```python
        try:
            evaluator = CustomEvaluator(custom_class="MyEvaluator")
            evaluator.eval(data)
        except CustomMethodEvaluatorError as e:
            print(f"Custom evaluator error: {e}")
        ```
    """

    def __init__(self, message: str = "Custom evaluator error", **kwargs):
        super().__init__(
            message=message,
            error_code="EXEC_004",
            suggestion="Review custom evaluator implementation and configuration",
            **kwargs
        )


# ===== Status Management Errors =====

class StatusError(PETsARDError):
    """
    Base class for status management errors.

    This category includes errors related to:
    - Snapshot operations
    - Timing records
    - State management
    """


class SnapshotError(StatusError):
    """
    Raised for snapshot operation errors.

    Common causes:
    - Attempting to access non-existent snapshot
    - Corrupted snapshot data
    - Missing snapshot metadata

    Resolution:
    1. Verify snapshot ID exists
    2. Check snapshot data integrity
    3. Review snapshot creation process

    Used in:
    - petsard/status.py: Snapshot restoration failures

    Example:
        ```python
        try:
            status.restore_snapshot("invalid_id")
        except SnapshotError as e:
            print(f"Snapshot error: {e}")
            print(f"Snapshot ID: {e.context.get('snapshot_id')}")
        ```
    """

    def __init__(self, message: str = "Snapshot error", snapshot_id: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="STATUS_001",
            snapshot_id=snapshot_id,
            suggestion="Verify snapshot ID and check data integrity",
            **kwargs
        )


class TimingError(StatusError):
    """
    Raised for timing record errors.

    Common causes:
    - Invalid timing data format
    - Missing paired START/END records
    - Corrupted timing information

    Resolution:
    1. Check timing record format
    2. Verify START/END record pairs
    3. Review timing data generation

    Used in:
    - petsard/status.py: Timing record processing failures

    Example:
        ```python
        try:
            status.record_timing_start(module, method)
        except TimingError as e:
            print(f"Timing error: {e}")
        ```
    """

    def __init__(self, message: str = "Timing error", **kwargs):
        super().__init__(
            message=message,
            error_code="STATUS_002",
            suggestion="Check timing record format and completeness",
            **kwargs
        )
