# Student Performance Data Warehouse & AI Early-Warning System
## Comprehensive System Architecture, Tech Stack, Methodology, & File Analysis

---

## 1. Executive Summary: What Has Been Made

This project is a university-grade **Student Performance Data Warehouse with Multi-Level Association Mining and an AI Early-Warning Decision Support System**, developed specifically to address and fulfill the **Data Warehousing and Data Mining (DWDM) Project-Based Learning (PBL)** curriculum evaluation rubric (**Questions 61 through 70**).

The system integrates:
1. **A Formal Relational Star Schema Data Warehouse** hosted on SQLite with surrogate primary keys, foreign key constraints (`PRAGMA foreign_keys = ON`), and composite uniqueness constraints enforcing strict fact table granularity.
2. **An End-to-End 3-Stage ETL Pipeline** (Extract, Transform, Load) with automated column alias matching, pre-ETL data quality profiling, deduplication, bounds clipping, mean imputation tagged with `is_imputed = 1`, and batch lineage audit logging.
3. **An OLAP Analytical Engine** supporting a multidimensional Data Cube ($\text{Student} \times \text{Subject} \times \text{Semester}$), Hierarchical Roll-up, Drill-down, Slicing, Dicing with departmental failure rankings, and mathematically verified **credit-weighted GPA** calculations.
4. **Multi-Level & Constraint-Based Association Rule Mining** using the Apriori algorithm across concept hierarchies (Level 1: Department $\rightarrow$ Result Status; Level 2: Subject $\rightarrow$ Letter Grade), plus constraint mining on low-attendance students ($<75\%$) reporting both **conditional support** and **global population support**.
5. **A Machine Learning Academic Risk Classifier** using Decision Trees trained with a **strict zero-target-leakage guarantee** (pre-exam timing only) and student-grouped test splitting (`GroupShuffleSplit`).
6. **An AI Early-Warning Triage Center** that prioritizes students into risk queues, provides multi-factor causal triggers, and recommends academic interventions with interactive faculty review workflows.
7. **A Statistical Correlation Module** using SciPy for Pearson linear correlation ($r$), Spearman monotonic rank correlation ($\rho$), exact two-tailed $p$-values, OLS regression trendlines ($y = mx + c$), and multivariable heatmaps.
8. **An Academic Reporting & Export Engine** that generates publication-quality multi-page PDF documents via ReportLab, interactive HTML reports, and FERPA-compliant privacy pseudonymization (`ANON-001`, `ANON-002`).
9. **A 12-Page Streamlit Dashboard** and an automated test suite with **26 passing unit and integration tests** (100% pass rate).

---

## 2. Technology Stack & Library Mapping

