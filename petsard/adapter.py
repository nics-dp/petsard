import functools
import logging
import time
from copy import deepcopy
from datetime import timedelta

import pandas as pd

from petsard.constrainer import Constrainer
from petsard.evaluator import Describer, Evaluator
from petsard.exceptions import ConfigError
from petsard.loader import Loader, Splitter
from petsard.metadater.metadata import Schema
from petsard.metadater.metadater import SchemaMetadater
from petsard.processor import Processor
from petsard.reporter import Reporter
from petsard.synthesizer import Synthesizer


class BaseAdapter:
    """
    The interface of the objects used by Executor.run()
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict):
                A dictionary containing configuration parameters.

        Attr.:
            module_name (str):
                The name of the module.
            logger (logging.Logger):
                The logger object for the module.
            config (dict):
                The configuration parameters for the module.
            input (dict):
                The input data for the module.
        """
        self.module_name: str = self.__class__.__name__.replace("Operator", "Op")
        self._logger = logging.getLogger(f"PETsARD.{self.module_name}")

        self.config = config
        self.input: dict = {}
        if config is None:
            self._logger.error("Configuration is None")
            self._logger.debug("Error details: ", exc_info=True)
            raise ConfigError

    def run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict): A input dictionary contains module required input from Status.
                See self.set_input() for more details.
        """
        start_time: time = time.time()
        self._logger.info(f"TIMING_START|{self.module_name}|run|{start_time}")
        self._logger.info(f"Starting {self.module_name} execution")

        try:
            self._run(input)

            elapsed_time: time = time.time() - start_time
            formatted_elapsed_time: str = str(timedelta(seconds=round(elapsed_time)))

            self._logger.info(
                f"TIMING_END|{self.module_name}|run|{time.time()}|{elapsed_time}"
            )
            self._logger.info(
                f"Completed {self.module_name} execution "
                f"(elapsed: {formatted_elapsed_time})"
            )
        except Exception as e:
            elapsed_time: time = time.time() - start_time
            self._logger.error(
                f"TIMING_ERROR|{self.module_name}|run|{time.time()}|{elapsed_time}|{str(e)}"
            )
            raise

    @classmethod
    def log_and_raise_config_error(cls, func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self._logger.error(f"Configuration error in {func.__name__}: {str(e)}")
                self._logger.debug("Error details: ", exc_info=True)
                raise ConfigError(f"Config error in {func.__name__}: {str(e)}") from e

        return wrapper

    @staticmethod
    def log_and_raise_not_implemented(func):
        """Decorator for handling not implemented methods"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except NotImplementedError:
                self._logger.error(
                    f"Method {func.__name__} not implemented in {self.module_name}"
                )
                raise NotImplementedError(
                    f"Method {func.__name__} must be implemented in {self.module_name}"
                ) from None

        return wrapper

    @log_and_raise_not_implemented
    def _run(self, input: dict):
        """
        Execute the module's functionality.

        Args:
            input (dict): A input dictionary contains module required input from Status.
                See self.set_input() for more details.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def set_input(self, status) -> dict:
        """
        Set the input for the module.

        Args:
            status (Status): The current status object.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def get_result(self):
        """
        Retrieve the result of the module's operation,
            as data storage varies between modules.
        """
        raise NotImplementedError

    @log_and_raise_not_implemented
    def get_metadata(self) -> Schema:
        """
        Retrieve the metadata of the loaded data.

        Returns:
            (Schema): The metadata of the loaded data.
        """
        raise NotImplementedError


