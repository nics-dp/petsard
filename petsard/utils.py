import importlib.util
import inspect
import logging
import os
import sys
from decimal import Decimal
from typing import Any, TypeVar, overload

from petsard.exceptions import ConfigError

# Define generic type variable to maintain input/output type consistency / 定義泛型類型變數，保持輸入輸出類型一致
T = TypeVar("T", int, float, Decimal, None)


@overload
def safe_round(value: None, decimals: int = 2) -> None: ...
@overload
def safe_round(value: int, decimals: int = 2) -> int: ...
@overload
def safe_round(value: float, decimals: int = 2) -> float: ...
@overload
def safe_round(value: Decimal, decimals: int = 2) -> Decimal: ...


def safe_round(
    value: int | float | Decimal | None, decimals: int = 2
) -> int | float | Decimal | None:
    """
    Safe rounding function that maintains input/output type consistency
    安全的四捨五入函數，保持輸入輸出類型一致

    Args:
        value: Value to round (int, float, Decimal or None) / 要四捨五入的值（int, float, Decimal 或 None）
        decimals: Number of decimal places (default: 2) / 小數位數（預設為 2）

    Returns:
        Rounded value maintaining original type / 四捨五入後的值，保持原始類型
        - int input returns original value (no rounding) / int 輸入直接返回原值（不進行四捨五入）
        - float input returns float / float 輸入返回 float
        - Decimal input returns Decimal / Decimal 輸入返回 Decimal
        - None input returns None / None 輸入返回 None
    """
    if value is None:
        return None

    # int type returns directly without rounding / int 類型直接返回，不需要四捨五入
    if isinstance(value, int):
        return value

    # float type / float 類型
    if isinstance(value, float):
        return round(value, decimals)

    # Decimal type / Decimal 類型
    if isinstance(value, Decimal):
        # Decimal.quantize needs a Decimal as precision reference / Decimal 的 quantize 需要一個 Decimal 作為精度參考
        if decimals == 0:
            return round(value, 0)  # Return Decimal integer / 返回 Decimal 整數
        else:
            # Create precision template, e.g., 0.01 for 2 decimal places / 建立精度模板，例如 0.01 代表保留 2 位小數
            precision = Decimal(10) ** -decimals
            return value.quantize(precision)

    # Should not reach here, but for type checker / 不應該到達這裡，但為了類型檢查器
    raise TypeError(f"Unsupported type for safe_round: {type(value)}")


def _resolve_module_path(
    module_path: str, logger: logging.Logger, search_paths: list[str] = None
) -> str:
    """
    Resolve module path by trying multiple search locations.

    Args:
        module_path (str): The module path to resolve
        logger (logging.Logger): Logger for recording messages
        search_paths (List[str], optional): Additional search paths to try

    Returns:
        str: The resolved absolute path to the module

    Raises:
        FileNotFoundError: If the module cannot be found in any search location
    """
    # If it's already an absolute path and exists, return it
    if os.path.isabs(module_path) and os.path.isfile(module_path):
        logger.debug(f"Using absolute path: {module_path}")
        return module_path

    # Get the current working directory
    cwd = os.getcwd()

    # Default search locations
    default_search_paths = [
        # 1. Direct path as provided
        module_path,
        # 2. Current working directory
        os.path.join(cwd, module_path),
    ]

    # Combine default and additional search paths
    all_search_paths = default_search_paths[:]
    if search_paths:
        # search_paths may contain directories, so we need to join them with module_path
        for search_dir in search_paths:
            # Skip non-directory paths
            if isinstance(search_dir, str) and os.path.isdir(search_dir):
                # Combine directory with module path
                full_path = os.path.join(search_dir, module_path)
                all_search_paths.append(full_path)
            else:
                # If it's not a directory, add it as is (could be a full path)
                all_search_paths.append(search_dir)

    # Try each search path
    for search_path in all_search_paths:
        abs_path = os.path.abspath(search_path)
        if os.path.isfile(abs_path):
            logger.debug(f"Found module at: {abs_path}")
            return abs_path

    # If not found, provide helpful error message
    searched_locations = "\n".join(
        [f"  - {os.path.abspath(path)}" for path in all_search_paths]
    )
    error_msg = (
        f"Module '{module_path}' not found in any of the following locations:\n"
        f"{searched_locations}"
    )
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)


def load_external_module(
    module_path: str,
    class_name: str,
    logger: logging.Logger,
    required_methods: dict[str, list[str]] = None,
    search_paths: list[str] = None,
) -> tuple[Any, type]:
    """
    Load external Python module and return the module instance and class.

    Args:
        module_path (str): Path to the external module (relative or absolute)
        class_name (str): Name of the class to load from the module
        logger (logging.Logger): Logger for recording messages
        required_methods (Dict[str, List[str]], optional):
            Dictionary mapping method names to required parameter names
            e.g. {"fit": ["data"], "sample": []}
        search_paths (List[str], optional):
            Additional search paths to try when resolving the module path

    Returns:
        Tuple[Any, Type]: A tuple containing the module instance and the class

    Raises:
        FileNotFoundError: If the module file does not exist
        ConfigError: If the module cannot be loaded or doesn't contain the specified class
    """
    # Resolve the module path
    resolved_path = _resolve_module_path(module_path, logger, search_paths)

    # Check if file exists
    if not os.path.isfile(resolved_path):
        error_msg = f"The module file '{resolved_path}' does not exist."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Get module name from file path
    module_name = os.path.splitext(os.path.basename(resolved_path))[0]

    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, resolved_path)
    if spec is None:
        error_msg = f"Failed to create spec for module '{module_name}' from path '{resolved_path}'."
        logger.error(error_msg)
        raise ConfigError(error_msg)

    module = importlib.util.module_from_spec(spec)
    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as e:
        error_msg = f"Error loading module '{module_name}': {str(e)}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e

    # Check if the specified class exists in the module
    if not hasattr(module, class_name):
        error_msg = (
            f"The class '{class_name}' does not exist in module '{module_name}'."
        )
        logger.error(error_msg)
        raise ConfigError(error_msg)

    # Get the class
    cls = getattr(module, class_name)

    logger.info(
        f"Successfully loaded external module '{module_name}' with class '{class_name}'."
    )

    if required_methods and isinstance(required_methods, dict):
        for method_name, required_params in required_methods.items():
            # Check if the class has the required method
            if not hasattr(cls, method_name):
                error_msg = f"The class '{class_name}' does not have the required method '{method_name}'."
                logger.error(error_msg)
                raise ConfigError(error_msg)

            # Check if the required method is callable
            method = getattr(cls, method_name)
            if not callable(method):
                error_msg = f"The attribute '{method_name}' in class '{cls.__name__}' must be a method."
                logger.error(error_msg)
                raise ConfigError(error_msg)

            # Check method signature if required parameters are specified
            if required_params:
                # Get the signature of the method
                sig = inspect.signature(method)
                method_params = list(sig.parameters.keys())

                # For instance methods, the first parameter is 'self', so we skip it
                if method_params and method_params[0] == "self":
                    method_params = method_params[1:]

                # Check if all required parameters exist in the method signature
                for param in required_params:
                    if param not in method_params:
                        error_msg = f"The method '{method_name}' in class '{cls.__name__}' must accept parameter '{param}'."
                        logger.error(error_msg)
                        raise ConfigError(error_msg)

    return module, cls
