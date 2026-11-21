"""Association Rule Mining Engine for Academic Performance.
Implements:
1. Multi-Level Association Rule Mining (Level 1: Department -> Result; Level 2: Subject -> Grade)
2. Constraint-Based Mining (Question 65: Attendance < threshold subset mining)
3. Apriori Algorithm (Question 66: Frequent itemsets and rules with mlxtend)
"""
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

try:
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder
    MLXTEND_AVAILABLE = True
except ImportError:
    MLXTEND_AVAILABLE = False

from database.warehouse import DataWarehouse, warehouse


class AcademicAssociationMiner:
    """Performs multi-level, constraint-based, and standard Apriori association mining."""

    def __init__(self, target_warehouse: Optional[DataWarehouse] = None):
        self.warehouse = target_warehouse or warehouse

    def get_data(self) -> pd.DataFrame:
        return self.warehouse.get_integrated_dataset()

    # =========================================================================
    # TRANSACTION BUILDERS
    # =========================================================================

    def build_apriori_transactions(self, df: pd.DataFrame) -> List[List[str]]:
        """Construct discrete transaction items from student performance records.
        Items:
        - Attendance: Low_Attendance (<75%), Normal_Attendance (75-85%), High_Attendance (>=85%)
        - Result: Failed_Subject, Passed_Subject
        - Backlogs: Backlog_Zero, Backlog_Low (1-2), Backlog_High (>=3)
        - GPA: GPA_Low (<6.0), GPA_Medium (6.0-8.0), GPA_High (>8.0)
        """
        transactions = []
        for _, row in df.iterrows():
            itemset = []
            
            # Attendance Item
            att = row.get("AttendancePercentage")
            if pd.notna(att):
                if att < 75.0:
                    itemset.append("Low_Attendance (<75%)")
                elif att < 85.0:
                    itemset.append("Normal_Attendance (75-85%)")
                else:
                    itemset.append("High_Attendance (>=85%)")

            # Exam Result Item
            status = row.get("ResultStatus")
            if status == "Pass":
                itemset.append("Passed_Subject")
            elif status == "Fail":
                itemset.append("Failed_Subject")

            # Backlog Category Item
            backlogs = row.get("BacklogCount")
            if pd.notna(backlogs):
                b = int(backlogs)
                if b == 0:
                    itemset.append("Backlog_Zero")
                elif b <= 2:
                    itemset.append("Backlog_Low (1-2)")
                else:
                    itemset.append("Backlog_High (>=3)")

            # Previous GPA Item
            gpa = row.get("PreviousGPA")
            if pd.notna(gpa):
                g = float(gpa)
                if g < 6.0:
                    itemset.append("Prior_GPA_Low (<6.0)")
                elif g <= 8.0:
                    itemset.append("Prior_GPA_Medium (6.0-8.0)")
                else:
                    itemset.append("Prior_GPA_High (>8.0)")

            if len(itemset) >= 2:
                transactions.append(itemset)

        return transactions

    def build_level1_transactions(self, df: pd.DataFrame) -> List[List[str]]:
        """Level 1 Concept Hierarchy: Department -> Result Category.
        Items: Dept_{Name}, Result_{Status}, Attendance_{Cat}
        """
        transactions = []
        for _, row in df.iterrows():
            itemset = []
            dept = row.get("Department")
            if pd.notna(dept) and str(dept).strip():
                itemset.append(f"Dept_{str(dept).replace(' ', '_')}")

            status = row.get("ResultStatus")
            if pd.notna(status):
                itemset.append(f"Result_{status}")

            att_cat = row.get("AttendanceCategory")
            if pd.notna(att_cat):
                itemset.append(f"Attendance_{att_cat.split(' ')[0]}")

            if len(itemset) >= 2:
                transactions.append(itemset)
        return transactions

    def build_level2_transactions(self, df: pd.DataFrame) -> List[List[str]]:
        """Level 2 Concept Hierarchy: Subject -> Grade Category.
        Items: Subject_{ID}, Grade_{Letter}, Attendance_{Cat}
        """
        transactions = []
        for _, row in df.iterrows():
            itemset = []
            sub = row.get("SubjectID")
            if pd.notna(sub) and str(sub).strip():
                itemset.append(f"Subject_{sub}")

            grade = row.get("Grade")
            if pd.notna(grade):
                itemset.append(f"Grade_{grade}")

            att_cat = row.get("AttendanceCategory")
            if pd.notna(att_cat):
                itemset.append(f"Attendance_{att_cat.split(' ')[0]}")

            if len(itemset) >= 2:
                transactions.append(itemset)
        return transactions

    # =========================================================================
    # CORE APRIORI & RULE MINING ENGINE
    # =========================================================================

    def mine_association_rules(
        self,
        transactions: List[List[str]],
        min_support: float = 0.05,
        min_confidence: float = 0.3,
        min_lift: float = 1.0,
        max_len: int = 4
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[str]]:
        """Execute Apriori algorithm and generate association rules.
        
        Returns:
            Tuple of (frequent_itemsets_df, association_rules_df, error_message)
        """
        if not MLXTEND_AVAILABLE:
            return pd.DataFrame(), pd.DataFrame(), "mlxtend library is not available in the environment."

        if not transactions or len(transactions) < 5:
            return pd.DataFrame(), pd.DataFrame(), f"Insufficient transactions for mining (only {len(transactions)} found; minimum 5 required)."

        try:
            # 1. One-hot encode transactions
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

            # 2. Generate Frequent Itemsets
            frequent_itemsets = apriori(
                df_encoded,
                min_support=min_support,
                use_colnames=True,
                max_len=max_len
            )

            if frequent_itemsets.empty:
                return pd.DataFrame(), pd.DataFrame(), f"No frequent itemsets found at min_support = {min_support:.3f}. Try lowering minimum support."

            # Add itemset length column
            frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(lambda x: len(x))
            frequent_itemsets["itemsets_str"] = frequent_itemsets["itemsets"].apply(lambda s: ", ".join(sorted(list(s))))

            # 3. Generate Association Rules
            rules = association_rules(
                frequent_itemsets,
                metric="confidence",
                min_threshold=min_confidence
            )

            if rules.empty:
                return frequent_itemsets, pd.DataFrame(), f"Frequent itemsets found ({len(frequent_itemsets)}), but no rules met min_confidence = {min_confidence:.2f}."

            # Filter by lift
            rules = rules[rules["lift"] >= min_lift].copy()
            if rules.empty:
                return frequent_itemsets, pd.DataFrame(), f"Rules found, but none met min_lift = {min_lift:.2f}."

            # Format antecedents and consequents into readable strings
            rules["antecedents_str"] = rules["antecedents"].apply(lambda s: ", ".join(sorted(list(s))))
            rules["consequents_str"] = rules["consequents"].apply(lambda s: ", ".join(sorted(list(s))))
            rules["rule_representation"] = rules["antecedents_str"] + " => " + rules["consequents_str"]

            # Sort by lift descending
            rules = rules.sort_values(by=["lift", "confidence"], ascending=[False, False]).reset_index(drop=True)

            return frequent_itemsets, rules, None

        except Exception as e:
            return pd.DataFrame(), pd.DataFrame(), f"Apriori mining error: {str(e)}"

    # =========================================================================
    # MULTI-LEVEL ASSOCIATION MINING (Section 7)
    # =========================================================================

    def run_multilevel_mining(
        self,
        min_support_lvl1: float = 0.05,
        min_confidence_lvl1: float = 0.3,
        min_support_lvl2: float = 0.02,
        min_confidence_lvl2: float = 0.3,
        min_lift: float = 1.0
    ) -> Dict[str, Any]:
        """Perform multi-level association rule mining across concept hierarchies."""
        df = self.get_data()
        if df.empty:
            return {"error": "Warehouse dataset is empty."}

        # Level 1: Department -> Result
        tx_lvl1 = self.build_level1_transactions(df)
        itemsets_lvl1, rules_lvl1, err_lvl1 = self.mine_association_rules(
            tx_lvl1,
            min_support=min_support_lvl1,
            min_confidence=min_confidence_lvl1,
            min_lift=min_lift
        )

        # Level 2: Subject -> Grade
        tx_lvl2 = self.build_level2_transactions(df)
        itemsets_lvl2, rules_lvl2, err_lvl2 = self.mine_association_rules(
            tx_lvl2,
            min_support=min_support_lvl2,
            min_confidence=min_confidence_lvl2,
            min_lift=min_lift
        )

        return {
            "level1": {
                "name": "Level 1: Department -> Result Category",
                "transaction_count": len(tx_lvl1),
                "itemsets": itemsets_lvl1,
                "rules": rules_lvl1,
                "error": err_lvl1,
                "hierarchy": "University -> Department -> Result (Coarse Grain)"
            },
            "level2": {
                "name": "Level 2: Subject -> Grade Category",
                "transaction_count": len(tx_lvl2),
                "itemsets": itemsets_lvl2,
                "rules": rules_lvl2,
                "error": err_lvl2,
                "hierarchy": "Department -> Subject -> Grade (Fine Grain)"
            }
        }

    # =========================================================================
    # CONSTRAINT-BASED MINING: ATTENDANCE < 75% (Question 65)
    # =========================================================================

    def run_constraint_mining(
        self,
        attendance_threshold: float = 75.0,
        min_support: float = 0.05,
        min_confidence: float = 0.3,
        min_lift: float = 1.0
    ) -> Dict[str, Any]:
        """Implement Question 65: Restrict analysis to students with attendance below threshold.
        Computes both conditional support within subset and global support in full dataset.
        """
        full_df = self.get_data()
        if full_df.empty:
            return {"error": "No data available in warehouse."}

        total_records_full = len(full_df)
        total_students_full = full_df["StudentID"].nunique()

        # Apply constraint: Attendance < threshold
        eligible_df = full_df[full_df["AttendancePercentage"] < attendance_threshold].copy()
        eligible_records = len(eligible_df)
        eligible_students = eligible_df["StudentID"].nunique()

        if eligible_records < 5:
            return {
                "error": f"Only {eligible_records} records found with attendance < {attendance_threshold}%. Minimum 5 required.",
                "total_students_full": total_students_full,
                "eligible_students": eligible_students,
                "eligible_records": eligible_records
            }

        # Build transactions on eligible subset
        transactions_subset = self.build_apriori_transactions(eligible_df)
        itemsets, rules, err = self.mine_association_rules(
            transactions_subset,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift
        )

        if not rules.empty:
            # Distinguish conditional support from full-population support:
            # Global Support = (Support_in_subset * Subset_Records) / Full_Records
            subset_ratio = eligible_records / total_records_full
            rules["conditional_support_pct"] = (rules["support"] * 100.0).round(2)
            rules["global_support_pct"] = (rules["support"] * subset_ratio * 100.0).round(2)
            rules["confidence_pct"] = (rules["confidence"] * 100.0).round(2)
            rules["lift"] = rules["lift"].round(2)

        return {
            "attendance_threshold": attendance_threshold,
            "total_students_full": total_students_full,
            "total_records_full": total_records_full,
            "eligible_students": eligible_students,
            "eligible_records": eligible_records,
            "subset_percentage": round((eligible_records / total_records_full) * 100.0, 2),
            "transactions_count": len(transactions_subset),
            "itemsets": itemsets,
            "rules": rules,
            "error": err
        }

    # =========================================================================
    # QUESTION 66: APRIORI PERFORMANCE & BACKLOG MINING
    # =========================================================================

    def run_apriori_backlog_mining(
        self,
        min_support: float = 0.05,
        min_confidence: float = 0.3,
        min_lift: float = 1.0
    ) -> Dict[str, Any]:
        """Implement Question 66: Apriori frequent patterns for attendance, backlogs, and results."""
        df = self.get_data()
        if df.empty:
            return {"error": "Warehouse dataset is empty."}

        transactions = self.build_apriori_transactions(df)
        itemsets, rules, err = self.mine_association_rules(
            transactions,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift
        )

        return {
            "transaction_count": len(transactions),
            "itemsets": itemsets,
            "rules": rules,
            "error": err
        }
