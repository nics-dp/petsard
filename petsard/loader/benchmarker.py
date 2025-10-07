import hashlib
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml

from petsard.config_base import BaseConfig
from petsard.exceptions import (
    BenchmarkDatasetsError,
    ConfigError,
    UnsupportedMethodError,
)


@dataclass
class BenchmarkerConfig(BaseConfig):
    """
    Configuration for the benchmarker.

    Attributes:
        _logger (logging.Logger): The logger object.
        YAML_FILENAME (str): The benchmark datasets YAML filename.
        benchmark_name (str): The benchmark name.
        benchmark_filename (str): The benchmark filename.
        benchmark_access (str): The benchmark access type.
        benchmark_region_name (str): The benchmark region name.
        benchmark_bucket_name (str): The benchmark bucket name.
        benchmark_sha256 (str): The benchmark SHA-256 value.
        filepath_raw (str): The raw file path.
    """

    YAML_FILENAME: str = "benchmark_datasets.yaml"

    benchmark_name: str | None = None
    benchmark_filename: str | None = None
    benchmark_access: str | None = None
    benchmark_region_name: str | None = None
    benchmark_bucket_name: str | None = None
    benchmark_sha256: str | None = None
    filepath_raw: str | None = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing BenchmarkerConfig")

        if not self.benchmark_name:
            error_msg = "benchmark_name must be specified for BenchmarkerConfig"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Load and organize yaml: BENCHMARK_CONFIG
        self._logger.info("Loading benchmark configuration")
        benchmark_config: dict = self._load_benchmark_config()

        # Check if benchmark name exists in BENCHMARK_CONFIG
        if self.benchmark_name not in benchmark_config:
            error_msg = f"Benchmark dataset {self.benchmark_name} is not supported"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        benchmark_value: dict = benchmark_config[self.benchmark_name]
        self._logger.debug(f"Found benchmark configuration for {self.benchmark_name}")

        self.benchmark_filename = benchmark_value["filename"]

        if benchmark_value["access"] != "public":
            error_msg = (
                f"Benchmark access type {benchmark_value['access']} is not supported"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        self.benchmark_access = benchmark_value["access"]
        self.benchmark_region_name = benchmark_value["region_name"]
        self.benchmark_bucket_name = benchmark_value["bucket_name"]
        self.benchmark_sha256 = benchmark_value["sha256"]
        self._logger.info(
            f"Configured benchmark dataset: {self.benchmark_name}, filename: {self.benchmark_filename}"
        )

    def _load_benchmark_config(self) -> dict:
        """
        Load benchmark datasets configuration.

        Return:
            config (dict):
                key (str): benchmark dataset name
                    filename (str): Its filename
                    access (str): Belong to public or private bucket.
                    region_name (str): Its AWS S3 region.
                    bucket_name (str): Its AWS S3 bucket.
                    sha256 (str): Its SHA-256 value.
        """
        self._logger.debug(f"Loading benchmark configuration from {self.YAML_FILENAME}")

        config: dict = {}
        error_msg: str = ""

        try:
            with resources.open_text("petsard.loader", self.YAML_FILENAME) as file:
                config = yaml.safe_load(file)
                self._logger.debug("Successfully loaded benchmark YAML configuration")
        except Exception as e:
            error_msg = f"Failed to load benchmark configuration: {str(e)}"
            self._logger.error(error_msg)
            raise BenchmarkDatasetsError(error_msg) from e

        REGION_NAME = config["region_name"]
        BUCKET_NAME = config["bucket_name"]

        config["datasets"] = {
            key: {
                "filename": value["filename"],
                "access": value["access"],
                "region_name": REGION_NAME,
                "bucket_name": BUCKET_NAME[value["access"]],
                "sha256": value["sha256"],
            }
            for key, value in config["datasets"].items()
        }

        self._logger.debug(f"Processed {len(config['datasets'])} benchmark datasets")
        return config["datasets"]

    def get_benchmarker_config(self) -> dict:
        """
        Get configuration dictionary for BenchmarkerRequests.

        Returns:
            dict: Configuration dictionary with required keys for BenchmarkerRequests
        """
        return {
            "benchmark_filename": self.benchmark_filename,
            "benchmark_bucket_name": self.benchmark_bucket_name,
            "benchmark_sha256": self.benchmark_sha256,
            "filepath": Path("benchmark").joinpath(self.benchmark_filename),
        }


def digest_sha256(filepath):
    """
    Calculate SHA-256 value of file. Load 128KB at one time.
    ...
    Args:
        filepath (str) Openable file full path.
    ...
    return:
        (str) SHA-256 value of file.
    """
    sha256hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(131072), b""):
            sha256hash.update(byte_block)
    return sha256hash.hexdigest()


