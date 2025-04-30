# === StateBasedActions ===
class StateBasedActions:
    def __init__(self):
        self.rules = [
            {"condition": self._creature_with_zero_toughness, "action": self._destroy_creature},
            {"condition": self._creature_with_lethal_damage, "action": self._destroy_creature},
            {"condition": self._player_zero_life, "action": self._player_lose}
        ]

    def check_and_apply(self, game_state):
        results = []
        for rule in self.rules:
            for player in game_state.get("players", []):
                for permanent in getattr(player, "battlefield", []):
                    if rule["condition"](permanent):
                        results.append(rule["action"](permanent, player, game_state))
                if rule["condition"](player):
                    results.append(rule["action"](player, None, game_state))
        return results

    def _creature_with_zero_toughness(self, permanent):
        return getattr(permanent, "type_line", "").lower().startswith("creature") and getattr(permanent, "toughness", 1) <= 0

    def _creature_with_lethal_damage(self, permanent):
        return getattr(permanent, "type_line", "").lower().startswith("creature") and getattr(permanent, "damage", 0) >= getattr(permanent, "toughness", 1)

    def _destroy_creature(self, creature, controller, game_state):
        game_state["zone_manager"].move_to_zone(creature, "graveyard", game_state)
        return f"{creature.name} is destroyed by SBA."

    def _player_zero_life(self, player):
        return getattr(player, "life", 1) <= 0

    def _player_lose(self, player, _, __):
        player.lose("life total is 0 or less")
        return f"{player.name} loses the game due to 0 life."
