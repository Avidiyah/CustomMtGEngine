import json

class OracleComplianceTestSuite:
    KNOWN_EFFECT_ACTIONS = {
        "draw_card", "create_token", "destroy", "deal_damage", "gain_life",
        "lose_life", "scry", "mill", "exile", "return_to_hand", "shuffle_library",
        "sacrifice", "tap", "untap", "add_mana", "counter", "put_counter",
        "reveal", "discard", "look_at", "fight", "transform"
    }

    @staticmethod
    def validate_tree(parsed_tree):
        assert isinstance(parsed_tree, dict), "Parsed tree must be a dictionary"

        # Validate effect_chain
        effect_chain = parsed_tree.get("effect_chain", [])
        assert isinstance(effect_chain, list), "effect_chain must be a list"
        assert len(effect_chain) > 0, "effect_chain must not be empty"

        for effect in effect_chain:
            assert "action" in effect, f"Effect missing action field: {effect}"
            assert effect["action"] in OracleComplianceTestSuite.KNOWN_EFFECT_ACTIONS, \
                f"Unknown effect action: {effect['action']}"

        # Validate conditions
        conditions = parsed_tree.get("conditions", [])
        assert isinstance(conditions, list), "conditions must be a list"
        for cond in conditions:
            assert isinstance(cond, dict), f"Condition must be a dict: {cond}"

        # Validate modifiers
        modifiers = parsed_tree.get("modifiers", [])
        assert isinstance(modifiers, list), "modifiers must be a list"
        for mod in modifiers:
            assert isinstance(mod, dict), f"Modifier must be a dict: {mod}"

        # Validate zones (optional)
        if "zones" in parsed_tree:
            zones = parsed_tree["zones"]
            assert isinstance(zones, list), "zones must be a list"
            for z in zones:
                assert isinstance(z, str), f"Zone must be a string: {z}"

        # Validate targets
        targets = parsed_tree.get("targets", {})
        assert isinstance(targets, dict), "targets must be a dictionary"
        for label, target in targets.items():
            assert isinstance(label, str), f"Target key must be string: {label}"
            assert isinstance(target, dict), f"Target value must be dict: {target}"

        return True

    @staticmethod
    def validate_tree_structure(parsed_tree):
        required_keys = ["effect_chain", "conditions", "modifiers", "targets"]
        for key in required_keys:
            assert key in parsed_tree, f"Missing key in tree: {key}"
        assert isinstance(parsed_tree["effect_chain"], list), "effect_chain must be a list"
        assert isinstance(parsed_tree["conditions"], list), "conditions must be a list"
        assert isinstance(parsed_tree["modifiers"], list), "modifiers must be a list"
        assert isinstance(parsed_tree["targets"], dict), "targets must be a dict"
        return True

    @staticmethod
    def run_batch_validation(parse_trees):
        passed = 0
        failed = 0

        for card_name, tree in parse_trees.items():
            try:
                OracleComplianceTestSuite.validate_tree_structure(tree)
                OracleComplianceTestSuite.validate_tree(tree)
                print(f"[PASS] {card_name}")
                passed += 1
            except AssertionError as e:
                print(f"[FAIL] {card_name}: {e}")
                failed += 1

        print(f"\nValidation complete: {passed} passed, {failed} failed")
