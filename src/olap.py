"""OLAP Engine and Data Cube Operations Module.
Implements multidimensional Data Cube (Student x Subject x Semester),
Hierarchical Roll-up, Drill-down, Slicing, Dicing, and Credit-Weighted GPA aggregation.
"""
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

from database.warehouse import DataWarehouse, warehouse


class OLAPEngine:
    """Provides analytical OLAP operations over the integrated Star Schema data."""

    def __init__(self, target_warehouse: Optional[DataWarehouse] = None):
        self.warehouse = target_warehouse or warehouse

    def get_base_data(self) -> pd.DataFrame:
        """Fetch base integrated dataset from warehouse."""
        return self.warehouse.get_integrated_dataset()

    def build_data_cube(
        self,
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Construct multi-dimensional Data Cube aggregated across chosen dimensions.
        Default grain: [StudentID, SubjectID, Semester].
        
        Properly computes:
        - attempt_count
        - avg_marks
        - pass_count, fail_count, pass_rate_pct
        - avg_attendance
        - credit_weighted_gpa = Sum(GradePoints * Credits) / Sum(Credits)
        """
        df = self.get_base_data()
        if df.empty:
            return pd.DataFrame()

        # Apply optional filters (Slice / Dice)
        if filters:
            for col, val in filters.items():
                if val is not None and col in df.columns:
                    if isinstance(val, (list, tuple)):
                        if len(val) > 0:
                            df = df[df[col].isin(val)]
                    else:
                        df = df[df[col] == val]

        if df.empty:
            return pd.DataFrame()

        group_cols = dimensions if dimensions else ["StudentID", "SubjectID", "Semester"]
        # Ensure all group columns exist
        group_cols = [c for c in group_cols if c in df.columns]
        if not group_cols:
            group_cols = ["Department", "Semester"]

        # Aggregate safely using credit weighting for GPA
        def aggregate_cube(group: pd.DataFrame) -> pd.Series:
            attempts = len(group)
            avg_marks = group["MarksObtained"].mean() if "MarksObtained" in group.columns else np.nan
            
            # Safe status counts when ResultStatus might be part of grouping index
            if "ResultStatus" in group.columns:
                pass_cnt = int((group["ResultStatus"] == "Pass").sum())
                fail_cnt = int((group["ResultStatus"] == "Fail").sum())
            else:
                name = getattr(group, "name", None)
                name_tuple = name if isinstance(name, tuple) else (name,)
                col_map = dict(zip(group_cols, name_tuple))
                val = col_map.get("ResultStatus")
                pass_cnt = attempts if val == "Pass" else 0
                fail_cnt = attempts if val == "Fail" else 0

            pass_rate = (pass_cnt / attempts * 100.0) if attempts > 0 else 0.0
            avg_att = group["AttendancePercentage"].mean() if "AttendancePercentage" in group.columns else np.nan
            
            # Weighted GPA: Sum(GradePoints * Credits) / Sum(Credits)
            if "Credits" in group.columns and "GradePoints" in group.columns:
                total_credits = group["Credits"].sum()
                if total_credits > 0:
                    weighted_gp = (group["GradePoints"] * group["Credits"]).sum()
                    weighted_gpa = weighted_gp / total_credits
                else:
                    weighted_gpa = group["GradePoints"].mean()
            else:
                weighted_gpa = np.nan

            return pd.Series({
                "Attempts": attempts,
                "Avg_Marks": round(avg_marks, 2) if pd.notna(avg_marks) else np.nan,
                "Pass_Count": pass_cnt,
                "Fail_Count": fail_cnt,
                "Pass_Rate_Pct": round(pass_rate, 2),
                "Avg_Attendance_Pct": round(avg_att, 2) if pd.notna(avg_att) else np.nan,
                "Credit_Weighted_GPA": round(weighted_gpa, 2) if pd.notna(weighted_gpa) else np.nan
            })

        cube = df.groupby(group_cols, observed=True).apply(aggregate_cube).reset_index()
        return cube

    def roll_up_hierarchy(self, level: str = "Department") -> pd.DataFrame:
        """Roll up from Subject level -> Department level -> University level.
        
        Levels:
        - 'Subject': Subject-level detail
        - 'Semester': Semester-level aggregation
        - 'Department': Department-level aggregation
        - 'University': Top-level university institution summary
        """
        df = self.get_base_data()
        if df.empty:
            return pd.DataFrame()

        if level == "Subject":
            group_cols = ["Department", "SubjectID", "SubjectName"]
        elif level == "Semester":
            group_cols = ["Department", "Semester"]
        elif level == "Department":
            group_cols = ["Department"]
        elif level == "University":
            # Overall single university aggregation
            df["University"] = "Central University Institute"
            group_cols = ["University"]
        else:
            group_cols = ["Department"]

        def agg_rollup(group: pd.DataFrame) -> pd.Series:
            total_attempts = len(group)
            unique_students = group["StudentID"].nunique()
            avg_marks = group["MarksObtained"].mean()
            pass_cnt = (group["ResultStatus"] == "Pass").sum()
            fail_cnt = (group["ResultStatus"] == "Fail").sum()
            pass_rate = (pass_cnt / total_attempts * 100.0) if total_attempts > 0 else 0.0
            fail_rate = (fail_cnt / total_attempts * 100.0) if total_attempts > 0 else 0.0
            avg_att = group["AttendancePercentage"].mean()
            
            # Truly credit-weighted GPA
            total_credits = group["Credits"].sum()
            if total_credits > 0:
                weighted_gp = (group["GradePoints"] * group["Credits"]).sum()
                weighted_gpa = weighted_gp / total_credits
            else:
                weighted_gpa = group["GradePoints"].mean()

            return pd.Series({
                "Unique_Students": unique_students,
                "Total_Exam_Attempts": total_attempts,
                "Avg_Marks": round(avg_marks, 2),
                "Pass_Count": pass_cnt,
                "Fail_Count": fail_cnt,
                "Pass_Rate_Pct": round(pass_rate, 2),
                "Fail_Rate_Pct": round(fail_rate, 2),
                "Avg_Attendance": round(avg_att, 2) if pd.notna(avg_att) else np.nan,
                "Weighted_GPA": round(weighted_gpa, 2)
            })

        result = df.groupby(group_cols, observed=True).apply(agg_rollup).reset_index()
        return result

    def drill_down_to_students(self, department: Optional[str] = None, semester: Optional[int] = None) -> pd.DataFrame:
        """Drill down from department/semester into individual student records."""
        df = self.get_base_data()
        if df.empty:
            return pd.DataFrame()

        if department:
            df = df[df["Department"] == department]
        if semester is not None:
            df = df[df["Semester"] == semester]

        return df[[
            "StudentID", "StudentName", "Department", "Semester", "SubjectID",
            "SubjectName", "MarksObtained", "Grade", "ResultStatus",
            "AttendancePercentage", "AttendanceCategory"
        ]].sort_values(by=["StudentID", "Semester", "SubjectID"])

    def slice_cube(self, dimension: str, value: Any) -> pd.DataFrame:
        """Slice the cube along a single dimension member (e.g. Semester == 3)."""
        return self.build_data_cube(
            dimensions=["StudentID", "SubjectID"],
            filters={dimension: value}
        )

    def dice_cube(
        self,
        departments: Optional[List[str]] = None,
        semesters: Optional[List[int]] = None,
        result_status: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Simultaneous multi-dimension dicing with Department Failure Rate Ranking."""
        df = self.get_base_data()
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()

        if departments:
            df = df[df["Department"].isin(departments)]
        if semesters:
            df = df[df["Semester"].isin(semesters)]
        if result_status:
            df = df[df["ResultStatus"].isin(result_status)]

        if df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Detailed diced summary
        diced_summary = self.build_data_cube(
            dimensions=["Department", "Semester", "ResultStatus"],
            filters={}
        )

        # Department-level Failure Rate Ranking within diced subset
        def dept_fail_stats(group: pd.DataFrame) -> pd.Series:
            total = len(group)
            fails = (group["ResultStatus"] == "Fail").sum()
            fail_rate = (fails / total * 100.0) if total > 0 else 0.0
            return pd.Series({
                "Student_Count": group["StudentID"].nunique(),
                "Total_Records": total,
                "Fail_Count": fails,
                "Failure_Rate_Pct": round(fail_rate, 2),
                "Avg_Attendance": round(group["AttendancePercentage"].mean(), 2)
            })

        dept_ranking = df.groupby("Department", observed=True).apply(dept_fail_stats).reset_index()
        dept_ranking = dept_ranking.sort_values(by="Failure_Rate_Pct", ascending=False)

        return df, dept_ranking
