"""File input/output layer.

Responsible for reading uploaded Excel/CSV files into pandas DataFrames and
returning lightweight metadata. Kept free of Streamlit so it can be tested
with plain file paths or file-like objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import IO, Union

import pandas as pd

from utils.helpers import human_readable_size

# A source can be a path string or any binary file-like object (e.g. an upload).
FileSource = Union[str, IO[bytes]]

SUPPORTED_EXTENSIONS: tuple[str, ...] = (".xlsx", ".xls", ".csv")


@dataclass(frozen=True)
class FileInfo:
    """Immutable metadata describing a loaded dataset.

    Attributes:
        name: Original file name.
        size_label: Human-readable file size (e.g. ``"2.1 MB"``).
        rows: Number of rows.
        columns: Number of columns.
    """

    name: str
    size_label: str
    rows: int
    columns: int


def _get_extension(filename: str) -> str:
    """Return the lower-cased file extension including the leading dot."""
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot != -1 else ""


def is_supported(filename: str) -> bool:
    """Check whether the file extension is supported.

    Args:
        filename: Name of the file to validate.

    Returns:
        ``True`` if the extension is one of :data:`SUPPORTED_EXTENSIONS`.
    """
    return _get_extension(filename) in SUPPORTED_EXTENSIONS


def read_file(source: FileSource, filename: str) -> pd.DataFrame:
    """Read an Excel or CSV source into a DataFrame.

    Args:
        source: A file path or binary file-like object.
        filename: The original file name, used to detect the format.

    Returns:
        The parsed :class:`pandas.DataFrame`.

    Raises:
        ValueError: If the extension is unsupported or the file is empty.
    """
    extension = _get_extension(filename)
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}."
        )

    if extension == ".csv":
        df = pd.read_csv(source)
    else:
        # openpyxl is the engine for modern .xlsx files.
        df = pd.read_excel(source, engine="openpyxl")

    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    return df


def build_file_info(df: pd.DataFrame, filename: str, size_bytes: int) -> FileInfo:
    """Assemble a :class:`FileInfo` summary from a DataFrame.

    Args:
        df: The loaded DataFrame.
        filename: Original file name.
        size_bytes: Raw file size in bytes.

    Returns:
        A populated :class:`FileInfo` instance.
    """
    return FileInfo(
        name=filename,
        size_label=human_readable_size(size_bytes),
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
    )