class LoaderAdapter(BaseAdapter):
    """
    LoaderAdapter is responsible for loading data using the configured Loader instance as a decorator.
    For benchmark:// protocol files, it handles downloading before loading.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Loader.

        Attributes:
            loader (Loader):
                An instance of the Loader class initialized with the provided configuration.
            is_benchmark (bool):
                Whether the filepath uses benchmark:// protocol.
            benchmarker_config (BenchmarkerConfig):
                Configuration for benchmark dataset if applicable.
            is_schema_benchmark (bool):
                Whether the schema uses benchmark:// protocol.
            schema_benchmarker_config (BenchmarkerConfig):
                Configuration for schema benchmark dataset if applicable.
        """
        super().__init__(config)

        # Copy config once at the beginning to avoid modifying the original
        config = config.copy()

        # Check if filepath uses benchmark:// protocol
        filepath = config.get("filepath", "")
        self.is_benchmark = filepath.lower().startswith("benchmark://")
        self.benchmarker_config = None

        if self.is_benchmark:
            # If benchmark protocol detected, prepare benchmarker
            import re
            from pathlib import Path

            from petsard.exceptions import UnsupportedMethodError
            from petsard.loader.benchmarker import BenchmarkerConfig

            benchmark_name = re.sub(
                r"^benchmark://", "", filepath, flags=re.IGNORECASE
            ).lower()

            self._logger.info(
                f"Detected benchmark protocol for filepath: {benchmark_name}"
            )

            # Create BenchmarkerConfig
            try:
                self.benchmarker_config = BenchmarkerConfig(
                    benchmark_name=benchmark_name, filepath_raw=filepath
                )
            except UnsupportedMethodError as e:
                # Convert UnsupportedMethodError to BenchmarkDatasetsError
                from petsard.exceptions import BenchmarkDatasetsError

                error_msg = (
                    f"Unsupported benchmark dataset '{benchmark_name}': {str(e)}"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

            # Update filepath in config to local path
            local_filepath = Path("benchmark").joinpath(
                self.benchmarker_config.benchmark_filename
            )
            config["filepath"] = str(local_filepath)

            self._logger.debug(f"Updated filepath to local path: {local_filepath}")

            # Download benchmark data file BEFORE initializing Loader
            self._logger.info(
                f"Downloading benchmark dataset in __init__: {benchmark_name}"
            )
            try:
                from petsard.exceptions import BenchmarkDatasetsError
                from petsard.loader.benchmarker import BenchmarkerRequests

                benchmarker = BenchmarkerRequests(
                    self.benchmarker_config.get_benchmarker_config()
                )
                benchmarker.download()
                self._logger.debug(
                    "Benchmark dataset downloaded successfully in __init__"
                )
            except BenchmarkDatasetsError as e:
                error_msg = f"Failed to download benchmark dataset '{benchmark_name}' during initialization: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except ImportError as e:
                error_msg = (
                    f"Cannot download benchmark dataset '{benchmark_name}': "
                    f"requests library is required. Install with: pip install petsard[load-benchmark]"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except Exception as e:
                error_msg = f"Failed to download benchmark dataset '{benchmark_name}' during initialization: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

        # Check if schema uses benchmark:// protocol
        schema = config.get("schema", "")
        self.is_schema_benchmark = isinstance(
            schema, str
        ) and schema.lower().startswith("benchmark://")
        self.schema_benchmarker_config = None

        if self.is_schema_benchmark:
            # If benchmark protocol detected for schema, prepare benchmarker
            import re
            from pathlib import Path

            from petsard.exceptions import UnsupportedMethodError
            from petsard.loader.benchmarker import BenchmarkerConfig

            schema_benchmark_name = re.sub(
                r"^benchmark://", "", schema, flags=re.IGNORECASE
            ).lower()

            self._logger.info(
                f"Detected benchmark protocol for schema: {schema_benchmark_name}"
            )

            # Create BenchmarkerConfig for schema
            try:
                self.schema_benchmarker_config = BenchmarkerConfig(
                    benchmark_name=schema_benchmark_name, filepath_raw=schema
                )
            except UnsupportedMethodError as e:
                # Convert UnsupportedMethodError to BenchmarkDatasetsError
                from petsard.exceptions import BenchmarkDatasetsError

                error_msg = (
                    f"Unsupported benchmark schema '{schema_benchmark_name}': {str(e)}"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

            # Update schema in config to local path
            local_schema_path = Path("benchmark").joinpath(
                self.schema_benchmarker_config.benchmark_filename
            )
            config["schema"] = str(local_schema_path)

            self._logger.debug(f"Updated schema to local path: {local_schema_path}")

            # Download benchmark schema file BEFORE initializing Loader
            self._logger.info(
                f"Downloading benchmark schema in __init__: {schema_benchmark_name}"
            )
            try:
                from petsard.exceptions import BenchmarkDatasetsError
                from petsard.loader.benchmarker import BenchmarkerRequests

                benchmarker = BenchmarkerRequests(
                    self.schema_benchmarker_config.get_benchmarker_config()
                )
                benchmarker.download()
                self._logger.debug(
                    "Benchmark schema downloaded successfully in __init__"
                )
            except BenchmarkDatasetsError as e:
                error_msg = f"Failed to download benchmark schema '{schema_benchmark_name}' during initialization: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except ImportError as e:
                error_msg = (
                    f"Cannot download benchmark schema '{schema_benchmark_name}': "
                    f"requests library is required. Install with: pip install petsard[load-benchmark]"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except Exception as e:
                error_msg = f"Failed to download benchmark schema '{schema_benchmark_name}' during initialization: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

        # Remove method parameter if exists, as Loader no longer accepts it
        config.pop("method", None)

        # Initialize Loader with the updated config
        self.loader = Loader(**config)
        self._schema_metadata = None  # Store the Schema

    def _run(self, input: dict):
        """
        Executes the data loading process using the Loader instance.
        For benchmark:// protocol, downloads dataset first.

        Args:
            input (dict): Loader input should contains nothing ({}).

        Attributes:
            loader.data (pd.DataFrame):
                An loading result data.
        """
        self._logger.debug("Starting data loading process")

        # Note: Benchmark files are already downloaded in __init__
        # We can skip the download here since they were downloaded before Loader initialization
        if self.is_benchmark and self.benchmarker_config:
            self._logger.debug(
                f"Benchmark dataset already downloaded in __init__: {self.benchmarker_config.benchmark_name}"
            )

        if self.is_schema_benchmark and self.schema_benchmarker_config:
            self._logger.debug(
                f"Benchmark schema already downloaded in __init__: {self.schema_benchmarker_config.benchmark_name}"
            )

        # Load data (regardless of whether it's benchmark or not)
        try:
            self.data, self._schema_metadata = self.loader.load()
        except FileNotFoundError as e:
            from petsard.exceptions import BenchmarkDatasetsError

            # Check if this is a benchmark file that failed to download
            if self.is_benchmark:
                error_msg = (
                    f"Benchmark dataset file not found after download attempt: {str(e)}. "
                    f"This may indicate download failure or SHA-256 verification failure."
                )
            elif self.is_schema_benchmark:
                error_msg = (
                    f"Benchmark schema file not found after download attempt: {str(e)}. "
                    f"This may indicate download failure or SHA-256 verification failure."
                )
            else:
                error_msg = f"File not found: {str(e)}"
            self._logger.error(error_msg)
            raise BenchmarkDatasetsError(error_msg) from e
        except Exception as e:
            # Handle any other loading errors
            if "Schema file not found" in str(e):
                if self.is_schema_benchmark:
                    from petsard.exceptions import BenchmarkDatasetsError

                    error_msg = (
                        f"Benchmark schema file not found: {self.schema_benchmarker_config.benchmark_filename}. "
                        f"The download may have failed or the file may be corrupted."
                    )
                    self._logger.error(error_msg)
                    raise BenchmarkDatasetsError(error_msg) from e
            raise

        # Use Schema directly
        self._logger.debug("Using Schema from Metadater")
        self.metadata = self._schema_metadata

        self._logger.debug("Data loading completed")

    def set_input(self, status) -> dict:
        """
        Sets the input for the LoaderAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict: An empty dictionary.
        """
        return self.input

    def get_result(self):
        """
        Retrieve the loading result.
        """
        return self.data

    def get_metadata(self) -> Schema:
        """
        Retrieve the metadata of the loaded data.

        Returns:
            (Schema): The metadata of the loaded data.
        """
        return self.metadata


class SplitterAdapter(BaseAdapter):
    """
    SplitterAdapter is responsible for splitting data
        using the configured Loader instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Splitter.

        Attributes:
            splitter (Splitter):
                An instance of the Splitter class initialized with the provided configuration.
        """
        super().__init__(config)

        # Check if it's custom_data method
        if config.get("method") == "custom_data":
            # Create LoaderAdapter instances (but don't run yet)
            ori_config = self._create_loader_config(config, "ori")
            self.ori_loader_adapter = LoaderAdapter(ori_config)

            ctrl_config = self._create_loader_config(config, "control")
            self.ctrl_loader_adapter = LoaderAdapter(ctrl_config)

            self.is_custom_data = True
            self.splitter = None
        else:
            self.splitter = Splitter(**config)
            self.is_custom_data = False

    def _create_loader_config(self, config: dict, key: str) -> dict:
        """
        Create Loader configuration for a specific key (ori/control).

        Args:
            config: Full configuration dictionary
            key: Either 'ori' or 'control'

        Returns:
            dict: Loader configuration for the specified key
        """
        # Parameters that should be excluded (Splitter-specific parameters)
        SPLITTER_ONLY_PARAMS = [
            "method",
            "num_samples",
            "train_split_ratio",
            "random_state",
            "max_overlap_ratio",
            "max_attempts",
        ]

        loader_config = {}
        for param_name, param_value in config.items():
            # Skip Splitter-specific parameters
            if param_name in SPLITTER_ONLY_PARAMS:
                continue

            if isinstance(param_value, dict) and key in param_value:
                loader_config[param_name] = param_value[key]
            elif not isinstance(param_value, dict):
                # Non-dict parameters are passed directly (if not excluded)
                loader_config[param_name] = param_value
        return loader_config

    def _run(self, input: dict):
        """
        Executes the data splitting process using the Splitter instance.

        Args:
            input (dict):
                Splitter input should contains
                    data (pd.DataFrame), metadata (Schema),
                    and exclude_index (list[set]).

        Attributes:
            data (Dict[int, Dict[str, pd.DataFrame]]):
                An splitting result data.
                    First layer is the splitting index, key as int, value as dictionary.
                    Second layer is the splitting result of specific splitting,
                    key as str: 'train' and 'validation', value as pd.DataFrame.
            train_indices (Dict[int, List[int]]):
                The original indices of training data for each sample.
        """
        self._logger.debug("Starting data splitting process")

        if self.is_custom_data:
            # Execute LoaderAdapters to load data
            self.ori_loader_adapter._run({})
            ori_data = self.ori_loader_adapter.get_result()
            ori_metadata = self.ori_loader_adapter.get_metadata()

            self.ctrl_loader_adapter._run({})
            ctrl_data = self.ctrl_loader_adapter.get_result()
            ctrl_metadata = self.ctrl_loader_adapter.get_metadata()

            # Update metadata with split information
            from copy import deepcopy

            train_metadata = deepcopy(ori_metadata)
            validation_metadata = deepcopy(ctrl_metadata)

            # Add split description
            split_info = f"Split info: train={ori_data.shape[0]} rows, validation={ctrl_data.shape[0]} rows"
            train_metadata.description = (
                f"{train_metadata.description or ''} | {split_info}".strip()
            )
            validation_metadata.description = (
                f"{validation_metadata.description or ''} | {split_info}".strip()
            )

            # Assemble results
            self.data = {
                1: {
                    "train": ori_data,
                    "validation": ctrl_data,
                }
            }
            self.metadata = {
                1: {
                    "train": train_metadata,
                    "validation": validation_metadata,
                }
            }
            self.train_indices = [set(ori_data.index.tolist())]
        else:
            # Normal splitting process
            # Only pass parameters that Splitter.split() accepts and are not empty
            split_params = {}
            for key, value in input.items():
                if key == "data":
                    split_params[key] = value
                elif key == "metadata":
                    split_params[key] = value
                elif key == "exist_train_indices" and value:  # Only pass when not empty
                    split_params[key] = value
            self.data, self.metadata, self.train_indices = self.splitter.split(
                **split_params
            )
        self._logger.debug("Data splitting completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the SplitterAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Splitter input should contains
                data (pd.DataFrame), exclude_index (list), and Metadata (Metadata)
        """
        if self.is_custom_data:
            # For custom_data, we don't need input data
            self.input["data"] = None
            self.input["metadata"] = None
        else:
            # Splitter accept following Loader only
            self.input["data"] = status.get_result("Loader")
            self.input["metadata"] = status.get_metadata("Loader")
        self.input["exist_train_indices"] = status.get_exist_train_indices()

        return self.input

    def get_result(self):
        """
        Retrieve the splitting result.
            Due to Config force num_samples = 1, return 1st dataset is fine.
        """
        result: dict = deepcopy(self.data[1])
        return result

    def get_metadata(self) -> Schema:
        """
        Retrieve the metadata.

        Returns:
            (Schema): The updated metadata.
        """
        return deepcopy(self.metadata[1]["train"])

    def get_train_indices(self) -> list[set]:
        """
        Retrieve the training indices for each sample.

        Returns:
            list[set]: Training indices as list of sets
        """
        return deepcopy(self.train_indices)


class PreprocessorAdapter(BaseAdapter):
    """
    PreprocessorAdapter is responsible for pre-processing data
        using the configured Processor instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Processor.

        Attributes:
            _processor (Processor): The processor object used by the Operator.
            _config (dict): The configuration parameters for the Processor.
            _sequence (list): The sequence of the pre-processing steps (if any
        """
        super().__init__(config)
        self.processor = None
        method = config["method"].lower() if "method" in config else "custom"
        self._sequence = None
        if "sequence" in config:
            self._sequence = config["sequence"]

        # Extract the processor configuration properly
        if method == "default":
            self._config = {}
        else:
            # For custom method, extract the "config" key if it exists
            # Otherwise use the config directly (for backward compatibility)
            if "config" in config:
                self._config = config["config"]
            else:
                # Remove non-processor keys from config
                self._config = {
                    k: v for k, v in config.items() if k not in ["method", "sequence"]
                }

    def _run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Preprocessor input should contains data (pd.DataFrame) and metadata (Metadata).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """

        self._logger.debug("Initializing processor")
        self.processor = Processor(metadata=input["metadata"], config=self._config)

        if self._sequence is None:
            self._logger.debug("Using default processing sequence")
            self.processor.fit(data=input["data"])
        else:
            self._logger.debug(f"Using custom sequence: {self._sequence}")
            self.processor.fit(data=input["data"], sequence=self._sequence)

        self._logger.debug("Transforming data")
        self.data_preproc = self.processor.transform(data=input["data"])

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the PreprocessorAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Preprocessor input should contains
                    data (pd.DataFrame) and metadata (Metadata).
        """
        pre_module = status.get_pre_module("Preprocessor")
        if pre_module == "Splitter":
            self.input["data"] = status.get_result(pre_module)["train"]
        else:  # Loader only
            self.input["data"] = status.get_result(pre_module)
        self.input["metadata"] = status.get_metadata(pre_module)

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        result: pd.DataFrame = deepcopy(self.data_preproc)
        return result

    def get_metadata(self) -> Schema:
        """
        Retrieve the metadata.
            If the encoder is EncoderUniform,
            update the metadata infer_dtype to numerical.

        Returns:
            (Schema): The updated metadata.
        """
        metadata: Schema = deepcopy(self.processor._metadata)

        # Note: The metadata update logic for EncoderUniform and ScalerTimeAnchor
        # needs to be adapted to work with Schema instead of legacy Metadata
        # This will be handled by the processor module's own refactoring

        return metadata


class SynthesizerAdapter(BaseAdapter):
    """
    SynthesizerAdapter is responsible for synthesizing data
        using the configured Synthesizer instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            synthesizer (Synthesizer):
                An instance of the Synthesizer class initialized with the provided configuration.
        """
        super().__init__(config)

        # Check if it's custom_data method
        if config.get("method") == "custom_data":
            # Extract Loader configuration (but don't run yet)
            loader_config = self._extract_loader_config(config)
            self.loader_adapter = LoaderAdapter(loader_config)

            # No need to create synthesizer for custom_data
            self.synthesizer = None
            self.is_custom_data = True
            self._sample_num_rows = config.get("sample_num_rows", 0)
        else:
            self.synthesizer: Synthesizer = Synthesizer(**config)
            self.is_custom_data = False
        self.data_syn: pd.DataFrame = None

    def _extract_loader_config(self, config: dict) -> dict:
        """
        Extract Loader-related configuration from synthesizer config.

        Args:
            config: Full synthesizer configuration

        Returns:
            dict: Configuration for Loader
        """
        # Common Loader parameters (removed 'method' as Loader no longer accepts it)
        LOADER_PARAMS = [
            "filepath",
            "delimiter",
            "encoding",
            "schema",
            "header",
            "index_col",
            "usecols",
            "dtype",
            "nrows",
            "skiprows",
            "na_values",
            "parse_dates",
            "date_format",
        ]
        loader_config = {
            k: v for k, v in config.items() if k in LOADER_PARAMS and v is not None
        }
        return loader_config

    def _run(self, input: dict):
        """
        Executes the data synthesizing using the Synthesizer instance.

        Args:
            input (dict): Synthesizer input should contains data (pd.DataFrame).

        Attributes:
            synthesizer.data_syn (pd.DataFrame):
                An synthesizing result data.
        """
        self._logger.debug("Starting data synthesizing process")

        if self.is_custom_data:
            # Execute LoaderAdapter to load custom data
            self._logger.debug("Using custom_data method")
            self.loader_adapter._run({})
            custom_data = self.loader_adapter.get_result()

            # Handle sample_num_rows if specified
            if self._sample_num_rows > 0 and self._sample_num_rows < len(custom_data):
                self._logger.warning(
                    f"sample_num_rows ({self._sample_num_rows}) is specified for custom_data. "
                    f"Will use first {self._sample_num_rows} rows."
                )
                self.data_syn = custom_data.iloc[: self._sample_num_rows].copy()
            else:
                self.data_syn = custom_data.copy()
        else:
            # Normal synthesizing process
            if self.synthesizer is None:
                raise ConfigError("Synthesizer not initialized properly")

            self.synthesizer.create(metadata=input["metadata"])
            self._logger.debug("Synthesizing model initialization completed")

            self.data_syn = self.synthesizer.fit_sample(data=input["data"])
            self._logger.debug("Train and sampling Synthesizing model completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the SynthesizerAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Synthesizer input should contains data (pd.DataFrame)
                    and SDV format metadata (dict or None).
        """
        if self.is_custom_data:
            # For custom_data, we don't need input from previous modules
            self.input["data"] = None
            self.input["metadata"] = None
        else:
            pre_module = status.get_pre_module("Synthesizer")

            # Check if metadata exists for the previous module
            try:
                self.input["metadata"] = status.get_metadata(pre_module)
                # Validate that the metadata has attributes
                if not self.input["metadata"].attributes:
                    self._logger.warning(
                        f"Metadata from {pre_module} has no attributes, setting to None"
                    )
                    self.input["metadata"] = None
            except Exception as e:
                self._logger.warning(f"Could not get metadata from {pre_module}: {e}")
                self.input["metadata"] = None

            if pre_module == "Splitter":
                self.input["data"] = status.get_result(pre_module)["train"]
            else:  # Loader or Preprocessor
                self.input["data"] = status.get_result(pre_module)

        return self.input

    def get_result(self):
        """
        Retrieve the synthesizing result.
        """
        return deepcopy(self.data_syn)


class PostprocessorAdapter(BaseAdapter):
    """
    PostprocessorAdapter is responsible for post-processing data
        using the configured Processor instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration parameters for the Processor.

        Attributes:
            _processor (Processor): The processor object used by the Operator.
            _config (dict): The configuration parameters for the Operator.
        """
        super().__init__(config)
        self.processor = None
        self._config = {} if config["method"].lower() == "default" else config

    def _run(self, input: dict):
        """
        Executes the data pre-process using the Processor instance.

        Args:
            input (dict):
                Postprocessor input should contains data (pd.DataFrame), preprocessor (Processor),
                and optional original_schema (Schema).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self._logger.debug("Starting data postprocessing process")

        self.processor = input["preprocessor"]
        self._logger.debug("Processor configuration loading completed")

        self.data_postproc = self.processor.inverse_transform(data=input["data"])
        self._logger.debug("Data postprocessing completed")

        # CRITICAL FIX: Processor.inverse_transform() may corrupt nullable integer dtypes
        # (e.g., Int64 → string → float64). We must restore dtypes from original schema.
        # 關鍵修復：Processor.inverse_transform() 可能破壞 nullable integer dtypes
        # （例如 Int64 → string → float64）。我們必須從原始 schema 恢復 dtypes。
        if "original_schema" in input and input["original_schema"]:
            self._logger.debug("Restoring dtypes from original schema")
            try:
                self.data_postproc = SchemaMetadater.align(
                    input["original_schema"], self.data_postproc
                )
                self._logger.info("✓ Successfully restored dtypes after postprocessing")
            except Exception as e:
                self._logger.warning(
                    f"Failed to restore dtypes from original schema: {e}"
                )

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the PostprocessorAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Postprocessor input should contains data (pd.DataFrame), preprocessor (Processor),
                and optional original_schema (Schema).
        """
        self.input["data"] = status.get_result(status.get_pre_module("Postprocessor"))
        self.input["preprocessor"] = status.get_processor()

        # CRITICAL: Get Preprocessor input schema for dtype restoration after inverse_transform
        # This solves the many-to-one transformation reversibility problem:
        # e.g., int64 → scaler_standard → float64 → inverse → ??? (should be int64)
        #
        # 關鍵：取得 Preprocessor 輸入 schema 用於 inverse_transform 後恢復 dtype
        # 這解決了多對一轉換的可逆性問題：
        # 例如 int64 → scaler_standard → float64 → inverse → ??? （應該是 int64）
        try:
            # First try to get the remembered Preprocessor input schema
            preprocessor_input_schema = status.get_preprocessor_input_schema()
            if preprocessor_input_schema:
                self.input["original_schema"] = preprocessor_input_schema
                self._logger.info(
                    "✓ 使用記憶的 Preprocessor 輸入 Schema 進行 dtype 還原"
                )
            # Fallback to Loader/Splitter schema if preprocessor input schema not available
            elif "Loader" in status.status:
                original_schema = status.get_metadata("Loader")
                self.input["original_schema"] = original_schema
                self._logger.debug(
                    "Using original schema from Loader for dtype restoration (fallback)"
                )
            elif "Splitter" in status.status:
                original_schema = status.get_metadata("Splitter")
                self.input["original_schema"] = original_schema
                self._logger.debug(
                    "Using original schema from Splitter for dtype restoration (fallback)"
                )
        except Exception as e:
            self._logger.warning(
                f"Could not retrieve original schema for dtype restoration: {e}"
            )

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        result: pd.DataFrame = deepcopy(self.data_postproc)
        return result


class ConstrainerAdapter(BaseAdapter):
    """
    ConstrainerAdapter is responsible for applying constraints to data
    using the configured Constrainer instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Initialize ConstrainerAdapter with given configuration.

        Args:
            config (dict): Configuration parameters for the Constrainer.
                Can use one of two approaches:
                1. constraints_yaml: Path to YAML file containing all constraint configurations
                2. Individual constraint parameters (nan_groups, field_constraints, etc.)

                Note: Cannot use both approaches simultaneously.

                Additional parameters:
                - method: 'auto' (default), 'resample', or 'validate'
                    * 'auto': 自動判斷（有 synthesizer 且非 custom_data 用 resample，否則用 validate）
                    * 'resample': 強制使用 resample 模式
                    * 'validate': 強制使用 validate 模式
                - source: Optional data source specification (for validate mode)
                    * Single string: "Loader" or "Splitter.train"
                    * List: ["Loader"] or ["Splitter.train", "Synthesizer"]
                    * If not specified, uses previous module's data (default behavior)

        Attributes:
            constrainer (Constrainer): An instance of the Constrainer class
                initialized with the provided configuration.
            validation_result (dict): Validation result when using validate mode.
            method (str): Constrainter 運作模式 ('auto', 'resample', 'validate')
            source: Optional data source specification

        Raises:
            ConfigError: If both constraints_yaml and individual constraint parameters are provided,
                or if the YAML file is invalid or not found.
        """
        super().__init__(config)
        self.validation_result = None  # 初始化驗證結果
        self.validation_results = {}  # 存儲多個 source 的驗證結果

        # 取得並驗證 method 參數
        self.method = config.pop("method", "auto").lower()
        if self.method not in ["auto", "resample", "validate"]:
            raise ConfigError(
                f"Invalid method '{self.method}'. Must be 'auto', 'resample', or 'validate'"
            )

        # 取得 source 參數（可選）
        self.source = config.pop("source", None)
        if self.source is not None:
            # 處理 source 參數格式
            if isinstance(self.source, str):
                # 單一字串轉為列表
                self.source = [self.source]
            elif isinstance(self.source, list):
                # 列表格式保持不變
                pass
            else:
                error_msg = f"source must be a string or list, got {type(self.source)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            self._logger.info(
                f"Constrainer will validate specified sources: {self.source}"
            )

        # Check if constraints_yaml parameter is provided
        constraints_yaml = config.pop("constraints_yaml", None)

        if constraints_yaml:
            # Define constraint parameter keys
            constraint_keys = {
                "nan_groups",
                "field_constraints",
                "field_combinations",
                "field_proportions",
            }

            # Check for conflicting parameters
            conflicting_keys = constraint_keys.intersection(config.keys())

            if conflicting_keys:
                error_msg = (
                    f"Cannot specify both 'constraints_yaml' and individual "
                    f"constraint parameters: {conflicting_keys}. "
                    f"Please use either constraints_yaml OR individual parameters, not both."
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # Load constraints from YAML file
            import sys
            from pathlib import Path

            import yaml

            self._logger.info(f"Loading constraints from YAML file: {constraints_yaml}")

            # Try to find the file in multiple locations
            # 嘗試在多個位置尋找檔案
            yaml_path = None

            # First try: relative to current working directory
            # 首先嘗試：相對於當前工作目錄
            if Path(constraints_yaml).exists():
                yaml_path = Path(constraints_yaml)
            else:
                # Second try: search in sys.path directories (like Python import)
                # 第二次嘗試：在 sys.path 目錄中搜尋（類似 Python import）
                for search_dir in sys.path:
                    candidate = Path(search_dir) / constraints_yaml
                    if candidate.exists():
                        yaml_path = candidate
                        self._logger.info(
                            f"Found constraints file in sys.path: {yaml_path}"
                        )
                        break

            if yaml_path is None:
                raise FileNotFoundError(
                    f"Could not find {constraints_yaml} in current directory or sys.path"
                )

            try:
                with open(yaml_path, encoding="utf-8") as f:
                    yaml_constraints = yaml.safe_load(f)

                if not isinstance(yaml_constraints, dict):
                    raise ConfigError(
                        f"Invalid YAML format: expected dict, got {type(yaml_constraints)}"
                    )

                # Merge YAML constraints into config (preserve sampling parameters)
                config.update(yaml_constraints)
                self._logger.debug(
                    f"Successfully loaded constraints from {constraints_yaml}"
                )

            except FileNotFoundError as e:
                error_msg = f"Constraints YAML file not found: {constraints_yaml}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e
            except yaml.YAMLError as e:
                error_msg = f"Invalid YAML format in {constraints_yaml}: {e}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

        # Transform field combinations before initializing
        config = self._transform_field_combinations(config)

        # Store sampling configuration if provided
        # 過濾掉 None 值和字串 "None"，讓它們在 _run 時自動偵測
        self.sample_dict = {}
        for key in ["target_rows", "sampling_ratio", "max_trials", "verbose_step"]:
            if key in config:
                value = config.pop(key)
                # 只有當值不是 None 且不是字串 "None" 時才加入
                if value is not None and value != "None":
                    self.sample_dict[key] = value

        # Store metadata for later use (will be set in set_input)
        self._metadata = None

        # Note: Constrainer initialization is deferred to _run() to allow metadata setup
        self.constrainer = None
        self._config = config

    def _run(self, input: dict):
        """
        Execute data constraining process using the Constrainer instance.

        支援兩種模式：
        1. resample 模式：有 synthesizer（且非 custom_data）時，反覆抽樣直到符合條件
        2. validate 模式：沒有 synthesizer 或使用 custom_data 時，只做驗證檢查

        支援多個 source：
        - 如果 input["data"] 是字典（多個 source），會分別驗證每個 source
        - 驗證結果存儲在 self.validation_results 中

        模式選擇邏輯：
        - method='auto': 自動判斷
          * 有 synthesizer 且非 custom_data → resample
          * 其他情況 → validate
        - method='resample': 強制使用 resample（需要有 synthesizer）
        - method='validate': 強制使用 validate

        Args:
            input (dict): Constrainer input should contain:
                - data (pd.DataFrame or dict): Single data or multiple data sources
                - synthesizer (optional): Synthesizer instance if resampling is needed
                - postprocessor (optional): Postprocessor instance if needed
                - is_custom_data (bool, optional): 標記是否為 custom_data
                - source_names (dict, optional): Mapping of data to source names

        Attributes:
            constrained_data (pd.DataFrame): The constrained result data.
            validation_result (dict, optional): Single validation result when using validate mode.
            validation_results (dict, optional): Multiple validation results for multiple sources.
        """
        self._logger.debug("Starting data constraining process")

        # 檢查是否為多個 source
        is_multiple_sources = (
            isinstance(input["data"], dict) and "source_names" in input
        )

        if is_multiple_sources:
            # 多個 source 的情況：分別驗證每個 source
            self._logger.info(f"Validating {len(input['data'])} sources separately")

            for source_name, source_data in input["data"].items():
                self._logger.info(f"Validating source: {source_name}")

                # 為每個 source 執行驗證
                validation_result = self.constrainer.validate(
                    data=source_data, return_details=True
                )

                # 添加 source 資訊到驗證結果
                validation_result["source_name"] = source_name

                # 存儲驗證結果
                self.validation_results[source_name] = validation_result

                # 記錄驗證結果
                self._logger.info(
                    f"✓ Source '{source_name}' 驗證完成：總共 {validation_result['total_rows']} 筆資料，"
                    f"通過 {validation_result['passed_rows']} 筆 "
                    f"({validation_result['pass_rate']:.2%})，"
                    f"未通過 {validation_result['failed_rows']} 筆"
                )

                if validation_result["is_fully_compliant"]:
                    self._logger.info(
                        f"✓ Source '{source_name}' 所有資料都符合條件限制（100% 通過）"
                    )
                else:
                    self._logger.warning(
                        f"⚠ Source '{source_name}' 部分資料不符合條件限制，通過率：{validation_result['pass_rate']:.2%}"
                    )

            # 對於多 source 的情況，constrained_data 保持原始資料結構
            self.constrained_data = input["data"]
            self.validation_result = None  # 多 source 時不使用單一驗證結果

        else:
            # 單一 source 的情況：使用原有邏輯
            data = input["data"]

            # 如果 target_rows 不存在或為 None，使用資料筆數
            if (
                "target_rows" not in self.sample_dict
                or self.sample_dict.get("target_rows") is None
            ):
                self.sample_dict["target_rows"] = len(data)

            # 決定使用哪種模式
            use_resample_mode = self._should_use_resample_mode(input)

            if use_resample_mode:
                # Mode 1: Resample mode - 反覆抽樣直到符合條件
                self._logger.info(
                    f"使用 resample 模式 (method={self.method})：將進行反覆抽樣直到符合條件"
                )

                if "synthesizer" not in input or input["synthesizer"] is None:
                    raise ConfigError(
                        "Resample mode requires a synthesizer, but no synthesizer was provided. "
                        "Please check your configuration or use method='validate' instead."
                    )

                self.constrained_data = self.constrainer.resample_until_satisfy(
                    data=data,
                    synthesizer=input["synthesizer"],
                    postprocessor=input.get("postprocessor"),
                    **self.sample_dict,
                )
                self.validation_result = None

                # 記錄抽樣次數
                if self.constrainer.resample_trails is not None:
                    self._logger.info(
                        f"✓ Resample 完成：經過 {self.constrainer.resample_trails} 次抽樣，"
                        f"取得 {len(self.constrained_data)} 筆符合條件的資料"
                    )
            else:
                # Mode 2: Validate mode - 只做驗證檢查
                reason = (
                    "custom_data" if input.get("is_custom_data") else "無 synthesizer"
                )
                self._logger.info(
                    f"使用 validate 模式 (method={self.method}, 原因={reason})：將只進行條件驗證檢查"
                )

                # 執行驗證
                self.validation_result = self.constrainer.validate(
                    data=data, return_details=True
                )

                # 記錄驗證結果
                self._logger.info(
                    f"✓ Validate 完成：總共 {self.validation_result['total_rows']} 筆資料，"
                    f"通過 {self.validation_result['passed_rows']} 筆 "
                    f"({self.validation_result['pass_rate']:.2%})，"
                    f"未通過 {self.validation_result['failed_rows']} 筆"
                )

                if self.validation_result["is_fully_compliant"]:
                    self._logger.info("✓ 所有資料都符合條件限制（100% 通過）")
                else:
                    self._logger.warning(
                        f"⚠ 部分資料不符合條件限制，通過率：{self.validation_result['pass_rate']:.2%}"
                    )

                    # 記錄各條件的違規統計（新的巢狀結構）
                    for constraint_type, type_violations in self.validation_result[
                        "constraint_violations"
                    ].items():
                        if isinstance(type_violations, dict):
                            # 檢查是否有錯誤訊息
                            if (
                                "error" in type_violations
                                and "failed_count" in type_violations
                            ):
                                # 舊格式或錯誤格式
                                self._logger.error(
                                    f"  - {constraint_type}: 驗證錯誤 - {type_violations.get('error')}"
                                )
                            else:
                                # 新格式：包含多條規則
                                for rule_name, rule_stats in type_violations.items():
                                    if (
                                        isinstance(rule_stats, dict)
                                        and rule_stats.get("failed_count", 0) > 0
                                    ):
                                        self._logger.warning(
                                            f"  - {constraint_type} - {rule_name}: {rule_stats['failed_count']} 筆違規 "
                                            f"({rule_stats['fail_rate']:.2%})"
                                        )

                # 對於 validate 模式，返回所有資料（包含違規的）
                # 讓使用者可以自行決定如何處理
                self.constrained_data = data.copy()

        self._logger.debug("Data constraining completed")

    def _should_use_resample_mode(self, input: dict) -> bool:
        """
        決定是否使用 resample 模式

        Args:
            input: Constrainer 的輸入字典

        Returns:
            bool: True 表示使用 resample 模式，False 表示使用 validate 模式
        """
        # 如果手動指定模式
        if self.method == "resample":
            return True
        elif self.method == "validate":
            return False

        # auto 模式：自動判斷
        # 條件：有 synthesizer 且不是 custom_data
        has_synthesizer = "synthesizer" in input and input["synthesizer"] is not None
        is_custom_data = input.get("is_custom_data", False)

        return has_synthesizer and not is_custom_data

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Set the input for the ConstrainerAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Constrainer input should contain:
                - data (pd.DataFrame or dict): Single data or multiple data sources
                - metadata (Schema, optional): Schema for field type checking
                - synthesizer (optional)
                - postprocessor (optional)
                - is_custom_data (bool): 標記是否為 custom_data
                - source_names (dict, optional): Mapping of data to source names
        """
        # Get metadata for field type checking
        # Priority: Loader > Splitter > Preprocessor
        try:
            if "Loader" in status.status:
                self._metadata = status.get_metadata("Loader")
                self._logger.debug("Using metadata from Loader for field type checking")
            elif "Splitter" in status.status:
                self._metadata = status.get_metadata("Splitter")
                self._logger.debug(
                    "Using metadata from Splitter for field type checking"
                )
            elif "Preprocessor" in status.status:
                self._metadata = status.get_metadata("Preprocessor")
                self._logger.debug(
                    "Using metadata from Preprocessor for field type checking"
                )
        except Exception as e:
            self._logger.warning(
                f"Could not retrieve metadata for field type checking: {e}"
            )
            self._metadata = None

        # Initialize Constrainer with metadata now that we have it
        if self.constrainer is None:
            self.constrainer = Constrainer(self._config, metadata=self._metadata)
            self._logger.debug("Initialized Constrainer with metadata")

        # Store metadata in input for potential future use
        self.input["metadata"] = self._metadata

        # 如果指定了 source，使用 source 指定的資料
        if self.source is not None:
            self._logger.info(f"Using specified sources: {self.source}")
            self.input["data"] = {}
            self.input["source_names"] = {}

            for source_spec in self.source:
                # 支援 "Module.key" 格式
                if "." in source_spec:
                    module_name, data_key = source_spec.split(".", 1)

                    # 別名映射：支援使用者熟悉的名稱
                    # ori -> train, control -> validation
                    key_aliases = {
                        "ori": "train",
                        "control": "validation",
                    }
                    # 創建反向映射以支援雙向查找
                    reverse_aliases = {v: k for k, v in key_aliases.items()}

                    data = status.get_data_by_module(module_name)
                    if data:
                        # 查找特定的鍵
                        found = False
                        # 首先嘗試原始鍵名
                        search_keys = [data_key]
                        # 如果有別名，也嘗試別名
                        if data_key in key_aliases:
                            search_keys.append(key_aliases[data_key])
                        if data_key in reverse_aliases:
                            search_keys.append(reverse_aliases[data_key])

                        for available_key, df in data.items():
                            # 檢查所有可能的鍵名格式
                            for search_key in search_keys:
                                if (
                                    available_key == f"{module_name}_{search_key}"
                                    or available_key == search_key
                                ):
                                    self.input["data"][source_spec] = df
                                    self.input["source_names"][source_spec] = (
                                        source_spec
                                    )
                                    if search_key != data_key:
                                        self._logger.debug(
                                            f"Using data from module: {module_name}.{data_key} "
                                            f"(mapped to {search_key})"
                                        )
                                    else:
                                        self._logger.debug(
                                            f"Using data from module: {module_name}.{data_key}"
                                        )
                                    found = True
                                    break
                            if found:
                                break

                        if not found:
                            error_msg = f"Key '{data_key}' not found in module '{module_name}'. Available keys: {list(data.keys())}"
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)
                    else:
                        error_msg = f"No data found from module: {module_name}"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                else:
                    # 簡單的模組名稱
                    data = status.get_data_by_module(source_spec)
                    if data:
                        # 取第一個可用的資料
                        first_key = next(iter(data.keys()))
                        self.input["data"][source_spec] = data[first_key]
                        self.input["source_names"][source_spec] = source_spec
                        self._logger.debug(
                            f"Using data from module: {source_spec} ({first_key})"
                        )
                    else:
                        error_msg = f"No data found from source: {source_spec}"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
        else:
            # 沒有指定 source，使用預設行為（前一個模組的資料）
            pre_module = status.get_pre_module("Constrainer")

            # Get data from previous module
            if pre_module == "Splitter":
                self.input["data"] = status.get_result(pre_module)["train"]
            else:  # Loader, Preprocessor, Synthesizer, or Postprocessor
                self.input["data"] = status.get_result(pre_module)

        # Get synthesizer if available and check if it's custom_data
        self.input["is_custom_data"] = False
        if "Synthesizer" in status.status:
            synthesizer = status.get_synthesizer()
            self.input["synthesizer"] = synthesizer

            # 檢查是否為 custom_data
            # SynthesizerAdapter 的 is_custom_data 屬性會標記這個資訊
            synthesizer_adapter = status.status.get("Synthesizer")
            if synthesizer_adapter and hasattr(synthesizer_adapter, "is_custom_data"):
                self.input["is_custom_data"] = synthesizer_adapter.is_custom_data
                if self.input["is_custom_data"]:
                    self._logger.debug("Detected custom_data from Synthesizer")

        # Get postprocessor if available
        if "Postprocessor" in status.status:
            self.input["postprocessor"] = status.get_processor()

        return self.input

    def get_result(self):
        """
        Retrieve the constraining result.

        Returns:
            pd.DataFrame or dict:
                - If validate mode: returns validation_result dict
                - If resample mode: returns constrained data DataFrame
        """
        # If validation result exists (validate mode), return it
        # This allows Reporter to access validation results
        if self.validation_result is not None:
            return deepcopy(self.validation_result)
        # Otherwise return constrained data (resample mode)
        return deepcopy(self.constrained_data)

    def get_validation_result(self) -> dict:
        """
        Retrieve the validation result (only available in validate mode).

        Returns:
            dict: Validation result containing:
                For single source:
                - total_rows (int): 總資料筆數
                - passed_rows (int): 通過所有條件的資料筆數
                - failed_rows (int): 未通過條件的資料筆數
                - pass_rate (float): 通過率 (0.0 到 1.0)
                - is_fully_compliant (bool): 是否百分百符合
                - constraint_violations (dict): 各條件的違規統計
                - violation_details (pd.DataFrame, optional): 違規記錄的詳細資訊

                For multiple sources:
                - dict[source_name, validation_result]: 每個 source 的驗證結果

            Returns None if resample mode was used (when synthesizer is available).
        """
        # 如果有多 source 的驗證結果，返回多 source 結果
        if self.validation_results:
            return deepcopy(self.validation_results)
        # 否則返回單一驗證結果
        return deepcopy(self.validation_result) if self.validation_result else None

    def _transform_field_combinations(self, config: dict) -> dict:
        """Transform field combinations from YAML list format to tuple format

        Args:
            config: Original config dictionary

        Returns:
            Updated config with transformed field_combinations
        """
        if "field_combinations" in config:
            # Deep copy to avoid modifying original config
            config = deepcopy(config)
            # Transform each combination from [dict, dict] to tuple(dict, dict)
            config["field_combinations"] = [
                tuple(combination) for combination in config["field_combinations"]
            ]
        return config


class EvaluatorAdapter(BaseAdapter):
    """
    EvaluatorAdapter is responsible for evaluating data
        using the configured Evaluator instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            evaluator (Evaluator):
                An instance of the Evaluator class initialized with the provided configuration.
        """
        super().__init__(config)
        self.evaluator = Evaluator(**config)
        self.evaluations: dict[str, pd.DataFrame] = None
        self._schema: Schema = None  # Store schema for data alignment

    def _run(self, input: dict):
        """
        Executes the data evaluating using the Evaluator instance.

        Args:
            input (dict): Evaluator input should contains data (dict) and optional schema.

        Attributes:
            evaluator.result (dict): An evaluating result data.
        """
        self._logger.debug("Starting data evaluating process")

        # CRITICAL FIX: Auto-align data types BEFORE evaluator.eval() to prevent dtype validation errors
        # 關鍵修復：在 evaluator.eval() 之前對齊資料型別，以防止 dtype 驗證錯誤
        if "schema" in input and input["schema"]:
            self._logger.debug("Schema found, aligning data types before evaluation")
            aligned_data = {}
            for key, df in input["data"].items():
                if df is not None and not df.empty:
                    self._logger.debug(f"Aligning data type for '{key}' data")
                    try:
                        aligned_data[key] = SchemaMetadater.align(input["schema"], df)
                        self._logger.info(
                            f"✓ Successfully aligned '{key}' data to schema"
                        )
                    except Exception as e:
                        self._logger.warning(
                            f"Failed to align '{key}' data: {e}. Using original data."
                        )
                        aligned_data[key] = df
                else:
                    aligned_data[key] = df
            input["data"] = aligned_data
            self._logger.debug("Data type alignment completed")

            # Remove schema from input as Evaluator.eval() doesn't accept it
            del input["schema"]

        self.evaluator.create()
        self._logger.debug("Evaluation model initialization completed")

        # Now call eval() with aligned data - verification will pass
        # 現在使用對齊後的資料呼叫 eval() - 驗證將會通過
        self.evaluations = self.evaluator.eval(**input)
        self._logger.debug("Data evaluating completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the EvaluatorAdapter.
        Evaluator 使用固定的資料源邏輯：ori, syn, control

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Evaluator input should contains data (dict) and optional schema.
        """
        # Evaluator 總是使用固定的資料源邏輯
        # ori 資料源
        if "Splitter" in status.status:
            self.input["data"] = {"ori": status.get_result("Splitter")["train"]}
        else:
            self.input["data"] = {"ori": status.get_result("Loader")}

        # syn 資料源
        self.input["data"]["syn"] = status.get_result(
            status.get_pre_module("Evaluator")
        )

        # control 資料源（如果有 Splitter）
        if "Splitter" in status.status:
            splitter_result = status.get_result("Splitter")
            if "validation" in splitter_result:
                self.input["data"]["control"] = splitter_result["validation"]

        # Try to get schema for data alignment
        # Priority: Loader > Splitter > Preprocessor
        schema = None
        try:
            if "Loader" in status.status:
                schema = status.get_metadata("Loader")
                self._logger.debug("Using schema from Loader for data alignment")
            elif "Splitter" in status.status:
                schema = status.get_metadata("Splitter")
                self._logger.debug("Using schema from Splitter for data alignment")
            elif "Preprocessor" in status.status:
                schema = status.get_metadata("Preprocessor")
                self._logger.debug("Using schema from Preprocessor for data alignment")
        except Exception as e:
            self._logger.warning(f"Could not retrieve schema for data alignment: {e}")

        if schema:
            self.input["schema"] = schema
            self._schema = schema  # Store for later use
        else:
            self._logger.warning("No schema available for data type alignment")

        return self.input

    def get_result(self) -> dict[str, pd.DataFrame]:
        """
        Retrieve the pre-processing result.

        Returns:
            (dict[str, pd.DataFrame]): The evaluation results.
        """
        return deepcopy(self.evaluations)


class DescriberAdapter(BaseAdapter):
    """
    DescriberAdapter is responsible for describing data
        using the configured Describer instance as a decorator.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            describer (Describer):
                An instance of the Describer class initialized with the provided configuration.
            source: Data source specification (required)
        """
        super().__init__(config)

        # 取得 source 參數（必要參數）
        self.source = config.pop("source", None)
        if self.source is None:
            error_msg = "source parameter is required for Describer"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 處理 source 參數格式
        if isinstance(self.source, str):
            # 單一字串轉為列表
            self.source = [self.source]
        elif isinstance(self.source, dict):
            # 字典格式（用於明確指定比較對象）
            # 例如：{"base": "Splitter.train", "target": "Synthesizer"}
            # 或向後相容：{"ori": "Splitter.train", "syn": "Synthesizer"}
            self._logger.info(f"Using explicit source mapping: {self.source}")
        elif isinstance(self.source, list):
            # 列表格式轉換為字典格式
            if len(self.source) == 2:
                # 對於 compare 模式，將列表轉換為字典
                self.source = {"base": self.source[0], "target": self.source[1]}
                self._logger.info(f"Converted list format to dict: {self.source}")
            elif len(self.source) == 1:
                # 對於 describe 模式，保持為單一元素列表
                pass
            else:
                error_msg = (
                    f"source list must have 1 or 2 elements, got {len(self.source)}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        else:
            error_msg = (
                f"source must be a string, list, or dict, got {type(self.source)}"
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 處理 method 參數 (default, describe, compare)
        method = config.get("method", "default")

        # 根據 method 決定 mode
        if method == "default":
            # default: 根據 source 數量自動決定
            source_count = (
                len(self.source)
                if isinstance(self.source, list)
                else len(self.source.keys())
                if isinstance(self.source, dict)
                else 1
            )

            if source_count == 1:
                config["mode"] = "describe"
                config["method"] = "describe"  # 設定實際的 method
                self._logger.info(
                    f"Default method resolved to: describe (1 source: {self.source})"
                )
            elif source_count == 2:
                config["mode"] = "compare"
                config["method"] = "describe"  # Describer 內部仍使用 describe
                self._logger.info(
                    f"Default method resolved to: compare (2 sources: {self.source})"
                )
            else:
                error_msg = f"Invalid number of sources for default method: {source_count}. Expected 1 for describe or 2 for compare"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        elif method == "describe":
            # describe: 單一資料集描述
            config["mode"] = "describe"
            source_count = (
                len(self.source)
                if isinstance(self.source, list)
                else len(self.source.keys())
                if isinstance(self.source, dict)
                else 1
            )

            if source_count != 1:
                self._logger.warning(
                    f"describe method expects 1 source, got {source_count}. Using first source only."
                )
                if isinstance(self.source, list):
                    self.source = [self.source[0]]
                elif isinstance(self.source, dict):
                    first_key = next(iter(self.source.keys()))
                    self.source = {first_key: self.source[first_key]}
        elif method == "compare":
            # compare: 資料集比較
            config["mode"] = "compare"
            config["method"] = "describe"  # Describer 內部使用 describe
            source_count = (
                len(self.source)
                if isinstance(self.source, list)
                else len(self.source.keys())
                if isinstance(self.source, dict)
                else 1
            )

            if source_count != 2:
                error_msg = (
                    f"compare method requires exactly 2 sources, got {source_count}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
        else:
            # 其他 method 值保持原樣傳遞
            # 根據 source 數量決定 mode
            source_count = (
                len(self.source)
                if isinstance(self.source, list)
                else len(self.source.keys())
                if isinstance(self.source, dict)
                else 1
            )

            if source_count == 1:
                config["mode"] = "describe"
            elif source_count == 2:
                config["mode"] = "compare"
            else:
                error_msg = f"Invalid number of sources: {source_count}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        self.describer = Describer(**config)
        self.description: dict[str, pd.DataFrame] = None

    def _run(self, input: dict):
        """
        Executes the data describing using the Describer instance.

        Args:
            input (dict): Describer input should contains data (dict) and optional metadata.

        Attributes:
            describer.result (dict): An describing result data.
        """
        self._logger.debug("Starting data describing process")

        # 如果有 metadata，使用它來對齊資料類型
        metadata = None
        if "metadata" in input and input["metadata"]:
            self._logger.debug("Metadata found, aligning data types")
            metadata = input["metadata"]

            # 對每個資料集進行類型對齊
            aligned_data = {}
            for key, df in input["data"].items():
                if df is not None and not df.empty:
                    self._logger.debug(f"Aligning data type for '{key}' data")
                    aligned_data[key] = SchemaMetadater.align(metadata, df)
                else:
                    aligned_data[key] = df
            input["data"] = aligned_data
            self._logger.debug("Data type alignment completed")

            # 移除 metadata，因為 BaseEvaluator 不接受它
            del input["metadata"]

        self.describer.create()
        self._logger.debug("Describing model initialization completed")

        # 如果是 compare 模式且有 metadata，將它儲存在 describer 實例中
        if self.describer.config.mode == "compare" and metadata:
            if hasattr(self.describer._impl, "metadata"):
                self.describer._impl.metadata = metadata
                self._logger.debug("Metadata set on DescriberCompare instance")
            else:
                # 如果 _impl 還沒有 metadata 屬性，動態添加
                self.describer._impl.metadata = metadata
                self._logger.debug(
                    "Metadata dynamically added to DescriberCompare instance"
                )

        self.description = self.describer.eval(**input)
        self._logger.debug("Data describing completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the DescriberAdapter.
        根據 mode 準備不同的資料格式

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Describer input should contains data (dict).
                - For describe mode: {"data": DataFrame}
                - For compare mode: {"ori": DataFrame, "syn": DataFrame}
        """

        # 根據 Describer 的 mode 決定資料格式
        if self.describer.config.mode == "describe":
            # describe 模式：單一資料源
            if len(self.source) != 1:
                error_msg = (
                    f"describe mode requires exactly 1 source, got {len(self.source)}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            module_name = self.source[0]
            data = status.get_data_by_module(module_name)
            if data:
                # 取第一個可用的資料
                first_key = next(iter(data.keys()))
                self.input["data"] = {"data": data[first_key]}
                self._logger.debug(
                    f"Using data from module: {module_name} ({first_key}) for describe mode"
                )

                # 取得 metadata
                try:
                    metadata = status.get_metadata(module_name)
                    if metadata:
                        self.input["metadata"] = metadata
                        self._logger.debug(f"Using metadata from module: {module_name}")
                except Exception as e:
                    self._logger.warning(
                        f"Could not get metadata from {module_name}: {e}"
                    )
            else:
                error_msg = f"No data found from source: {module_name}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        elif self.describer.config.mode == "compare":
            # compare 模式：兩個資料源
            if len(self.source) != 2:
                error_msg = (
                    f"compare mode requires exactly 2 sources, got {len(self.source)}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # 取得兩個資料源
            self.input["data"] = {}

            # 只支援字典格式：{"base": "Splitter.train", "target": "Synthesizer"}
            # 向後相容：也支援 {"ori": "Splitter.train", "syn": "Synthesizer"}

            if not isinstance(self.source, dict):
                error_msg = (
                    f"compare mode requires source to be a dict with 'base' and 'target' keys, "
                    f"got {type(self.source)}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # 明確指定格式
            source_mapping = self.source.copy()
            # 支援向後相容：如果使用 ori/syn，映射到 base/target
            if "ori" in source_mapping and "base" not in source_mapping:
                source_mapping["base"] = source_mapping.pop("ori")
                self._logger.info("Mapped 'ori' to 'base' for backward compatibility")
            if "syn" in source_mapping and "target" not in source_mapping:
                source_mapping["target"] = source_mapping.pop("syn")
                self._logger.info("Mapped 'syn' to 'target' for backward compatibility")

            # 驗證必要的鍵
            if "base" not in source_mapping or "target" not in source_mapping:
                error_msg = (
                    f"compare mode requires 'base' and 'target' keys in source dict, "
                    f"got keys: {list(source_mapping.keys())}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            for key, source_spec in source_mapping.items():
                # 支援 "Module.key" 格式
                if "." in source_spec:
                    module_name, data_key = source_spec.split(".", 1)
                    data = status.get_data_by_module(module_name)
                    if data:
                        # 查找特定的鍵
                        found = False
                        for available_key, df in data.items():
                            if (
                                available_key == f"{module_name}_{data_key}"
                                or available_key == data_key
                            ):
                                self.input["data"][key] = df
                                self._logger.debug(
                                    f"Using data from module: {module_name}.{data_key} as '{key}' for compare mode"
                                )
                                found = True
                                break

                        if not found:
                            error_msg = f"Key '{data_key}' not found in module '{module_name}'. Available keys: {list(data.keys())}"
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)
                    else:
                        error_msg = f"No data found from module: {module_name}"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                else:
                    # 簡單的模組名稱
                    data = status.get_data_by_module(source_spec)
                    if data:
                        # 取第一個可用的資料
                        first_key = next(iter(data.keys()))
                        self.input["data"][key] = data[first_key]
                        self._logger.debug(
                            f"Using data from module: {source_spec} ({first_key}) as '{key}' for compare mode"
                        )
                    else:
                        error_msg = (
                            f"No data found from source: {source_spec} for '{key}'"
                        )
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

            # 取得 metadata (優先使用第一個資料源的 metadata)
            for module_name in self.source:
                try:
                    metadata = status.get_metadata(module_name)
                    if metadata:
                        self.input["metadata"] = metadata
                        self._logger.debug(f"Using metadata from module: {module_name}")
                        break
                except Exception as e:
                    self._logger.warning(
                        f"Could not get metadata from {module_name}: {e}"
                    )

        return self.input

    def get_result(self):
        """
        Retrieve the pre-processing result.
        """
        return deepcopy(self.description)


class ReporterAdapter(BaseAdapter):
    """
    Operator class for generating reports using the Reporter class.

    Args:
        config (dict): Configuration parameters for the Reporter.

    Attributes:
        reporter (Reporter): Instance of the Reporter class.
        report (dict): Dictionary to store the generated reports.
        source_filter: Optional source filter for selecting specific data sources

    Methods:
        _run(input: dict): Runs the Reporter to create and generate reports.
        set_input(status) -> dict: Sets the input data for the Reporter.
        get_result(): Placeholder method for getting the result.

    """

    def __init__(self, config: dict):
        super().__init__(config)

        # 如果 Reporter 有 source 參數，提取出來
        # 注意：這個 source 是用於 ReporterSaveData 的，不是用於選擇輸入資料
        # 所以我們保留原有的 Reporter 初始化邏輯
        self.reporter = Reporter(**config)
        self.report: dict = {}

    def _run(self, input: dict):
        """
        Runs the Reporter to create and generate reports.
        Adapts to the new functional Reporter architecture

        Args:
            input (dict): Input data for the Reporter.
                - data (dict): The data to be reported.
        """
        self._logger.debug("Starting data reporting process")

        # Use the new functional Reporter interface
        processed_data = self.reporter.create(data=input["data"])
        self._logger.debug("Reporting configuration initialization completed")

        # Call the functional report method
        result = self.reporter.report(processed_data)

        # Handle different types of Reporter results
        if isinstance(result, dict) and "Reporter" in result:
            # ReporterSaveReport
            temp = result["Reporter"]

            # Check if it's the old format (single granularity)
            if "eval_expt_name" in temp and "report" in temp:
                # Old format: single granularity
                if "warnings" in temp:
                    return
                eval_expt_name = temp["eval_expt_name"]
                report = deepcopy(temp["report"])
                self.report[eval_expt_name] = report
            else:
                # New format: multiple granularities
                for eval_expt_name, granularity_data in temp.items():
                    if not isinstance(granularity_data, dict):
                        continue

                    # Skip granularities with warnings
                    if "warnings" in granularity_data:
                        continue

                    # Validate required keys
                    if not all(
                        key in granularity_data for key in ["eval_expt_name", "report"]
                    ):
                        continue

                    # Skip if report is None
                    if granularity_data["report"] is None:
                        continue

                    report = deepcopy(granularity_data["report"])
                    self.report[eval_expt_name] = report
        elif isinstance(result, dict):
            # ReporterSaveData or other types
            self.report = deepcopy(result)
        else:
            # ReporterSaveTiming or other types that return DataFrame
            self.report = (
                {"timing_report": deepcopy(result)} if result is not None else {}
            )

        self._logger.debug("Data reporting completed")

    def set_input(self, status) -> dict:
        """
        Sets the input data for the Reporter.
        使用原有邏輯，因為 Reporter 需要完整的模組資訊

        Args:
            status: The status object.

        Returns:
            dict: The input data for the Reporter.
        """
        # Reporter 的資料源選擇邏輯是在 ReporterSaveData 內部處理的
        # 這裡保持原有邏輯，因為需要保留完整的 index_tuple 結構
        full_expt = status.get_full_expt()

        data = {}
        for module in full_expt.keys():
            index_dict = status.get_full_expt(module=module)
            result = status.get_result(module=module)

            # if module.get_result is a dict,
            #   add key into expt_name: expt_name[key]
            if isinstance(result, dict):
                for key in result.keys():
                    temp_dict: dict = index_dict.copy()
                    temp_dict[module] = f"{index_dict[module]}_[{key}]"
                    index_tuple = tuple(
                        item for pair in temp_dict.items() for item in pair
                    )
                    data[index_tuple] = deepcopy(result[key])
            else:
                index_tuple = tuple(
                    item for pair in index_dict.items() for item in pair
                )
                data[index_tuple] = deepcopy(result)
        self.input["data"] = data
        self.input["data"]["exist_report"] = status.get_report()

        # Add timing data support
        if hasattr(status, "get_timing_report_data"):
            timing_data = status.get_timing_report_data()
            if not timing_data.empty:
                self.input["data"]["timing_data"] = timing_data

        # Add validation results support - 傳遞 Constrainer 驗證結果給 Reporter
        if hasattr(status, "get_validation_result"):
            validation_results = status.get_validation_result()
            if validation_results:
                # 將驗證結果加入 data 字典，讓 ReporterSaveValidation 能夠使用
                for module_name, validation_result in validation_results.items():
                    # 檢查是否為多 source 的驗證結果（字典中的字典）
                    if isinstance(validation_result, dict) and all(
                        isinstance(v, dict) and "source_name" in v
                        for v in validation_result.values()
                    ):
                        # 多 source 的情況：為每個 source 創建獨立的 index_tuple
                        for source_name, source_validation in validation_result.items():
                            # 為驗證結果創建特殊的 index_tuple
                            # 格式: (Module, experiment_name, source_name)
                            module_expt = status.get_full_expt().get(module_name)
                            if module_expt:
                                # 將 source_name 添加到 index_tuple 中
                                index_tuple = (module_name, module_expt, source_name)
                                self.input["data"][index_tuple] = source_validation
                    else:
                        # 單一 source 的情況：使用原有邏輯
                        # 為驗證結果創建特殊的 index_tuple
                        # 格式: (Module, experiment_name)
                        module_expt = status.get_full_expt().get(module_name)
                        if module_expt:
                            index_tuple = (module_name, module_expt)
                            self.input["data"][index_tuple] = validation_result

        return self.input

    def get_result(self):
        """
        Placeholder method for getting the result.

        Returns:
            (dict) key as module name,
            value as raw/processed data (others) or report data (Reporter)
        """
        return deepcopy(self.report)
