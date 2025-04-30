
# TargetingSystem.py â€” Oracle-Compliant Filtering and Declaration

class TargetingSystem:
    def __init__(self):
        self.pending_targets = {}

    def declare_targets(self, source, targets, filters=None):
        self.pending_targets[source] = {
            "declared": targets,
            "filters": filters or []
        }

    def validate_targets(self, source):
        entry = self.pending_targets.get(source)
        if not entry:
            return False

        filters = entry.get("filters", [])
        valid_targets = []

        for t in entry["declared"]:
            if self.is_valid(t, filters):
                valid_targets.append(t)

        return len(valid_targets) == len(entry["declared"])

    def is_valid(self, target, filters):
        if not filters:
            return True  # If no filters, accept all

        for f in filters:
            # Match type_line for creatures, planeswalkers, etc.
            if hasattr(target, "type_line") and f.lower() in target.type_line.lower():
                return True
            # Direct class name match (e.g. Player)
            if target.__class__.__name__.lower() == f.lower():
                return True
        return False

    def get_targets(self, source):
        entry = self.pending_targets.get(source)
        if entry:
            return entry["declared"]
        return []