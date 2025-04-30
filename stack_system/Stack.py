# === Stack ===
class Stack:
    def __init__(self, manager=None):
        self.manager = manager
        self.stack = []

    def push(self, item):
        self.stack.append(item)
        return f"{item['source']} added to stack."

    def peek(self):
        if self.stack:
            return self.stack[-1]
        return None

    def resolve_next(self):
        if self.stack:
            item = self.stack.pop()
            targets = item.get('targets', [])
            if targets:
                legal_targets = [t for t in targets if self.is_target_still_legal(t)]
                if not legal_targets:
                    if self.manager and hasattr(self.manager, 'memory_tracker'):
                        self.manager.memory_tracker.log_spell_event(item['source'], "fizzled")
                    return f"{item['source']} fizzles — all targets illegal."
                else:
                    item['targets'] = legal_targets  # Update only legal targets
                    if self.manager and hasattr(self.manager, 'memory_tracker'):
                        self.manager.memory_tracker.log_spell_event(item['source'], "resolved")
            return f"{item['source']} resolves: {item['effect']()}"
        return "Stack is empty."

    def is_target_still_legal(self, target):
        """Check whether a target is still legal for the spell or ability."""
        if hasattr(target, "is_valid") and callable(target.is_valid):
            return target.is_valid()
        return True

    def resolve(self):
        return self.resolve_next()

    def is_empty(self):
        return len(self.stack) == 0

    def log(self):
        if not self.stack:
            return "Stack is empty."
        return "\n".join(f"{i + 1}: {item['source']}" for i, item in enumerate(reversed(self.stack)))

    def __str__(self):
        return f"Stack [{len(self.stack)} items]:\n" + self.log()

    def add_trigger(self, card, effect):
        """Add a triggered ability onto the stack"""
        self.stack.append({
            "source": card.name,
            "effect": lambda: effect.get("action", "Triggered action unresolved"),
            "description": effect.get("raw_text", "Triggered ability")
        })
