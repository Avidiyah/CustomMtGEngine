"""Command line entry points for running engine tests.

This module exposes thin wrappers around the various test suites in
:mod:`testing_tools`.  It is intentionally lightweight so tests can be
invoked programmatically or via ``python -m ui_simulator.TestRunner``.
"""

from __future__ import annotations

import argparse
import json

from testing_tools import OracleComplianceTestSuite, OracleExecutionTestSuite


def run_oracle_tests() -> None:
    """Validate Oracle parsing against ``oracle_tests.json``."""
    with open("oracle_tests.json", "r") as fh:
        records = json.load(fh)
    tests = {c["card_name"]: c["expected_output"] for c in records}
    OracleComplianceTestSuite.run_batch_validation(tests)

    
def run_execution_tests() -> None:
    """Execute stack resolution tests defined in ``simulation_tests.json``."""
    OracleExecutionTestSuite.run_all()


def run_integration_tests() -> None:
    """Placeholder for higher level end-to-end simulations."""
    OracleComplianceTestSuite.run_batch_validation(parsed_trees)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run engine test suites")
    parser.add_argument(
        "suite",
        choices=["oracle", "execution", "integration"],
        help="Which suite to run",
    )
    args = parser.parse_args(argv)

    if args.suite == "oracle":
        run_oracle_tests()
    elif args.suite == "execution":
        run_execution_tests()
    else:
        run_integration_tests()

if __name__ == "__main__":
    main()
