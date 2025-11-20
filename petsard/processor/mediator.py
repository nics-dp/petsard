import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from petsard.exceptions import UnfittedError
from petsard.processor.encoder import EncoderOneHot
from petsard.processor.missing import MissingDrop
from petsard.processor.outlier import (
    OutlierIQR,
    OutlierIsolationForest,
    OutlierLOF,
    OutlierZScore,
)
from petsard.processor.scaler import ScalerTimeAnchor


class Mediator:
    """
    Deal with the processors with the same type to
    manage (column-wise) global behaviours including dropping the records.
    It is responsible for two actions:
        1. Gather all columns needed to process
        2. Coordinate and perform global behaviours
    """

    def __init__(self) -> None:
        self._process_col: list = []
        self._is_fitted: bool = False

        # for working config adjustment
        self.map: dict = {}

    def fit(self, data: None) -> None:
        """
        Base method of `fit`.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        # in most cases, mediator doesn't need data to fit
        # just to keep the interface unified
        self._fit(data)

        self._is_fitted = True

    def _fit():
        """
        _fit method is implemented in subclasses.

        fit method is responsible for general action defined by the base class.
        _fit method is for specific procedure conducted by each subclasses.
        """
        raise NotImplementedError(
            "_fit method should be implemented " + "in subclasses."
        )

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `transform`.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)

    def _transform():
        """
        _transform method is implemented in subclasses.

        transform method is responsible for general action
            defined by the base class.
        _transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_transform method should be implemented " + "in subclasses."
        )

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `inverse_transform`.
        Only for MediatorEncoder currently.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if len(self._process_col) == 0:
            return data
        else:
            return self._inverse_transform(data)

    def _inverse_transform():
        """
        _inverse_transform method is implemented in subclasses.

        inverse_transform method is responsible for general action
            defined by the base class.
        _inverse_transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_inverse_transform method should be implemented " + "in subclasses."
        )


class MediatorMissing(Mediator):
    """
    Deal with global behaviours in MissingHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config["missing"]

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if isinstance(obj, MissingDrop):
                self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            # restore the original data from the boolean data
            transformed[col_name] = (
                self._config.get(col_name, None).data_backup[~process_filter].values
            )

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = (
                    self._config.get(col, None).data_backup[~process_filter].values
                )

            return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        raise NotImplementedError("_inverse_transform is not supported in this class")


