# Student Performance Data Warehouse with Multi-Level Association Mining & AI Early-Warning System

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2%20App%20Router-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v3.4-38B2AC.svg)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-DataWarehouse-003B57.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-26%20Passed-success.svg)](https://pytest.org/)
[![DWDM PBL](https://img.shields.io/badge/DWDM-University%20PBL-indigo.svg)](#pbl-rubric--question-mapping)

A university-grade **Data Warehousing and Data Mining (DWDM) Project-Based Learning (PBL)** software system that integrates a formal relational Star Schema data warehouse, an end-to-end 3-stage ETL pipeline, multidimensional OLAP data cubes, multi-level association rule mining, constraint-based Apriori mining, zero-target-leakage Decision Tree classification, SciPy statistical correlation, and an AI early-warning decision-support triage dashboard.

---

## 📑 PBL Rubric & Question Mapping (Questions 61–70)

The application explicitly fulfills and documents all university DWDM PBL evaluation components:

| Category & Rubric Weight | PBL Question | Academic Requirement & Description | Implemented Module & UI Page | Verification Status |
| :--- | :---: | :--- | :--- | :---: |
| **Schema & ETL (20%)** | **Q61** | **Star Schema Design:** Grain declaration, surrogate keys, Dimension tables (`DimStudent`, `DimSubject`, `DimSemester`, `DimDepartment`, `DimDate`), Fact tables (`FactExamResult`, `FactAttendance`). | `database/schema.sql`, `src/star_schema.py`, Page 5 | ✅ Passed (`test_schema.py`) |
| | **Q62** | **Warehouse Integrity & Storage:** Foreign key constraints, unique fact grain enforcement, surrogate mapping, index optimizations. | `database/warehouse.py`, Page 5 | ✅ Passed (`test_schema.py`) |
| | **Q63** | **Data Ingestion & Profiling:** Automated alias detection, missing-value profiling, data health scoring (0–100%). | `src/upload.py`, `src/mapping.py`, `src/validation.py`, Page 2 & 3 | ✅ Passed (`test_etl.py`) |
| | **Q64** | **3-Stage ETL Pipeline:** Extract, Transform (deduplication, bounds capping, mean imputation with `is_imputed` flag), and Load with audit logging. | `src/etl.py`, Page 4 | ✅ Passed (`test_etl.py`) |
| **Multi-Level Association Rules (25%)** | **Q65** | **Constraint-Based Mining:** Attendance threshold filtering (<75%), conditional support vs global population support calculation, lift. | `src/association_mining.py`, Page 8 | ✅ Passed (`test_mining.py`) |
| | **Q66** | **Apriori Algorithm:** One-hot transactions, frequent itemset discovery across attendance, backlogs, and academic performance. | `src/association_mining.py`, Page 7 & 8 | ✅ Passed (`test_mining.py`) |
| | **Q69 (Assoc)** | **Multi-Level Concept Hierarchies:** Level 1 (`Department` &rarr; `Result`), Level 2 (`Subject` &rarr; `Grade`), separate support/confidence controls. | `src/association_mining.py`, Page 7 | ✅ Passed (`test_mining.py`) |
| **Decision Tree Classification (25%)** | **Q67** | **Academic Risk Classifier:** Decision tree predicting Pass, Fail, and At-Risk; **strict zero-target-leakage guarantee** (pre-exam timing only); student-grouped holdout test splitting. | `src/decision_tree.py`, Page 9 | ✅ Passed (`test_prediction.py`) |
| | **Q70** | **AI Early-Warning System:** Student risk triage queue, multi-factor risk triggers, faculty intervention recommendations, and status workflows. | `src/early_warning.py`, Page 11 | ✅ Passed (`test_prediction.py`) |
| **OLAP & Correlation (30%)** | **Q68** | **Statistical Correlation:** SciPy Pearson $r$, Spearman rank $\rho$, $p$-values, linear regression equation ($y = mx + c$), $R^2$, and scatter trendlines. | `src/correlation.py`, Page 10 | ✅ Passed (`test_correlation.py`) |
| | **Q69 (OLAP)** | **OLAP Operations:** Multidimensional Cube (Student &times; Subject &times; Semester), Roll-up (Dept/University), Drill-down, Slice, Dice with Failure Ranking; **credit-weighted GPA**. | `src/olap.py`, Page 6 | ✅ Passed (`test_olap.py`) |

---

## 🏛️ Architecture & Star Schema Design

```
                     +-------------------+
                     |   DimDepartment   |
                     +-------------------+
                     | PK DepartmentKey  |
                     |    DepartmentName |
                     +---------+---------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
+-----------------------+             +-----------------------+
|      DimStudent       |             |      DimSubject       |
+-----------------------+             +-----------------------+
| PK StudentKey         |             | PK SubjectKey         |
|    StudentID (UK)     |             |    SubjectID (UK)     |
|    StudentName        |             |    SubjectName        |
| FK DepartmentKey      |             |    Credits            |
|    BacklogCount       |             | FK DepartmentKey      |
|    PreviousGPA        |             +-----------+-----------+
+-----------+-----------+                         |
            |                                     |
            +------------------+------------------+
                               |
                               v
            +-------------------------------------------+
            |               FactExamResult              |
            +-------------------------------------------+
            | PK ResultKey                              |
            | FK StudentKey                             |
            | FK SubjectKey                             |
            | FK SemesterKey                            |
            | FK DepartmentKey                          |
            | FK DateKey (-1 for Unknown Date)          |
            |    InternalMarks (0 - 50)                 |
            |    MarksObtained (0 - 100)                |
            |    GradePoints (0.0 - 10.0)               |
            |    Grade ('O', 'A+', 'A', 'B', 'C', 'F')  |
            |    Credits                                |
            |    ResultStatus ('Pass' / 'Fail')         |
            |    IsImputed (Boolean)                    |
            | UK (StudentKey, SubjectKey, SemesterKey)  |
            +---------------------+---------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
|      DimSemester      |                   |    FactAttendance     |
+-----------------------+                   +-----------------------+
| PK SemesterKey        |                   | PK AttendanceKey      |
|    SemesterNumber     |                   | FK StudentKey, ...    |
|    AcademicYear       |                   |    ClassesHeld        |
+-----------------------+                   |    ClassesAttended    |
                                            |    AttendancePct      |
                                            |    AttendanceCategory |
                                            +-----------------------+
```

### Fact Table Granularity
- **`FactExamResult` Grain:** One student course examination outcome per subject per semester `(StudentKey, SubjectKey, SemesterKey)`.
- **`FactAttendance` Grain:** One student course attendance record per subject per semester `(StudentKey, SubjectKey, SemesterKey)`.
- **Uniqueness Guarantee:** Enforced via SQLite composite `UNIQUE` constraints to mathematically prevent duplicate fact records and double-counting during roll-up aggregations.

---

## ⚙️ 3-Stage ETL Methodology

1. **Extract:**
   - Ingests single-file or multi-file CSV and Excel (`.xlsx`, `.xls`) uploads.
   - Preserves raw uploaded records unchanged.
   - Detects file encodings (`utf-8`, `latin1`, `windows-1252`) and structural metadata.
2. **Transform:**
   - **Schema Normalization:** Trims whitespace, standardizes casing, formats canonical types.
   - **Deduplication:** Configurable strategies (`drop_grain`, `drop_exact`, `none`).
   - **Attendance Calculation:** $\text{Attendance Percentage} = \frac{\text{Classes Attended}}{\text{Classes Held}} \times 100$.
   - **Bounds Validation:** Validates and clips out-of-range marks ($[0, 100]$) and attendance ($[0, 100\%]$).
   - **Missing Value Resolution:** Replaces missing exam marks with the subject mean and tags records with `is_imputed = 1` for auditing; avoids fabricating arbitrary values.
   - **Grading & Results:** Assigns standard 10-point grade points, grades (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`), and status (`Pass` / `Fail`).
3. **Load:**
   - Inserts dimensions and generates integer surrogate keys.
   - Inserts fact records with foreign key resolution and upsert collision handling.
   - Writes batch lineage records to `ETLAuditLog`.

---

## 🧊 OLAP Operations & Multidimensional Analysis

- **Data Cube (Student &times; Subject &times; Semester):** Computes total attempts, average marks, pass/fail counts, pass rate, average attendance, and credit-weighted GPA.
- **Credit-Weighted GPA Aggregation:** Uses $\text{Weighted GPA} = \frac{\sum (\text{GradePoints} \times \text{Credits})}{\sum \text{Credits}}$ rather than unweighted averages.
- **Hierarchical Roll-up:** Aggregates from Subject &rarr; Semester &rarr; Department &rarr; University level.
- **Drill-down:** Inspects individual student exam records filtered by department and semester.
- **Slice:** Slices the multidimensional cube across a single dimension member (e.g., `Semester == 3`).
- **Dice:** Filters across multiple dimensions simultaneously (Department &times; Semester &times; Result Status) and ranks departments by failure rate with sample size indicators.

---

## ⛓️ Multi-Level & Constraint-Based Association Mining

- **Multi-Level Hierarchies:**
  - *Institutional:* $\text{University} \rightarrow \text{Department} \rightarrow \text{Program} \rightarrow \text{Subject}$
  - *Performance:* $\text{Academic Performance} \rightarrow \text{Result Category (Pass/Fail)} \rightarrow \text{Grade Category (O to F)}$
  - **Level 1 Mining:** Discovers rules between departments and overall results (e.g., $\text{Dept\_ComputerScience} \land \text{Attendance\_Low} \Rightarrow \text{Result\_Fail}$).
  - **Level 2 Mining:** Discovers rules between specific course codes and letter grades (e.g., $\text{Subject\_CS101} \land \text{Attendance\_Low} \Rightarrow \text{Grade\_F}$).
- **Constraint-Based Mining (Question 65):**
  - Restricts analysis to students whose attendance is below the mandatory threshold ($< 75\%$).
  - Evaluates both **Conditional Support** ($\text{Support within subset}$) and **Global Support** ($\text{Support across entire university dataset}$).
- **Apriori Association Engine (Question 66):**
  - Powered by `mlxtend` with one-hot encoded transaction itemsets.
  - Generates Support, Confidence, and Lift metrics.

---

## 🌳 Decision Tree Risk Classifier & AI Early-Warning

- **Strict Target Leakage Safeguards:** Features are strictly limited to pre-examination indicators:
  - Attendance Percentage
  - Internal Assessment Marks ($/50$)
  - Previous Cumulative GPA
  - Active Backlog Count
  - Department
  - *Forbidden as Predictors:* Final Marks Obtained, Grade, Grade Points, Result Status.
- **Student Grouped Splitting:** Uses `GroupShuffleSplit` by `StudentID` so that repeated records from the same student never leak between the training set and the holdout test set.
- **Early-Warning Decision Support (Question 70):**
  - Generates student risk triage queues (**Critical Risk / Fail**, **At-Risk / Borderline**, **On-Track / Pass**).
  - Pinpoints specific multi-factor risk triggers (e.g., "Attendance 62% + Internals 18/50 + 2 Backlogs").
  - Suggests recommended academic interventions (e.g., remedial tutoring, faculty mentoring).
  - Includes interactive faculty review tracking ("Pending Review", "Intervention Scheduled", "Resolved").

---

## 📈 Statistical Correlation Analysis (Question 68)

- Computes **Pearson linear correlation ($r$)** and **Spearman monotonic rank correlation ($\rho$)** using SciPy.
- Reports exact $p$-values, degrees of freedom ($N$), regression trendline equation ($y = mx + c$), and $R^2$.
- Renders an interactive Plotly scatter plot with linear regression trendlines and a multivariable correlation heatmap.
- Explicitly documents that statistical correlation indicates co-movement rather than direct causation.

---

## 🚀 Installation & Execution

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Windows PowerShell or Linux Bash

### 1. Clone or Open Workspace
```bash
cd d:\dwdmPBL
```

### 2. Create and Activate Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python & Node.js Dependencies
```bash
# Python Backend Dependencies
pip install -r requirements.txt

# Next.js Frontend Dependencies
cd frontend
npm install
cd ..
```

### 4. Launch the Full-Stack Application

**Option A — One-Click Scripts:**
- Windows Command Prompt: `start_servers.bat`
- Windows PowerShell: `.\start_servers.ps1`

**Option B — Manual Launch:**
```bash
# Terminal 1: Python FastAPI Backend
python server.py
# Listening on http://127.0.0.1:8000 (Swagger docs at /docs)

# Terminal 2: Next.js Modern Frontend
cd frontend
npm run dev
# Dashboard available at http://localhost:3000
```

---

## 🧪 Automated Testing

The project includes an automated test suite verifying all 10 PBL questions with deterministic test fixtures:

```bash
python -m pytest tests/ -v
```

### Test Suite Summary:
- `tests/test_schema.py`: Star schema tables, surrogate keys, unique fact grain enforcement, foreign key constraints.
- `tests/test_etl.py`: Column mapping inference, anomaly detection, bounds clipping, mean imputation, warehouse loading.
- `tests/test_olap.py`: Multidimensional cube aggregation, mathematical proof of credit-weighted GPA, roll-up, slice, dice.
- `tests/test_mining.py`: Apriori frequent itemsets, Q65 constraint-based mining, multi-level hierarchy rule discovery.
- `tests/test_prediction.py`: Strict target-leakage prevention assertions, Decision Tree evaluation, student risk triage generation.
- `tests/test_correlation.py`: SciPy Pearson and Spearman tests, zero-variance handling, multivariable correlation matrix.
- `tests/test_generator.py`: Synthetic dataset generation, noisy edge-case datasets, FERPA privacy anonymization.
- `tests/test_reporting.py`: Full academic PDF report generation via ReportLab, privacy pseudonymization, and HTML generation.

**Status:** `26 passed (100% pass rate)`.

---

## 📁 Repository Directory Structure

```
dwdmPBL/
├── server.py                   # FastAPI REST backend (31 endpoints)
├── start_servers.bat           # 1-click launcher for Windows Batch
├── start_servers.ps1           # 1-click launcher for Windows PowerShell
├── requirements.txt            # Python package dependencies
├── README.md                   # Academic documentation and PBL rubric mapping
├── PROJECT_ANALYSIS.md         # Comprehensive PBL architectural & code analysis
├── .gitignore                  # Git ignore rules
├── frontend/                   # Modern Next.js 14 Web Dashboard
│   ├── package.json            # Node.js dependencies
│   ├── tailwind.config.ts      # Tailwind CSS config (Deep Rust & Pearl theme)
│   ├── tsconfig.json           # TypeScript configuration
│   └── src/
│       ├── app/                # Next.js App Router (layout.tsx, page.tsx, globals.css)
│       ├── components/         # Reusable UI & views
│       │   ├── ui/             # MetricCard, KPI tokens
│       │   └── views/          # 11 Dedicated DWDM PBL analytical views
│       └── lib/
│           └── api.ts          # Strongly typed client for 31 FastAPI endpoints
├── config/
│   ├── __init__.py
│   └── settings.py             # Canonical schema aliases, grading scales, PBL mappings
├── data/
│   ├── sample/                 # Generated synthetic benchmark datasets (CSV)
│   └── processed/
├── database/
│   ├── __init__.py
│   ├── schema.sql              # Star Schema DDL with foreign keys and constraints
│   ├── warehouse.db            # Embedded SQLite data warehouse
│   └── warehouse.py            # SQLite connection, execution layer, audit logs
├── src/
│   ├── __init__.py
│   ├── upload.py               # Robust CSV and Excel ingestion
│   ├── mapping.py              # Flexible column mapping & join validation
│   ├── validation.py           # Pre-ETL data quality audit profiler
│   ├── etl.py                  # 3-Stage Extract-Transform-Load engine
│   ├── data_generator.py       # Realistic synthetic university dataset generator
│   ├── star_schema.py          # Architectural documentation & Mermaid ER diagram
│   ├── olap.py                 # Data Cube, Roll-up, Drill-down, Slice, Dice, GPA
│   ├── association_mining.py   # Apriori, Multi-Level & Q65 Constraint-Based Mining
│   ├── decision_tree.py        # Q67 Decision Tree risk classifier & leakage safeguards
│   ├── early_warning.py        # Q70 AI student risk triage & intervention workflows
│   ├── correlation.py          # Q68 SciPy Pearson and Spearman correlation analysis
│   └── reporting.py            # Privacy anonymization & ReportLab PDF / HTML generator
└── tests/
    ├── __init__.py
    ├── test_schema.py          # Schema & surrogate key constraints tests
    ├── test_etl.py             # ETL transformation & imputation tests
    ├── test_olap.py            # OLAP aggregations & weighted GPA tests
    ├── test_mining.py          # Multi-level & constraint mining tests
    ├── test_prediction.py      # Decision tree & leakage safeguard tests
    ├── test_correlation.py     # SciPy correlation tests
    ├── test_generator.py       # Synthetic data & anonymization tests
    └── test_reporting.py       # PDF & HTML report generation tests
```

---

## 🔒 Privacy, Security, & Institutional Compliance

- **Local Storage:** All processing and data warehouse queries execute locally on the embedded SQLite database. No student records are transmitted to external APIs or cloud services.
- **SQL Injection Prevention:** All warehouse queries utilize parameterized SQL statements.
- **FERPA / Academic Privacy:** The reporting module includes student identifier anonymization (`ANON-001`, `ANON-002`...) for public research reports and academic exports.
- **Reset Controls:** The dashboard provides a one-click warehouse reset button to purge uploaded student records and re-initialize empty schemas.

---

## 🎓 University PBL Submission Details
- **Project Title:** Student Performance Data Warehouse with Multi-Level Association Mining and AI Early-Warning System
- **Curriculum:** Data Warehousing and Data Mining (DWDM)
- **Evaluation Rubric:** Questions 61–70 (100% Implemented and Verified)
