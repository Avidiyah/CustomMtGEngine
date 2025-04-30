# === PATCHED TriggerClauseParser.py ===
from .Tokenizer import TokenType

class TriggerClauseParser:
    def __init__(self):
        pass

    def parse_trigger_clause(self, tokens, start_index):
        trigger_type = tokens[start_index].value
        i = start_index + 1

        subject_tokens = []
        action_tokens = []
        condition_tokens = []

        in_condition = False
        delayed = False
        zone_change = None

        while i < len(tokens):
            token = tokens[i]

            if token.value in [",", "then"]:
                break

            if token.type == TokenType.CONDITION_WORD:
                in_condition = True

            if in_condition:
                condition_tokens.append(token)
            else:
                if token.type == TokenType.ACTION_WORD or token.type == TokenType.ABILITY_KEYWORD:
                    action_tokens.append(token)
                else:
                    subject_tokens.append(token)

            i += 1

        # Zone Change Detection
        combined_subject = " ".join(t.value for t in subject_tokens).lower()
        combined_action = " ".join(t.value for t in action_tokens).lower()

        if "dies" in combined_subject:
            zone_change = {"from": "battlefield", "to": "graveyard"}
        elif "is exiled" in combined_subject:
            zone_change = {"from": "battlefield", "to": "exile"}
        elif "enters the battlefield" in combined_subject:
            zone_change = {"to": "battlefield"}
        elif "leaves the battlefield" in combined_subject:
            zone_change = {"from": "battlefield"}

        if "next end step" in combined_subject or "next end step" in combined_action:
            delayed = True

        subject = self._parse_subject(subject_tokens)

        trigger_node = {
            "trigger": {
                "type": trigger_type,
                "event": {
                    "subject": subject,
                    "action": " ".join(t.value for t in action_tokens),
                    "condition": " ".join(t.value for t in condition_tokens) if condition_tokens else None,
                    "zone_change": zone_change
                },
                "delayed": delayed
            }
        }

        return trigger_node, i

    def _parse_subject(self, tokens):
        subject = {
            "amount": None,
            "controller": None,
            "type": None,
            "modifiers": []
        }

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value in ["each", "any", "one", "up to"]:
                subject["amount"] = token.value
            elif token.value == "a":
                subject["amount"] = 1
            elif token.value in ["you", "your"]:
                if i + 1 < len(tokens) and tokens[i+1].value in ["control", "controls"]:
                    subject["controller"] = "you"
                    i += 1
                else:
                    subject["controller"] = "you"
            elif token.value == "opponent":
                if i + 1 < len(tokens) and tokens[i+1].value in ["control", "controls"]:
                    subject["controller"] = "opponent"
                    i += 1
                else:
                    subject["controller"] = "opponent"
            elif token.type == TokenType.TARGETING_WORD or token.value in ["creature", "land", "planeswalker", "artifact", "enchantment", "spell", "permanent"]:
                if subject["type"]:
                    if isinstance(subject["type"], list):
                        subject["type"].append(token.value)
                    else:
                        subject["type"] = [subject["type"], token.value]
                else:
                    subject["type"] = token.value
            i += 1

        return subject
