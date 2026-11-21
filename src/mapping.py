"""Column mapping, alias inference, and multi-file integration module.
Enables flexible schema normalization, join cardinality validation, and feature availability checks.
"""
import re
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

from config.settings import CANONICAL_COLUMNS


def normalize_string(s: str) -> str:
    """Normalize string by removing underscores, dashes, spaces, and converting to lowercase."""
    return re.sub(r"[^a-zA-Z0-9]", "", str(s)).lower()


class ColumnMapper:
    """Infers and manages mapping between source file columns and canonical academic warehouse fields."""

    @staticmethod
    def infer_mappings(columns: List[str]) -> Dict[str, Optional[str]]:
        """Automatically match source column names against canonical aliases.
        
        Returns:
            Dictionary mapping canonical_field_name -> matched_source_column (or None)
        """
        mappings: Dict[str, Optional[str]] = {canon: None for canon in CANONICAL_COLUMNS}
        normalized_cols = {col: normalize_string(col) for col in columns}

        for canon_name, info in CANONICAL_COLUMNS.items():
            aliases = [normalize_string(canon_name)] + [normalize_string(a) for a in info.get("aliases", [])]
            
            # Exact normalized match
            for src_col, norm_src in normalized_cols.items():
                if norm_src in aliases:
                    mappings[canon_name] = src_col
                    break

        return mappings

    @staticmethod
    def assess_feature_availability(mapped_fields: List[str]) -> Dict[str, Dict[str, Any]]:
        """Determine which DWDM PBL analysis modules are available based on mapped columns."""
        present = set(mapped_fields)
        
        availability = {
            "Star Schema & DW Load": {
                "available": "student_id" in present and "subject_id" in present and "semester" in present,
                "missing": [f for f in ["student_id", "subject_id", "semester"] if f not in present],
                "impact": "Core data warehouse requires student, subject, and semester keys."
            },
            "OLAP & Data Cube": {
                "available": "student_id" in present and "subject_id" in present and "semester" in present and "marks_obtained" in present,
                "missing": [f for f in ["student_id", "subject_id", "semester", "marks_obtained"] if f not in present],
                "impact": "Data cube and roll-ups require marks, student, and subject dimensions."
            },
            "Multi-Level Association Mining": {
                "available": "department" in present and "marks_obtained" in present and "subject_id" in present,
                "missing": [f for f in ["department", "marks_obtained", "subject_id"] if f not in present],
                "impact": "Requires Department, Subject, and Performance (marks) for hierarchical rule discovery."
            },
            "Constraint-Based Mining (<75% Att)": {
                "available": "marks_obtained" in present and ("attendance_pct" in present or ("classes_held" in present and "classes_attended" in present)),
                "missing": [f for f in ["marks_obtained", "attendance_pct"] if f not in present],
                "impact": "Constraint-based mining requires attendance percentage to filter <75% cohort."
            },
            "Decision Tree Classification": {
                "available": "marks_obtained" in present and (
                    "internal_marks" in present or "attendance_pct" in present or "previous_gpa" in present or "backlog_count" in present
                ),
                "missing": [f for f in ["marks_obtained", "internal_marks/attendance_pct/previous_gpa"] if f not in present],
                "impact": "Requires outcome target (marks) and at least one pre-exam predictor to avoid target leakage."
            },
            "Statistical Correlation": {
                "available": "marks_obtained" in present and ("attendance_pct" in present or ("classes_held" in present and "classes_attended" in present)),
                "missing": [f for f in ["marks_obtained", "attendance_pct"] if f not in present],
                "impact": "Pearson and Spearman correlation require numeric attendance and exam marks."
            },
            "Early-Warning Risk Center": {
                "available": "student_id" in present and (
                    "attendance_pct" in present or "internal_marks" in present or "backlog_count" in present
                ),
                "missing": [f for f in ["student_id", "attendance_pct/internal_marks"] if f not in present],
                "impact": "Early warning triage requires student IDs and early risk indicators."
            }
        }
        return availability

    @staticmethod
    def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Rename columns according to confirmed canonical mapping.
        
        Args:
            df: Input source DataFrame
            mapping: Dict of {canonical_name: source_column_name}
        """
        # Invert mapping: source_column -> canonical_name
        rename_dict = {}
        for canon, src in mapping.items():
            if src and src in df.columns:
                rename_dict[src] = canon

        mapped_df = df.rename(columns=rename_dict).copy()
        return mapped_df

    @staticmethod
    def validate_and_join_datasets(
        dfs: Dict[str, pd.DataFrame],
        join_configs: List[Dict[str, Any]]
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Safely join multiple relational datasets with join cardinality checks
        to prevent silent Cartesian product row inflation.
        """
        warnings = []
        if not dfs:
            return None, ["No dataframes provided for joining."]

        base_name = join_configs[0]["base_table"] if join_configs else list(dfs.keys())[0]
        merged_df = dfs[base_name].copy()

        for config in join_configs:
            right_name = config["target_table"]
            if right_name not in dfs:
                continue

            right_df = dfs[right_name]
            left_keys = config["left_keys"]
            right_keys = config["right_keys"]
            how = config.get("how", "left")

            # Check keys exist
            missing_left = [k for k in left_keys if k not in merged_df.columns]
            missing_right = [k for k in right_keys if k not in right_df.columns]
            if missing_left or missing_right:
                warnings.append(f"Join between {base_name} and {right_name} skipped due to missing keys: {missing_left + missing_right}")
                continue

            # Check cardinality: is right_df unique on right_keys?
            right_dups = right_df.duplicated(subset=right_keys).sum()
            if right_dups > 0 and how in ["left", "inner"]:
                warnings.append(
                    f"Warning: Joining on non-unique key in '{right_name}' ({right_dups} duplicate keys). "
                    "This may duplicate fact records. Consider aggregating or cleaning duplicates first."
                )

            merged_df = pd.merge(
                merged_df,
                right_df,
                left_on=left_keys,
                right_on=right_keys,
                how=how,
                suffixes=("", f"_{right_name}")
            )

        return merged_df, warnings
