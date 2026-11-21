"""Tests for Apriori, Multi-Level, and Constraint-Based Association Mining."""
import pytest
import pandas as pd
from database.warehouse import DataWarehouse
from src.etl import AcademicETLPipeline
from src.association_mining import AcademicAssociationMiner


@pytest.fixture
def populated_mining_engine(tmp_path):
    db_file = tmp_path / "test_mining_wh.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)

    # Construct deterministic transaction dataset
    # Pattern: Students with low attendance (<75%) frequently fail and have high backlogs
    rows = []
    # 20 students with Low Attendance, Fail, High Backlogs
    for i in range(1, 21):
        rows.append({
            "student_id": f"S_LOW_{i}", "student_name": f"Student L{i}", "department": "Computer Science",
            "subject_id": "CS101", "subject_name": "Data Structures", "credits": 4.0, "semester": 3,
            "marks_obtained": 30.0, "attendance_pct": 55.0, "internal_marks": 15.0, "backlog_count": 3
        })
    # 20 students with High Attendance, Pass, Zero Backlogs
    for i in range(1, 21):
        rows.append({
            "student_id": f"S_HIGH_{i}", "student_name": f"Student H{i}", "department": "Electronics",
            "subject_id": "EC101", "subject_name": "Circuits", "credits": 4.0, "semester": 3,
            "marks_obtained": 85.0, "attendance_pct": 92.0, "internal_marks": 45.0, "backlog_count": 0
        })

    pipeline = AcademicETLPipeline(wh)
    pipeline.run(pd.DataFrame(rows))
    return AcademicAssociationMiner(wh)


def test_apriori_frequent_itemsets_and_rules(populated_mining_engine):
    res = populated_mining_engine.run_apriori_backlog_mining(min_support=0.1, min_confidence=0.5)
    assert res["error"] is None
    assert not res["itemsets"].empty
    assert not res["rules"].empty

    # Verify that Low_Attendance => Failed_Subject or Backlog_High => Failed_Subject was found
    rule_strings = res["rules"]["rule_representation"].tolist()
    has_low_att_rule = any("Low_Attendance" in r and "Failed_Subject" in r for r in rule_strings)
    assert has_low_att_rule


def test_constraint_based_mining_q65(populated_mining_engine):
    # Restrict to attendance < 75%
    res = populated_mining_engine.run_constraint_mining(
        attendance_threshold=75.0,
        min_support=0.2,
        min_confidence=0.6
    )
    assert res["error"] is None
    assert res["eligible_records"] == 20
    assert res["total_records_full"] == 40
    assert res["subset_percentage"] == 50.0

    rules = res["rules"]
    assert not rules.empty
    # Verify conditional support is computed and distinct from global support
    first_rule = rules.iloc[0]
    assert first_rule["conditional_support_pct"] > first_rule["global_support_pct"]


def test_multilevel_concept_hierarchy_mining(populated_mining_engine):
    res = populated_mining_engine.run_multilevel_mining(
        min_support_lvl1=0.1,
        min_confidence_lvl1=0.5,
        min_support_lvl2=0.1,
        min_confidence_lvl2=0.5
    )
    assert res["level1"]["error"] is None
    assert res["level2"]["error"] is None
    assert not res["level1"]["rules"].empty
    assert not res["level2"]["rules"].empty
