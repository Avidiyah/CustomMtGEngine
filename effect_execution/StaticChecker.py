# === StaticChecker ===
# from oracle_parser.OracleRulesLayer import LayerManager  # TODO: implement rule engine


class _StubLayerManager:
    """Temporary stand-in until the full LayerManager exists."""

    def register_effect(self, _effect):
        pass

    def apply_layers(self, _game_state):
        pass

class StaticChecker:
    def __init__(self):
        self.layer_manager = _StubLayerManager()
        pass

    def register(self, effect):
        """Register a StaticEffectDescriptor or similar into the LayerManager."""
        self.layer_manager.register_effect(effect)

    def apply(self, game_state):
        """Apply all registered static effects through the LayerManager."""
        self.layer_manager.apply_layers(game_state)
