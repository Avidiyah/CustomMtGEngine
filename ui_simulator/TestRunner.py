import argparse
import json
import sys
import os
sys.path.append(os.path.abspath("../testing_tools"))

from testing_tools import OracleComplianceTestSuite
from testing_tools import OracleExecutionTestSuite


def load_test_data(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)


def run_compliance_tests():
    data = load_test_data("oracle_tests.json")
    parsed_trees = {card['card_name']: card['expected_output'] for card in data}
    OracleComplianceTestSuite.run_batch_validation(parsed_trees)


def run_simulation_tests():
    OracleExecutionTestSuite.run_all()


def main():
    print("\nRunning Oracle Compliance Test Suite...\n")
    run_compliance_tests()

    print("\nRunning Oracle Execution Test Suite...\n")
    run_simulation_tests()


if __name__ == "__main__":
    main()