class BaseBenchmarker(ABC):
    """
    BaseBenchmarker
        Base class for all "Benchmarker".
        The "Benchmarker" class defines the common API
        that all the "Loader" need to implement, as well as common functionality.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict) The configuration of the benchmarker.
                benchmark_bucket_name (str) The name of the S3 bucket.
                benchmark_filename (str)
                    The name of the benchmark data from benchmark_datasets.yaml.
                benchmark_sha256 (str)
                    The SHA-256 value of the benchmark data from benchmark_datasets.yaml.
                filepath (str) The full path of the benchmark data in local.
                benchmark_already_exist (bool)
                    If the benchmark data already exist. Default is False.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing Benchmarker with benchmark_filename: {config['benchmark_filename']}"
        )

        self.config: dict = config
        self.config["benchmark_already_exist"] = False
        if os.path.exists(self.config["filepath"]):
            # if same name data already exist, check the sha256hash,
            #     if match, ignore download and continue,
            #     if NOT match, raise Error
            self._verify_file(already_exist=True)
        else:
            # if same name data didn't exist,
            #     confirm "./benchmark/" folder is exist (create it if not)
            os.makedirs("benchmark", exist_ok=True)

    @abstractmethod
    def download(self):
        """
        Download the data
        """
        raise NotImplementedError()

    def _verify_file(self, already_exist: bool = True):
        """
        Verify the exist file is match to records
        Raises BenchmarkDatasetsError if SHA-256 verification fails

        Args:
            already_exist (bool) If the file already exist. Default is True.
              False means verify under download process.
        """
        file_sha256hash = digest_sha256(self.config["filepath"])
        expected_sha256 = self.config["benchmark_sha256"]

        # Always log the SHA-256 comparison
        self._logger.info(
            f"SHA-256 verification for: {self.config['filepath']}\n"
            f"  Expected SHA-256: {expected_sha256}\n"
            f"  Actual SHA-256:   {file_sha256hash}"
        )

        if file_sha256hash == expected_sha256:
            self.config["benchmark_already_exist"] = True
            self._logger.info(
                f"SHA-256 verification PASSED for: {self.config['filepath']}"
            )
        else:
            # Raise error on SHA-256 mismatch
            if already_exist:
                error_msg = (
                    f"SHA-256 verification FAILED for existing file: {self.config['filepath']}\n"
                    f"  Expected SHA-256: {expected_sha256}\n"
                    f"  Actual SHA-256:   {file_sha256hash}\n"
                    f"The existing file may be outdated or modified. Please delete it and retry."
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg)
            else:
                error_msg = (
                    f"SHA-256 verification FAILED for downloaded file: {self.config['benchmark_filename']}\n"
                    f"  Source: {self.config['benchmark_bucket_name']}\n"
                    f"  Expected SHA-256: {expected_sha256}\n"
                    f"  Actual SHA-256:   {file_sha256hash}\n"
                    f"The download may be corrupted. Please try again."
                )
                self._logger.error(error_msg)
                # Delete the corrupted file
                try:
                    os.remove(self.config["filepath"])
                    self._logger.debug(
                        f"Removed corrupted file: {self.config['filepath']}"
                    )
                except OSError as e:
                    self._logger.debug(f"Failed to remove corrupted file: {e}")
                raise BenchmarkDatasetsError(error_msg)


class BenchmarkerRequests(BaseBenchmarker):
    """
    BenchmarkerRequests
        Download benchmark dataset via requests.
        Expect for public bucket.

    """

    def __init__(self, config: dict):
        super().__init__(config)

    def download(self) -> None:
        """
        Use requests.get() to download data,
            than confirm its SHA-256 is matched.

        """
        # 檢查 requests 是否已安裝
        try:
            import requests
        except ImportError as e:
            error_msg = (
                f"Cannot download benchmark file '{self.config['benchmark_filename']}': "
                f"The 'requests' library is required for downloading benchmark datasets.\n"
                f"Please install it with: pip install petsard[load-benchmark]"
            )
            self._logger.error(error_msg)
            raise BenchmarkDatasetsError(error_msg) from e

        if self.config["benchmark_already_exist"]:
            self._logger.info(f"Using existing local file: {self.config['filepath']}")
        else:
            url = (
                f"https://"
                f"{self.config['benchmark_bucket_name']}"
                f".s3.amazonaws.com/"
                f"{self.config['benchmark_filename']}"
            )
            self._logger.info(f"Downloading benchmark file from: {url}")

            try:
                with requests.get(url, stream=True, timeout=300) as response:
                    if response.status_code == 200:
                        total_size = int(response.headers.get("content-length", 0))
                        downloaded_size = 0

                        with open(self.config["filepath"], "wb") as f:
                            # load 8KB at one time
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)

                                    # Log progress for large files
                                    if (
                                        total_size > 0
                                        and downloaded_size % (1024 * 1024) == 0
                                    ):
                                        progress = (downloaded_size / total_size) * 100
                                        self._logger.debug(
                                            f"Download progress: {downloaded_size / (1024 * 1024):.1f}MB / "
                                            f"{total_size / (1024 * 1024):.1f}MB ({progress:.1f}%)"
                                        )

                        self._logger.info(
                            f"Download completed: {self.config['benchmark_filename']} "
                            f"({downloaded_size / (1024 * 1024):.1f}MB)"
                        )
                    elif response.status_code == 404:
                        error_msg = (
                            f"Benchmark file not found on server: {self.config['benchmark_filename']}\n"
                            f"  URL: {url}\n"
                            f"The file may have been removed or the URL may be incorrect."
                        )
                        self._logger.error(error_msg)
                        raise BenchmarkDatasetsError(error_msg)
                    else:
                        error_msg = (
                            f"Failed to download benchmark file: {self.config['benchmark_filename']}\n"
                            f"  HTTP Status: {response.status_code}\n"
                            f"  URL: {url}\n"
                            f"Please check your internet connection and try again."
                        )
                        self._logger.error(error_msg)
                        raise BenchmarkDatasetsError(error_msg)
            except requests.exceptions.Timeout as e:
                error_msg = (
                    f"Download timeout for benchmark file: {self.config['benchmark_filename']}\n"
                    f"The file may be too large or the connection may be slow.\n"
                    f"Please try again with a better connection."
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except requests.exceptions.ConnectionError as e:
                error_msg = (
                    f"Connection error while downloading benchmark file: {self.config['benchmark_filename']}\n"
                    f"Please check your internet connection and try again.\n"
                    f"Error details: {str(e)}"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e
            except Exception as e:
                # Clean up partial download
                if os.path.exists(self.config["filepath"]):
                    try:
                        os.remove(self.config["filepath"])
                        self._logger.debug(
                            f"Removed partial download: {self.config['filepath']}"
                        )
                    except OSError as remove_error:
                        self._logger.debug(
                            f"Failed to remove partial download: {remove_error}"
                        )

                error_msg = (
                    f"Unexpected error downloading benchmark file: {self.config['benchmark_filename']}\n"
                    f"Error: {str(e)}"
                )
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

            # Verify the downloaded file
            self._verify_file(already_exist=False)
