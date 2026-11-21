"""Star Schema metadata, documentation, and architecture introspection module.
Provides schema definitions, fact grain documentation, surrogate key mappings,
and Mermaid ER diagram generation for dashboard display and export.
"""
from typing import Dict, List, Any
import pandas as pd
from database.warehouse import DataWarehouse, warehouse


class StarSchemaInspector:
    """Provides architectural documentation and introspection for the Star Schema."""

    @staticmethod
    def get_fact_grain_documentation() -> Dict[str, Dict[str, Any]]:
        """Document the exact grain and measures of each fact table."""
        return {
            "FactExamResult": {
                "grain": "One student assessment outcome per subject per semester (StudentKey, SubjectKey, SemesterKey)",
                "surrogate_key": "ResultKey (INTEGER AUTOINCREMENT)",
                "dimension_keys": ["StudentKey", "SubjectKey", "SemesterKey", "DepartmentKey", "DateKey"],
                "measures": [
                    {"name": "MarksObtained", "type": "Numeric (Additive)", "desc": "Score achieved in exam (0-100)"},
                    {"name": "MaximumMarks", "type": "Numeric", "desc": "Maximum attainable exam marks (100.0)"},
                    {"name": "InternalMarks", "type": "Numeric", "desc": "Continuous internal assessment score (0-50)"},
                    {"name": "GradePoints", "type": "Numeric (Semi-Additive)", "desc": "Derived grade point (0.0 to 10.0)"},
                    {"name": "Credits", "type": "Numeric", "desc": "Course credit weighting (e.g. 3.0 or 4.0)"}
                ],
                "degenerate_dimensions": ["Grade", "ResultStatus ('Pass'/'Fail')", "IsImputed"]
            },
            "FactAttendance": {
                "grain": "One student course attendance summary per subject per semester (StudentKey, SubjectKey, SemesterKey)",
                "surrogate_key": "AttendanceKey (INTEGER AUTOINCREMENT)",
                "dimension_keys": ["StudentKey", "SubjectKey", "SemesterKey", "DepartmentKey", "DateKey"],
                "measures": [
                    {"name": "ClassesHeld", "type": "Integer (Additive)", "desc": "Total lecture sessions conducted"},
                    {"name": "ClassesAttended", "type": "Integer (Additive)", "desc": "Lecture sessions student attended"},
                    {"name": "AttendancePercentage", "type": "Numeric (Non-Additive)", "desc": "(ClassesAttended / ClassesHeld) * 100"}
                ],
                "degenerate_dimensions": ["AttendanceCategory ('Low (<75%)', 'Normal', 'High')"]
            }
        }

    @staticmethod
    def get_dimension_documentation() -> Dict[str, Dict[str, Any]]:
        """Document dimension tables, natural business keys, and hierarchies."""
        return {
            "DimStudent": {
                "surrogate_key": "StudentKey",
                "natural_key": "StudentID",
                "attributes": ["StudentName", "Program", "Batch", "BacklogCount", "PreviousGPA"],
                "hierarchy": "Student -> Program -> Department -> University"
            },
            "DimSubject": {
                "surrogate_key": "SubjectKey",
                "natural_key": "SubjectID",
                "attributes": ["SubjectName", "Credits"],
                "hierarchy": "Subject -> Department -> University"
            },
            "DimSemester": {
                "surrogate_key": "SemesterKey",
                "natural_key": "(SemesterNumber, AcademicYear)",
                "attributes": ["TermDescription"],
                "hierarchy": "Semester -> Academic Year"
            },
            "DimDepartment": {
                "surrogate_key": "DepartmentKey",
                "natural_key": "DepartmentName",
                "attributes": ["Faculty"],
                "hierarchy": "Department -> Faculty -> University"
            },
            "DimDate": {
                "surrogate_key": "DateKey",
                "natural_key": "FullDate",
                "attributes": ["Day", "Month", "Quarter", "Year", "IsWeekend"],
                "hierarchy": "Day -> Month -> Quarter -> Year"
            }
        }

    @staticmethod
    def get_mermaid_schema_diagram() -> str:
        """Generate a Mermaid ER diagram representing the academic Star Schema."""
        return """erDiagram
    DimDepartment ||--o{ DimStudent : "enrolls"
    DimDepartment ||--o{ DimSubject : "offers"
    DimDepartment ||--o{ FactExamResult : "aggregates"
    DimDepartment ||--o{ FactAttendance : "aggregates"
    
    DimStudent ||--o{ FactExamResult : "evaluates"
    DimStudent ||--o{ FactAttendance : "records"
    
    DimSubject ||--o{ FactExamResult : "assessed_in"
    DimSubject ||--o{ FactAttendance : "tracks"
    
    DimSemester ||--o{ FactExamResult : "conducted_in"
    DimSemester ||--o{ FactAttendance : "occurs_in"
    
    DimDate ||--o{ FactExamResult : "dated_on"
    DimDate ||--o{ FactAttendance : "dated_on"

    DimDepartment {
        int DepartmentKey PK
        string DepartmentName UK
        string Faculty
    }

    DimStudent {
        int StudentKey PK
        string StudentID UK
        string StudentName
        int DepartmentKey FK
        string Program
        int BacklogCount
        float PreviousGPA
    }

    DimSubject {
        int SubjectKey PK
        string SubjectID UK
        string SubjectName
        float Credits
        int DepartmentKey FK
    }

    DimSemester {
        int SemesterKey PK
        int SemesterNumber
        string AcademicYear
    }

    DimDate {
        int DateKey PK
        string FullDate
        int Year
        int Month
    }

    FactExamResult {
        int ResultKey PK
        int StudentKey FK
        int SubjectKey FK
        int SemesterKey FK
        int DepartmentKey FK
        int DateKey FK
        float InternalMarks
        float MarksObtained
        float GradePoints
        string Grade
        float Credits
        string ResultStatus
        boolean IsImputed
    }

    FactAttendance {
        int AttendanceKey PK
        int StudentKey FK
        int SubjectKey FK
        int SemesterKey FK
        int DepartmentKey FK
        int DateKey FK
        int ClassesHeld
        int ClassesAttended
        float AttendancePercentage
        string AttendanceCategory
    }
"""
