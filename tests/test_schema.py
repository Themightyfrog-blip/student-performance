"""Tests for Star Schema initialization, surrogate keys, and integrity constraints."""
import pytest
import sqlite3
import pandas as pd
from database.warehouse import DataWarehouse


@pytest.fixture
def temp_warehouse(tmp_path):
    db_file = tmp_path / "test_warehouse.db"
    wh = DataWarehouse(db_file)
    wh.init_database(force=True)
    return wh


def test_schema_tables_exist(temp_warehouse):
    counts = temp_warehouse.get_table_counts()
    assert "DimStudent" in counts
    assert "DimSubject" in counts
    assert "DimDepartment" in counts
    assert "DimSemester" in counts
    assert "DimDate" in counts
    assert "FactExamResult" in counts
    assert "FactAttendance" in counts
    assert "ETLAuditLog" in counts
    # DimDate should have the default -1 Unknown Date record
    assert counts["DimDate"] == 1


def test_fact_table_grain_uniqueness_constraint(temp_warehouse):
    conn = temp_warehouse.get_connection()
    cursor = conn.cursor()

    # Insert prerequisite dimension records
    cursor.execute("INSERT INTO DimDepartment (DepartmentName) VALUES ('Computer Science');")
    dept_key = cursor.lastrowid

    cursor.execute("INSERT INTO DimSemester (SemesterNumber, AcademicYear) VALUES (3, '2024-2025');")
    sem_key = cursor.lastrowid

    cursor.execute("INSERT INTO DimSubject (SubjectID, SubjectName, Credits, DepartmentKey) VALUES ('CS101', 'Data Structures', 4.0, ?);", (dept_key,))
    sub_key = cursor.lastrowid

    cursor.execute("INSERT INTO DimStudent (StudentID, StudentName, DepartmentKey) VALUES ('STU001', 'Alice', ?);", (dept_key,))
    stu_key = cursor.lastrowid

    # Insert first fact record
    cursor.execute("""
        INSERT INTO FactExamResult (StudentKey, SubjectKey, SemesterKey, DepartmentKey, MarksObtained, GradePoints, Grade, Credits, ResultStatus)
        VALUES (?, ?, ?, ?, 85.0, 9.0, 'A+', 4.0, 'Pass');
    """, (stu_key, sub_key, sem_key, dept_key))
    conn.commit()

    # Attempt inserting duplicate fact record at identical grain (StudentKey, SubjectKey, SemesterKey)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO FactExamResult (StudentKey, SubjectKey, SemesterKey, DepartmentKey, MarksObtained, GradePoints, Grade, Credits, ResultStatus)
            VALUES (?, ?, ?, ?, 70.0, 8.0, 'A', 4.0, 'Pass');
        """, (stu_key, sub_key, sem_key, dept_key))
        conn.commit()

    conn.close()


def test_audit_logging(temp_warehouse):
    temp_warehouse.log_etl_event("BATCH-TEST-01", "Extract", "Ingested Files", 150, "Test details")
    logs = temp_warehouse.get_audit_logs()
    assert len(logs) == 1
    assert logs.iloc[0]["BatchId"] == "BATCH-TEST-01"
    assert logs.iloc[0]["RecordsAffected"] == 150
