# === PriorityManager ===
class PriorityManager:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.active_index = 0
        self.passed = [False, False]

    def current_player(self):
        return self.players[self.active_index]

    def pass_priority(self):
        self.passed[self.active_index] = True
        if all(self.passed):
            self.reset()
            return True
        self.active_index = 1 - self.active_index
        return False

    def hold_priority(self):
        """Allow the current player to hold priority after casting or activating."""
        self.passed[self.active_index] = False  # Do not toggle active player, just hold

    def both_players_passed(self):
        return all(self.passed)

    def reset(self):
        self.passed = [False, False]
        self.active_index = 0

    def is_mana_ability(self, ability):
        """Determine if an ability is a mana ability that should resolve immediately."""
        if hasattr(ability, "behavior_tree"):
            actions = [e.get("action", "") for e in ability.behavior_tree.get("effect_chain", [])]
            return all(action == "add_mana" for action in actions)
        return False
