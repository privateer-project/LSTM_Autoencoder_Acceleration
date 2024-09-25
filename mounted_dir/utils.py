import numpy as np
from typing import Any, Dict, Type, List

def get_average_difference(input_vector: np.ndarray, output_vector: np.ndarray) -> float:
    return sum(abs(input_vector - output_vector))/len(input_vector)

def convert_types(c_type: Type) -> Type[np.generic]:
    """
    Converts a Python type to the corresponding NumPy type used for buffer allocation on the FPGA.

    Args:
        c_type (Type): The Python data type to convert (e.g., int, float).

    Returns:
        Type[np.generic]: The corresponding NumPy data type (e.g., np.int32, np.float32).

    Raises:
        ValueError: If the provided type is not supported for conversion.
    """
    if c_type is int:
        return np.int32
    if c_type is float:
        return np.float32
    raise ValueError(f"Unsupported type: {c_type}")