import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from petsard.exceptions import UnfittedError


class Scaler:
    """
    Base class for all Scaler classes.
    """

    PROC_TYPE = ("scaler",)

    def __init__(self) -> None:
        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data needed to be fitted.
        """
        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

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

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Args:
            data (pd.Series): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

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

    def inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `inverse_transform`.

        Args:
            data (pd.Series): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if isinstance(data, pd.Series):
            data = data.values.reshape(-1, 1)

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
            "_inverse_transform method should be " + "implemented in subclasses."
        )


class ScalerStandard(Scaler):
    """
    Apply StandardScaler.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler()

    def _fit(self, data: np.ndarray) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.
        """
        self.model.fit(data)

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct standardisation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        return self.model.transform(data)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Args:
            data (np.ndarray): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return self.model.inverse_transform(data)


class ScalerZeroCenter(ScalerStandard):
    """
    Apply StandardScaler without std scaling.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = StandardScaler(with_std=False)


class ScalerMinMax(ScalerStandard):
    """
    Apply MinMaxScaler.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model: MinMaxScaler = MinMaxScaler()


class ScalerLog(Scaler):
    """
    Scale the data by log transformation.
    """

    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: np.ndarray) -> None:
        """
        Check whether the log transformation can be performed.

        Args:
            data (np.ndarray): The data needed to be transformed.
        """
        if (data <= 0).any():
            raise ValueError("Log transformation does not support non-positive values.")

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct log transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        if (data <= 0).any():
            raise ValueError("Log transformation does not support non-positive values.")
        else:
            return np.log(np.asarray(data, dtype=float))

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Args:
            data (np.ndarray): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return np.exp(np.asarray(data, dtype=float))


class ScalerLog1p(Scaler):
    """
    Scale the data by log1p transformation (log(1+x)).
    """

    def __init__(self) -> None:
        super().__init__()

    def _fit(self, data: np.ndarray) -> None:
        """
        Check whether the log1p transformation can be performed.

        Args:
            data (np.ndarray): The data needed to be transformed.
        """
        if (data < -1).any():
            raise ValueError("Log1p transformation requires values >= -1")

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """
        Conduct log1p transformation.

        Args:
            data (np.ndarray): The data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        if (data < -1).any():
            raise ValueError("Log1p transformation requires values >= -1")
        else:
            return np.log1p(np.asarray(data, dtype=float))

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Inverse the transformed data to the data in the original scale.

        Args:
            data (np.ndarray): The data needed to be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return np.expm1(np.asarray(data, dtype=float))


class ScalerTimeAnchor(Scaler):
    """
    Scale the data by time difference from a reference time series.

    Supports both single reference (str) and multiple references (list).
    When reference is a list, MediatorScaler will handle the multi-column expansion.
    """

    def __init__(self, reference: str | list[str], unit: str = "D") -> None:
        super().__init__()
        if unit not in ["D", "S"]:
            raise ValueError("unit must be either 'D'(days) or 'S'(seconds)")
        self.unit: str = unit
        self.reference: str | list[str] = reference
        # Mark whether this is multi-reference mode
        self._is_multi_reference: bool = isinstance(reference, list)
        self._reference_list: list[str] | None = (
            reference if self._is_multi_reference else None
        )

    def set_reference_time(self, reference_series: pd.Series) -> None:
        """Set reference series for row-wise time difference calculation

        Note: This is only used for single reference mode.
        For multi-reference mode, MediatorScaler handles the reference setting.
        """
        if not pd.api.types.is_datetime64_any_dtype(reference_series):
            raise ValueError("Reference data must be datetime type")
        self.reference_series = reference_series

    def _fit(self, data: np.ndarray) -> None:
        """Validate data type and reference

        For multi-reference mode, skip all validation as MediatorScaler handles it.
        The anchor column will be checked during transform when converting references.
        """
        # Skip all fit validation for multi-reference mode
        # MediatorScaler will validate datetime types during transform()
        if self._is_multi_reference:
            return

        # Single reference mode: check if reference series is set
        if not hasattr(self, "reference_series"):
            raise ValueError(
                "Reference series not set. Use set_reference_time() first."
            )

        # Convert data to pandas Series for datetime validation
        data_series = pd.Series(data.ravel())
        if not pd.api.types.is_datetime64_any_dtype(data_series):
            raise ValueError("Data must be in datetime format")

        # Check length match
        if len(data) != len(self.reference_series):
            raise ValueError("Target and reference must have same length")

    def _transform(self, data: np.ndarray) -> np.ndarray:
        """Transform to time differences

        For multi-reference mode, return data unchanged (anchor column is not transformed).
        MediatorScaler handles the transformation of reference columns.
        """
        # Multi-reference mode: anchor column should not be transformed
        # MediatorScaler already handled transforming the reference columns
        # Return 1D array to avoid dimension issues
        if self._is_multi_reference:
            return data.ravel()

        # Single reference mode: transform as usual
        if len(data) != len(self.reference_series):
            raise ValueError("Target and reference must have same length")

        delta = pd.Series(data.ravel()) - self.reference_series

        if self.unit == "D":
            return (delta.dt.total_seconds() / (24 * 3600)).values.reshape(-1, 1)
        else:
            return delta.dt.total_seconds().values.reshape(-1, 1)

    def _inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Restore to original datetime

        For multi-reference mode, return data unchanged (anchor column was not transformed).
        MediatorScaler handles the inverse transformation of reference columns.
        """
        # Multi-reference mode: anchor column was not transformed, return as-is
        # MediatorScaler already handled inverse transforming the reference columns
        # Return 1D array to avoid dimension issues
        if self._is_multi_reference:
            return data.ravel()

        # Single reference mode: inverse transform as usual
        if self.unit == "D":
            delta = pd.Series(data.ravel()) * pd.Timedelta(days=1)
        else:
            delta = pd.Series(data.ravel()) * pd.Timedelta(seconds=1)

        return (self.reference_series + delta).values.reshape(-1, 1)
