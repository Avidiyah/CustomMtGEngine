# === OracleTestSuite.py ===
# Phase 3.1 — Automated Oracle Text → Behavior Tree → Validation Tests

import json
from OracleParser import OracleParser
from data_layer.CardDataManager import CardDataManager
from TreeValidator import TreeValidator

class OracleTestSuite:
    def __init__(self, test_cases=None):
        self.parser = OracleParser()
        self.card_loader = CardDataManager()
        self.tree_validator = TreeValidator()
        self.test_cases = test_cases if test_cases else []
        self.results = []

    def load_test_cases(self, filepath):
        with open(filepath, 'r') as f:
            self.test_cases = json.load(f)

    def run_all(self):
        for case in self.test_cases:
            result = self.run_single(case)
            self.results.append(result)

    def run_single(self, case):
        card_name = case["card"]
        expected_tree = case.get("expected_tree")

        card = self.card_loader.get_card_by_name(card_name)
        self.parser.parse_oracle_text(card, card.oracle_text)
        parsed_tree = card.behavior_tree

        tree_issues = self.tree_validator.validate(parsed_tree, card_name)
        tree_valid = len(tree_issues) == 0

        structure_check_passed = True
        if expected_tree:
            structure_check_passed = self.compare_trees(parsed_tree, expected_tree)

        passed = tree_valid and structure_check_passed

        return {
            "card": card_name,
            "passed": passed,
            "parsed": parsed_tree,
            "expected": expected_tree,
            "tree_issues": tree_issues
        }


    def compare_trees(self, actual, expected):
        return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)

    def summarize(self):
        passed = [r for r in self.results if r["passed"]]
        failed = [r for r in self.results if not r["passed"]]
        return {
            "total": len(self.results),
            "passed": len(passed),
            "failed": len(failed),
            "failures": failed
        }
