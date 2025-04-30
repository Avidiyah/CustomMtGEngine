# === PATCHED ConditionClauseParser.py ===
from .Tokenizer import TokenType, Tokenizer

class ConditionClauseParser:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def parse_condition_clause(self, tokens, start_index):
        """Parses a conditional clause starting at 'if', 'as long as', or 'while'."""
        condition_tokens = []
        effect_tokens = []
        i = start_index + 1
        in_effect = False

        while i < len(tokens):
            token = tokens[i]
            if token.value in [",", "then"]:
                in_effect = True
                i += 1
                continue
            if not in_effect:
                condition_tokens.append(token)
            else:
                effect_tokens.append(token)
            i += 1

        return self._parse_condition_subject(condition_tokens)

    def parse_condition_text(self, condition_str):
        """New: Parses a condition string directly (for AST compatibility)."""
        tokens = self.tokenizer.tokenize(condition_str)
        return self._parse_condition_subject(tokens)

    def _parse_condition_subject(self, tokens):
        # Dummy structure to simulate subject parsing
        parsed = {
            "controller": None,
            "type": None,
            "subtype": None,
            "count": None,
            "raw": " ".join(token.value for token in tokens)
        }

        for i, token in enumerate(tokens):
            if token.value in ["you", "your"]:
                parsed["controller"] = "you"
            elif token.value == "opponent":
                parsed["controller"] = "opponent"
            elif token.value in ["creature", "artifact", "permanent", "spell"]:
                parsed["type"] = token.value
            elif token.value[0].isupper() and i > 0:
                parsed["subtype"] = token.value
            elif token.value in ["another", "a", "one", "two"]:
                parsed["count"] = ">=1"

        return parsed
