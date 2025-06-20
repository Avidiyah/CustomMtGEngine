import json
from game_core import GameManager
from ..data_layer import CardDataManager
from game_core import PhaseManager, Player
from stack_system import StackEngine, TriggerEngine
from ..data_layer import Card

class OracleExecutionTestSuite:
    @staticmethod
    def load_tests(json_path="simulation_tests.json"):
        with open(json_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def find_target_by_name(gm, name):
        for player in gm.players:
            for zone_name in ["battlefield", "graveyard", "hand"]:
                for card in getattr(player, zone_name):
                    if card.name == name:
                        return card
        return None

    @staticmethod
    def setup_game(test_case):
        players = [Player(name=n) for n in test_case.get("players", ["Player A", "Player B"])]
        phase_manager = PhaseManager()
        stack = StackEngine()
        trigger_engine = TriggerEngine()

        gm = GameManager(players, stack, phase_manager, trigger_engine)

        # Apply zone setups and card injection
        for zone_name, cards_by_player in test_case["setup"].get("zones", {}).items():
            for player_index, card_list in enumerate(cards_by_player):
                for card_name in card_list:
                    card_data = CardDataManager.load_card(card_name)
                    card_obj = Card(card_name)
                    card_obj.oracle_text = card_data.get("oracle_text", "")
                    card_obj.type_line = card_data.get("type_line", "")
                    card_obj.mana_cost = card_data.get("mana_cost", "")
                    getattr(gm.players[player_index], zone_name).append(card_obj)

        return gm

    @staticmethod
    def simulate_actions(gm, actions):
        for action in actions:
            if action["type"] == "cast":
                card = next((c for c in gm.players[action["player"]].hand if c.name == action["card"]), None)
                target = OracleExecutionTestSuite.find_target_by_name(gm, action["target"])
                gm.cast_spell(card, target)

            elif action["type"] == "pass_priority":
                gm.pass_priority()

            elif action["type"] == "declare_attackers":
                gm.declare_attackers(action["attackers"])

            # Add more as needed

        gm.resolve_stack()

    @staticmethod
    def check_expected_state(gm, expected):
        errors = []

        if "player1_life" in expected:
            actual = gm.players[0].life
            if actual != expected["player1_life"]:
                errors.append(f"Expected life: {expected['player1_life']}, got {actual}")

        if "graveyard_contains" in expected:
            zone_names = [c.name for c in gm.players[0].graveyard]
            for name in expected["graveyard_contains"]:
                if name not in zone_names:
                    errors.append(f"Missing in graveyard: {name}")

        if "hand_count" in expected:
            hand_size = len(gm.players[0].hand)
            if hand_size != expected["hand_count"]:
                errors.append(f"Expected hand count {expected['hand_count']}, got {hand_size}")

        return errors

    @staticmethod
    def run_all():
        tests = OracleExecutionTestSuite.load_tests()
        passed = 0
        failed = 0

        for test_case in tests:
            gm = OracleExecutionTestSuite.setup_game(test_case)
            OracleExecutionTestSuite.simulate_actions(gm, test_case["setup"].get("actions", []))
            errors = OracleExecutionTestSuite.check_expected_state(gm, test_case.get("expected_state", {}))

            if errors:
                print(f"[FAIL] {test_case['test_id']}:")
                for err in errors:
                    print("  -", err)
                failed += 1
            else:
                print(f"[PASS] {test_case['test_id']}")
                passed += 1

        print(f"\nSimulation complete: {passed} passed, {failed} failed")
