from .RuleModifierLexicon import STATIC_RULE_MODIFIERS, CONDITIONALS
from effect_execution import StaticEffectDescriptor
import time

class OracleRulesLayer:
    @staticmethod
    def parse(card):
        OracleRulesLayer.extract_flags(card)
        OracleRulesLayer.extract_abilities(card)

    @staticmethod
    def extract_flags(card):
        card.oracle_flags = set()
        for keyword in card.oracle_text.lower().split():
            if keyword in ["flying", "trample", "vigilance", "haste", "flash", "deathtouch", "lifelink", "menace", "reach"]:
                card.oracle_flags.add(keyword)
            if "incubate" in card.oracle_text.lower():
                card.oracle_flags.add("incubate")
            if "proliferate" in card.oracle_text.lower():
                card.oracle_flags.add("proliferate")
            if "crew" in card.oracle_text.lower():
                card.oracle_flags.add("crew")
            if "corrupted" in card.oracle_text.lower():
                card.oracle_flags.add("corrupted")
            if "mill" in card.oracle_text.lower():
                card.oracle_flags.add("mill")

    @staticmethod
    def extract_abilities(card):
        card.abilities = []
        raw_abilities = [line.strip() for line in card.oracle_text.replace("\n", " ").split(". ") if line.strip()]

        for raw in raw_abilities:
            ability_type = "static"
            condition = "always"

            if raw.lower().startswith(("at the beginning", "whenever", "when ")):
                ability_type = "triggered"
                condition = "trigger_detected"
            elif raw.lower().startswith("if"):
                ability_type = "replacement"
                condition = "replacement_condition"
            elif ":" in raw:
                ability_type = "activated"
                condition = "cost_paid"

            normalized_raw = raw.lower()
            assigned_layer = OracleRulesLayer.determine_layer(normalized_raw)

            effect_descriptor = StaticEffectDescriptor(
                target_class="permanent",  # Placeholder (to improve later with actual parser)
                granted_abilities=[],
                power_boost=0,
                toughness_boost=0,
                restrictions=[],
                rules_overwrites=[],
                keywords_removed=[],
                layer=assigned_layer,
                duration="permanent",
                source=None,  # Assigned later
                timestamp=time.time(),
                dependency_targets=[]
            )

            card.abilities.append({
                "type": ability_type,
                "condition": condition,
                "effect_descriptor": effect_descriptor
            })

    @staticmethod
    def determine_layer(text):
        if "becomes a copy" in text:
            return "Layer 1"
        elif "you control" in text or "gain control" in text:
            return "Layer 2"
        elif "becomes" in text and ("type" in text or "creature" in text or "artifact" in text):
            return "Layer 4"
        elif "color" in text:
            return "Layer 5"
        elif any(keyword in text for keyword in ["gains", "has", "loses"]):
            return "Layer 6"
        elif any(keyword in text for keyword in ["gets +", "gets -", "+1/+1", "-1/-1"]):
            return "Layer 7c"
        else:
            return None

# === Injected LayerManager ===
class LayerManager:
    def __init__(self):
        # Initialize main layers 1-7
        self.layers = {i: [] for i in range(1, 8)}
        # Sublayers inside Layer 7
        self.sublayers_7 = {'7a': [], '7b': [], '7c': [], '7d': []}

    def register_effect(self, effect):
        """
        Registers a static continuous effect into the appropriate layer.
        Effect must have a 'layer' attribute set.
        """
        layer = effect.layer if hasattr(effect, 'layer') else None

        if layer is None:
            raise ValueError(f"Effect {effect} missing layer information!")

        if isinstance(layer, int) and 1 <= layer <= 6:
            self.layers[layer].append(effect)
        elif isinstance(layer, str) and layer in self.sublayers_7:
            self.sublayers_7[layer].append(effect)
        elif layer == 7:
            self.sublayers_7['7d'].append(effect)
        else:
            raise ValueError(f"Invalid layer designation for effect: {layer}")

    def apply_layers(self, game_state):
        """
        Applies all static continuous effects in correct Comprehensive Rules 613 order.
        """
        for layer_num in range(1, 7):
            effects = sorted(self.layers[layer_num], key=lambda e: e.timestamp)
            for effect in effects:
                effect.apply(game_state)

        for sublayer in ['7a', '7b', '7c', '7d']:
            effects = sorted(self.sublayers_7[sublayer], key=lambda e: e.timestamp)
            for effect in effects:
                effect.apply(game_state)
