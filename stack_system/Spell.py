# === Spell.py (Patched for Oracle Behavior Trees) ===

from ..data_layer import CardComponent
from effect_execution import EffectEngine, EffectContext

class Spell(CardComponent):
    def __init__(self, card, controller):
        """
        Spell now wraps the actual Card object and the controller (Player).
        """
        self.card = card
        self.controller = controller
        self.engine = EffectEngine()

    def on_play(self, game_state):
        """
        Resolves the spell by executing its parsed behavior tree if available.
        """
        print(f"[Spell] Resolving {self.card.name} by Oracle behavior.")

        context = EffectContext(source=self.card, controller=self.controller, game_state=game_state)
        result = self.engine.execute(self.card.behavior_tree, context)
        
        print(f"[Spell] Result: {result}")
        return result
