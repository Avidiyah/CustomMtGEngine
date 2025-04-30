# === StateMemoryTracker.py ===
# Logs and retrieves key game events and transitions for later reference.

class StateMemoryTracker:
    def __init__(self):
        self.memory = {
            "zone_changes": [],       # List of {"object": ..., "from": ..., "to": ..., "timestamp": ...}
            "combat_events": [],      # List of {"attacker": ..., "defender": ..., "damage": ..., "blocked": ...}
            "spell_events": [],       # List of {"spell": ..., "event": "cast" | "countered" | "resolved"}
            "target_events": [],      # List of {"source": ..., "target": ..., "timestamp": ...}
            "custom_tags": {}         # Dict[str, object] – e.g., {"that_creature": creature_obj}
        }

    def log_zone_change(self, obj, from_zone, to_zone, timestamp=None):
        entry = {"object": obj, "from": from_zone, "to": to_zone, "timestamp": timestamp}
        self.memory["zone_changes"].append(entry)
        print(f"[Memory] Zone change: {entry}")

    def log_combat_event(self, attacker, defender, damage=0, blocked=False):
        entry = {"attacker": attacker, "defender": defender, "damage": damage, "blocked": blocked}
        self.memory["combat_events"].append(entry)
        print(f"[Memory] Combat event: {entry}")

    def log_spell_event(self, spell, event_type):
        entry = {"spell": spell, "event": event_type}
        self.memory["spell_events"].append(entry)
        print(f"[Memory] Spell event: {entry}")

    def log_target_event(self, source, target, timestamp=None):
        entry = {"source": source, "target": target, "timestamp": timestamp}
        self.memory["target_events"].append(entry)
        print(f"[Memory] Targeting event: {entry}")

    def tag_reference(self, tag, obj):
        self.memory["custom_tags"][tag] = obj
        print(f"[Memory] Set reference tag '{tag}' to object {obj}")

    def get_reference_by_tag(self, tag):
        return self.memory["custom_tags"].get(tag)

    def get_last_zone_change(self, filter_func=None):
        for entry in reversed(self.memory["zone_changes"]):
            if not filter_func or filter_func(entry):
                return entry
        return None

    def get_recent_combat(self, filter_func=None):
        for entry in reversed(self.memory["combat_events"]):
            if not filter_func or filter_func(entry):
                return entry
        return None

    def clear_all(self):
        for key in self.memory:
            self.memory[key] = [] if isinstance(self.memory[key], list) else {}
        print("[Memory] Cleared all tracked events.")
