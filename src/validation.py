"""Data validation and quality profiling module.
Identifies anomalies, out-of-range marks, attendance discrepancies,
missing values, duplicate keys, and integrity violations.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


class DataQualityValidator:
    """Performs comprehensive pre-ETL and post-ETL data quality checks."""

    @staticmethod
    def audit_dataset(
        df: pd.DataFrame,
        pass_mark: float = 40.0,
        max_marks: float = 100.0
    ) -> Dict[str, Any]:
        """Audit dataset for quality issues and return structured audit report."""
        total_rows = len(df)
        issues = []
        metrics: Dict[str, Any] = {
            "total_rows": total_rows,
            "duplicate_rows": 0,
            "duplicate_grain_records": 0,
            "missing_marks_count": 0,
            "out_of_range_marks_count": 0,
            "missing_attendance_count": 0,
            "invalid_attendance_count": 0,
            "unmatched_departments": 0,
            "clean_rows": 0
        }

        if total_rows == 0:
            return {"metrics": metrics, "issues": ["Dataset is empty."], "quality_score": 0.0}

        # 1. Exact Duplicate Rows
        exact_dups = df.duplicated().sum()
        metrics["duplicate_rows"] = int(exact_dups)
        if exact_dups > 0:
            issues.append(f"Found {exact_dups} exact duplicate row(s).")

        # 2. Fact Grain Duplicates (student_id, subject_id, semester)
        grain_cols = [c for c in ["student_id", "subject_id", "semester"] if c in df.columns]
        if len(grain_cols) == 3:
            grain_dups = df.duplicated(subset=grain_cols).sum()
            metrics["duplicate_grain_records"] = int(grain_dups)
            if grain_dups > 0:
                issues.append(f"Found {grain_dups} record(s) with duplicate academic grain (same student, subject, semester).")

        # 3. Marks Validation
        if "marks_obtained" in df.columns:
            marks_series = pd.to_numeric(df["marks_obtained"], errors="coerce")
            missing_marks = marks_series.isna().sum()
            metrics["missing_marks_count"] = int(missing_marks)
            if missing_marks > 0:
                issues.append(f"Found {missing_marks} missing / non-numeric exam marks record(s).")

            # Out of bounds (< 0 or > max_marks)
            invalid_marks = ((marks_series < 0) | (marks_series > max_marks)).sum()
            metrics["out_of_range_marks_count"] = int(invalid_marks)
            if invalid_marks > 0:
                issues.append(f"Found {invalid_marks} mark(s) outside valid range [0, {max_marks}].")

        # 4. Attendance Validation
        if "attendance_pct" in df.columns or "attendance_percentage" in df.columns:
            att_col = "attendance_pct" if "attendance_pct" in df.columns else "attendance_percentage"
            att_series = pd.to_numeric(df[att_col], errors="coerce")
            missing_att = att_series.isna().sum()
            metrics["missing_attendance_count"] = int(missing_att)
            if missing_att > 0:
                issues.append(f"Found {missing_att} missing attendance record(s).")

            invalid_att = ((att_series < 0) | (att_series > 100.0)).sum()
            metrics["invalid_attendance_count"] = int(invalid_att)
            if invalid_att > 0:
                issues.append(f"Found {invalid_att} attendance percentage value(s) outside range [0%, 100%].")

        # 5. Attendance Class Counts Consistency (if both classes_held and classes_attended exist)
        if "classes_held" in df.columns and "classes_attended" in df.columns:
            held = pd.to_numeric(df["classes_held"], errors="coerce")
            attended = pd.to_numeric(df["classes_attended"], errors="coerce")
            inconsistent = ((attended > held) & (held > 0)).sum()
            if inconsistent > 0:
                issues.append(f"Found {inconsistent} record(s) where classes attended exceeds classes held.")

        # Compute overall data quality health score (0 - 100%)
        issue_penalty = (
            metrics["duplicate_rows"] * 2 +
            metrics["duplicate_grain_records"] * 5 +
            metrics["out_of_range_marks_count"] * 5 +
            metrics["invalid_attendance_count"] * 5 +
            metrics["missing_marks_count"] * 3
        )
        quality_score = max(0.0, round(100.0 - (issue_penalty / max(1, total_rows)) * 100.0, 1))

        return {
            "metrics": metrics,
            "issues": issues,
            "quality_score": quality_score
        }
