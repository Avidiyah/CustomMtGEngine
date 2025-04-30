# === PatternLayer.py ===
from .Tokenizer import TokenType
from .TriggerClauseParser import TriggerClauseParser
from .ConditionClauseParser import ConditionClauseParser  # NEW

class ActionMatcher:
    def match(self, tokens):
        for i in range(len(tokens) - 1):
            token = tokens[i]
            next_token = tokens[i+1]

            if token.type == TokenType.ACTION_WORD:
                if token.value == "draw" and next_token.type == TokenType.NUMERIC:
                    return {"action": "draw_card", "amount": int(next_token.metadata.get("value", 1))}
                if token.value == "destroy" and next_token.type == TokenType.TARGETING_WORD:
                    return {"action": "destroy_target", "target": next_token.value}
                if token.value == "exile" and next_token.type == TokenType.TARGETING_WORD:
                    return {"action": "exile_target", "target": next_token.value}
        return None

class TriggerMatcher:
    def match(self, tokens):
        for token in tokens:
            if token.type == TokenType.TRIGGER_WORD:
                return {"trigger": token.value}
        return None

class ConditionMatcher:
    def match(self, tokens):
        for token in tokens:
            if token.type == TokenType.CONDITION_WORD:
                return {"condition": token.value}
        return None

class PatternLayer:
    def __init__(self):
        self.action_matcher = ActionMatcher()
        self.trigger_matcher = TriggerMatcher()
        self.condition_matcher = ConditionMatcher()
        self.trigger_clause_parser = TriggerClauseParser()
        self.condition_clause_parser = ConditionClauseParser()  # NEW

    def match_token_stream(self, tokens):
        effects = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token.type == TokenType.TRIGGER_WORD:
                trigger_node, next_index = self.trigger_clause_parser.parse_trigger_clause(tokens, i)
                effects.append(trigger_node)
                i = next_index
                continue
            elif token.type == TokenType.CONDITION_WORD:
                condition_node, next_index = self.condition_clause_parser.parse_condition_clause(tokens, i)
                effects.append(condition_node)
                i = next_index
                continue

            condition = self.condition_matcher.match([token])
            if condition:
                effects.append(condition)

            action = self.action_matcher.match([token])
            if action:
                effects.append(action)

            i += 1

        return effects
