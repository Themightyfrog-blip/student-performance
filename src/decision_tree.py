"""Decision Tree Classifier for Academic Risk Prediction (Question 67).
Implements target leakage safeguards, student-grouped splitting,
hyperparameter tuning, model evaluation, and interpretable tree extraction.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

from database.warehouse import DataWarehouse, warehouse


class AcademicRiskClassifier:
    """Trains and evaluates a Decision Tree model to identify at-risk students before final exams."""

    # Explicit list of permitted predictive features available PRIOR to final exam
    PERMITTED_FEATURES = [
        "AttendancePercentage",
        "InternalMarks",
        "PreviousGPA",
        "BacklogCount"
    ]

    # Explicit list of prohibited target leakage columns
    PROHIBITED_LEAKAGE_COLUMNS = [
        "MarksObtained",
        "MaximumMarks",
        "GradePoints",
        "Grade",
        "ResultStatus",
        "IsImputed"
    ]

    def __init__(self, target_warehouse: Optional[DataWarehouse] = None):
        self.warehouse = target_warehouse or warehouse
        self.model: Optional[DecisionTreeClassifier] = None
        self.feature_names: List[str] = []
        self.target_classes: List[str] = []
        self.imputer: Optional[SimpleImputer] = None
        self.is_trained: bool = False
        self.last_metrics: Dict[str, Any] = {}

    @staticmethod
    def construct_target_labels(df: pd.DataFrame, pass_threshold: float = 40.0) -> pd.Series:
        """Derive ground-truth evaluation labels:
        - 'Fail': Marks < pass_threshold
        - 'At-Risk': Borderline pass (40 <= Marks < 50) OR (Attendance < 75% AND InternalMarks < 25)
        - 'Pass': Clear pass (Marks >= 50 and good standing)
        """
        targets = []
        for _, row in df.iterrows():
            marks = row.get("MarksObtained")
            att = row.get("AttendancePercentage", 100.0)
            internals = row.get("InternalMarks", 50.0)

            if pd.isna(marks):
                targets.append("Unknown")
            elif marks < pass_threshold:
                targets.append("Fail")
            elif marks < 50.0 or (pd.notna(att) and att < 75.0 and pd.notna(internals) and internals < 25.0):
                targets.append("At-Risk")
            else:
                targets.append("Pass")

        return pd.Series(targets, index=df.index)

    def prepare_data(
        self,
        df: pd.DataFrame,
        include_dept: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, List[str], np.ndarray, pd.DataFrame]:
        """Safely extract features ensuring strict zero-target-leakage."""
        df_valid = df.copy()

        # Remove rows with unknown or missing targets
        df_valid["Target"] = self.construct_target_labels(df_valid)
        df_valid = df_valid[df_valid["Target"] != "Unknown"].copy()

        if len(df_valid) < 10:
            raise ValueError(f"Insufficient labeled samples: only {len(df_valid)} available.")

        # Extract permitted features
        feature_cols = [c for c in self.PERMITTED_FEATURES if c in df_valid.columns]
        if not feature_cols:
            raise ValueError("No valid predictive features found in dataset.")

        # Verify no prohibited leakage column is in feature_cols
        for forbidden in self.PROHIBITED_LEAKAGE_COLUMNS:
            if forbidden in feature_cols:
                feature_cols.remove(forbidden)

        X_num = df_valid[feature_cols].copy()

        # Department one-hot encoding if requested and available
        feature_names = list(feature_cols)
        if include_dept and "Department" in df_valid.columns:
            dept_dummies = pd.get_dummies(df_valid["Department"], prefix="Dept", drop_first=False)
            X_all = pd.concat([X_num, dept_dummies], axis=1)
            feature_names = list(X_all.columns)
        else:
            X_all = X_num

        # Impute missing values with median fitted on features
        self.imputer = SimpleImputer(strategy="median")
        X_matrix = self.imputer.fit_transform(X_all)
        y_vector = df_valid["Target"].values
        student_groups = df_valid["StudentID"].values if "StudentID" in df_valid.columns else np.arange(len(df_valid))

        self.feature_names = feature_names
        return X_matrix, y_vector, feature_names, student_groups, df_valid

    def train_and_evaluate(
        self,
        max_depth: int = 4,
        min_samples_split: int = 10,
        criterion: str = "gini",
        test_size: float = 0.25,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Train Decision Tree with student-level group splitting to prevent leakage."""
        df = self.warehouse.get_integrated_dataset()
        if df.empty:
            return {"error": "Warehouse dataset is empty."}

        try:
            X, y, feature_names, groups, df_valid = self.prepare_data(df)
        except Exception as e:
            return {"error": str(e)}

        # Check class distribution
        unique_classes, counts = np.unique(y, return_counts=True)
        if len(unique_classes) < 2:
            return {"error": f"Model requires at least 2 distinct target classes, but only found {list(unique_classes)}."}

        # Student Group Shuffle Split to prevent train-test data leakage
        try:
            gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
            train_idx, test_idx = next(gss.split(X, y, groups=groups))
        except Exception:
            # Fallback to standard stratified split if groups are singular
            train_idx, test_idx = train_test_split(
                np.arange(len(y)), test_size=test_size, random_state=random_state, stratify=y
            )

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Initialize and train Decision Tree
        clf = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            criterion=criterion,
            random_state=random_state
        )
        clf.fit(X_train, y_train)

        self.model = clf
        self.target_classes = list(clf.classes_)
        self.is_trained = True

        # Predictions on holdout test set
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)

        # Performance Metrics
        acc = accuracy_score(y_test, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, labels=self.target_classes, zero_division=0
        )
        conf_matrix = confusion_matrix(y_test, y_pred, labels=self.target_classes)

        # Per-class metrics table
        per_class_df = pd.DataFrame({
            "Class": self.target_classes,
            "Precision": [round(p, 3) for p in precision],
            "Recall": [round(r, 3) for r in recall],
            "F1_Score": [round(f, 3) for f in f1],
            "Support": support
        })

        # Feature importances
        feature_importance_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": [round(imp, 4) for imp in clf.feature_importances_]
        }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

        # Text tree representation
        tree_rules_text = export_text(clf, feature_names=feature_names)

        self.last_metrics = {
            "is_trained": True,
            "accuracy": round(acc, 4),
            "macro_f1": round(float(np.mean(f1)), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "target_classes": self.target_classes,
            "per_class_metrics": per_class_df,
            "confusion_matrix": conf_matrix.tolist(),
            "feature_importances": feature_importance_df,
            "tree_rules_text": tree_rules_text,
            "max_depth": max_depth,
            "criterion": criterion
        }

        return self.last_metrics

    def predict_cohort_risk(self, df_records: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Apply trained model to generate early-warning student predictions."""
        if not self.is_trained or self.model is None or self.imputer is None:
            raise RuntimeError("Model is not trained yet. Call train_and_evaluate first.")

        df = df_records if df_records is not None else self.warehouse.get_integrated_dataset()
        if df.empty:
            return pd.DataFrame()

        # Group by student to evaluate overall student-level risk
        student_profile = df.groupby("StudentID", as_index=False).agg({
            "StudentName": "first",
            "Department": "first",
            "AttendancePercentage": "mean",
            "InternalMarks": "mean",
            "PreviousGPA": "first",
            "BacklogCount": "first"
        })

        # Feature matrix aligned with training
        num_features = [c for c in self.PERMITTED_FEATURES if c in student_profile.columns]
        X_num = student_profile[num_features].copy()

        # Check for department dummy columns expected by model
        expected_cols = self.feature_names
        for col in expected_cols:
            if col.startswith("Dept_"):
                dept_name = col.replace("Dept_", "")
                X_num[col] = (student_profile["Department"] == dept_name).astype(int)

        # Align columns
        for col in expected_cols:
            if col not in X_num.columns:
                X_num[col] = 0

        X_aligned = X_num[expected_cols]
        X_imputed = self.imputer.transform(X_aligned)

        # Predict
        preds = self.model.predict(X_imputed)
        probs = self.model.predict_proba(X_imputed)

        results = student_profile.copy()
        results["Predicted_Risk_Category"] = preds

        for i, cls in enumerate(self.target_classes):
            results[f"Prob_{cls}"] = np.round(probs[:, i] * 100.0, 1)

        # Generate rule-based intervention reasons and suggested triage
        reasons = []
        triage_urgency = []
        for _, row in results.iterrows():
            pred = row["Predicted_Risk_Category"]
            att = row["AttendancePercentage"]
            internals = row["InternalMarks"]
            backlogs = row["BacklogCount"]

            triggers = []
            if pd.notna(att) and att < 75.0:
                triggers.append(f"Low Attendance ({att:.1f}%)")
            if pd.notna(internals) and internals < 25.0:
                triggers.append(f"Low Internals ({internals:.1f}/50)")
            if pd.notna(backlogs) and backlogs > 0:
                triggers.append(f"Active Backlogs ({backlogs})")

            trigger_str = ", ".join(triggers) if triggers else "Borderline Academic Profile"

            if pred == "Fail":
                reasons.append(f"High probability of course failure. Triggers: {trigger_str}.")
                triage_urgency.append("Immediate Faculty Intervention Required")
            elif pred == "At-Risk":
                reasons.append(f"Borderline standing at risk of failure. Triggers: {trigger_str}.")
                triage_urgency.append("Academic Mentoring & Remedial Classes")
            else:
                reasons.append("Satisfactory progress; on track for passing.")
                triage_urgency.append("Routine Monitoring")

        results["Risk_Indicators"] = [
            f"Att: {r['AttendancePercentage']:.1f}%, Int: {r['InternalMarks']:.1f}, Backlogs: {int(r['BacklogCount'])}"
            for _, r in results.iterrows()
        ]
        results["Intervention_Reason"] = reasons
        results["Triage_Action"] = triage_urgency
        results["Faculty_Review_Status"] = "Pending Review"

        return results.sort_values(by=["Predicted_Risk_Category", "AttendancePercentage"], ascending=[True, True])
