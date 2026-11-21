"""Source package for DWDM Student Performance Data Warehouse."""
import sys
from pathlib import Path

# Ensure root workspace directory is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.etl import AcademicETLPipeline, ETLSummary, enrich_attendance_with_academics
