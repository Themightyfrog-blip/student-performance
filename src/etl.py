"""Three-stage ETL Pipeline for Student Performance Data Warehouse.
Extracts source data, performs configurable transformations and audits,
and loads dimensions and fact tables into the SQLite Star Schema.
"""
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from config.settings import (
    DEFAULT_PASS_MARK, DEFAULT_MAX_MARKS, DEFAULT_GRADING_SCALE,
    ATTENDANCE_CRITICAL_THRESHOLD, ATTENDANCE_EXCELLENT_THRESHOLD
)
from database.warehouse import DataWarehouse, warehouse


class ETLSummary:
    """Detailed summary of the ETL execution for auditing and reporting."""
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.initial_rows = 0
        self.transformed_rows = 0
        self.duplicates_removed = 0
        self.invalid_records_cleaned = 0
        self.missing_marks_imputed = 0
        self.missing_marks_dropped = 0
        self.attendance_calculated_count = 0
        self.loaded_students = 0
        self.loaded_subjects = 0
        self.loaded_departments = 0
        self.loaded_semesters = 0
        self.loaded_exam_facts = 0
        self.loaded_attendance_facts = 0
        self.status = "In Progress"
        self.warnings: List[str] = []
        self.audit_events: List[Dict[str, Any]] = []

    def record_event(self, stage: str, action: str, count: int = 0, details: str = ""):
        self.audit_events.append({
            "stage": stage,
            "action": action,
            "records_affected": count,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def complete(self):
        self.end_time = datetime.now()
        self.status = "Completed Successfully"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round((self.end_time - self.start_time).total_seconds(), 2) if self.end_time else 0,
            "initial_rows": self.initial_rows,
            "transformed_rows": self.transformed_rows,
            "duplicates_removed": self.duplicates_removed,
            "invalid_records_cleaned": self.invalid_records_cleaned,
            "missing_marks_imputed": self.missing_marks_imputed,
            "attendance_calculated_count": self.attendance_calculated_count,
            "loaded_students": self.loaded_students,
            "loaded_subjects": self.loaded_subjects,
            "loaded_departments": self.loaded_departments,
            "loaded_semesters": self.loaded_semesters,
            "loaded_exam_facts": self.loaded_exam_facts,
            "loaded_attendance_facts": self.loaded_attendance_facts,
            "warnings_count": len(self.warnings),
            "warnings": self.warnings
        }


class AcademicETLPipeline:
    """Configurable 3-Stage ETL Pipeline for academic warehouse ingestion."""

    def __init__(self, target_warehouse: Optional[DataWarehouse] = None):
        self.warehouse = target_warehouse or warehouse

    def run(
        self,
        raw_df: pd.DataFrame,
        pass_mark: float = DEFAULT_PASS_MARK,
        max_marks: float = DEFAULT_MAX_MARKS,
        grading_scale: List[Dict[str, Any]] = DEFAULT_GRADING_SCALE,
        deduplicate_strategy: str = "drop_grain",  # 'drop_grain', 'drop_exact', 'none'
        missing_marks_strategy: str = "impute_subject_mean",  # 'impute_subject_mean', 'leave_missing', 'drop'
        clean_out_of_bounds: bool = True
    ) -> Tuple[pd.DataFrame, ETLSummary]:
        """Execute full Extract -> Transform -> Load pipeline."""
        batch_id = f"ETL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        summary = ETLSummary(batch_id)

        # =====================================================================
        # STAGE 1: EXTRACT
        # =====================================================================
        summary.initial_rows = len(raw_df)
        summary.record_event("Extract", "Ingested Raw Records", summary.initial_rows, "Extracted source dataset into pipeline")
        self.warehouse.log_etl_event(batch_id, "Extract", "Ingested Raw Records", summary.initial_rows)

        if raw_df.empty:
            summary.status = "Failed: Empty Source Data"
            return pd.DataFrame(), summary

        # Create working copy to preserve original uploaded data unchanged
        df = raw_df.copy()

        # =====================================================================
        # STAGE 2: TRANSFORM
        # =====================================================================
        
        # 1. Normalize column text strings (strip whitespace, normalize casing)
        str_cols = ["department", "program", "student_name", "subject_name"]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        if "department" in df.columns:
            df["department"] = df["department"].str.title()
        else:
            df["department"] = "General Engineering"

        if "program" not in df.columns:
            df["program"] = "B.Tech"

        if "student_name" not in df.columns:
            df["student_name"] = "Student " + df["student_id"].astype(str)

        if "credits" not in df.columns:
            df["credits"] = 3.0
        else:
            df["credits"] = pd.to_numeric(df["credits"], errors="coerce").fillna(3.0)

        if "semester" not in df.columns:
            df["semester"] = 1
        else:
            df["semester"] = pd.to_numeric(df["semester"], errors="coerce").fillna(1).astype(int)

        if "academic_year" not in df.columns:
            df["academic_year"] = "2024-2025"

        # 2. Duplicate Resolution
        grain_keys = ["student_id", "subject_id", "semester"]
        has_grain = all(k in df.columns for k in grain_keys)

        if deduplicate_strategy == "drop_exact":
            dups = df.duplicated().sum()
            if dups > 0:
                df = df.drop_duplicates()
                summary.duplicates_removed = int(dups)
                summary.record_event("Transform", "Exact Duplicates Removed", int(dups), "Dropped exact duplicate rows")
        elif deduplicate_strategy == "drop_grain" and has_grain:
            dups = df.duplicated(subset=grain_keys).sum()
            if dups > 0:
                df = df.drop_duplicates(subset=grain_keys, keep="first")
                summary.duplicates_removed = int(dups)
                summary.record_event("Transform", "Grain Duplicates Removed", int(dups), "Kept first instance for each student-subject-semester")

        # 3. Attendance Calculation and Normalization
        # Attendance Percentage = (Classes Attended / Classes Held) * 100
        df["attendance_percentage"] = np.nan
        df["classes_held_clean"] = np.nan
        df["classes_attended_clean"] = np.nan

        # Check for attendance columns
        has_counts = "classes_held" in df.columns and "classes_attended" in df.columns
        has_pct = "attendance_pct" in df.columns or "attendance_percentage" in df.columns
        pct_col_name = "attendance_pct" if "attendance_pct" in df.columns else "attendance_percentage"

        if has_counts:
            held_num = pd.to_numeric(df["classes_held"], errors="coerce")
            att_num = pd.to_numeric(df["classes_attended"], errors="coerce")
            
            # Safe calculation
            valid_mask = (held_num > 0) & (att_num >= 0) & (att_num <= held_num)
            calculated_pct = np.where(valid_mask, (att_num / held_num) * 100.0, np.nan)
            
            df["attendance_percentage"] = calculated_pct
            df["classes_held_clean"] = held_num
            df["classes_attended_clean"] = att_num
            summary.attendance_calculated_count = int(valid_mask.sum())
            summary.record_event("Transform", "Calculated Attendance", summary.attendance_calculated_count, "Derived attendance percentage from held and attended counts")

        if has_pct:
            direct_pct = pd.to_numeric(df[pct_col_name], errors="coerce")
            # If attendance_percentage wasn't computed from class counts, fill from direct percentage
            df["attendance_percentage"] = df["attendance_percentage"].fillna(direct_pct)

        # Fallback default if completely missing
        df["attendance_percentage"] = df["attendance_percentage"].fillna(75.0)

        # Clean out-of-bounds attendance
        if clean_out_of_bounds:
            bad_att = (df["attendance_percentage"] < 0) | (df["attendance_percentage"] > 100.0)
            bad_att_count = int(bad_att.sum())
            if bad_att_count > 0:
                df.loc[bad_att, "attendance_percentage"] = np.clip(df.loc[bad_att, "attendance_percentage"], 0.0, 100.0)
                summary.invalid_records_cleaned += bad_att_count
                summary.record_event("Transform", "Attendance Bounds Cleaned", bad_att_count, "Clipped attendance values to [0.0, 100.0]")

        # Categorize Attendance
        df["attendance_category"] = np.where(
            df["attendance_percentage"] < ATTENDANCE_CRITICAL_THRESHOLD,
            "Low (<75%)",
            np.where(
                df["attendance_percentage"] < ATTENDANCE_EXCELLENT_THRESHOLD,
                "Normal (75-85%)",
                "High (>=85%)"
            )
        )

        # 4. Marks Processing and Missing Value Handling
        if "marks_obtained" in df.columns:
            df["marks_obtained"] = pd.to_numeric(df["marks_obtained"], errors="coerce")
        else:
            df["marks_obtained"] = np.nan
        df["is_imputed"] = 0

        # Out of bounds marks check
        if clean_out_of_bounds:
            valid_marks = df["marks_obtained"].notna()
            bad_marks = valid_marks & ((df["marks_obtained"] < 0) | (df["marks_obtained"] > max_marks))
            bad_marks_count = int(bad_marks.sum())
            if bad_marks_count > 0:
                df.loc[bad_marks, "marks_obtained"] = np.clip(df.loc[bad_marks, "marks_obtained"], 0.0, max_marks)
                summary.invalid_records_cleaned += bad_marks_count
                summary.record_event("Transform", "Marks Bounds Cleaned", bad_marks_count, f"Clipped marks to valid range [0, {max_marks}]")

        missing_marks_mask = df["marks_obtained"].isna()
        missing_count = int(missing_marks_mask.sum())

        # Only attempt subject-mean imputation if at least some valid marks exist in dataset
        if 0 < missing_count < len(df):
            if missing_marks_strategy == "impute_subject_mean":
                subject_means = df.groupby("subject_id")["marks_obtained"].transform("mean")
                overall_mean = df["marks_obtained"].mean()
                impute_values = subject_means.fillna(overall_mean if pd.notna(overall_mean) else pass_mark)
                df.loc[missing_marks_mask, "marks_obtained"] = impute_values[missing_marks_mask].round(1)
                df.loc[missing_marks_mask, "is_imputed"] = 1
                summary.missing_marks_imputed = missing_count
                summary.record_event("Transform", "Imputed Missing Marks", missing_count, "Substituted subject mean for missing exam marks; marked is_imputed=1")
            elif missing_marks_strategy == "drop":
                df = df[~missing_marks_mask].copy()
                summary.missing_marks_dropped = missing_count
                summary.record_event("Transform", "Dropped Missing Marks", missing_count, "Removed rows with missing marks per user configuration")
            else:
                summary.warnings.append(f"{missing_count} records have missing marks and were preserved without imputation.")
        elif missing_count == len(df):
            summary.warnings.append("Uploaded dataset contains attendance only (no exam marks). Attendance facts will be loaded into warehouse.")

        # 5. Internal Marks
        if "internal_marks" in df.columns:
            df["internal_marks"] = pd.to_numeric(df["internal_marks"], errors="coerce")
        else:
            df["internal_marks"] = np.nan

        # 6. Previous GPA and Backlogs
        if "previous_gpa" in df.columns:
            df["previous_gpa"] = pd.to_numeric(df["previous_gpa"], errors="coerce")
        else:
            df["previous_gpa"] = np.nan

        if "backlog_count" in df.columns:
            df["backlog_count"] = pd.to_numeric(df["backlog_count"], errors="coerce").fillna(0).astype(int)
        else:
            df["backlog_count"] = 0

        # 7. Compute Grade, GradePoints, and ResultStatus
        def assign_grade_info(marks: float) -> Tuple[str, float, str]:
            if pd.isna(marks):
                return "Unknown", 0.0, "Unknown"
            for tier in grading_scale:
                if tier["min"] <= marks <= tier["max"]:
                    return tier["grade"], float(tier["grade_point"]), tier["status"]
            # Fallback for borderline or float rounding
            if marks >= pass_mark:
                return "C", 5.0, "Pass"
            return "F", 0.0, "Fail"

        grade_results = [assign_grade_info(m) for m in df["marks_obtained"]]
        df["grade"] = [g[0] for g in grade_results]
        df["grade_points"] = [g[1] for g in grade_results]
        df["result_status"] = [g[2] for g in grade_results]

        summary.transformed_rows = len(df)
        summary.record_event("Transform", "Transformation Completed", summary.transformed_rows, "Completed type casting, cleaning, and grading derivation")
        self.warehouse.log_etl_event(batch_id, "Transform", "Transformation Completed", summary.transformed_rows)

        # =====================================================================
        # STAGE 3: LOAD
        # =====================================================================
        self._load_into_warehouse(df, summary, batch_id)

        summary.complete()
        self.warehouse.log_etl_event(batch_id, "Load", "Warehouse Load Complete", summary.loaded_exam_facts, f"Batch {batch_id} fully loaded")

        return df, summary

    def _load_into_warehouse(self, df: pd.DataFrame, summary: ETLSummary, batch_id: str) -> None:
        """Insert cleaned dimensions and facts into SQLite star schema using surrogate keys."""
        conn = self.warehouse.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Load DimDepartment
            unique_depts = df["department"].dropna().unique()
            for dept in unique_depts:
                cursor.execute(
                    "INSERT OR IGNORE INTO DimDepartment (DepartmentName) VALUES (?);",
                    (dept,)
                )
            conn.commit()
            cursor.execute("SELECT DepartmentKey, DepartmentName FROM DimDepartment;")
            dept_map = {row["DepartmentName"]: row["DepartmentKey"] for row in cursor.fetchall()}
            summary.loaded_departments = len(dept_map)

            # 2. Load DimSubject
            sub_grouped = df.groupby("subject_id").first().reset_index()
            for _, row in sub_grouped.iterrows():
                dept_key = dept_map.get(row.get("department"))
                sub_name = row.get("subject_name", row["subject_id"])
                cursor.execute(
                    """
                    INSERT INTO DimSubject (SubjectID, SubjectName, Credits, DepartmentKey)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(SubjectID) DO UPDATE SET
                        SubjectName = excluded.SubjectName,
                        Credits = excluded.Credits,
                        DepartmentKey = excluded.DepartmentKey;
                    """,
                    (row["subject_id"], sub_name, float(row["credits"]), dept_key)
                )
            conn.commit()
            cursor.execute("SELECT SubjectKey, SubjectID FROM DimSubject;")
            subject_map = {row["SubjectID"]: row["SubjectKey"] for row in cursor.fetchall()}
            summary.loaded_subjects = len(subject_map)

            # 3. Load DimSemester
            sem_combos = df[["semester", "academic_year"]].drop_duplicates()
            for _, row in sem_combos.iterrows():
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO DimSemester (SemesterNumber, AcademicYear, TermDescription)
                    VALUES (?, ?, ?);
                    """,
                    (int(row["semester"]), str(row["academic_year"]), f"Semester {row['semester']} ({row['academic_year']})")
                )
            conn.commit()
            cursor.execute("SELECT SemesterKey, SemesterNumber, AcademicYear FROM DimSemester;")
            sem_map = {(row["SemesterNumber"], row["AcademicYear"]): row["SemesterKey"] for row in cursor.fetchall()}
            summary.loaded_semesters = len(sem_map)

            # 4. Load DimStudent
            student_grouped = df.groupby("student_id").first().reset_index()
            for _, row in student_grouped.iterrows():
                dept_key = dept_map.get(row.get("department"), 1)
                cursor.execute(
                    """
                    INSERT INTO DimStudent (StudentID, StudentName, DepartmentKey, Program, BacklogCount, PreviousGPA)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(StudentID) DO UPDATE SET
                        StudentName = excluded.StudentName,
                        DepartmentKey = excluded.DepartmentKey,
                        Program = excluded.Program,
                        BacklogCount = excluded.BacklogCount,
                        PreviousGPA = excluded.PreviousGPA;
                    """,
                    (
                        str(row["student_id"]),
                        str(row.get("student_name", "")),
                        dept_key,
                        str(row.get("program", "B.Tech")),
                        int(row.get("backlog_count", 0)),
                        float(row["previous_gpa"]) if pd.notna(row.get("previous_gpa")) else None
                    )
                )
            conn.commit()
            cursor.execute("SELECT StudentKey, StudentID FROM DimStudent;")
            student_map = {row["StudentID"]: row["StudentKey"] for row in cursor.fetchall()}
            summary.loaded_students = len(student_map)

            # 5. Load FactExamResult & FactAttendance
            exam_facts = []
            att_facts = []

            for _, row in df.iterrows():
                s_key = student_map.get(str(row["student_id"]))
                sub_key = subject_map.get(str(row["subject_id"]))
                sem_key = sem_map.get((int(row["semester"]), str(row["academic_year"])))
                d_key = dept_map.get(row.get("department"))

                if s_key and sub_key and sem_key and d_key:
                    # FactExamResult record (only if exam marks exist)
                    if pd.notna(row.get("marks_obtained")):
                        exam_facts.append((
                            s_key, sub_key, sem_key, d_key, -1,
                            float(row["internal_marks"]) if pd.notna(row.get("internal_marks")) else None,
                            float(row["marks_obtained"]),
                            float(row.get("max_marks", 100.0)),
                            float(row["grade_points"]) if pd.notna(row.get("grade_points")) else 0.0,
                            str(row.get("grade", "F")),
                            float(row.get("credits", 3.0)),
                            str(row.get("result_status", "Fail")),
                            int(row.get("is_imputed", 0))
                        ))

                    # FactAttendance record (only if attendance exists)
                    if pd.notna(row.get("attendance_percentage")):
                        att_facts.append((
                            s_key, sub_key, sem_key, d_key, -1,
                            int(row["classes_held_clean"]) if pd.notna(row.get("classes_held_clean")) else None,
                            int(row["classes_attended_clean"]) if pd.notna(row.get("classes_attended_clean")) else None,
                            float(row["attendance_percentage"]),
                            str(row.get("attendance_category", "Normal (75-85%)"))
                        ))

            if exam_facts:
                cursor.executemany(
                    """
                    INSERT INTO FactExamResult (
                        StudentKey, SubjectKey, SemesterKey, DepartmentKey, DateKey,
                        InternalMarks, MarksObtained, MaximumMarks, GradePoints, Grade,
                        Credits, ResultStatus, IsImputed
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(StudentKey, SubjectKey, SemesterKey) DO UPDATE SET
                        MarksObtained = excluded.MarksObtained,
                        GradePoints = excluded.GradePoints,
                        Grade = excluded.Grade,
                        ResultStatus = excluded.ResultStatus,
                        IsImputed = excluded.IsImputed;
                    """,
                    exam_facts
                )
                summary.loaded_exam_facts = len(exam_facts)

            if att_facts:
                cursor.executemany(
                    """
                    INSERT INTO FactAttendance (
                        StudentKey, SubjectKey, SemesterKey, DepartmentKey, DateKey,
                        ClassesHeld, ClassesAttended, AttendancePercentage, AttendanceCategory
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(StudentKey, SubjectKey, SemesterKey) DO UPDATE SET
                        ClassesHeld = excluded.ClassesHeld,
                        ClassesAttended = excluded.ClassesAttended,
                        AttendancePercentage = excluded.AttendancePercentage,
                        AttendanceCategory = excluded.AttendanceCategory;
                    """,
                    att_facts
                )
                summary.loaded_attendance_facts = len(att_facts)
            conn.commit()
            summary.record_event(
                "Load",
                "Loaded Fact Tables",
                len(exam_facts) + len(att_facts),
                f"Successfully loaded {len(exam_facts)} exam facts and {len(att_facts)} attendance facts into Star Schema"
            )

        except Exception as e:
            conn.rollback()
            summary.status = f"Failed during Load: {str(e)}"
            summary.warnings.append(f"Load error: {str(e)}")
            raise e
        finally:
            conn.close()


def enrich_attendance_with_academics(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Enriches an attendance-only dataset with realistic, correlated academic indicators
    (departments, exam marks, internals, GPAs, backlogs) so that students' uploaded attendance
    can be used seamlessly across all DWDM operations (OLAP cubes, multi-level Apriori,
    decision trees, statistical correlation, and early-warning alerts).

    Args:
        df: Input DataFrame containing student attendance records.
        seed: Random seed for reproducible, realistic academic correlation.

    Returns:
        pd.DataFrame: Enriched DataFrame ready for full Star Schema ETL.
    """
    from src.mapping import ColumnMapper

    rng = np.random.RandomState(seed)
    inferred = ColumnMapper.infer_mappings(list(df.columns))
    mapping = {k: v for k, v in inferred.items() if v is not None}
    mapped = ColumnMapper.apply_mapping(df, mapping)
    res = mapped.copy()

    # 1. Standardize or calculate attendance percentage
    if "attendance_pct" in res.columns:
        att = pd.to_numeric(res["attendance_pct"], errors="coerce")
    elif "classes_held" in res.columns and "classes_attended" in res.columns:
        held = pd.to_numeric(res["classes_held"], errors="coerce").fillna(40)
        attended = pd.to_numeric(res["classes_attended"], errors="coerce").fillna(30)
        att = (attended / np.maximum(held, 1) * 100.0).round(2)
        res["attendance_pct"] = att
    else:
        att = pd.Series(75.0, index=res.index)
        res["attendance_pct"] = att

    # Fill any missing attendance values with mean
    att = att.fillna(att.mean() if not pd.isna(att.mean()) else 75.0).clip(20.0, 100.0)
    res["attendance_pct"] = att

    # 2. Derive Department from Subject Code prefix if missing
    dept_map = {
        "CS": "Computer Science & Engineering",
        "IT": "Information Technology",
        "EC": "Electronics & Communication",
        "EE": "Electrical Engineering",
        "ME": "Mechanical Engineering",
        "CE": "Civil Engineering",
        "AI": "Artificial Intelligence & Data Science",
        "DS": "Data Science",
        "MA": "Mathematics",
        "PH": "Physics"
    }

    def infer_dept(sub_val):
        sub_str = str(sub_val).strip()
        letters = "".join([c for c in sub_str if c.isalpha()])[:2].upper()
        return dept_map.get(letters, "Computer Science & Engineering")

    if "department" not in res.columns or res["department"].isnull().all():
        if "subject_id" in res.columns:
            res["department"] = res["subject_id"].apply(infer_dept)
        else:
            res["department"] = "Computer Science & Engineering"

    # 3. Subject Names and Credits
    subject_titles = {
        "CS101": "Introduction to Programming",
        "CS102": "Data Structures & Algorithms",
        "CS201": "Database Management Systems",
        "CS301": "Operating Systems & Networking",
        "EC101": "Basic Electronic Devices",
        "EC102": "Digital Logic & Circuit Design",
        "EC201": "Signals and Linear Systems",
        "EC202": "Microprocessors & Interfacing",
        "ME101": "Engineering Thermodynamics",
        "ME102": "Fluid Mechanics & Machines",
        "ME201": "Solid Mechanics & Kinematics",
        "ME202": "Manufacturing Technologies"
    }

    if "subject_name" not in res.columns or res["subject_name"].isnull().all():
        if "subject_id" in res.columns:
            res["subject_name"] = res["subject_id"].apply(
                lambda s: subject_titles.get(str(s).strip(), f"{str(s).strip()} Core Subject")
            )
        else:
            res["subject_name"] = "Core Subject"

    if "credits" not in res.columns or res["credits"].isnull().all():
        res["credits"] = 4.0

    # 4. Student Demographics
    if "student_name" not in res.columns or res["student_name"].isnull().all():
        if "student_id" in res.columns:
            res["student_name"] = "Student " + res["student_id"].astype(str)
        else:
            res["student_name"] = "Student " + pd.Series(range(1, len(res) + 1)).astype(str)

    if "program" not in res.columns or res["program"].isnull().all():
        res["program"] = "B.Tech"

    if "semester" not in res.columns or res["semester"].isnull().all():
        res["semester"] = 4

    if "academic_year" not in res.columns or res["academic_year"].isnull().all():
        res["academic_year"] = "2023-2024"

    # 5. Synthesize Correlated Examination Marks (r ~ 0.70 positive correlation)
    # Higher attendance yields statistically higher expected exam scores
    att_arr = att.values
    noise_exam = rng.normal(0, 7.5, size=len(res))
    simulated_marks = 0.68 * att_arr + 22.0 + noise_exam
    res["marks_obtained"] = np.clip(simulated_marks, 24.0, 98.0).round(1)
    res["max_marks"] = 100.0

    noise_internal = rng.normal(0, 3.5, size=len(res))
    simulated_internals = 0.35 * att_arr + 10.0 + noise_internal
    res["internal_marks"] = np.clip(simulated_internals, 10.0, 48.0).round(1)

    # 6. Prior Academic History (GPA & Backlogs)
    gpa_noise = rng.normal(0, 0.45, size=len(res))
    simulated_gpa = (att_arr / 12.0) + 1.2 + gpa_noise
    res["previous_gpa"] = np.clip(simulated_gpa, 4.0, 9.8).round(2)

    backlogs = np.zeros(len(res), dtype=int)
    low_att_indices = np.where(att_arr < 70.0)[0]
    if len(low_att_indices) > 0:
        backlogs[low_att_indices] = rng.choice([1, 2, 3], size=len(low_att_indices), p=[0.5, 0.3, 0.2])
    res["backlog_count"] = backlogs

    if "exam_date" not in res.columns or res["exam_date"].isnull().all():
        res["exam_date"] = "2024-05-15"

    return res

