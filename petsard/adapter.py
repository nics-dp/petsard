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

            from petsard.loader.benchmarker import BenchmarkerConfig

            benchmark_name = re.sub(
                r"^benchmark://", "", filepath, flags=re.IGNORECASE
            ).lower()

            self._logger.info(f"Detected benchmark protocol: {benchmark_name}")

            # Create BenchmarkerConfig
            self.benchmarker_config = BenchmarkerConfig(
                benchmark_name=benchmark_name, filepath_raw=filepath
            )

            # Update filepath in config to local path
            local_filepath = Path("benchmark").joinpath(
                self.benchmarker_config.benchmark_filename
            )
            config["filepath"] = str(local_filepath)

            self._logger.debug(f"Updated filepath to local path: {local_filepath}")

        # Remove method parameter if exists, as Loader no longer accepts it
        config.pop("method", None)

        # Create Loader instance with possibly updated config
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

        # If benchmark protocol, download dataset first
        if self.is_benchmark and self.benchmarker_config:
            self._logger.info(
                f"Downloading benchmark dataset: {self.benchmarker_config.benchmark_name}"
            )
            try:
                from petsard.exceptions import BenchmarkDatasetsError
                from petsard.loader.benchmarker import BenchmarkerRequests

                BenchmarkerRequests(
                    self.benchmarker_config.get_benchmarker_config()
                ).download()
                self._logger.debug("Benchmark dataset downloaded successfully")
            except Exception as e:
                error_msg = f"Failed to download benchmark dataset: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

        # Load data (regardless of whether it's benchmark or not)
        self.data, self._schema_metadata = self.loader.load()

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
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).

        Attributes:
            processor (Processor):
                An instance of the Processor class initialized with the provided configuration.
        """
        self._logger.debug("Starting data postprocessing process")

        self.processor = input["preprocessor"]
        self._logger.debug("Processor configuration loading completed")

        self.data_postproc = self.processor.inverse_transform(data=input["data"])
        self._logger.debug("Data postprocessing completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the PostprocessorAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Postprocessor input should contains data (pd.DataFrame) and preprocessor (Processor).
        """
        self.input["data"] = status.get_result(status.get_pre_module("Postprocessor"))
        self.input["preprocessor"] = status.get_processor()

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

        Attributes:
            constrainer (Constrainer): An instance of the Constrainer class
                initialized with the provided configuration.
        """
        # Transform field combinations before initializing
        config = self._transform_field_combinations(config)
        super().__init__(config)

        # Store sampling configuration if provided
        self.sample_dict = {}
        self.sample_dict.update(
            {
                key: config.pop(key)
                for key in [
                    "target_rows",
                    "sampling_ratio",
                    "max_trials",
                    "verbose_step",
                ]
                if key in config
            }
        )

        self.constrainer = Constrainer(config)

    def _run(self, input: dict):
        """
        Execute data constraining process using the Constrainer instance.

        Args:
            input (dict): Constrainer input should contain:
                - data (pd.DataFrame): Data to be constrained
                - synthesizer (optional): Synthesizer instance if resampling is needed
                - postprocessor (optional): Postprocessor instance if needed

        Attributes:
            constrained_data (pd.DataFrame): The constrained result data.
        """
        self._logger.debug("Starting data constraining process")

        if "target_rows" not in self.sample_dict:
            self.sample_dict["target_rows"] = len(input["data"])

        if "synthesizer" in input:
            # Use resample_until_satisfy if sampling parameters and synthesizer are provided
            self._logger.debug("Using resample_until_satisfy method")
            self.constrained_data = self.constrainer.resample_until_satisfy(
                data=input["data"],
                synthesizer=input["synthesizer"],
                postprocessor=input.get("postprocessor"),
                **self.sample_dict,
            )
        else:
            # Use simple apply method
            self._logger.debug("Using apply method")
            self.constrained_data = self.constrainer.apply(input["data"])

        self._logger.debug("Data constraining completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Set the input for the ConstrainerAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict: Constrainer input should contain:
                - data (pd.DataFrame)
                - synthesizer (optional)
                - postprocessor (optional)
        """
        pre_module = status.get_pre_module("Constrainer")

        # Get data from previous module
        if pre_module == "Splitter":
            self.input["data"] = status.get_result(pre_module)["train"]
        else:  # Loader, Preprocessor, Synthesizer, or Postprocessor
            self.input["data"] = status.get_result(pre_module)

        # Get synthesizer if available
        if "Synthesizer" in status.status:
            self.input["synthesizer"] = status.get_synthesizer()

        # Get postprocessor if available
        if "Postprocessor" in status.status:
            self.input["postprocessor"] = status.get_processor()

        return self.input

    def get_result(self):
        """
        Retrieve the constraining result.

        Returns:
            pd.DataFrame: The constrained data.
        """
        return deepcopy(self.constrained_data)

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

        # Auto-align data types if schema is available
        if "schema" in input and input["schema"]:
            self._logger.debug("Schema found, aligning data types")
            aligned_data = {}
            for key, df in input["data"].items():
                if df is not None and not df.empty:
                    self._logger.debug(f"Aligning data type for '{key}' data")
                    aligned_data[key] = SchemaMetadater.align(input["schema"], df)
                else:
                    aligned_data[key] = df
            input["data"] = aligned_data
            self._logger.debug("Data type alignment completed")

            # Remove schema from input as Evaluator.eval() doesn't accept it
            del input["schema"]

        self.evaluator.create()
        self._logger.debug("Evaluation model initialization completed")

        self.evaluations = self.evaluator.eval(**input)
        self._logger.debug("Data evaluating completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the EvaluatorAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Evaluator input should contains data (dict) and optional schema.
        """
        if "Splitter" in status.status:
            self.input["data"] = {
                "ori": status.get_result("Splitter")["train"],
                "syn": status.get_result(status.get_pre_module("Evaluator")),
                "control": status.get_result("Splitter")["validation"],
            }
        else:  # Loader only
            self.input["data"] = {
                "ori": status.get_result("Loader"),
                "syn": status.get_result(status.get_pre_module("Evaluator")),
            }

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

    INPUT_PRIORITY: list[str] = [
        "Postprocessor",
        "Synthesizer",
        "Preprocessor",
        "Splitter",
        "Loader",
    ]

    def __init__(self, config: dict):
        """
        Attributes:
            describer (Describer):
                An instance of the Describer class initialized with the provided configuration.
        """
        super().__init__(config)
        self.describer = Describer(**config)
        self.description: dict[str, pd.DataFrame] = None

    def _run(self, input: dict):
        """
        Executes the data describing using the Describer instance.

        Args:
            input (dict): Describer input should contains data (dict).

        Attributes:
            describer.result (dict): An describing result data.
        """
        self._logger.debug("Starting data describing process")

        self.describer.create()
        self._logger.debug("Describing model initialization completed")

        self.description = self.describer.eval(**input)
        self._logger.debug("Data describing completed")

    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """
        Sets the input for the DescriberAdapter.

        Args:
            status (Status): The current status object.

        Returns:
            dict:
                Describer input should contains data (dict).
        """

        self.input["data"] = None
        for module in self.INPUT_PRIORITY:
            if module in status.status:
                self.input["data"] = {
                    "data": (
                        status.get_result("Splitter")["train"]
                        if module == "Splitter"
                        else status.get_result(module)
                    )
                }
                break

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

    Methods:
        _run(input: dict): Runs the Reporter to create and generate reports.
        set_input(status) -> dict: Sets the input data for the Reporter.
        get_result(): Placeholder method for getting the result.

    """

    def __init__(self, config: dict):
        super().__init__(config)
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

        Args:
            status: The status object.

        Returns:
            dict: The input data for the Reporter.
        """
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

        return self.input

    def get_result(self):
        """
        Placeholder method for getting the result.

        Returns:
            (dict) key as module name,
            value as raw/processed data (others) or report data (Reporter)
        """
        return deepcopy(self.report)
