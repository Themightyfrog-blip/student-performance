"""File upload, inspection, and parsing module.
Handles CSV and Excel file formats with robust encoding detection,
schema inspection, and safe data previewing.
"""
import io
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union


class FileLoader:
    """Robust loader for academic datasets supporting CSV and Excel."""

    SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls"]

    @staticmethod
    def load_file(file_obj: Union[str, Path, io.BytesIO, Any], filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Load a CSV or Excel file safely.
        
        Returns:
            Tuple of (DataFrame, error_message). DataFrame is None if an error occurred.
        """
        ext = Path(filename).suffix.lower()
        if ext not in FileLoader.SUPPORTED_EXTENSIONS:
            return None, f"Unsupported file extension '{ext}'. Please upload .csv, .xlsx, or .xls files."

        try:
            if ext == ".csv":
                # Try common encodings
                for encoding in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
                    try:
                        if hasattr(file_obj, "seek"):
                            file_obj.seek(0)
                        df = pd.read_csv(file_obj, encoding=encoding)
                        if df.empty:
                            return None, f"File '{filename}' is empty."
                        return df, None
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue
                return None, f"Unable to parse '{filename}' with supported encodings (utf-8, latin1, cp1252)."

            elif ext in [".xlsx", ".xls"]:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_excel(file_obj, engine="openpyxl" if ext == ".xlsx" else None)
                if df.empty:
                    return None, f"File '{filename}' contains no rows."
                return df, None

        except Exception as e:
            return None, f"Error reading '{filename}': {str(e)}"

        return None, "Unknown loading failure."

    @staticmethod
    def get_file_metadata(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Compute structural metadata for an uploaded dataset."""
        return {
            "filename": filename,
            "row_count": int(len(df)),
            "col_count": int(df.shape[1]),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_counts": {col: int(df[col].isna().sum()) for col in df.columns},
            "sample_head": df.head(5).to_dict(orient="records")
        }