| Layer / Purpose | Technology / Library | Version / Role |
| :--- | :--- | :--- |
| **Language & Runtime** | **Python** | 3.10, 3.11, 3.12 |
| **Data Warehouse Database** | **SQLite3 & SQL DDL** | Embedded relational data warehouse with foreign keys, surrogate keys, composite unique constraints, and B-Tree indexes. |
| **ETL & Data Manipulation** | **Pandas & NumPy** | `pandas>=2.0.0`, `numpy>=1.24.0` for vectorized transformations, joins, missing data handling, and aggregation. |
| **File Parsing & I/O** | **OpenPyXL** | `openpyxl>=3.1.0` for parsing `.xlsx` workbooks alongside multi-encoding CSV processing (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`). |
| **Data Mining (Apriori)** | **mlxtend** | `mlxtend>=0.23.0` for `TransactionEncoder`, `apriori()`, and `association_rules()`. |
| **Machine Learning** | **scikit-learn** | `scikit-learn>=1.3.0` for `DecisionTreeClassifier`, `GroupShuffleSplit`, `SimpleImputer`, confusion matrices, and text rule extraction. |
| **Statistical Analysis** | **SciPy** | `scipy>=1.10.0` (`scipy.stats`) for Pearson $r$, Spearman $\rho$, $p$-values, and linear regression (`linregress`). |
| **Web Dashboard & UI** | **Streamlit** | `streamlit>=1.30.0` for multi-page routing, session state, metric KPI cards, and custom CSS styling. |
| **Data Visualization** | **Plotly** | `plotly>=5.18.0` for interactive regression scatter plots, correlation heatmaps, histograms, and departmental bar charts. |
| **Document Generation** | **ReportLab** | Multi-page publication-quality academic PDF generation with flowable tables, custom typography, running headers/footers, and two-pass `NumberedCanvas`. |
| **Automated Testing** | **pytest** | `pytest>=7.4.0` with 26 unit and integration test fixtures verifying all 10 PBL requirements. |

---

## 3. Exhaustive File-by-File Breakdown

```
dwdmPBL/
├── app.py                      # 12-page Streamlit web dashboard application
├── requirements.txt            # Python package dependencies
├── README.md                   # Academic documentation and PBL rubric mapping
├── PROJECT_ANALYSIS.md         # Full architectural, technical, and methodological analysis
├── .gitignore                  # Git ignore rules
├── config/
│   ├── __init__.py             # Config package marker
│   └── settings.py             # Canonical schema aliases, grading scales, PBL mappings
├── data/
│   └── sample/                 # Generated synthetic benchmark datasets (CSV)
│       ├── departments.csv
│       ├── subjects.csv
│       ├── students.csv
│       ├── attendance.csv
│       ├── exam_results.csv
│       ├── combined.csv
│       └── noisy_test_records.csv
├── database/
│   ├── __init__.py             # Database package marker
│   ├── schema.sql              # Star Schema DDL with foreign keys and constraints
│   ├── warehouse.py            # SQLite connection, execution layer, audit logs
│   └── warehouse.db            # Persistent SQLite database file
├── src/
│   ├── __init__.py             # Source package marker
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
│   ├── reporting.py            # Privacy anonymization & executive PDF/HTML report generator
│   └── ui_helpers.py           # Streamlit CSS styling, KPI cards, visual tokens
└── tests/
    ├── __init__.py             # Tests package marker
    ├── test_schema.py          # Schema & surrogate key constraints tests
    ├── test_etl.py             # ETL transformation & imputation tests
    ├── test_olap.py            # OLAP aggregations & weighted GPA tests
    ├── test_mining.py          # Multi-level & constraint mining tests
    ├── test_prediction.py      # Decision tree & leakage safeguard tests
    ├── test_correlation.py     # SciPy correlation tests
    ├── test_generator.py       # Synthetic data & anonymization tests
    └── test_reporting.py       # Full PDF & HTML report generation tests
```

### Detailed File Catalog

#### Root Directory
- `app.py`: Main dashboard entry point (1,050 lines) implementing the complete 12-page Streamlit analytical workflow:
  1. *Overview & Dashboard*: Real-time KPI summary, pass rate charts, attendance histograms.
  2. *Data Upload & Ingestion*: Multi-file upload, format detection, automatic joining, attendance enrichment loader.
  3. *Column Mapping*: Interactive alias matching against canonical academic fields and feature availability checks.
  4. *Data Quality & ETL Pipeline*: Pre-ETL anomaly audit, health score (0–100%), deduplication/imputation execution, audit trail.
  5. *Star Schema Architecture*: Interactive Mermaid ER diagram, fact grain declarations, measure documentation.
  6. *OLAP & Data Cube*: Cube aggregation, Hierarchical Roll-up, Drill-down, Slice, Dice with failure ranking.
  7. *Multi-Level Association Mining*: Apriori mining for Level 1 (Department $\rightarrow$ Result) and Level 2 (Subject $\rightarrow$ Grade).
  8. *Constraint-Based Mining (<75% Att)*: Implementation of Question 65 distinguishing conditional support from global support.
  9. *Decision Tree Classifier*: Model configuration, training with group splitting, confusion matrix, feature importance, text rules.
  10. *Statistical Correlation Analysis*: SciPy Pearson $r$, Spearman $\rho$, $p$-values, linear regression trendlines, heatmap.
  11. *AI Early-Warning Center*: Student risk triage queue, multi-factor triggers, recommended faculty interventions, review workflow.
  12. *Export & Academic Reports*: Integrated CSV export, ReportLab PDF download, executive HTML download, FERPA toggle.
- `requirements.txt`: Specifies pinned library versions for production execution.
- `README.md`: Official project documentation detailing PBL questions, installation, and architectural diagrams.
- `.gitignore`: Standard exclusion for virtual environments, caches, and database logs.

#### Configuration Directory (`config/`)
- `config/settings.py`:
  - Centralizes file paths (`data/`, `database/`, `warehouse.db`).
  - `CANONICAL_COLUMNS`: Comprehensive dictionary of canonical fields (`student_id`, `department`, `subject_id`, `marks_obtained`, `attendance_pct`, `internal_marks`, etc.) with regex and alias mappings (e.g., `roll_no`, `usn`, `cie`, `sgpa`).
  - `DEFAULT_GRADING_SCALE`: 10-point academic grading scale (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`) with grade points, score ranges, and pass/fail statuses.
  - Threshold constants: $75.0\%$ mandatory minimum attendance, $85.0\%$ excellent attendance.
  - `PBL_RUBRIC_MAPPING`: Official syllabus mapping connecting Questions 61–70 to modules and weights.
