"""Statistical Correlation Analysis Module (Question 68).
Computes Pearson and Spearman rank correlation between attendance and performance using SciPy,
generates correlation matrices, calculates p-values, and explains statistical vs causal implications.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from scipy import stats

from database.warehouse import DataWarehouse, warehouse


class CorrelationAnalyzer:
    """Executes genuine statistical correlation tests and multidimensional correlation heatmaps."""

    def __init__(self, target_warehouse: Optional[DataWarehouse] = None):
        self.warehouse = target_warehouse or warehouse

    def analyze_attendance_vs_marks(
        self,
        df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Compute Pearson and Spearman correlation between Attendance Percentage and Final Marks Obtained."""
        data = df if df is not None else self.warehouse.get_integrated_dataset()
        if data.empty:
            return {"error": "Warehouse dataset is empty."}

        if "AttendancePercentage" not in data.columns or "MarksObtained" not in data.columns:
            return {"error": "Dataset must contain both 'AttendancePercentage' and 'MarksObtained' columns."}

        # Drop NaNs and ensure numeric
        clean_df = data[["AttendancePercentage", "MarksObtained"]].dropna().copy()
        clean_df["AttendancePercentage"] = pd.to_numeric(clean_df["AttendancePercentage"], errors="coerce")
        clean_df["MarksObtained"] = pd.to_numeric(clean_df["MarksObtained"], errors="coerce")
        clean_df = clean_df.dropna()

        n_obs = len(clean_df)
        if n_obs < 3:
            return {"error": f"Insufficient complete paired observations (only {n_obs} found; minimum 3 required)."}

        att_vals = clean_df["AttendancePercentage"].values
        marks_vals = clean_df["MarksObtained"].values

        # Check for constant arrays (zero variance)
        if np.std(att_vals) == 0 or np.std(marks_vals) == 0:
            return {
                "error": "Cannot compute correlation because one of the variables has zero variance (constant values).",
                "observations": n_obs
            }

        # Pearson correlation
        pearson_res = stats.pearsonr(att_vals, marks_vals)
        pearson_r = float(pearson_res.statistic)
        pearson_p = float(pearson_res.pvalue)

        # Spearman rank correlation
        spearman_res = stats.spearmanr(att_vals, marks_vals)
        spearman_rho = float(spearman_res.statistic)
        spearman_p = float(spearman_res.pvalue)

        # Linear regression trendline slope & intercept
        slope, intercept, r_val, p_val, std_err = stats.linregress(att_vals, marks_vals)

        # Interpret correlation strength
        abs_r = abs(pearson_r)
        if abs_r >= 0.7:
            strength = "Strong"
        elif abs_r >= 0.4:
            strength = "Moderate"
        elif abs_r >= 0.2:
            strength = "Weak"
        else:
            strength = "Negligible"

        direction = "Positive" if pearson_r > 0 else "Negative"

        interpretation = (
            f"A {strength.lower()} {direction.lower()} linear relationship (r = {pearson_r:.3f}, p = {pearson_p:.2e}) "
            f"is observed across {n_obs} student observations. "
            f"{'The relationship is statistically significant at p < 0.05.' if pearson_p < 0.05 else 'The relationship is not statistically significant at p < 0.05.'} "
            "Note: Statistical correlation demonstrates co-movement, not causal proof that attendance directly causes marks."
        )

        return {
            "observations": n_obs,
            "pearson_r": round(pearson_r, 4),
            "pearson_p_value": pearson_p,
            "spearman_rho": round(spearman_rho, 4),
            "spearman_p_value": spearman_p,
            "strength": strength,
            "direction": direction,
            "slope": round(float(slope), 4),
            "intercept": round(float(intercept), 4),
            "trendline_r2": round(float(r_val**2), 4),
            "interpretation": interpretation,
            "data_sample": clean_df
        }

    def compute_multivariable_matrix(
        self,
        df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Compute full pairwise correlation matrix for all numeric academic variables."""
        data = df if df is not None else self.warehouse.get_integrated_dataset()
        if data.empty:
            return {"error": "Warehouse dataset is empty."}

        numeric_candidates = [
            "AttendancePercentage", "MarksObtained", "InternalMarks",
            "PreviousGPA", "BacklogCount", "Credits", "GradePoints"
        ]
        available_numeric = [col for col in numeric_candidates if col in data.columns]

        if len(available_numeric) < 2:
            return {"error": "Not enough numeric academic columns available for multi-variable correlation matrix."}

        clean_sub = data[available_numeric].apply(pd.to_numeric, errors="coerce").dropna()
        if len(clean_sub) < 3:
            return {"error": "Not enough complete observations across numeric variables."}

        corr_matrix = clean_sub.corr(method="pearson").round(3)
        return {
            "columns": available_numeric,
            "matrix": corr_matrix,
            "observations": len(clean_sub)
        }
