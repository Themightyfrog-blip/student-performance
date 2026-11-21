"""Tests for SciPy Statistical Correlation Analysis (Question 68)."""
import pytest
import pandas as pd
import numpy as np
from src.correlation import CorrelationAnalyzer


def test_perfect_linear_correlation():
    # Construct exact linear dataset: Marks = 0.8 * Attendance + 20
    att = np.array([50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    marks = 0.8 * att + 20.0
    df = pd.DataFrame({"AttendancePercentage": att, "MarksObtained": marks})

    analyzer = CorrelationAnalyzer()
    res = analyzer.analyze_attendance_vs_marks(df)

    assert res["error"] is None if "error" in res else True
    assert res["observations"] == 6
    # Pearson r should be exactly 1.0 (perfect positive linear correlation)
    assert pytest.approx(res["pearson_r"], 0.001) == 1.000
    assert res["strength"] == "Strong"
    assert res["direction"] == "Positive"
    assert res["pearson_p_value"] < 0.001


def test_zero_variance_constant_array_handled():
    # All attendance values identical -> zero variance
    df = pd.DataFrame({
        "AttendancePercentage": [75.0, 75.0, 75.0, 75.0],
        "MarksObtained": [40.0, 60.0, 70.0, 90.0]
    })
    analyzer = CorrelationAnalyzer()
    res = analyzer.analyze_attendance_vs_marks(df)
    assert "error" in res
    assert "zero variance" in res["error"].lower()


def test_insufficient_observations_handled():
    df = pd.DataFrame({
        "AttendancePercentage": [80.0, 90.0],
        "MarksObtained": [60.0, 70.0]
    })
    analyzer = CorrelationAnalyzer()
    res = analyzer.analyze_attendance_vs_marks(df)
    assert "error" in res
    assert "insufficient" in res["error"].lower()


def test_multivariable_correlation_matrix():
    df = pd.DataFrame({
        "AttendancePercentage": [60.0, 70.0, 80.0, 90.0, 95.0],
        "MarksObtained": [45.0, 55.0, 68.0, 82.0, 91.0],
        "InternalMarks": [22.0, 28.0, 34.0, 42.0, 46.0],
        "PreviousGPA": [5.5, 6.2, 7.1, 8.4, 9.0],
        "BacklogCount": [2, 1, 0, 0, 0]
    })
    analyzer = CorrelationAnalyzer()
    res = analyzer.compute_multivariable_matrix(df)
    assert "error" not in res
    assert res["matrix"].shape == (5, 5)
    # Diagonal must be 1.0
    for col in res["columns"]:
        assert res["matrix"].loc[col, col] == 1.0
