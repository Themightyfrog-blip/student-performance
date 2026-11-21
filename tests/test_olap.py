"""Tests for OLAP Data Cube, Roll-up, Drill-down, Slice, Dice, and Credit-Weighted GPA."""
import pytest
import pandas as pd
from database.warehouse import DataWarehouse
from src.etl import AcademicETLPipeline
from src.olap import OLAPEngine


@pytest.fixture
def populated_olap_engine(tmp_path):
    db_file = tmp_path / "test_olap_wh.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)

    # Deterministic test dataset with known mathematical outcomes:
    # Student S1:
    #   Sub1: Credits=4.0, Marks=85 (Grade=A+, GradePoints=9.0)
    #   Sub2: Credits=2.0, Marks=55 (Grade=B, GradePoints=6.0)
    # Expected weighted GPA for S1 = (9.0*4.0 + 6.0*2.0) / (4.0 + 2.0) = (36 + 12) / 6 = 48 / 6 = 8.00!
    # Unweighted average = (9.0 + 6.0) / 2 = 7.50 (Distinct from weighted GPA!)
    test_data = pd.DataFrame([
        {
            "student_id": "S1", "student_name": "Alice", "department": "Computer Science",
            "subject_id": "CS101", "subject_name": "DS", "credits": 4.0, "semester": 3,
            "marks_obtained": 85.0, "attendance_pct": 90.0, "internal_marks": 40.0
        },
        {
            "student_id": "S1", "student_name": "Alice", "department": "Computer Science",
            "subject_id": "CS102", "subject_name": "DBMS", "credits": 2.0, "semester": 3,
            "marks_obtained": 55.0, "attendance_pct": 80.0, "internal_marks": 30.0
        },
        {
            "student_id": "S2", "student_name": "Bob", "department": "Mechanical",
            "subject_id": "ME101", "subject_name": "Thermo", "credits": 4.0, "semester": 3,
            "marks_obtained": 35.0, "attendance_pct": 60.0, "internal_marks": 15.0 # Fail
        }
    ])

    pipeline = AcademicETLPipeline(wh)
    pipeline.run(test_data)
    return OLAPEngine(wh)


def test_credit_weighted_gpa_calculation(populated_olap_engine):
    cube = populated_olap_engine.build_data_cube(dimensions=["StudentID"])
    s1_row = cube[cube["StudentID"] == "S1"].iloc[0]
    
    # Mathematical proof: (9*4 + 6*2)/6 = 8.00
    assert s1_row["Credit_Weighted_GPA"] == 8.00
    assert s1_row["Pass_Count"] == 2
    assert s1_row["Fail_Count"] == 0
    assert s1_row["Pass_Rate_Pct"] == 100.0


def test_olap_roll_up_department_and_university(populated_olap_engine):
    dept_rollup = populated_olap_engine.roll_up_hierarchy(level="Department")
    assert len(dept_rollup) == 2  # Computer Science & Mechanical

    cs_row = dept_rollup[dept_rollup["Department"] == "Computer Science"].iloc[0]
    assert cs_row["Pass_Rate_Pct"] == 100.0
    assert cs_row["Fail_Rate_Pct"] == 0.0

    mech_row = dept_rollup[dept_rollup["Department"] == "Mechanical"].iloc[0]
    assert mech_row["Pass_Rate_Pct"] == 0.0
    assert mech_row["Fail_Rate_Pct"] == 100.0

    # University roll-up
    uni_rollup = populated_olap_engine.roll_up_hierarchy(level="University")
    assert len(uni_rollup) == 1
    assert uni_rollup.iloc[0]["Total_Exam_Attempts"] == 3


def test_olap_slice_and_dice(populated_olap_engine):
    # Slice cube by department
    sliced = populated_olap_engine.slice_cube(dimension="Department", value="Computer Science")
    assert len(sliced) == 2

    # Dice cube by department & result status
    subset_df, ranking = populated_olap_engine.dice_cube(departments=["Mechanical"], result_status=["Fail"])
    assert len(subset_df) == 1
    assert ranking.iloc[0]["Department"] == "Mechanical"
    assert ranking.iloc[0]["Failure_Rate_Pct"] == 100.0
