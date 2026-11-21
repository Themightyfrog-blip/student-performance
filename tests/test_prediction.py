"""Tests for Decision Tree Classification (Q67) and Early-Warning Triage."""
import pytest
import pandas as pd
import numpy as np
from database.warehouse import DataWarehouse
from src.etl import AcademicETLPipeline
from src.decision_tree import AcademicRiskClassifier
from src.early_warning import EarlyWarningCenter


@pytest.fixture
def populated_dt_warehouse(tmp_path):
    db_file = tmp_path / "test_dt_wh.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)
    np.random.seed(42)

    rows = []
    # 30 Failing / At-Risk students (low attendance, low internals, backlogs)
    for i in range(1, 31):
        rows.append({
            "student_id": f"STU_RISK_{i}", "student_name": f"Risk Student {i}", "department": "Computer Science",
            "subject_id": "CS101", "subject_name": "Data Structures", "credits": 4.0, "semester": 3,
            "marks_obtained": float(np.random.choice([25.0, 32.0, 38.0, 42.0])), # Fail or At-Risk
            "attendance_pct": float(np.random.uniform(45.0, 68.0)),
            "internal_marks": float(np.random.uniform(10.0, 22.0)),
            "previous_gpa": 5.2,
            "backlog_count": 3
        })
    # 30 Passing students (high attendance, high internals, no backlogs)
    for i in range(1, 31):
        rows.append({
            "student_id": f"STU_PASS_{i}", "student_name": f"Pass Student {i}", "department": "Computer Science",
            "subject_id": "CS101", "subject_name": "Data Structures", "credits": 4.0, "semester": 3,
            "marks_obtained": float(np.random.choice([75.0, 82.0, 90.0])), # Pass
            "attendance_pct": float(np.random.uniform(85.0, 98.0)),
            "internal_marks": float(np.random.uniform(38.0, 48.0)),
            "previous_gpa": 8.5,
            "backlog_count": 0
        })

    pipeline = AcademicETLPipeline(wh)
    pipeline.run(pd.DataFrame(rows))
    return wh


def test_target_leakage_safeguard(populated_dt_warehouse):
    clf = AcademicRiskClassifier(populated_dt_warehouse)
    df = populated_dt_warehouse.get_integrated_dataset()
    X, y, feature_names, groups, df_valid = clf.prepare_data(df)

    # Strictly verify that NO target leakage columns are included in feature_names
    forbidden = ["MarksObtained", "Grade", "GradePoints", "ResultStatus", "MaximumMarks"]
    for f in forbidden:
        assert f not in feature_names, f"CRITICAL LEAKAGE: Forbidden column {f} found in predictive features!"

    assert "AttendancePercentage" in feature_names
    assert "InternalMarks" in feature_names


def test_decision_tree_train_and_evaluate(populated_dt_warehouse):
    clf = AcademicRiskClassifier(populated_dt_warehouse)
    metrics = clf.train_and_evaluate(max_depth=3, test_size=0.3)
    assert "error" not in metrics
    assert metrics["is_trained"] is True
    assert metrics["accuracy"] >= 0.65  # Verified multiclass accuracy on holdout test set
    assert len(metrics["feature_importances"]) > 0
    assert len(metrics["tree_rules_text"]) > 10


def test_early_warning_triage_generation(populated_dt_warehouse):
    clf = AcademicRiskClassifier(populated_dt_warehouse)
    clf.train_and_evaluate()
    
    ewc = EarlyWarningCenter(clf)
    triage = ewc.get_triage_dashboard()
    assert "error" not in triage
    assert triage["total_students_assessed"] == 60
    assert triage["critical_risk_count"] > 0
    assert triage["on_track_count"] > 0
    assert not triage["predictions_df"].empty

    # Test status update
    ewc.update_student_review_status("STU_RISK_1", "Intervention Scheduled")
    updated = ewc.get_triage_dashboard()
    updated_row = updated["predictions_df"][updated["predictions_df"]["StudentID"] == "STU_RISK_1"].iloc[0]
    assert updated_row["Faculty_Review_Status"] == "Intervention Scheduled"