class MediatorOutlier(Mediator):
    """
    Deal with global behaviours in OutlierHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._config: dict = config["outlier"]
        self.model = None

        # indicator for using global outlier methods,
        # such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator: bool = False

        # Track detected methods for warning
        global_methods_found = []
        field_specific_methods = []

        # if any column in the config sets outlier method
        # as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for _col, obj in self._config.items():
            if isinstance(obj, OutlierIsolationForest):
                global_methods_found.append((_col, "IsolationForest"))
                if not self._global_model_indicator:
                    self.model = IsolationForest()
                    self._global_model_indicator = True
            elif isinstance(obj, OutlierLOF):
                global_methods_found.append((_col, "LOF"))
                if not self._global_model_indicator:
                    self.model = LocalOutlierFactor()
                    self._global_model_indicator = True
            elif isinstance(obj, (OutlierIQR, OutlierZScore)):
                field_specific_methods.append((_col, type(obj).__name__))

        # Warning 1: Multiple global methods detected
        if len(global_methods_found) > 1:
            methods_str = ", ".join(
                [f"{col}={method}" for col, method in global_methods_found]
            )
            self._logger.warning(
                f"⚠️ Multiple global outlier methods detected: {methods_str}. "
                f"Only the first one ({global_methods_found[0][1]}) will be used for ALL numerical columns."
            )

        # Warning 2: Mixing global and field-specific methods
        if self._global_model_indicator and field_specific_methods:
            global_method = global_methods_found[0][1]
            ignored_fields = ", ".join(
                [f"{col}={method}" for col, method in field_specific_methods]
            )
            self._logger.warning(
                f"⚠️ Global outlier method ({global_method}) will override field-specific methods. "
                f"Ignored settings: {ignored_fields}. "
                f"All numerical columns will be processed using {global_method}."
            )

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        if self._global_model_indicator:
            # global transformation from sklearn only accepts numeric type data
            self._process_col = list(
                data.columns[data.apply(pd.api.types.is_numeric_dtype, axis=0)]
            )

            if len(self._process_col) < 1:
                raise ValueError(
                    "There should be at least one numerical column \
                        to fit the model."
                )
        else:
            for col, obj in self._config.items():
                if type(obj) in [OutlierIQR, OutlierZScore]:
                    self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if self._global_model_indicator:
            # the model may classify most data as outliers
            # after transformation by other processors
            # so fit_predict will be used in _transform
            predict_result: np.ndarray = self.model.fit_predict(data[self._process_col])
            self.result: np.ndarray = predict_result
            process_filter: np.ndarray = predict_result == -1.0

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            return transformed
        elif len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            # restore the original data from the boolean data
            transformed[col_name] = self._config.get(col_name, None).data_backup[
                ~process_filter
            ]

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = self._config.get(col, None).data_backup[
                    ~process_filter
                ]

            return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        raise NotImplementedError("_inverse_transform is not supported in this class")


class MediatorEncoder(Mediator):
    """
    Deal with global behaviours in Encoder.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config["encoder"]

        # store the original column order
        self._colname: list = []

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            # Only EncoderOneHot needs MediatorEncoder to manage column creation
            # EncoderDateDiff handles DataFrame transformation directly
            if isinstance(obj, EncoderOneHot):
                self._process_col.append(col)

        self._colname = data.columns

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.
        Can be seperated into two steps:
        1. Create propers new column names (to avoid duplicates).
        2. Drop the original columns and insert the new ones to the dataframe.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        transformed = data.copy()

        for col in self._process_col:
            label_list = self._config[col].labels[1:]

            # prevent duplicates
            n = 1
            new_labels = [str(col) + "_" + str(label) for label in label_list]

            # check if the new labels and the original columns overlap
            while len(set(new_labels) & set(self._colname)) != 0:
                n = n + 1
                new_labels = [str(col) + "_" * n + str(label) for label in label_list]

            ohe_df = pd.DataFrame(self._config[col]._transform_temp, columns=new_labels)

            self.map[col] = new_labels

            # clear the temp
            self._config[col]._transform_temp = None

            transformed.drop(col, axis=1, inplace=True)
            transformed = pd.concat([transformed, ohe_df], axis=1)

        return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        """
        Conduct global inverse transformation.
        Can be seperated into two steps:
        1. Retrieve new column data and extract values.
        2. Drop the new columns and insert the original ones to the dataframe.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        transformed = data.copy()

        for ori_col, new_col in self.map.items():
            transformed.drop(new_col, axis=1, inplace=True)
            transformed[ori_col] = (
                self._config[ori_col].model.inverse_transform(data[new_col]).ravel()
            )

        return transformed.reindex(columns=self._colname)


class MediatorScaler(Mediator):
    """
    Mediator for scaling operations that require global coordination.
    Ensures TimeAnchor transformations are performed before other scaling operations.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize MediatorScaler.

        Args:
            config (dict): Configuration dictionary containing scaler settings
        """
        super().__init__()
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._config = config["scaler"]

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Find and process TimeAnchor scalers with comprehensive error checking.

        This method validates TimeAnchor scaler configurations by checking:
        - Reference column specification (string or list)
        - Correct unit setting
        - Reference column existence
        - Reference column datetime type

        When reference is a list, it creates multiple output columns (one per reference).
        """
        self.time_anchor_cols: list[str] = []
        self.reference_cols: dict[str, str | list[str]] = {}

        for col, processor in self._config.items():
            # Check if it's a TimeAnchor scaler
            if isinstance(processor, ScalerTimeAnchor):
                # Check if reference column is specified
                if not hasattr(processor, "reference"):
                    self.logger.error(
                        f"TimeAnchor scaler {col} has no reference column specified"
                    )
                    raise ValueError(
                        f"TimeAnchor scaler {col} has no reference column specified"
                    )

                ref_col = processor.reference

                # Validate unit, default to 'D'
                unit = processor.unit
                if unit not in ["D", "S"]:
                    self.logger.error(
                        f"TimeAnchor scaler {col} has incorrect unit, must be 'D'(days) or 'S'(seconds)"
                    )
                    raise ValueError(
                        f"TimeAnchor scaler {col} has incorrect unit, must be 'D'(days) or 'S'(seconds)"
                    )

                # Handle both single reference (str) and multiple references (list)
                ref_cols_to_check = [ref_col] if isinstance(ref_col, str) else ref_col

                for ref in ref_cols_to_check:
                    # Check if reference column exists in dataset
                    if ref not in data.columns:
                        self.logger.error(
                            f"Reference column {ref} does not exist in dataset"
                        )
                        raise ValueError(
                            f"Reference column {ref} does not exist in dataset"
                        )

                self.time_anchor_cols.append(col)
                self.reference_cols[col] = ref_col

                # For list reference, we'll handle it in transform
                # Don't set reference_time here for list references
                if isinstance(ref_col, str):
                    processor.set_reference_time(data[ref_col])
                else:
                    # Store that this processor has multiple references
                    processor._is_multi_reference = True
                    processor._reference_list = ref_col

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data, ensuring TimeAnchor operations are done first

        Design:
        - Single reference: transforms anchor column using reference
        - Multiple references: transforms reference columns using anchor as reference
          (anchor stays as datetime, references become time differences)
        """
        result = data.copy()
        self.original_dtypes = result.dtypes.to_dict()

        # Track column mapping for multi-reference mode
        self.map = {}

        # First transform TimeAnchor columns
        for col in self.time_anchor_cols:
            processor = self._config[col]
            if not isinstance(processor, ScalerTimeAnchor):
                continue

            ref_col = self.reference_cols[col]

            # Handle multi-reference mode
            if isinstance(ref_col, list):
                self.logger.debug(
                    f"Processing TimeAnchor: anchor '{col}' stays as datetime, "
                    f"transforming {len(ref_col)} reference columns to time differences"
                )

                # Ensure anchor column is datetime type
                if not pd.api.types.is_datetime64_any_dtype(result[col]):
                    self.logger.debug(f"Converting anchor '{col}' to datetime")
                    result[col] = pd.to_datetime(result[col])

                # Transform each reference column to time difference from anchor
                for ref in ref_col:
                    # Ensure reference column is datetime type
                    if not pd.api.types.is_datetime64_any_dtype(result[ref]):
                        self.logger.debug(f"Converting reference '{ref}' to datetime")
                        result[ref] = pd.to_datetime(result[ref])

                    # Use anchor (col) as reference time
                    processor.set_reference_time(result[col])
                    # Transform the reference column
                    result[ref] = processor.transform(result[ref])

                    self.logger.debug(
                        f"  Transformed '{ref}': time difference from anchor '{col}' (in {processor.unit})"
                    )

                # Keep anchor column as-is (datetime)
                # Track which reference columns were transformed
                self.map[col] = ref_col

            else:
                # Single reference mode: transform anchor using reference
                # Ensure both columns are datetime type
                if not pd.api.types.is_datetime64_any_dtype(result[ref_col]):
                    self.logger.debug(f"Converting reference '{ref_col}' to datetime")
                    result[ref_col] = pd.to_datetime(result[ref_col])
                if not pd.api.types.is_datetime64_any_dtype(result[col]):
                    self.logger.debug(f"Converting anchor '{col}' to datetime")
                    result[col] = pd.to_datetime(result[col])

                processor.set_reference_time(result[ref_col])
                result[col] = processor.transform(result[col])
                self.logger.debug(
                    f"Transformed anchor '{col}' using reference '{ref_col}'"
                )

        # Then transform other columns
        for col, processor in self._config.items():
            if processor is not None and not isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.transform(data[col])

        return result

    def _inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform data in the correct order

        Design:
        - Single reference: restore anchor from time difference
        - Multiple references: restore reference columns from time differences
          (anchor column is unchanged as it was kept as datetime)
        """
        result = data.copy()

        # First inverse transform non-TimeAnchor columns
        for col, processor in self._config.items():
            if processor is not None and not isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.inverse_transform(data[col])

        # Then inverse transform TimeAnchor columns
        for col, processor in self._config.items():
            if isinstance(processor, ScalerTimeAnchor):
                # Handle multi-reference mode
                if hasattr(self, "map") and col in self.map:
                    # Multi-reference: restore reference columns from time differences
                    ref_cols = self.map[col]

                    self.logger.debug(
                        f"Inverse transforming {len(ref_cols)} reference columns using anchor '{col}'"
                    )

                    # Use anchor (col) as reference to restore each reference column
                    processor.set_reference_time(data[col])
                    for ref in ref_cols:
                        result[ref] = processor.inverse_transform(data[ref])
                        self.logger.debug(f"  Restored '{ref}' to datetime")

                    # Anchor column stays as-is (it was never transformed)

                else:
                    # Single reference mode: restore anchor from time difference
                    result[col] = processor.inverse_transform(data[col])

                    if hasattr(self, "original_dtypes") and col in self.original_dtypes:
                        result[col] = result[col].astype(self.original_dtypes[col])

        return result