- `config/__init__.py`: Package initialization.

#### Database Directory (`database/`)
- `database/schema.sql`:
  - DDL creating the formal Star Schema:
    - Dimensions: `DimDepartment`, `DimDate` (with default `-1` Unknown Date record), `DimSemester`, `DimSubject`, `DimStudent`.
    - Facts: `FactExamResult` and `FactAttendance`.
    - Integrity Constraints: Composite unique keys (`uq_exam_grain` and `uq_attendance_grain`) on `(StudentKey, SubjectKey, SemesterKey)` to eliminate duplicate fact rows.
    - Audit Trail: `ETLAuditLog` recording batch IDs, stages, actions, affected rows, and execution timestamps.
    - Performance Indexes: B-Tree indexes on foreign keys, `ResultStatus`, and `AttendanceCategory`.
- `database/warehouse.py`:
  - `DataWarehouse`: SQLite connection manager, executes DDL scripts, initializes schemas, and handles database resets.
  - `log_etl_event()`: Transactional logging of ETL batch events.
  - `get_table_counts()`: Live row counts across warehouse tables.
  - `get_integrated_dataset()`: Parameterized SQL join combining fact tables with dimensions for downstream analytics.
- `database/warehouse.db`: Persistent SQLite warehouse database file.
- `database/__init__.py`: Package initialization.

