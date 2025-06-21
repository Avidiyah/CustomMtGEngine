# === EffectParser.py ===
# Parses AST into behavior trees and static abilities

from .EffectRegistry import STANDARD_EFFECTS
from .Tokenizer import Tokenizer

class EffectParser:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def parse_ast(self, ast_node, card=None):
        behavior_tree = {
            "effect_chain": [],
            "conditions": [],
            "targets": {},
            "zones": [],
            "timing": [],
            "modifiers": [],
            "repeat": False,
            "modal_choices": [],
            "choose_count": None
        }

        if isinstance(ast_node, list):
            for node in ast_node:
                subtree = self.parse_ast(node, card=card)
                if subtree:
                    behavior_tree["effect_chain"].append(subtree)
            return behavior_tree

        if isinstance(ast_node, dict):
            node_type = ast_node.get("type", "")

            if node_type == "modal":
                behavior_tree["choose_count"] = 1
                behavior_tree["modal_choices"] = [
                    self.parse_ast(option, card=card) for option in ast_node.get("options", [])
                ]
                return behavior_tree

            if node_type == "conditional":
                condition = ast_node.get("condition", "")
                then_branch = self.parse_ast(ast_node.get("then", []), card=card)
                else_branch = self.parse_ast(ast_node.get("else", []), card=card) if "else" in ast_node else None

                return {
                    "type": "conditional",
                    "condition": condition,
                    "then": then_branch,
                    "else": else_branch
                }

            if node_type == "repeat":
                inner = self.parse_ast(ast_node.get("children", []), card=card)
                inner["repeat"] = True
                return inner

            if node_type == "effect":
                effect_text = ast_node.get("content", "").lower()
                parsed = self._parse_effect(effect_text)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    return {"action": "unparsed_effect", "raw_text": effect_text}

        return {"action": "unparsed_effect", "raw_node": ast_node}

    def _parse_effect(self, text):
        for key, entry in STANDARD_EFFECTS.items():
            if any(phrase in text for phrase in entry["phrases"]):
                return entry["parse"](text)
        return {"action": "unparsed_effect", "raw_text": text}
