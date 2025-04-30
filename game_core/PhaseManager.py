# === PhaseManager ===
class PhaseManager:
    def __init__(self):
        self.phases = [
            "Untap", "Upkeep", "Draw", "Precombat Main",
            "Beginning of Combat", "Declare Attackers", "Declare Blockers",
            "Combat Damage", "End of Combat", "Postcombat Main",
            "End Step", "Cleanup"
        ]
        self.current_index = 0

    def current_phase(self):
        return self.phases[self.current_index]

    def next_phase(self):
        self.current_index = (self.current_index + 1) % len(self.phases)

    def pass_priority(self, game_state):
        """Pass priority to next player, but inject pending triggers first"""
        if "trigger_engine" in game_state and "stack" in game_state:
            game_state["trigger_engine"].inject_pending_triggers_to_stack(game_state["stack"])
        if "priority_manager" in game_state and game_state["priority_manager"] is not None:
            game_state["priority_manager"].pass_to_next_player()
