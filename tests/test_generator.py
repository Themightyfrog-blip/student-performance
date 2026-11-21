"""Tests for Synthetic Data Generator and Report Export Anonymization."""
import pytest
import pandas as pd
from src.data_generator import AcademicDataGenerator
from src.reporting import ProjectReportGenerator


def test_synthetic_data_generator_generation():
    gen = AcademicDataGenerator(seed=123)
    data = gen.generate_dataset(num_students=30, semesters=[3, 4])
    
    assert "students" in data
    assert "subjects" in data
    assert "exam_results" in data
    assert "attendance" in data
    assert "combined" in data

    assert len(data["students"]) == 30
    assert not data["exam_results"].empty
    assert not data["attendance"].empty
    assert not data["combined"].empty


def test_noisy_dataset_generation():
    gen = AcademicDataGenerator(seed=123)
    data = gen.generate_dataset(num_students=20)
    noisy = gen.generate_noisy_test_dataset(data["combined"])
    
    # Must contain missing values and duplicates
    assert noisy["marks_obtained"].isna().sum() > 0
    assert noisy.duplicated().sum() > 0


def test_privacy_anonymization_in_reports():
    df = pd.DataFrame([
        {"StudentID": "STU101", "StudentName": "Aditi Sharma", "MarksObtained": 85.0},
        {"StudentID": "STU102", "StudentName": "Rahul Verma", "MarksObtained": 90.0}
    ])
    anon_df = ProjectReportGenerator.anonymize_student_identifiers(df, id_col="StudentID")
    
    assert "STU101" not in anon_df["StudentID"].values
    assert "Aditi Sharma" not in anon_df["StudentName"].values
    assert anon_df.iloc[0]["StudentID"].startswith("ANON-")
