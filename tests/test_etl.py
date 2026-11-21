"""Tests for the 3-Stage ETL Pipeline, column mapping, and data validation."""
import pytest
import pandas as pd
import numpy as np
from database.warehouse import DataWarehouse
from src.etl import AcademicETLPipeline
from src.mapping import ColumnMapper
from src.validation import DataQualityValidator
from src.upload import FileLoader


@pytest.fixture
def temp_wh(tmp_path):
    db_file = tmp_path / "test_etl_wh.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)
    return wh


def test_column_mapping_inference():
    raw_columns = ["Roll_No", "Course_Code", "Final_Marks", "Attendance_Pct", "Dept_Name", "Sem"]
    mappings = ColumnMapper.infer_mappings(raw_columns)
    assert mappings["student_id"] == "Roll_No"
    assert mappings["subject_id"] == "Course_Code"
    assert mappings["marks_obtained"] == "Final_Marks"
    assert mappings["attendance_pct"] == "Attendance_Pct"
    assert mappings["department"] == "Dept_Name"
    assert mappings["semester"] == "Sem"


def test_data_quality_validator_detects_anomalies():
    dirty_data = pd.DataFrame([
        {"student_id": "S1", "subject_id": "C1", "semester": 1, "marks_obtained": 80.0, "attendance_pct": 85.0},
        {"student_id": "S1", "subject_id": "C1", "semester": 1, "marks_obtained": 80.0, "attendance_pct": 85.0},  # Exact Duplicate
        {"student_id": "S2", "subject_id": "C1", "semester": 1, "marks_obtained": -10.0, "attendance_pct": 70.0}, # Out of bounds
        {"student_id": "S3", "subject_id": "C1", "semester": 1, "marks_obtained": np.nan, "attendance_pct": 115.0}, # Missing mark & bad att
    ])

    report = DataQualityValidator.audit_dataset(dirty_data)
    assert report["metrics"]["duplicate_rows"] == 1
    assert report["metrics"]["out_of_range_marks_count"] == 1
    assert report["metrics"]["missing_marks_count"] == 1
    assert report["metrics"]["invalid_attendance_count"] == 1
    assert report["quality_score"] < 100.0


def test_etl_imputation_and_bounds_cleaning(temp_wh):
    raw_df = pd.DataFrame([
        {"student_id": "S01", "subject_id": "MATH1", "semester": 1, "department": "Science", "marks_obtained": 60.0, "attendance_pct": 80.0},
        {"student_id": "S02", "subject_id": "MATH1", "semester": 1, "department": "Science", "marks_obtained": 80.0, "attendance_pct": 90.0},
        {"student_id": "S03", "subject_id": "MATH1", "semester": 1, "department": "Science", "marks_obtained": np.nan, "attendance_pct": 75.0}, # Needs impute
        {"student_id": "S04", "subject_id": "MATH1", "semester": 1, "department": "Science", "marks_obtained": 120.0, "attendance_pct": 110.0}, # Needs bounds clean
    ])

    pipeline = AcademicETLPipeline(temp_wh)
    transformed_df, summary = pipeline.run(
        raw_df,
        missing_marks_strategy="impute_subject_mean",
        clean_out_of_bounds=True
    )

    # Imputed mark should equal mean of S01 and S02 (60+80)/2 = 70.0 (or including capped 100)
    imputed_row = transformed_df[transformed_df["student_id"] == "S03"].iloc[0]
    assert imputed_row["is_imputed"] == 1
    assert pd.notna(imputed_row["marks_obtained"])

    # Out of bounds check: 120 clipped to 100, 110% clipped to 100%
    capped_row = transformed_df[transformed_df["student_id"] == "S04"].iloc[0]
    assert capped_row["marks_obtained"] == 100.0
    assert capped_row["attendance_percentage"] == 100.0

    # Verify warehouse load counts
    counts = temp_wh.get_table_counts()
    assert counts["FactExamResult"] == 4
    assert counts["FactAttendance"] == 4
    assert counts["DimStudent"] == 4


def test_enrich_attendance_with_academics(temp_wh):
    """Verify that attendance-only records (like user uploaded attendance.csv)
    are successfully enriched with correlated academic marks and loaded into star schema."""
    from src.etl import enrich_attendance_with_academics

    user_att_df = pd.DataFrame({
        "student_id": ["STU0001", "STU0001", "STU0002", "STU0002"],
        "subject_id": ["CS101", "CS102", "EC201", "EC202"],
        "semester_no": [4, 4, 4, 4],
        "classes_held": [40, 50, 45, 60],
        "classes_attended": [35, 45, 30, 50],
        "attendance_percentage": [87.5, 90.0, 66.7, 83.3]
    })

    enriched = enrich_attendance_with_academics(user_att_df, seed=42)
    assert "marks_obtained" in enriched.columns
    assert "internal_marks" in enriched.columns
    assert "department" in enriched.columns
    assert len(enriched) == 4

    # Run through ETL pipeline
    pipeline = AcademicETLPipeline(temp_wh)
    clean_df, summary = pipeline.run(enriched)

    assert summary.status == "Completed Successfully"
    assert summary.loaded_exam_facts == 4
    assert summary.loaded_attendance_facts == 4

    # Verify integrated view
    df_int = temp_wh.get_integrated_dataset()
    assert not df_int.empty
    assert "Grade" in df_int.columns
    assert "ResultStatus" in df_int.columns
    assert set(df_int["Department"].dropna()) == {"Computer Science & Engineering", "Electronics & Communication"}

