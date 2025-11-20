from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from petsard.exceptions import UnfittedError
from petsard.processor.schema_transform import SchemaTransformMixin, schema_transform


def dict_get_na(dictionary: dict, key: str) -> Any:
    """
    Get value from dictionary by key, handling NaN keys.

    Args:
        dictionary (dict): The dictionary to search.
        key (str): The key to look for.

    Returns:
        Any: The value associated with the key, or None if not found.
    """
    if pd.isna(key):
        for k, v in dictionary.items():
            if pd.isna(k):
                return v
    return dictionary.get(key, None)


class Encoder:
    """
    Base class for all Encoder classes.
    """

    PROC_TYPE = ("encoder",)

    def __init__(self) -> None:
        # Mapping dict
        self.cat_to_val = None

        # Labels
        self.labels = None

        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data to be fitted.
        """
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
            data (pd.Series): The data to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        # Check whether the categories of the column are
        # included in the fitted instance
        data_set = {x for x in set(data.unique()) if pd.notna(x)}
        labels_set = {x for x in set(self.labels) if pd.notna(x)}
        if not data_set.issubset(labels_set):
            raise ValueError(
                "The data contains categories that the object hasn't seen",
                " in the fitting process.",
                " Please check the data categories again.",
            )

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

    def inverse_transform(self, data: pd.Series) -> pd.Series | np.ndarray:
        """
        Base method of `inverse_transform`.

        Args:
            data (pd.Series): The data to be inverse transformed.

        Return:
            (pd.Series | np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

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


class EncoderUniform(SchemaTransformMixin, Encoder):
    """
    Implement a uniform encoder.
    Convert categorical data to uniformly distributed numeric values (0-1)
    """

    SCHEMA_TRANSFORM = schema_transform(
        input_category=True,
        output_type="float64",
        output_category=False,
        description="Uniform encoding: categorical -> uniform distribution (0-1)",
    )

    def __init__(self) -> None:
        super().__init__()

        # Lower and upper values
        self.upper_values = None
        self.lower_values = None

        # Initiate a random generator
        self._rgenerator = np.random.default_rng()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        # Filter the counts > 0
        normalize_value_counts = data.value_counts(normalize=True, dropna=False).loc[
            lambda x: x > 0.0
        ]
        # Get keys (original labels)
        self.labels = normalize_value_counts.index.get_level_values(0).to_list()
        # Get values (upper and lower bounds)
        self.upper_values = np.cumsum(normalize_value_counts.values)
        self.lower_values = np.roll(self.upper_values, 1)
        # To make sure the range of the data is in [0, 1].
        # That is, the range of an uniform dist.
        self.upper_values[-1] = 1.0
        self.lower_values[0] = 0.0

        self.cat_to_val = dict(
            zip(
                self.labels,
                list(zip(self.lower_values, self.upper_values, strict=False)),
                strict=False,
            )
        )

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a uniform distribution.
            For example, a column with two categories (e.g., 'Male', 'Female')
                  can be mapped to [0.0, 0.5) and [0.5, 1], respectively.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        if isinstance(data.dtype, pd.api.types.CategoricalDtype):
            data_obj = data.astype(object)
        else:
            data_obj = data.copy()

        return data_obj.map(
            lambda x: self._rgenerator.uniform(
                dict_get_na(self.cat_to_val, x)[0],
                dict_get_na(self.cat_to_val, x)[1],
                size=1,
            )[0]
        ).values

    def _inverse_transform(self, data: pd.Series) -> pd.Series:
        """
        Inverse the transformed data to the categorical data.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            (pd.Series): The inverse transformed data.
        """

        # Check the range of the data is valid
        if data.max() > 1 or data.min() < 0:
            raise ValueError(
                "The range of the data is out of range.",
                " Please check the data again.",
            )

        bins_val = np.append(self.lower_values, 1.0)

        result = pd.cut(
            data,
            right=False,
            include_lowest=True,
            bins=bins_val,
            labels=[
                "pd.NA-PETsARD-impossible" if pd.isna(label) else label
                for label in self.labels
            ],
            ordered=False,
        ).astype("object")

        # Ensure result is a pandas Series before calling replace
        if isinstance(result, np.ndarray):
            result = pd.Series(result)

        return result.replace("pd.NA-PETsARD-impossible", pd.NA)


class EncoderLabel(SchemaTransformMixin, Encoder):
    """
    Implement a label encoder.
    Convert categorical data to integer labels
    """

    PROC_TYPE = ("encoder", "discretizing")

    SCHEMA_TRANSFORM = schema_transform(
        input_category=True,
        output_type="int64",
        output_category=False,
        description="Label encoding: categorical -> integer labels",
    )

    def __init__(self) -> None:
        super().__init__()
        self.model = LabelEncoder()
        self._na_marker = "__PETSARD_NA_MARKER__"
        self._has_na = False

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Handles pd.NA values by replacing them with a special marker string
        that sklearn's LabelEncoder can process.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        # Check if data contains NA values
        self._has_na = data.isna().any()

        # Convert Categorical to object to allow adding marker
        if isinstance(data.dtype, pd.CategoricalDtype):
            data = data.astype(object)

        # Replace pd.NA with a marker string for sklearn compatibility
        data_processed = data.fillna(self._na_marker)

        self.model.fit(data_processed)

        # Get keys (original labels) - replace marker back to pd.NA in labels
        self.labels = [
            pd.NA if label == self._na_marker else label
            for label in self.model.classes_
        ]

        self.cat_to_val = dict(
            zip(
                self.labels,
                list(self.model.transform(self.model.classes_)),
                strict=False,
            )
        )

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a series of integer labels.

        Handles pd.NA values by replacing them with the marker before transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Convert Categorical to object to allow adding marker
        if isinstance(data.dtype, pd.CategoricalDtype):
            data = data.astype(object)

        # Replace pd.NA with marker for sklearn compatibility
        data_processed = data.fillna(self._na_marker)
        return self.model.transform(data_processed)

    def _inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Inverse the transformed data to the categorical data.

        Handles pd.NA values by converting the marker back to pd.NA.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """
        result = self.model.inverse_transform(data)

        # Replace marker back to pd.NA if it was present in original data
        if self._has_na:
            result = np.array(
                [pd.NA if val == self._na_marker else val for val in result],
                dtype=object,
            )

        return result


class EncoderOneHot(SchemaTransformMixin, Encoder):
    """
    Implement a one-hot encoder.
    Convert categorical data to multiple binary columns (one-hot encoding)
    """

    SCHEMA_TRANSFORM = schema_transform(
        input_category=True,
        output_type="int64",
        output_category=False,
        creates_columns=True,
        removes_columns=True,
        column_pattern="{column}_{value}",
        description="One-hot encoding: categorical -> multiple binary columns",
    )

    def __init__(self) -> None:
        super().__init__()
        self.model = OneHotEncoder(sparse_output=False, drop="first")

        # for the use in Mediator
        self._transform_temp: np.ndarray = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        self.model.fit(data.values.reshape(-1, 1))

        # Set original labels
        self.labels = self.model.categories_[0].tolist()

    def _transform(self, data: pd.Series) -> None:
        """
        Transform categorical data to a one-hot numeric array.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            None: The transformed data is stored in _transform_temp.
            data (pd.Series): Original data (dummy).
        """

        self._transform_temp = self.model.transform(data.values.reshape(-1, 1))

        return data

    def _inverse_transform(self, data: pd.Series) -> None:
        """
        Inverse the transformed data to the categorical data.
        This is a dummy method, and it is implemented in MediatorEncoder.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            data (pd.Series): Original data (dummy).
        """

        return data


class EncoderDateDiff(Encoder):
    """
    Encoder for calculating day differences between dates using a baseline date.

    This encoder takes a baseline date column and related date columns,
    and calculates the difference in days between the baseline date and
    each related date during transformation.

    Attributes:
        baseline_date (str): Name of the column containing the baseline date
        related_date_list (List[str]): List of column names containing dates to compare with baseline
        diff_unit (str): Unit for the difference calculation ('days', 'weeks', 'months', 'years')
        absolute_value (bool): Whether to return absolute differences
    """

    def __init__(
        self,
        baseline_date: str,
        related_date_list: list[str] | None = None,
        diff_unit: str = "days",
        absolute_value: bool = False,
    ) -> None:
        """
        Initialize the DateDiffEncoder.

        Args:
            baseline_date: Name of the column containing the baseline date
            related_date_list: List of column names containing dates to compare
            diff_unit: Unit for difference calculation ('days', 'weeks', 'months', 'years')
            absolute_value: Whether to return absolute differences
        """
        super().__init__()

        self.baseline_date = baseline_date
        self.related_date_list = related_date_list or []
        self.diff_unit = diff_unit
        self.absolute_value = absolute_value

        # Validate diff_unit
        if diff_unit not in ["days", "weeks", "months", "years"]:
            raise ValueError(
                "diff_unit must be one of: 'days', 'weeks', 'months', 'years'"
            )

        # Will be populated during fit
        self._original_dtypes = {}
        self.is_fitted = False

    def _calc_date_diff(self, baseline_date, compare_date) -> float | None:
        """
        Calculate the difference between two dates.

        Args:
            baseline_date: The baseline date
            compare_date: The date to compare with the baseline

        Returns:
            Difference between dates in the specified unit, or None if inputs are invalid
        """
        if pd.isna(baseline_date) or pd.isna(compare_date):
            return None

        # Convert to pandas Timestamp if not already
        if not isinstance(baseline_date, pd.Timestamp):
            try:
                baseline_date = pd.to_datetime(baseline_date)
            except Exception:
                return None

        if not isinstance(compare_date, pd.Timestamp):
            try:
                compare_date = pd.to_datetime(compare_date)
            except Exception:
                return None

        # Calculate difference in days
        diff_days = (compare_date - baseline_date).days

        # Apply absolute value if needed
        if self.absolute_value:
            diff_days = abs(diff_days)

        # Convert to requested unit
        if self.diff_unit == "days":
            return diff_days
        elif self.diff_unit == "weeks":
            return diff_days / 7
        elif self.diff_unit == "months":
            # Approximate months calculation
            return diff_days / 30.44
        elif self.diff_unit == "years":
            # Approximate years calculation
            return diff_days / 365.25
        else:
            return diff_days  # Default to days

    def _calc_date_from_diff(self, baseline_date, diff_value) -> pd.Timestamp | None:
        """
        Calculate a date from a baseline date and a difference value.

        Args:
            baseline_date: The baseline date
            diff_value: The difference value in the specified unit

        Returns:
            Calculated date, or None if inputs are invalid
        """
        if pd.isna(baseline_date) or pd.isna(diff_value):
            return None

        # Convert to pandas Timestamp if not already
        if not isinstance(baseline_date, pd.Timestamp):
            try:
                baseline_date = pd.to_datetime(baseline_date)
            except Exception:
                return None

        # Convert diff_value to days based on the unit
        days = diff_value
        if self.diff_unit == "weeks":
            days = diff_value * 7
        elif self.diff_unit == "months":
            days = diff_value * 30.44  # Approximate
        elif self.diff_unit == "years":
            days = diff_value * 365.25  # Approximate

        # Calculate the date
        return baseline_date + pd.Timedelta(days=days)

    def fit(self, data: pd.DataFrame) -> None:
        """
        Fit method - override base class to handle DataFrame input

        Args:
            data: DataFrame containing the date columns
        """
        self._fit(data)
        self._is_fitted = True

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method - override base class to handle DataFrame input

        Args:
            data: DataFrame containing the date columns

        Returns:
            DataFrame with date differences
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        return self._transform(data)

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform method - override base class to handle DataFrame input

        Args:
            data: DataFrame containing the baseline date and difference values

        Returns:
            DataFrame with dates calculated from differences
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        return self._inverse_transform(data)

    # In EncoderDateDiff
    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit method adapted for Processor architecture

        Args:
            data: DataFrame containing the date columns
        """
        # Verify columns exist
        if self.baseline_date not in data.columns:
            raise ValueError(
                f"Baseline date column '{self.baseline_date}' not found in data"
            )

        for col in self.related_date_list:
            if col not in data.columns:
                raise ValueError(f"Related date column '{col}' not found in data")

        # Store original data types
        self._original_dtypes = {
            col: data[col].dtype
            for col in [self.baseline_date] + self.related_date_list
            if col in data.columns  # Add safety check
        }

        # Set labels to empty list for MediatorEncoder compatibility
        # EncoderDateDiff doesn't use labels since it's not a categorical encoder
        self.labels = []

        # Mark as fitted
        self.is_fitted = True

    def _transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform date columns to difference values.

        Args:
            X: DataFrame containing the date columns

        Returns:
            DataFrame with date differences
        """
        if not self.is_fitted:
            self._fit(X)

        result = X.copy()

        # Ensure baseline date is datetime
        if not pd.api.types.is_datetime64_any_dtype(result[self.baseline_date]):
            result[self.baseline_date] = pd.to_datetime(
                result[self.baseline_date], errors="coerce"
            )

        # Calculate differences for each related date
        for col in self.related_date_list:
            # Ensure current date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(result[col]):
                result[col] = pd.to_datetime(result[col], errors="coerce")

            # Calculate difference
            # Capture loop variable to avoid B023
            def calc_diff(row, column=col):
                return self._calc_date_diff(row[self.baseline_date], row[column])

            result[col] = result.apply(calc_diff, axis=1)

        return result

    def _inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform difference values back to date columns.

        Args:
            X: DataFrame containing the baseline date and difference values

        Returns:
            DataFrame with dates calculated from differences
        """
        if not self.is_fitted:
            raise ValueError("Encoder has not been fitted yet")

        result = X.copy()

        # Ensure baseline date is datetime
        if not pd.api.types.is_datetime64_any_dtype(result[self.baseline_date]):
            result[self.baseline_date] = pd.to_datetime(
                result[self.baseline_date], errors="coerce"
            )

        # Calculate dates from differences
        for col in self.related_date_list:
            if col in result.columns:
                # Calculate date from difference
                # Capture loop variable to avoid B023
                def calc_date(row, column=col):
                    return self._calc_date_from_diff(
                        row[self.baseline_date], row[column]
                    )

                result[col] = result.apply(calc_date, axis=1)

                # Convert back to original dtype if possible
                if col in self._original_dtypes:
                    try:
                        original_dtype = self._original_dtypes[col]
                        if pd.api.types.is_datetime64_any_dtype(original_dtype):
                            # Already datetime, no need to convert
                            pass
                        elif pd.api.types.is_string_dtype(original_dtype):
                            # Convert to string format
                            result[col] = result[col].dt.strftime("%Y-%m-%d")
                        # Add other dtype conversions if needed
                    except Exception:
                        # If conversion fails, keep as datetime
                        pass

        return result
        return result
