# === Spell.py (Patched for Oracle Behavior Trees) ===

from data_layer.CardComponent import CardComponent
from effect_execution.EffectInterpreter import EffectInterpreter

class Spell(CardComponent):
    def __init__(self, card, controller):
        """
        Spell now wraps the actual Card object and the controller (Player).
        """
        self.card = card
        self.controller = controller
        self.interpreter = EffectInterpreter()

    def on_play(self, game_state):
        """
        Resolves the spell by executing its parsed behavior tree if available.
        """
        print(f"[Spell] Resolving {self.card.name} by Oracle behavior.")

        result = self.interpreter.execute(self.card, self.controller, game_state)

        print(f"[Spell] Result: {result}")
        return result
