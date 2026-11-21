-- ====================================================================
-- Star Schema Definition: Student Performance Data Warehouse
-- Conforming to DWDM PBL Requirements (Questions 61-62)
-- Granularity:
--   FactExamResult: (StudentKey, SubjectKey, SemesterKey)
--   FactAttendance: (StudentKey, SubjectKey, SemesterKey)
-- ====================================================================

PRAGMA foreign_keys = ON;

-- Dimension: DimDepartment
CREATE TABLE IF NOT EXISTS DimDepartment (
    DepartmentKey INTEGER PRIMARY KEY AUTOINCREMENT,
    DepartmentName TEXT NOT NULL UNIQUE,
    Faculty TEXT DEFAULT 'Faculty of Engineering & Technology',
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: DimDate
CREATE TABLE IF NOT EXISTS DimDate (
    DateKey INTEGER PRIMARY KEY, -- e.g. YYYYMMDD, with -1 representing Unknown/Unspecified Date
    FullDate TEXT,
    Day INTEGER,
    Month INTEGER,
    Quarter INTEGER,
    Year INTEGER,
    IsWeekend BOOLEAN DEFAULT 0
);

-- Dimension: DimSemester
CREATE TABLE IF NOT EXISTS DimSemester (
    SemesterKey INTEGER PRIMARY KEY AUTOINCREMENT,
    SemesterNumber INTEGER NOT NULL,
    AcademicYear TEXT NOT NULL,
    TermDescription TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_semester UNIQUE (SemesterNumber, AcademicYear)
);

-- Dimension: DimSubject
CREATE TABLE IF NOT EXISTS DimSubject (
    SubjectKey INTEGER PRIMARY KEY AUTOINCREMENT,
    SubjectID TEXT NOT NULL UNIQUE,
    SubjectName TEXT NOT NULL,
    Credits REAL NOT NULL DEFAULT 3.0,
    DepartmentKey INTEGER,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (DepartmentKey) REFERENCES DimDepartment(DepartmentKey)
);

-- Dimension: DimStudent
CREATE TABLE IF NOT EXISTS DimStudent (
    StudentKey INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID TEXT NOT NULL UNIQUE,
    StudentName TEXT,
    DepartmentKey INTEGER NOT NULL,
    Program TEXT DEFAULT 'B.Tech',
    Batch TEXT DEFAULT '2021-2025',
    BacklogCount INTEGER DEFAULT 0,
    PreviousGPA REAL DEFAULT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (DepartmentKey) REFERENCES DimDepartment(DepartmentKey)
);

-- Fact Table: FactExamResult
-- Grain: One student assessment per subject per semester
CREATE TABLE IF NOT EXISTS FactExamResult (
    ResultKey INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentKey INTEGER NOT NULL,
    SubjectKey INTEGER NOT NULL,
    SemesterKey INTEGER NOT NULL,
    DepartmentKey INTEGER NOT NULL,
    DateKey INTEGER NOT NULL DEFAULT -1,
    InternalMarks REAL,
    MarksObtained REAL NOT NULL,
    MaximumMarks REAL NOT NULL DEFAULT 100.0,
    GradePoints REAL NOT NULL,
    Grade TEXT NOT NULL,
    Credits REAL NOT NULL,
    ResultStatus TEXT NOT NULL, -- 'Pass' or 'Fail'
    IsImputed BOOLEAN DEFAULT 0,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (StudentKey) REFERENCES DimStudent(StudentKey),
    FOREIGN KEY (SubjectKey) REFERENCES DimSubject(SubjectKey),
    FOREIGN KEY (SemesterKey) REFERENCES DimSemester(SemesterKey),
    FOREIGN KEY (DepartmentKey) REFERENCES DimDepartment(DepartmentKey),
    FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey),
    CONSTRAINT uq_exam_grain UNIQUE (StudentKey, SubjectKey, SemesterKey)
);

-- Fact Table: FactAttendance
-- Grain: One student attendance record per subject per semester
CREATE TABLE IF NOT EXISTS FactAttendance (
    AttendanceKey INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentKey INTEGER NOT NULL,
    SubjectKey INTEGER NOT NULL,
    SemesterKey INTEGER NOT NULL,
    DepartmentKey INTEGER NOT NULL,
    DateKey INTEGER NOT NULL DEFAULT -1,
    ClassesHeld INTEGER DEFAULT NULL,
    ClassesAttended INTEGER DEFAULT NULL,
    AttendancePercentage REAL NOT NULL,
    AttendanceCategory TEXT NOT NULL, -- 'Low (<75%)', 'Normal (75-85%)', 'High (>=85%)'
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (StudentKey) REFERENCES DimStudent(StudentKey),
    FOREIGN KEY (SubjectKey) REFERENCES DimSubject(SubjectKey),
    FOREIGN KEY (SemesterKey) REFERENCES DimSemester(SemesterKey),
    FOREIGN KEY (DepartmentKey) REFERENCES DimDepartment(DepartmentKey),
    FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey),
    CONSTRAINT uq_attendance_grain UNIQUE (StudentKey, SubjectKey, SemesterKey)
);

-- ETL Audit & Lineage Log
CREATE TABLE IF NOT EXISTS ETLAuditLog (
    LogId INTEGER PRIMARY KEY AUTOINCREMENT,
    BatchId TEXT NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Stage TEXT NOT NULL, -- 'Extract', 'Transform', 'Load'
    Action TEXT NOT NULL,
    RecordsAffected INTEGER DEFAULT 0,
    Details TEXT
);

-- Indexes for OLAP query performance and rapid roll-up / drill-down
CREATE INDEX IF NOT EXISTS idx_fer_student ON FactExamResult(StudentKey);
CREATE INDEX IF NOT EXISTS idx_fer_subject ON FactExamResult(SubjectKey);
CREATE INDEX IF NOT EXISTS idx_fer_semester ON FactExamResult(SemesterKey);
CREATE INDEX IF NOT EXISTS idx_fer_dept ON FactExamResult(DepartmentKey);
CREATE INDEX IF NOT EXISTS idx_fer_status ON FactExamResult(ResultStatus);

CREATE INDEX IF NOT EXISTS idx_fa_student ON FactAttendance(StudentKey);
CREATE INDEX IF NOT EXISTS idx_fa_subject ON FactAttendance(SubjectKey);
CREATE INDEX IF NOT EXISTS idx_fa_semester ON FactAttendance(SemesterKey);
CREATE INDEX IF NOT EXISTS idx_fa_dept ON FactAttendance(DepartmentKey);
CREATE INDEX IF NOT EXISTS idx_fa_category ON FactAttendance(AttendanceCategory);
