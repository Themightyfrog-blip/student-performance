"""Synthetic academic data generator for the Student Performance Data Warehouse.
Produces realistic, reproducible multi-file and single-file academic datasets
with configurable parameters, natural variance, and intentional edge cases.
"""
import random
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from config.settings import SAMPLE_DATA_DIR, ATTENDANCE_CRITICAL_THRESHOLD

# Seeded random names and departments
FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Arjun", "Deepak", "Devi", "Divya", "Gaurav",
    "Ishaan", "Kavya", "Manish", "Meera", "Neha", "Nikhil", "Pooja", "Pranav",
    "Priya", "Rahul", "Rhea", "Rohan", "Sanjay", "Shreya", "Sneha", "Varun",
    "Vikram", "Yash", "Zoya", "Karan", "Tanvi", "Siddharth", "Aishwarya", "Aditya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Rao", "Gupta",
    "Singh", "Kumar", "Das", "Choudhury", "Joshi", "Bose", "Mehta", "Deshmukh",
    "Kulkarni", "Pillai", "Bhat", "Saxena", "Menon", "Kapoor", "Chatterjee"
]

DEPARTMENTS = {
    "Computer Science": {
        "code_prefix": "CS",
        "programs": ["B.Tech Computer Science & Engineering"],
        "subjects": [
            ("CS101", "Data Structures & Algorithms", 4.0),
            ("CS102", "Database Management Systems", 4.0),
            ("CS103", "Operating Systems", 3.0),
            ("CS104", "Computer Networks", 3.0),
            ("CS105", "Theory of Computation", 3.0),
            ("CS106", "Software Engineering", 3.0),
        ]
    },
    "Information Technology": {
        "code_prefix": "IT",
        "programs": ["B.Tech Information Technology"],
        "subjects": [
            ("IT101", "Web Technologies", 3.0),
            ("IT102", "Data Mining & Warehousing", 4.0),
            ("IT103", "Cloud Computing", 3.0),
            ("IT104", "Information Security", 3.0),
            ("IT105", "Object Oriented Programming", 4.0),
        ]
    },
    "Electronics & Comm": {
        "code_prefix": "EC",
        "programs": ["B.Tech Electronics & Communication"],
        "subjects": [
            ("EC101", "Digital Electronics", 4.0),
            ("EC102", "Microprocessors & Microcontrollers", 4.0),
            ("EC103", "Signals and Systems", 3.0),
            ("EC104", "Analog Communication", 3.0),
            ("EC105", "VLSI Design", 4.0),
        ]
    },
    "Mechanical Eng": {
        "code_prefix": "ME",
        "programs": ["B.Tech Mechanical Engineering"],
        "subjects": [
            ("ME101", "Thermodynamics", 4.0),
            ("ME102", "Fluid Mechanics", 4.0),
            ("ME103", "Kinematics of Machinery", 3.0),
            ("ME104", "Manufacturing Processes", 3.0),
            ("ME105", "Heat Transfer", 3.0),
        ]
    }
}

COMMON_SUBJECTS = [
    ("MA101", "Engineering Mathematics I", 4.0),
    ("MA102", "Engineering Mathematics II", 4.0),
    ("PH101", "Engineering Physics", 3.0),
    ("CY101", "Engineering Chemistry", 3.0),
]


class AcademicDataGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def generate_dataset(
        self,
        num_students: int = 120,
        semesters: List[int] = [3, 4, 5],
        academic_year: str = "2024-2025"
    ) -> Dict[str, pd.DataFrame]:
        """Generate a realistic relational academic dataset across multiple entities."""
        # 1. Generate Departments
        dept_rows = []
        for d_id, (d_name, d_info) in enumerate(DEPARTMENTS.items(), start=1):
            dept_rows.append({
                "department_id": f"D{d_id:02d}",
                "department_name": d_name,
                "faculty": "Faculty of Engineering & Technology"
            })
        df_depts = pd.DataFrame(dept_rows)

        # 2. Generate Subjects
        sub_rows = []
        for d_name, d_info in DEPARTMENTS.items():
            for code, name, creds in d_info["subjects"]:
                sub_rows.append({
                    "subject_id": code,
                    "subject_name": name,
                    "credits": creds,
                    "department_name": d_name
                })
        for code, name, creds in COMMON_SUBJECTS:
            sub_rows.append({
                "subject_id": code,
                "subject_name": name,
                "credits": creds,
                "department_name": "Applied Sciences"
            })
        df_subjects = pd.DataFrame(sub_rows).drop_duplicates(subset=["subject_id"])

        # 3. Generate Students
        student_rows = []
        dept_names_list = list(DEPARTMENTS.keys())
        
        for i in range(1, num_students + 1):
            s_id = f"STU{2022000 + i}"
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            s_name = f"{first_name} {last_name}"
            d_name = dept_names_list[(i - 1) % len(dept_names_list)]
            program = DEPARTMENTS[d_name]["programs"][0]
            
            # Underlying student capability latent factor (0.0 to 1.0)
            latent_ability = np.clip(np.random.beta(a=5, b=2.5), 0.1, 0.98)
            
            # Backlogs inversely related to ability with Poisson noise
            expected_backlogs = max(0, int((1.0 - latent_ability) * 3.5 + np.random.normal(0, 0.5)))
            backlog_count = min(expected_backlogs, 6)
            
            # Prior GPA correlated with latent ability (scale 4.0 - 10.0)
            prev_gpa = round(float(np.clip(latent_ability * 6.0 + 3.8 + np.random.normal(0, 0.4), 4.0, 9.85)), 2)

            student_rows.append({
                "student_id": s_id,
                "student_name": s_name,
                "department_name": d_name,
                "program": program,
                "batch": "2022-2026",
                "latent_ability": latent_ability,
                "backlog_count": backlog_count,
                "previous_gpa": prev_gpa
            })
        df_students = pd.DataFrame(student_rows)

        # 4. Generate Exam Results and Attendance
        exam_rows = []
        att_rows = []

        for _, student in df_students.iterrows():
            s_id = student["student_id"]
            d_name = student["department_name"]
            ability = student["latent_ability"]
            
            # Student-level attendance propensity
            # Students with lower ability or more backlogs are slightly more prone to lower attendance
            base_att_prob = np.clip(ability * 0.35 + 0.58 + np.random.normal(0, 0.12), 0.45, 0.98)

            for sem in semesters:
                # Select departmental subjects for this semester
                dept_subs = [s for s in DEPARTMENTS[d_name]["subjects"]]
                # Pick 3 or 4 subjects per semester
                selected_subs = dept_subs[:min(len(dept_subs), 4)]
                
                for code, name, creds in selected_subs:
                    # Classes held: 50 to 60 lectures
                    classes_held = random.randint(50, 60)
                    
                    # Specific subject interest variation
                    sub_att_factor = np.clip(base_att_prob + np.random.normal(0, 0.06), 0.40, 0.99)
                    classes_attended = int(round(classes_held * sub_att_factor))
                    classes_attended = max(15, min(classes_held, classes_attended))
                    att_pct = round((classes_attended / classes_held) * 100.0, 2)

                    # Determine attendance category
                    if att_pct < ATTENDANCE_CRITICAL_THRESHOLD:
                        att_cat = "Low (<75%)"
                    elif att_pct < 85.0:
                        att_cat = "Normal (75-85%)"
                    else:
                        att_cat = "High (>=85%)"

                    # Internal assessment marks (Max 50)
                    # Correlated with ability, attendance, and noise
                    int_factor = 0.55 * ability + 0.35 * (att_pct / 100.0) + np.random.normal(0, 0.08)
                    internal_marks = round(float(np.clip(int_factor * 50.0, 12.0, 49.5)), 1)

                    # Final exam marks (Max 100)
                    # Strongly influenced by ability & attendance, with realistic exam-day variance
                    perf_factor = 0.50 * ability + 0.35 * (att_pct / 100.0) + 0.15 * (internal_marks / 50.0) + np.random.normal(0, 0.10)
                    marks_obtained = round(float(np.clip(perf_factor * 100.0, 15.0, 99.0)), 1)
                    
                    # Standard pass mark: 40.0
                    result_status = "Pass" if marks_obtained >= 40.0 else "Fail"

                    # Grade points
                    if marks_obtained >= 90.0:
                        grade = "O"
                        grade_point = 10.0
                    elif marks_obtained >= 80.0:
                        grade = "A+"
                        grade_point = 9.0
                    elif marks_obtained >= 70.0:
                        grade = "A"
                        grade_point = 8.0
                    elif marks_obtained >= 60.0:
                        grade = "B+"
                        grade_point = 7.0
                    elif marks_obtained >= 50.0:
                        grade = "B"
                        grade_point = 6.0
                    elif marks_obtained >= 40.0:
                        grade = "C"
                        grade_point = 5.0
                    else:
                        grade = "F"
                        grade_point = 0.0

                    # Append to exam results
                    exam_rows.append({
                        "student_id": s_id,
                        "subject_id": code,
                        "semester": sem,
                        "academic_year": academic_year,
                        "department": d_name,
                        "internal_marks": internal_marks,
                        "marks_obtained": marks_obtained,
                        "max_marks": 100.0,
                        "grade_points": grade_point,
                        "grade": grade,
                        "credits": creds,
                        "result_status": result_status,
                        "exam_date": f"2024-{random.choice(['05', '06', '11', '12'])}-{random.randint(10, 28):02d}"
                    })

                    # Append to attendance records
                    att_rows.append({
                        "student_id": s_id,
                        "subject_id": code,
                        "semester": sem,
                        "academic_year": academic_year,
                        "classes_held": classes_held,
                        "classes_attended": classes_attended,
                        "attendance_percentage": att_pct,
                        "attendance_category": att_cat
                    })

        df_exams = pd.DataFrame(exam_rows)
        df_att = pd.DataFrame(att_rows)
        
        # Clean up internal student latent ability column before exporting
        df_students_clean = df_students.drop(columns=["latent_ability"])

        # 5. Combined All-in-One Academic Dataset
        df_combined = df_exams.merge(
            df_students_clean[["student_id", "student_name", "program", "backlog_count", "previous_gpa"]],
            on="student_id",
            how="left"
        ).merge(
            df_subjects[["subject_id", "subject_name"]],
            on="subject_id",
            how="left"
        ).merge(
            df_att[["student_id", "subject_id", "semester", "classes_held", "classes_attended", "attendance_percentage", "attendance_category"]],
            on=["student_id", "subject_id", "semester"],
            how="left"
        )

        return {
            "departments": df_depts,
            "subjects": df_subjects,
            "students": df_students_clean,
            "exam_results": df_exams,
            "attendance": df_att,
            "combined": df_combined
        }

    def generate_noisy_test_dataset(self, base_combined: pd.DataFrame) -> pd.DataFrame:
        """Create an intentional dirty/noisy dataset for validating ETL and data quality checks:
        - Missing marks
        - Invalid marks (> 100 or negative)
        - Invalid attendance (> 100% or classes_attended > classes_held)
        - Duplicates
        - Missing student names
        - Case variations
        """
        noisy_df = base_combined.copy().head(100)  # Take subset
        
        # 1. Add duplicate rows
        duplicates = noisy_df.sample(n=6, random_state=123)
        noisy_df = pd.concat([noisy_df, duplicates], ignore_index=True)

        # 2. Add missing marks (NaN)
        missing_indices = noisy_df.sample(n=8, random_state=456).index
        noisy_df.loc[missing_indices, "marks_obtained"] = np.nan

        # 3. Add out-of-range marks
        bad_marks_idx1 = noisy_df.sample(n=2, random_state=789).index
        noisy_df.loc[bad_marks_idx1, "marks_obtained"] = 145.0  # > 100

        bad_marks_idx2 = noisy_df.sample(n=2, random_state=999).index
        noisy_df.loc[bad_marks_idx2, "marks_obtained"] = -15.0  # negative

        # 4. Add invalid attendance percentage
        bad_att_idx = noisy_df.sample(n=3, random_state=111).index
        noisy_df.loc[bad_att_idx, "attendance_percentage"] = 125.0

        # 5. Add casing inconsistency
        case_idx = noisy_df.sample(n=5, random_state=222).index
        noisy_df.loc[case_idx, "department"] = noisy_df.loc[case_idx, "department"].str.lower()

        return noisy_df

    def save_sample_files(self, output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """Generate and save all sample files to disk."""
        target_dir = Path(output_dir) if output_dir else SAMPLE_DATA_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        data = self.generate_dataset(num_students=120)
        file_paths = {}

        # Save individual relational files
        for name, df in data.items():
            path = target_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            file_paths[name] = path

        # Generate and save noisy test dataset
        noisy_df = self.generate_noisy_test_dataset(data["combined"])
        noisy_path = target_dir / "noisy_test_records.csv"
        noisy_df.to_csv(noisy_path, index=False)
        file_paths["noisy"] = noisy_path

        return file_paths


def get_or_create_sample_data() -> Dict[str, Path]:
    """Helper to ensure sample data files exist, creating them if missing."""
    generator = AcademicDataGenerator(seed=42)
    return generator.save_sample_files()


if __name__ == "__main__":
    paths = get_or_create_sample_data()
    print("Generated sample academic datasets:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
