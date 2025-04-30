# === ReplacementEffectManager ===
class ReplacementEffect:
    def applies(self, event):
        return False

    def replace(self, event):
        return event

class ReplacementEffectManager:
    def __init__(self):
        self.effects = []

    def register(self, effect):
        self.effects.append(effect)

    def apply_replacements(self, event):
        for effect in self.effects:
            if effect.applies(event):
                event = effect.replace(event)
        return event
