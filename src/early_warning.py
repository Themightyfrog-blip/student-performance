"""AI Early-Warning Decision Support and Student Triage Center (Question 70).
Generates risk assessments, prioritizes high-risk alerts, provides actionable intervention
guidance, and supports faculty review workflows without making definitive academic judgments.
"""
from typing import Dict, List, Optional, Any
import pandas as pd
from database.warehouse import DataWarehouse, warehouse
from src.decision_tree import AcademicRiskClassifier


class EarlyWarningCenter:
    """Manages student risk triage, intervention tracking, and early alerts."""

    def __init__(self, classifier: Optional[AcademicRiskClassifier] = None):
        self.classifier = classifier or AcademicRiskClassifier()
        # In-memory tracking of faculty review status overrides
        self.status_overrides: Dict[str, str] = {}

    def get_triage_dashboard(self) -> Dict[str, Any]:
        """Generate high-level triage metrics and filtered student risk cohorts."""
        if not self.classifier.is_trained:
            # Auto-train if possible
            metrics = self.classifier.train_and_evaluate()
            if "error" in metrics:
                return {"error": metrics["error"]}

        try:
            predictions_df = self.classifier.predict_cohort_risk()
        except Exception as e:
            return {"error": str(e)}

        if predictions_df.empty:
            return {"error": "No students found to evaluate."}

        # Apply any recorded faculty status updates
        for s_id, status in self.status_overrides.items():
            mask = predictions_df["StudentID"] == s_id
            if mask.any():
                predictions_df.loc[mask, "Faculty_Review_Status"] = status

        total_students = len(predictions_df)
        fail_cohort = predictions_df[predictions_df["Predicted_Risk_Category"] == "Fail"]
        at_risk_cohort = predictions_df[predictions_df["Predicted_Risk_Category"] == "At-Risk"]
        pass_cohort = predictions_df[predictions_df["Predicted_Risk_Category"] == "Pass"]

        critical_count = len(fail_cohort)
        at_risk_count = len(at_risk_cohort)
        safe_count = len(pass_cohort)

        # Department-wise risk breakdown
        dept_risk = predictions_df.groupby(["Department", "Predicted_Risk_Category"]).size().unstack(fill_value=0).reset_index()

        return {
            "total_students_assessed": total_students,
            "critical_risk_count": critical_count,
            "at_risk_count": at_risk_count,
            "on_track_count": safe_count,
            "risk_percentage": round(((critical_count + at_risk_count) / max(1, total_students)) * 100.0, 1),
            "predictions_df": predictions_df,
            "critical_cohort": fail_cohort,
            "at_risk_cohort": at_risk_cohort,
            "department_breakdown": dept_risk
        }

    def update_student_review_status(self, student_id: str, new_status: str) -> None:
        """Update faculty review action status for a student."""
        self.status_overrides[student_id] = new_status
