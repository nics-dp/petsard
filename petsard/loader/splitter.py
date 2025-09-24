import random

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.metadater.metadata import Schema


class Splitter:
    """
    Splitter is an independent module for Executor use. Included:
    a.) split input data via assigned ratio (train_split_ratio)
    b.) resampling assigned times (num_samples)
    c.) output their train/validation indexes (self.index_samples) and pd.DataFrame data (self.data)
    """

    def __init__(
        self,
        num_samples: int | None = 1,
        train_split_ratio: float | None = 0.8,
        random_state: int | float | str | None = None,
        max_overlap_ratio: float | None = 1.0,
        max_attempts: int | None = 30,
    ):
        """
        Args:
            num_samples (int, optional):
                Number of times to resample the data. Default is 1.
            train_split_ratio (float, optional):
                Ratio of data to assign to the training set,
                must between 0 ~ 1. Default is 0.8.
            random_state (int | float | str, optional):
                Seed for random number generation. Default is None.
            max_overlap_ratio (float, optional):
                Maximum allowed overlap ratio between samples.
                Default is 1.0 (100%). Set to 0.0 for no overlap.
            max_attempts (int, optional):
                Maximum number of attempts for sampling. Default is 30.

        Attr:
            config (dict):
                The configuration of Splitter containing:
                num_samples, train_split_ratio, random_state, max_overlap_ratio, max_attempts.
        """
        if not (0.0 <= train_split_ratio <= 1.0):
            raise ConfigError(
                "Splitter: train_split_ratio must be a float between 0 and 1."
            )
        if not (0.0 <= max_overlap_ratio <= 1.0):
            raise ConfigError(
                "Splitter: max_overlap_ratio must be a float between 0 and 1."
            )

        self.config = {
            "num_samples": num_samples,
            "train_split_ratio": train_split_ratio,
            "random_state": random_state,
            "max_overlap_ratio": max_overlap_ratio,
            "max_attempts": max_attempts,
        }

    def split(
        self,
        data: pd.DataFrame,
        metadata: Schema,
        exist_train_indices: list[set] = None,
    ) -> tuple[dict, dict, list[set]]:
        """
        Perform index bootstrapping on the Splitter-initialized data
            and split it into train and validation sets
            using the generated index samples.

        Args:
            data (pd.DataFrame): The dataset which wait for split.
            metadata (Schema): The metadata of the dataset.
            exist_train_indices (list[set], optional):
                The existing train index sets we want to avoid overlapping with.

        Returns:
            tuple[dict, dict, list[set]]:
                - Split data: {1: {train: pd.DataFrame, validation: pd.DataFrame}, 2: ...}
                - Metadata: {1: {train: Schema, validation: Schema}, 2: ...}
                - Train indices: [{train_indices_set1}, {train_indices_set2}, ...]
        """
        if data is None:
            raise ConfigError("Data must be provided for splitting")
        if metadata is None:
            raise ConfigError("Metadata must be provided for splitting")

        data.reset_index(drop=True, inplace=True)  # avoid unexpected index

        index_result = self._bootstrapping(
            index=data.index.tolist(), exist_train_indices=exist_train_indices
        )

        split_data = {}
        metadata_dict = {}
        train_indices_list = []

        for key, index in index_result.items():
            split_data[key] = {
                "train": data.iloc[index["train"]].reset_index(drop=True),
                "validation": data.iloc[index["validation"]].reset_index(drop=True),
            }

            # Create metadata for both train and validation
            train_metadata = self._update_metadata_with_split_info(
                metadata,
                len(index["train"]),
                len(index["validation"]),
            )
            validation_metadata = self._update_metadata_with_split_info(
                metadata,
                len(index["train"]),
                len(index["validation"]),
            )

            metadata_dict[key] = {
                "train": train_metadata,
                "validation": validation_metadata,
            }

            train_indices_list.append(set(index["train"]))

        return split_data, metadata_dict, train_indices_list

    def get_train_indices(self) -> list[set]:
        """
        取得最後一次分割的訓練索引列表，用於向後相容性。

        Returns:
            list[set]: 訓練索引集合列表
        """
        # 這個方法主要用於向後相容，實際使用建議直接使用 split() 的返回值
        if hasattr(self, "_last_train_indices"):
            return self._last_train_indices
        return []

    def _update_metadata_with_split_info(
        self, metadata: Schema, train_rows: int, validation_rows: int
    ) -> Schema:
        """
        Update metadata with split information using functional approach.

        Args:
            metadata: Original metadata from training data
            train_rows: Number of training rows
            validation_rows: Number of validation rows

        Returns:
            Updated metadata with split information
        """
        # Create new metadata instance with updated split information
        # Store split info in description field or create new stats
        split_description = (
            f"{metadata.description or ''} | Split info: train={train_rows} rows, validation={validation_rows} rows"
        ).strip()

        # Since Schema is now mutable, we can create a copy and update it
        from copy import deepcopy

        updated_metadata = deepcopy(metadata)
        updated_metadata.description = split_description

        # Store split info in a custom field if needed for programmatic access
        # We can add it as a comment in the description for now

        return updated_metadata

    def _bootstrapping(
        self, index: list, exist_train_indices: list[set] = None
    ) -> dict[int, dict[str, list[int]]]:
        """
        拔靴法生成隨機索引樣本用於資料分割。

        Args:
            index (list): 待分割資料集的索引列表
            exist_train_indices (list[set]): 現有的訓練索引集合列表，用於避免重疊
        """
        if self.config["random_state"] is not None:
            random.seed(self.config["random_state"])

        sample_size = int(len(index) * self.config["train_split_ratio"])

        # 初始化現有訓練索引集合列表
        existing_train_sets = []
        if exist_train_indices:
            existing_train_sets = [
                set(idx_set) if not isinstance(idx_set, set) else idx_set
                for idx_set in exist_train_indices
            ]

        sampled_index = {}

        for n in range(self.config["num_samples"]):
            attempts = 0
            while attempts < self.config["max_attempts"]:
                sampled_indices = set(random.sample(index, sample_size))

                # 檢查是否與現有訓練集合重疊過多
                if self._check_overlap_acceptable(sampled_indices, existing_train_sets):
                    # 將當前樣本加入現有訓練集合列表，供後續比較使用
                    existing_train_sets.append(sampled_indices)

                    sampled_index[n + 1] = {
                        "train": list(sampled_indices),
                        "validation": list(set(index) - sampled_indices),
                    }
                    break

                attempts += 1

            if attempts == self.config["max_attempts"]:
                raise ConfigError(
                    f"Splitter: "
                    f"Unable to sample {self.config['num_samples']} pairs of index "
                    f"with a ratio of {self.config['train_split_ratio']} "
                    f"and max overlap ratio of {self.config['max_overlap_ratio']:.1%} "
                    f"within {self.config['max_attempts']} attempts.\n"
                    f"Consider reducing num_samples, increasing max_overlap_ratio, "
                    f"or increasing max_attempts."
                )
        return sampled_index

    def _check_overlap_acceptable(
        self, new_train_sample: set, existing_train_sets: list[set]
    ) -> bool:
        """
        檢查新訓練樣本與現有訓練集合的重疊是否可接受。

        Args:
            new_train_sample (set): 新的訓練樣本索引集合
            existing_train_sets (list[set]): 現有的訓練索引集合列表

        Returns:
            bool: 如果重疊可接受則返回 True，否則返回 False
        """
        max_overlap_ratio = self.config["max_overlap_ratio"]

        for existing_train_set in existing_train_sets:
            # 1. 檢查是否完全一致
            if new_train_sample == existing_train_set:
                return False

            # 2. 檢查重疊比率是否超過限制
            if max_overlap_ratio < 1.0:  # 只有在不是 100% 時才檢查
                overlap_size = len(new_train_sample.intersection(existing_train_set))
                overlap_ratio = overlap_size / len(new_train_sample)

                if overlap_ratio > max_overlap_ratio:
                    return False

        return True
