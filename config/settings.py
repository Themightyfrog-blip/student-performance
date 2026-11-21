"""Configuration settings and domain constants for the Student Performance Data Warehouse.
"""
from pathlib import Path
from typing import Dict, List, Any

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = BASE_DIR / "database"
DEFAULT_DB_PATH = DATABASE_DIR / "warehouse.db"

# Ensure directories exist
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Canonical Academic Schema Fields & Common Aliases
CANONICAL_COLUMNS: Dict[str, Dict[str, Any]] = {
    "student_id": {
        "label": "Student Identifier",
        "required": True,
        "type": "string",
        "aliases": ["studentid", "student_id", "roll_no", "roll_number", "rollno", "enrollment_no", "usn", "reg_no", "regno"]
    },
    "student_name": {
        "label": "Student Name",
        "required": False,
        "type": "string",
        "aliases": ["studentname", "student_name", "name", "full_name", "candidate_name"]
    },
    "department": {
        "label": "Department / Branch",
        "required": True,
        "type": "string",
        "aliases": ["department", "department_name", "dept", "dept_name", "branch", "stream"]
    },
    "program": {
        "label": "Degree / Program",
        "required": False,
        "type": "string",
        "aliases": ["program", "degree", "course", "program_name", "study_program"]
    },
    "subject_id": {
        "label": "Subject Code / ID",
        "required": True,
        "type": "string",
        "aliases": ["subject_id", "subjectid", "subject_code", "course_code", "sub_code", "subcode"]
    },
    "subject_name": {
        "label": "Subject Name",
        "required": False,
        "type": "string",
        "aliases": ["subject", "subject_name", "course_name", "sub_name", "title"]
    },
    "credits": {
        "label": "Subject Credits",
        "required": False,
        "type": "numeric",
        "default": 3.0,
        "aliases": ["credits", "credit_hours", "subject_credits", "cred", "cr"]
    },
    "semester": {
        "label": "Semester / Term",
        "required": True,
        "type": "numeric",
        "aliases": ["semester", "semester_no", "term", "sem", "sem_no"]
    },
    "academic_year": {
        "label": "Academic Year",
        "required": False,
        "type": "string",
        "default": "2024-2025",
        "aliases": ["academic_year", "acad_year", "year", "session", "batch"]
    },
    "internal_marks": {
        "label": "Internal Assessment Marks",
        "required": False,
        "type": "numeric",
        "aliases": ["internal_marks", "internal_assessment", "cie", "internals", "ia_marks", "midterm_score", "internal_score"]
    },
    "marks_obtained": {
        "label": "Final Exam Marks Obtained",
        "required": True,
        "type": "numeric",
        "aliases": ["marks", "marks_obtained", "final_marks", "score", "total_marks", "see_marks", "exam_score"]
    },
    "max_marks": {
        "label": "Maximum Marks",
        "required": False,
        "type": "numeric",
        "default": 100.0,
        "aliases": ["max_marks", "maximum_marks", "out_of", "total_max"]
    },
    "attendance_pct": {
        "label": "Attendance Percentage (%)",
        "required": False,
        "type": "numeric",
        "aliases": ["attendance", "attendance_percentage", "attendance_pct", "attendance_rate", "att_pct"]
    },
    "classes_held": {
        "label": "Classes Held (Conducted)",
        "required": False,
        "type": "numeric",
        "aliases": ["classes_held", "total_classes", "sessions_conducted", "lectures_held"]
    },
    "classes_attended": {
        "label": "Classes Attended",
        "required": False,
        "type": "numeric",
        "aliases": ["classes_attended", "attended_classes", "sessions_attended", "lectures_attended"]
    },
    "backlog_count": {
        "label": "Previous Backlogs / Failures",
        "required": False,
        "type": "numeric",
        "default": 0,
        "aliases": ["backlogs", "backlog_count", "previous_failures", "arrears", "active_backlogs"]
    },
    "previous_gpa": {
        "label": "Previous Semester GPA",
        "required": False,
        "type": "numeric",
        "aliases": ["previous_gpa", "prev_gpa", "sgpa", "cgpa", "past_gpa"]
    },
    "exam_date": {
        "label": "Exam / Record Date",
        "required": False,
        "type": "date",
        "aliases": ["exam_date", "date", "assessment_date", "exam_dt"]
    }
}

# Standard 10-point Academic Grading Scale
DEFAULT_GRADING_SCALE = [
    {"min": 90.0, "max": 100.0, "grade": "O", "grade_point": 10.0, "desc": "Outstanding", "status": "Pass"},
    {"min": 80.0, "max": 89.99, "grade": "A+", "grade_point": 9.0, "desc": "Excellent", "status": "Pass"},
    {"min": 70.0, "max": 79.99, "grade": "A", "grade_point": 8.0, "desc": "Very Good", "status": "Pass"},
    {"min": 60.0, "max": 69.99, "grade": "B+", "grade_point": 7.0, "desc": "Good", "status": "Pass"},
    {"min": 50.0, "max": 59.99, "grade": "B", "grade_point": 6.0, "desc": "Above Average", "status": "Pass"},
    {"min": 40.0, "max": 49.99, "grade": "C", "grade_point": 5.0, "desc": "Pass", "status": "Pass"},
    {"min": 0.0, "max": 39.99, "grade": "F", "grade_point": 0.0, "desc": "Fail", "status": "Fail"},
]

DEFAULT_PASS_MARK = 40.0
DEFAULT_MAX_MARKS = 100.0

# Attendance Categorization Constants
ATTENDANCE_CRITICAL_THRESHOLD = 75.0  # Mandatory institutional minimum
ATTENDANCE_EXCELLENT_THRESHOLD = 85.0

# PBL Rubric & Question Mapping
PBL_RUBRIC_MAPPING = {
    "Schema and ETL (20%)": [
        {"q": "Q61", "title": "Star Schema Architecture & Fact/Dimension Granularity", "module": "database/warehouse.py"},
        {"q": "Q62", "title": "Data Warehouse Storage & Surrogate Key Constraints", "module": "src/star_schema.py"},
        {"q": "Q63", "title": "Flexible Ingestion & Data Quality Auditing", "module": "src/validation.py"},
        {"q": "Q64", "title": "Configurable 3-Stage ETL Pipeline & Referential Integrity", "module": "src/etl.py"}
    ],
    "Multi-Level Association Rules (25%)": [
        {"q": "Q65", "title": "Constraint-Based Association Mining (< 75% Attendance)", "module": "src/association_mining.py"},
        {"q": "Q66", "title": "Apriori Performance & Backlog Association Mining", "module": "src/association_mining.py"},
        {"q": "Q69_assoc", "title": "Hierarchical Multi-Level Mining (Dept->Result, Subject->Grade)", "module": "src/association_mining.py"}
    ],
    "Decision Tree Classification (25%)": [
        {"q": "Q67", "title": "Academic Risk Classifier & Target-Leakage Prevention", "module": "src/decision_tree.py"},
        {"q": "Q70", "title": "AI Early-Warning Decision Support & Intervention Alerts", "module": "src/early_warning.py"}
    ],
    "OLAP Operations and Correlation (30%)": [
        {"q": "Q68", "title": "Pearson & Spearman Correlation Analysis (Attendance vs Performance)", "module": "src/correlation.py"},
        {"q": "Q69_olap", "title": "OLAP Operations (Cube, Roll-up, Drill-down, Slice, Dice, Credit-Weighted GPA)", "module": "src/olap.py"}
    ]
}
