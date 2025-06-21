from OracleComplianceTestSuite import OracleComplianceTestSuite
from oracle_parser.OracleParser import oracle_tokenizer,match_oracle_phrases,parse_oracle_text_to_behavior_tree

# Initialize your parser
parser = IntegratedOracleParser()

# Initialize your test framework
test_framework = OracleTestFramework(parser)

# Example test: Parsing a card
example_card_name = "Divination"
example_oracle_text = "Draw two cards."
expected_behavior_structure = {
    "effect_chain": [{"action": "draw_card"}, {"action": "draw_card"}],
    "conditions": [],
    "targets": {},
    "zones": [],
    "timing": [],
    "modifiers": [],
    "repeat": False
}

test_framework.run_single_parsing_test(example_card_name, example_oracle_text, expected_behavior_structure)
