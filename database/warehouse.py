"""Database management and SQLite warehouse connection layer.
Provides schema initialization, transactional execution, and audit logging.
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime

from config.settings import DEFAULT_DB_PATH, DATABASE_DIR

class DataWarehouse:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_initialized()

    def ensure_initialized(self) -> None:
        """Check if tables exist, and initialize if missing."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DimDepartment';")
                if not cursor.fetchone():
                    self.init_database(force=False)
        except Exception:
            pass

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with foreign keys enabled."""
        self.ensure_initialized()
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self, force: bool = False) -> None:
        """Initialize the star schema tables.
        
        If force=True, drops existing tables before re-creating.
        """
        schema_file = DATABASE_DIR / "schema.sql"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema definition file not found at {schema_file}")

        with schema_file.open("r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if force:
                # Drop in dependency order
                cursor.execute("DROP TABLE IF EXISTS ETLAuditLog;")
                cursor.execute("DROP TABLE IF EXISTS FactAttendance;")
                cursor.execute("DROP TABLE IF EXISTS FactExamResult;")
                cursor.execute("DROP TABLE IF EXISTS DimStudent;")
                cursor.execute("DROP TABLE IF EXISTS DimSubject;")
                cursor.execute("DROP TABLE IF EXISTS DimSemester;")
                cursor.execute("DROP TABLE IF EXISTS DimDepartment;")
                cursor.execute("DROP TABLE IF EXISTS DimDate;")

            cursor.executescript(schema_sql)

            # Ensure default 'Unknown Date' record exists in DimDate
            cursor.execute("""
                INSERT OR IGNORE INTO DimDate (DateKey, FullDate, Day, Month, Quarter, Year, IsWeekend)
                VALUES (-1, 'Unknown Date', 0, 0, 0, 0, 0);
            """)
            conn.commit()

    def reset_database(self) -> None:
        """Drop all tables and reinitialize empty schema."""
        self.init_database(force=True)

    def log_etl_event(self, batch_id: str, stage: str, action: str, records_affected: int = 0, details: str = "") -> None:
        """Record an event into the ETLAuditLog table."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO ETLAuditLog (BatchId, Stage, Action, RecordsAffected, Details)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (batch_id, stage, action, records_affected, details)
                )
                conn.commit()
        except Exception:
            pass  # Avoid masking main ETL exceptions if logging fails

    def get_audit_logs(self, limit: int = 100) -> pd.DataFrame:
        """Retrieve recent ETL audit logs."""
        query = "SELECT LogId, BatchId, Timestamp, Stage, Action, RecordsAffected, Details FROM ETLAuditLog ORDER BY LogId DESC LIMIT ?;"
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all warehouse tables."""
        tables = [
            "DimDepartment", "DimDate", "DimSemester", "DimSubject",
            "DimStudent", "FactExamResult", "FactAttendance", "ETLAuditLog"
        ]
        counts = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    counts[table] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    counts[table] = 0
        return counts

    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        """Execute a parameterized SQL query and return a pandas DataFrame."""
        with self.get_connection() as conn:
            if params:
                return pd.read_sql_query(query, conn, params=params)
            return pd.read_sql_query(query, conn)

    def get_integrated_dataset(self) -> pd.DataFrame:
        """Fetch denormalized integrated dataset joining facts and dimensions for analysis.
        Ensures consistent grain and zero duplication.
        Supports both marks-based and attendance-based ingestion.
        """
        counts = self.get_table_counts()
        has_exams = counts.get("FactExamResult", 0) > 0
        has_att = counts.get("FactAttendance", 0) > 0

        if has_exams:
            sql = """
            SELECT 
                s.StudentID,
                s.StudentName,
                d.DepartmentName AS Department,
                s.Program,
                s.BacklogCount,
                s.PreviousGPA,
                sub.SubjectID,
                sub.SubjectName,
                sub.Credits,
                sem.SemesterNumber AS Semester,
                sem.AcademicYear,
                fer.InternalMarks,
                fer.MarksObtained,
                fer.MaximumMarks,
                fer.GradePoints,
                fer.Grade,
                fer.ResultStatus,
                fa.ClassesHeld,
                fa.ClassesAttended,
                fa.AttendancePercentage,
                fa.AttendanceCategory
            FROM FactExamResult fer
            JOIN DimStudent s ON fer.StudentKey = s.StudentKey
            JOIN DimDepartment d ON fer.DepartmentKey = d.DepartmentKey
            JOIN DimSubject sub ON fer.SubjectKey = sub.SubjectKey
            JOIN DimSemester sem ON fer.SemesterKey = sem.SemesterKey
            LEFT JOIN FactAttendance fa ON (
                fa.StudentKey = fer.StudentKey 
                AND fa.SubjectKey = fer.SubjectKey 
                AND fa.SemesterKey = fer.SemesterKey
            );
            """
            return self.execute_query(sql)
        elif has_att:
            sql = """
            SELECT 
                s.StudentID,
                s.StudentName,
                d.DepartmentName AS Department,
                s.Program,
                s.BacklogCount,
                s.PreviousGPA,
                sub.SubjectID,
                sub.SubjectName,
                sub.Credits,
                sem.SemesterNumber AS Semester,
                sem.AcademicYear,
                NULL AS InternalMarks,
                NULL AS MarksObtained,
                100.0 AS MaximumMarks,
                NULL AS GradePoints,
                NULL AS Grade,
                NULL AS ResultStatus,
                fa.ClassesHeld,
                fa.ClassesAttended,
                fa.AttendancePercentage,
                fa.AttendanceCategory
            FROM FactAttendance fa
            JOIN DimStudent s ON fa.StudentKey = s.StudentKey
            JOIN DimDepartment d ON fa.DepartmentKey = d.DepartmentKey
            JOIN DimSubject sub ON fa.SubjectKey = sub.SubjectKey
            JOIN DimSemester sem ON fa.SemesterKey = sem.SemesterKey;
            """
            return self.execute_query(sql)
        return pd.DataFrame()


# Global singleton instance for convenient access across pages
warehouse = DataWarehouse()
