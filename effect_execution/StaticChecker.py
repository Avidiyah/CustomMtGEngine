# === StaticChecker ===
from oracle_parser.OracleRulesLayer import LayerManager

class StaticChecker:
    def __init__(self):
        self.layer_manager = LayerManager()

    def register(self, effect):
        """Register a StaticEffectDescriptor or similar into the LayerManager."""
        self.layer_manager.register_effect(effect)

    def apply(self, game_state):
        """Apply all registered static effects through the LayerManager."""
        self.layer_manager.apply_layers(game_state)
