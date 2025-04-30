from .GameManager import GameManager  # for memory tracker access
# === ZoneManager ===
from stack_system.Stack import Stack

class ZoneManager:
    def __init__(self):
        self.zones = [
            "library", "hand", "battlefield", "graveyard",
            "exile", "stack", "command", "ante"
        ]
        self.zone_visibility = {
            "library": "private",
            "hand": "private",
            "battlefield": "public",
            "graveyard": "public",
            "exile": "mixed",
            "stack": "public",
            "command": "public",
            "ante": "special"
        }

    def move_to_zone(self, card, new_zone, game_state=None, face_down=False):
        if new_zone not in self.zones:
            return f"Invalid zone: {new_zone}"

        old_zone = getattr(card, "zone", None)
        if old_zone and game_state:
            for player in game_state.get("players", []):
                zone_list = getattr(player, old_zone, None)
                if isinstance(zone_list, list) and card in zone_list:
                    zone_list.remove(card)

        card.zone = new_zone
        card.is_face_down = face_down

        if game_state:
            for player in game_state.get("players", []):
                if card.controller is None:
                    card.controller = player
                if card.controller == player:
                    zone_list = getattr(player, new_zone, None)
                    if isinstance(zone_list, list) and card not in zone_list:
                        zone_list.append(card)

        if new_zone == "stack" and hasattr(game_state.get("stack", None), "push"):
            game_state["stack"].push(card)

        result = f"{card.name} moves to {new_zone}."

        if new_zone == "battlefield" and game_state:
            oracle = getattr(card, "oracle_text", "").lower()
            if "enters the battlefield" in oracle and "trigger_engine" in game_state:
                def effect():
                    return f"{card.name}'s ETB trigger resolves."
                game_state["trigger_engine"].register(lambda state: True, effect, source=card.name)
                result += f" {card.name}'s ETB trigger registered."

        return result

    def zone_exists(self, zone_name):
        return zone_name in self.zones

    def get_zone_cards(self, player, zone_name):
        if zone_name not in self.zones:
            return []
        return getattr(player, zone_name, [])

    def get_zone_visibility(self, zone_name):
        return self.zone_visibility.get(zone_name, "unknown")

    def turn_face_up(self, card):
        card.is_face_down = False
        return f"{card.name} is turned face-up."
