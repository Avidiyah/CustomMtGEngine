# === DynamicReferenceManager.py ===
# Tracks dynamic object references across game state changes.

class DynamicReferenceManager:
    def __init__(self):
        self.references = {}

    def set_reference(self, tag, obj):
        self.references[tag] = obj
        print(f"[DynamicReferenceManager] Set reference '{tag}' to {obj}.")

    def get_reference(self, tag):
        return self.references.get(tag, None)

    def clear_reference(self, tag):
        if tag in self.references:
            del self.references[tag]
            print(f"[DynamicReferenceManager] Cleared reference '{tag}'.")

    def clear_all(self):
        self.references.clear()
        print("[DynamicReferenceManager] Cleared all references.")
