# === PATCHED OracleParserPipeline.py ===

from effect_execution.StaticEffectDescriptor import StaticEffectDescriptor
import time

from .EffectPhraseRegistry import STANDARD_EFFECTS, KEYWORD_ABILITIES
from .oracle_ast_compiler_clean import OracleASTCompiler
from .EffectParser import EffectParser

class OracleParserPipeline:
    def __init__(self):
        self.ast_compiler = OracleASTCompiler()
        self.effect_parser = EffectParser()

    def parse_oracle_text(self, card, oracle_text):
        card.behavior_tree = []
        card.static_ability_tags = []
        card.static_effects = []

        normalized_text = oracle_text.lower().strip()

        # === Step 1: Compile to AST ===
        ast_tree = self.ast_compiler.compile(normalized_text)

        # === Step 2: Parse AST into Behavior Tree ===
        behavior_tree = self.effect_parser.parse_ast(ast_tree, card=card)

        card.behavior_tree.append(behavior_tree)

        # === Step 3: Detect Static Abilities Separately ===
        for keyword in KEYWORD_ABILITIES:
            if keyword in normalized_text:
                card.static_ability_tags.append(keyword)

        # === Step 4: Detect Simple Buffs (e.g., +1/+1 globally) ===
        if "+1/+1" in normalized_text or "-1/-1" in normalized_text:
            boost = normalized_text.count("+1/+1") - normalized_text.count("-1/-1")
            descriptor = StaticEffectDescriptor(
                target_class="creatures you control",
                granted_abilities=[],
                power_boost=boost,
                toughness_boost=boost,
                layer="7c",
                duration="permanent",
                timestamp=time.time()
            )
            card.static_effects.append(descriptor)