#### Source Implementation (`src/`)
- `src/upload.py`:
  - `FileLoader`: Ingests `.csv`, `.xlsx`, and `.xls` files with automatic multi-encoding fallback (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`) and extracts structural metadata.
- `src/mapping.py`:
  - `ColumnMapper`: Matches uploaded headers against canonical aliases using normalized token matching.
  - `assess_feature_availability()`: Pre-flight check determining which analytical modules can execute with the uploaded columns.
  - `validate_and_join_datasets()`: Joins multi-table uploads while verifying key uniqueness to prevent Cartesian product inflation.
- `src/validation.py`:
  - `DataQualityValidator`: Profiles raw datasets prior to ETL for duplicate rows, grain violations, missing/invalid marks ($< 0$ or $> 100$), invalid attendance ($< 0\%$ or $> 100\%$), and count contradictions ($\text{attended} > \text{held}$), generating an overall Data Quality Health Score (0–100%).
- `src/etl.py`:
  - `ETLSummary`: Data class tracking execution duration, row counts, cleaned records, and warnings.
  - `AcademicETLPipeline`: Orchestrates Extract (raw read), Transform (deduplication, bounds clipping, mean imputation flagged with `is_imputed = 1`, 10-point grade derivation), and Load (dimension surrogate key generation, fact upserts via `INSERT ... ON CONFLICT DO UPDATE`).
  - `enrich_attendance_with_academics()`: Generates realistic, correlated academic indicators for attendance-only uploads so all DWDM operations function out-of-the-box.
- `src/data_generator.py`:
  - `AcademicDataGenerator`: Creates synthetic benchmark university data across 4 departments, 16 courses, and multiple terms. Models student ability using a Beta distribution, simulating correlated attendance and marks.
  - Generates `noisy_test_records.csv` with intentional flaws (missing values, negative marks, $>100\%$ attendance) to test ETL resilience.
- `src/star_schema.py`:
  - `StarSchemaInspector`: Introspects warehouse metadata, defines additive/semi-additive/non-additive measures, natural-to-surrogate key mappings, and outputs a Mermaid ER diagram.
- `src/olap.py`:
  - `OLAPEngine`:
    - `build_data_cube()`: Aggregates attempts, pass/fail counts, pass rates, average attendance, and calculates **credit-weighted GPA**:
      $$\text{Credit-Weighted GPA} = \frac{\sum (\text{GradePoints} \times \text{Credits})}{\sum \text{Credits}}$$
    - `roll_up_hierarchy()`: Aggregates from Subject $\rightarrow$ Semester $\rightarrow$ Department $\rightarrow$ University level.
    - `drill_down_to_students()`: Drills down into individual student course records.
    - `slice_cube()`: Slices across a single dimension member.
    - `dice_cube()`: Filters across multiple dimensions simultaneously (Department $\times$ Semester $\times$ Status) and ranks departments by failure rate.
- `src/association_mining.py`:
  - `AcademicAssociationMiner`:
    - Builds one-hot encoded transaction itemsets from discretized academic factors (attendance tier, pass/fail, backlogs, GPA).
    - Apriori Mining (Question 66): Discovers frequent itemsets and association rules using `mlxtend`.
    - Multi-Level Mining (Question 69): Evaluates Level 1 (Department $\rightarrow$ Result) and Level 2 (Subject $\rightarrow$ Grade) with independent support/confidence thresholds.
    - Constraint-Based Mining (Question 65): Restricts population to attendance $<75\%$ and evaluates both **conditional support** (in subset) and **global support** (across university population).
- `src/decision_tree.py`:
  - `AcademicRiskClassifier`:
    - Strict Zero-Target-Leakage Guarantee: Predictive features are restricted to pre-examination indicators (`AttendancePercentage`, `InternalMarks`, `PreviousGPA`, `BacklogCount`, and department dummies). Post-exam metrics (`MarksObtained`, `GradePoints`, `Grade`, `ResultStatus`) are strictly prohibited.
    - Uses `GroupShuffleSplit` by `StudentID` to prevent student-level data leakage between training and testing splits.
    - Computes test accuracy, macro F1-score, per-class metrics, confusion matrix, feature importances, and text rules.
- `src/early_warning.py`:
  - `EarlyWarningCenter`: Evaluates student cohorts into priority queues (**Critical Risk / Fail**, **At-Risk / Borderline**, **On-Track / Pass**), identifies multi-factor triggers, suggests academic interventions, and tracks faculty review status.
- `src/correlation.py`:
  - `CorrelationAnalyzer`:
    - Calculates Pearson $r$ and Spearman $\rho$ with exact $p$-values using SciPy.
    - Computes linear regression slope, intercept ($y = mx + c$), and $R^2$.
    - Robustly handles zero-variance and small-sample edge cases.
    - Computes pairwise Pearson correlation matrices across numeric features.
- `src/reporting.py`:
  - `NumberedCanvas`: Two-pass canvas dynamically computing total page numbers and printing running headers/footers.
  - `generate_pdf_report()`: Generates a publication-quality multi-page PDF report via ReportLab with tables, styles, and evaluator sign-off blocks.
  - `generate_html_summary_report()`: Generates a responsive single-file executive HTML report.
  - `anonymize_student_identifiers()`: Anonymizes student IDs (`ANON-001`, `ANON-002`) for FERPA compliance.
- `src/ui_helpers.py`: Injects custom CSS, renders KPI metric cards, manages session state, and displays empty-state action cards.
- `src/__init__.py`: Package initialization.

#### Sample Data Directory (`data/sample/`)
- `departments.csv`: Department dimension seed data (`D01` to `D04`).
- `subjects.csv`: Subject catalog with course codes, titles, and credit weightings (3.0 and 4.0).
- `students.csv`: Student cohort master records with department affiliations, backlogs, and prior GPAs.
- `attendance.csv`: Lecture attendance records (classes held, attended, percentage, category).
- `exam_results.csv`: Final exam outcome records (internals, final marks, grade points, letter grades, pass/fail status).
- `combined.csv`: Pre-joined single-file dataset for unified ingestion.
- `noisy_test_records.csv`: Deliberately corrupted dataset containing duplicate rows, missing marks, negative scores (`-15.0`), scores $>100$, and $>100\%$ attendance to verify ETL validation.

#### Automated Tests Directory (`tests/`)
- `tests/test_schema.py`: Verifies table creation, surrogate key autoincrement, unique grain constraint enforcement, and audit logging.
- `tests/test_etl.py`: Tests alias mapping inference, anomaly detection, subject-mean imputation, bounds clipping, and attendance enrichment.
- `tests/test_olap.py`: Verifies exact credit-weighted GPA calculation against known mathematical test fixtures, hierarchical roll-up, slice, and dice.
- `tests/test_mining.py`: Verifies Apriori itemset/rule generation, Question 65 constraint-based mining, and multi-level hierarchies.
- `tests/test_prediction.py`: Strictly asserts zero target-leakage features, verifies Decision Tree training/evaluation, and tests early-warning triage queue generation.
- `tests/test_correlation.py`: Tests perfect linear correlation ($r=1.000$), zero-variance error handling, insufficient observation checks, and multivariable correlation matrices.
- `tests/test_generator.py`: Tests synthetic data generation, dirty test data generation, and FERPA report anonymization.
- `tests/test_reporting.py`: Validates PDF stream generation (`%PDF` magic byte header), PDF generation with anonymization, and HTML report content.

---

## 4. How the System Works: Architecture & Data Flow

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

### End-to-End Workflow Stages

1. **Ingestion & Inspection**:
   - The user uploads CSV or Excel files via Streamlit.
   - Files are parsed with automatic character encoding detection (`utf-8`, `utf-8-sig`, `latin1`, `cp1252`).
   - Multiple relational files are joined on common business keys (`student_id`, `subject_id`).
2. **Schema Normalization & Profiling**:
   - Columns are mapped to canonical names using alias dictionaries (`roll_no` $\rightarrow$ `student_id`, `cie` $\rightarrow$ `internal_marks`).
   - `DataQualityValidator` checks for duplicate rows, grain violations, missing marks, and bounds errors, calculating a Data Quality Health Score.
3. **ETL Execution**:
   - Cleans and clips numerical values to valid ranges ($[0, 100]$ for marks and $[0\%, 100\%]$ for attendance).
   - Missing marks are imputed using the subject-level mean and tagged with `is_imputed = 1` for transparency.
   - Letter grades and grade points are assigned based on the 10-point scale.
   - Surrogate keys are assigned and dimension records are inserted.
   - Fact records are loaded with composite unique constraints via `INSERT ... ON CONFLICT DO UPDATE`.
   - Execution details are logged to `ETLAuditLog`.
4. **Multidimensional OLAP**:
   - The Data Cube aggregates marks, attendance, pass/fail counts, and computes credit-weighted GPA.
   - Users can roll up along concept hierarchies (Subject $\rightarrow$ Semester $\rightarrow$ Department $\rightarrow$ University), drill down to individual students, slice by a single dimension member, or dice across multiple dimensions with department failure ranking.
5. **Data Mining & Predictive Modeling**:
   - *Association Mining*: Transaction itemsets are generated and mined with Apriori across concept hierarchies (Level 1: Dept $\rightarrow$ Result; Level 2: Subject $\rightarrow$ Grade) and under low-attendance constraints ($<75\%$).
   - *Decision Tree Risk Prediction*: Trained on pre-exam indicators with student group splitting to evaluate failure risk without target leakage.
   - *Statistical Correlation*: Evaluates Pearson $r$ and Spearman $\rho$ with linear regression equations.
6. **Early-Warning Decision Support**:
   - Students are classified into triage queues (**Critical Risk**, **At-Risk**, **On-Track**) with specific risk triggers and intervention recommendations.
   - Faculty can track and update review statuses ("Pending Review", "Intervention Scheduled", "Resolved").
7. **Consolidated Academic Reporting**:
   - Generates publication-ready PDF reports via ReportLab and standalone HTML reports.
   - Provides FERPA privacy anonymization (`ANON-001`, `ANON-002`) for student privacy.

---

## 5. Core Methodologies & Academic Principles

### A. Data Warehousing Methodology
- **Star Schema Architecture**: Denormalized dimension tables surround fact tables to optimize read-heavy OLAP queries and minimize expensive multi-table joins.
- **Fact Table Granularity**: Declared as **one student exam assessment per subject per semester** `(StudentKey, SubjectKey, SemesterKey)`. Enforced via composite uniqueness constraints in SQLite.
- **Surrogate Key Design**: Surrogate integer keys (`StudentKey`, `SubjectKey`, etc.) decouple warehouse storage from source system natural key formats, ensuring fast integer join indexing.
- **Measure Classification**:
  - Additive measures: `MarksObtained`, `ClassesHeld`, `ClassesAttended`.
  - Semi-additive measures: `GradePoints` (meaningful across subjects for a student, but not summable across students).
  - Non-additive measures: `AttendancePercentage` (recalculated from class counts at aggregated levels).

### B. ETL Methodology
- **Audit Logging & Lineage**: Every batch run records start/end timestamps, affected row counts, and status to `ETLAuditLog`.
- **Audited Imputation**: Imputes missing marks with the subject mean and marks them with `is_imputed = 1` rather than fabricating arbitrary values.
- **Idempotent Loading**: Upsert logic ensures that re-running the pipeline updates existing records rather than producing duplicates.

### C. Multidimensional OLAP Methodology
- **Credit-Weighted GPA**:
  $$\text{Credit-Weighted GPA} = \frac{\sum_{i=1}^{n} (\text{GradePoints}_i \times \text{Credits}_i)}{\sum_{i=1}^{n} \text{Credits}_i}$$
  Prevents the distortion introduced by simple unweighted averaging when course credit values vary.
- **Concept Hierarchy Roll-Up**: Traverses institutional dimensions:
  $$\text{Subject} \longrightarrow \text{Semester} \longrightarrow \text{Department} \longrightarrow \text{University}$$

### D. Multi-Level & Constraint-Based Association Mining
- **Apriori Algorithm**: Discretizes metrics into transaction items (Attendance tiers, Pass/Fail, Backlogs, GPA brackets) to find rules meeting support, confidence, and lift thresholds.
- **Multi-Level Concept Hierarchies**: Evaluates coarse-grained rules at Level 1 (Department $\rightarrow$ Result) and fine-grained rules at Level 2 (Subject $\rightarrow$ Grade) using separate threshold controls.
- **Constraint-Based Formulation (Question 65)**: Restricts analysis to the low-attendance sub-population ($<75\%$) and differentiates between:
  $$\text{Conditional Support} = \frac{\text{Count}(\text{Itemset in Constrained Subset})}{\text{Total Records in Constrained Subset}}$$
  $$\text{Global Support} = \text{Conditional Support} \times \left(\frac{\text{Total Records in Constrained Subset}}{\text{Total University Population Records}}\right)$$

### E. Machine Learning & Zero-Target-Leakage Methodology
- **Target Leakage Safeguard**: Features are strictly limited to pre-examination indicators:
  - Allowed: `AttendancePercentage`, `InternalMarks`, `PreviousGPA`, `BacklogCount`, `Department`.
  - Forbidden: `MarksObtained`, `MaximumMarks`, `GradePoints`, `Grade`, `ResultStatus`.
- **Student-Grouped Holdout Splitting**: Uses `GroupShuffleSplit` on `StudentID` so that all records from any single student reside exclusively in either the training set or the test set.

### F. Statistical Correlation Methodology
- Uses SciPy to test both linear relationships (Pearson $r$) and monotonic rank relationships (Spearman $\rho$).
- Reports exact $p$-values and fits linear regression lines ($y = mx + c$).
- Distinguishes correlation from causation in both the UI and generated reports.

### G. Privacy & Institutional Security
- **Local Embedded Processing**: Executes entirely on local SQLite with zero external cloud transmission of student records.
- **SQL Injection Prevention**: Uses parameterized SQL queries (`?` bindings).
- **FERPA Compliance**: Provides automated pseudonymization (`ANON-001`, `ANON-002`) for public exports and reports.

---

## 6. PBL Rubric & Question Mapping (Questions 61–70)

| Rubric Weight | Question | Requirement Description | Implementation Location | Verification Status |
| :---: | :---: | :--- | :--- | :---: |
| **20%** | **Q61** | **Star Schema Design:** Grain declaration, surrogate keys, dimension and fact tables. | `database/schema.sql`, `src/star_schema.py`, Page 5 | ✅ Passed (`test_schema.py`) |
| | **Q62** | **Warehouse Integrity:** Foreign key enforcement, composite unique constraints, indexes. | `database/warehouse.py`, Page 5 | ✅ Passed (`test_schema.py`) |
| | **Q63** | **Data Ingestion & Profiling:** Alias inference, missing value profiling, health scoring. | `src/upload.py`, `src/mapping.py`, `src/validation.py`, Page 2 & 3 | ✅ Passed (`test_etl.py`) |
| | **Q64** | **3-Stage ETL Pipeline:** Extract, Transform (cleaning, bounds, imputation), Load, audit logs. | `src/etl.py`, Page 4 | ✅ Passed (`test_etl.py`) |
| **25%** | **Q65** | **Constraint-Based Mining:** Attendance threshold filtering ($<75\%$), conditional vs global support. | `src/association_mining.py`, Page 8 | ✅ Passed (`test_mining.py`) |
| | **Q66** | **Apriori Algorithm:** One-hot transactions, frequent itemset discovery across attendance and backlogs. | `src/association_mining.py`, Page 7 & 8 | ✅ Passed (`test_mining.py`) |
| | **Q69 (Assoc)** | **Multi-Level Concept Hierarchies:** Level 1 (Dept $\rightarrow$ Result), Level 2 (Subject $\rightarrow$ Grade). | `src/association_mining.py`, Page 7 | ✅ Passed (`test_mining.py`) |
| **25%** | **Q67** | **Academic Risk Classifier:** Zero-target-leakage decision tree, student-grouped splitting. | `src/decision_tree.py`, Page 9 | ✅ Passed (`test_prediction.py`) |
| | **Q70** | **AI Early-Warning System:** Student risk triage queue, multi-factor triggers, faculty review actions. | `src/early_warning.py`, Page 11 | ✅ Passed (`test_prediction.py`) |
| **30%** | **Q68** | **Statistical Correlation:** SciPy Pearson $r$, Spearman $\rho$, $p$-values, OLS regression ($y = mx + c$), $R^2$. | `src/correlation.py`, Page 10 | ✅ Passed (`test_correlation.py`) |
| | **Q69 (OLAP)** | **OLAP Operations:** Multidimensional Cube, Roll-up, Drill-down, Slice, Dice; credit-weighted GPA. | `src/olap.py`, Page 6 | ✅ Passed (`test_olap.py`) |

---

## 7. Automated Test Suite Verification

The project includes an automated test suite executed via `pytest tests/ -v`. All 26 test cases pass with a 100% success rate:

```
tests/test_correlation.py::test_perfect_linear_correlation PASSED
tests/test_correlation.py::test_zero_variance_constant_array_handled PASSED
tests/test_correlation.py::test_insufficient_observations_handled PASSED
tests/test_correlation.py::test_multivariable_correlation_matrix PASSED
tests/test_etl.py::test_column_mapping_inference PASSED
tests/test_etl.py::test_data_quality_validator_detects_anomalies PASSED
tests/test_etl.py::test_etl_imputation_and_bounds_cleaning PASSED
tests/test_etl.py::test_enrich_attendance_with_academics PASSED
tests/test_generator.py::test_synthetic_data_generator_generation PASSED
tests/test_generator.py::test_noisy_dataset_generation PASSED
tests/test_generator.py::test_privacy_anonymization_in_reports PASSED
tests/test_mining.py::test_apriori_frequent_itemsets_and_rules PASSED
tests/test_mining.py::test_constraint_based_mining_q65 PASSED
tests/test_mining.py::test_multilevel_concept_hierarchy_mining PASSED
tests/test_olap.py::test_credit_weighted_gpa_calculation PASSED
tests/test_olap.py::test_olap_roll_up_department_and_university PASSED
tests/test_olap.py::test_olap_slice_and_dice PASSED
tests/test_prediction.py::test_target_leakage_safeguard PASSED
tests/test_prediction.py::test_decision_tree_train_and_evaluate PASSED
tests/test_prediction.py::test_early_warning_triage_generation PASSED
tests/test_reporting.py::test_generate_pdf_report_valid_pdf_stream PASSED
tests/test_reporting.py::test_generate_pdf_report_with_anonymization PASSED
tests/test_reporting.py::test_generate_html_report_contains_all_sections PASSED
tests/test_schema.py::test_schema_tables_exist PASSED
tests/test_schema.py::test_fact_table_grain_uniqueness_constraint PASSED
tests/test_schema.py::test_audit_logging PASSED

======================= 26 passed in 22.00s =======================
```
