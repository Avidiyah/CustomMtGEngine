# === run_oracle_tests.py ===
# Entry point for running OracleTestSuite

from OracleTestSuite import OracleTestSuite

def main():
    suite = OracleTestSuite()
    suite.load_test_cases("oracle_tests.json")
    suite.run_all()
    summary = suite.summarize()

    print(f"\n[Oracle Test Suite Summary]")
    print(f"Total tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")

    if summary['failures']:
        print("\n[Failures]")
        for fail in summary['failures']:
            print(f"- Card: {fail['card']}")
            print(f"  Tree Issues: {fail.get('tree_issues', 'N/A')}")

if __name__ == "__main__":
    main()
