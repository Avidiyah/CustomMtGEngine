# Splits Oracle text into Token objects

# Token types
class TokenType:
    TRIGGER_WORD = "trigger_word"
    CONDITION_WORD = "condition_word"
    ACTION_WORD = "action_word"
    COST_WORD = "cost_word"
    TARGETING_WORD = "targeting_word"
    ZONE_REFERENCE = "zone_reference"
    TIMING_MODIFIER = "timing_modifier"
    NUMERIC = "numeric"
    ABILITY_KEYWORD = "ability_keyword"
    ARTICLE_INDEFINITE = "article_indefinite"
    ARTICLE_DEFINITE = "article_definite"
    PRONOUN_SUBJECT = "pronoun_subject"
    PRONOUN_POSSESSIVE = "pronoun_possessive"
    QUANTIFIER = "quantifier"
    VERB_CONTROL = "verb_control"
    VERB_STATE = "verb_state"
    VERB_BE = "verb_be"
    MODAL_VERB = "modal_verb"
    PREPOSITION = "preposition"
    TEMPORAL_MODIFIER = "temporal_modifier"
    NOUN_PLAYER_ROLE = "noun_player_role"

    RESOURCE_TERM = "resource_term"
    OBJECT_TERM = "object_term"
    EFFECT_TERM = "effect_term"

    UNKNOWN = "unknown"

# Token object
class Token:
    def __init__(self, token_type, value, metadata=None):
        self.type = token_type
        self.value = value
        self.metadata = metadata if metadata is not None else {}

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, metadata={self.metadata})"

# Tokenizer class
class Tokenizer:
    def __init__(self):
        self.trigger_words = [
            "when", "whenever", "at the beginning of", "at end of combat",
            "at the start of your upkeep", "at the end of your turn", "at your end step"
        ]
        self.condition_words = [
            "if", "unless", "as long as", "until", "during", "instead", "after", "before", "whilst"
        ]
        self.articles_indefinite = ["a", "an"]
        self.articles_definite = ["the"]
        self.pronouns_subject = ["you", "they"]
        self.pronouns_possessive = ["your", "their"]
        self.quantifiers = ["each", "any", "one", "all", "up to"]
        self.verbs_control = ["control", "controls"]
        self.verbs_state = ["has", "have"]
        self.verbs_be = ["is", "are", "was", "were"]
        self.modal_verbs = ["choose", "may", "must", "can", "shall", "could"]
        self.prepositions = ["of", "with", "without"]
        self.temporal_modifiers = ["during", "before", "after"]
        self.noun_player_roles = ["opponent", "player"]
        self.resource_terms = ["life", "mana", "damage", "counter", "token"]
        self.object_terms = ["card", "spell", "permanent", "player", "ability", "emblem"]
        self.effect_terms = ["gain", "lose", "prevent", "add", "remove", "create", "destroy"]
        self.action_words = [
            "draw", "discard", "destroy", "exile", "tap", "untap", "create", "gain", "lose",
            "search", "reveal", "return", "counter", "sacrifice", "sacrifices", "pay", "cast", "attack",
            "block", "equip", "enchant", "flip", "mill", "venture", "explore", "investigate",
            "amass", "fight", "adapt", "proliferate", "scry", "connive"
        ]
        self.targeting_words = [
            "target", "choose", "each", "any", "up to", "each opponent", "each player",
            "each creature", "opponent", "player", "planeswalker", "artifact",
            "enchantment", "creature", "land", "spell", "permanent", "nonland",
            "nontoken", "noncreature", "nonartifact"
        ]
        self.zone_references = [
            "battlefield", "graveyard", "exile", "library", "hand", "stack", "command zone"
        ]
        self.timing_modifiers = [
            "only as a sorcery", "instant speed", "during your upkeep", "during combat",
            "end of turn", "before damage", "after blockers are declared", "at any time"
        ]
        self.ability_keywords = [
            "flying", "first strike", "double strike", "deathtouch", "lifelink",
            "vigilance", "trample", "hexproof", "menace", "ward", "indestructible",
            "protection", "haste", "reach"
        ]
        self.quantifiers += [
            "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "x",
            "any number", "at least", "no more than"
        ]

    def tokenize(self, text):
        text = text.lower()
        text = self.clean_punctuation(text)
        words = text.split()

        tokens = []
        i = 0
        while i < len(words):
            word = words[i]

            # Handle multi-word phrases first
            phrase_4 = " ".join(words[i:i+5])
            phrase_3 = " ".join(words[i:i+4])
            phrase_2 = " ".join(words[i:i+3])
            phrase_1 = " ".join(words[i:i+2])

            if phrase_4 in self.trigger_words or phrase_4 in self.timing_modifiers:
                tokens.append(Token(TokenType.TRIGGER_WORD, phrase_4))
                i += 5
                continue
            elif phrase_3 in self.trigger_words or phrase_3 in self.timing_modifiers:
                tokens.append(Token(TokenType.TRIGGER_WORD, phrase_3))
                i += 4
                continue
            elif phrase_2 in self.trigger_words or phrase_2 in self.timing_modifiers:
                tokens.append(Token(TokenType.TRIGGER_WORD, phrase_2))
                i += 3
                continue
            elif phrase_1 in self.trigger_words or phrase_1 in self.timing_modifiers:
                tokens.append(Token(TokenType.TRIGGER_WORD, phrase_1))
                i += 2
                continue

            # Single-word classification
            if word in self.trigger_words:
                tokens.append(Token(TokenType.TRIGGER_WORD, word))
            elif word in self.condition_words:
                tokens.append(Token(TokenType.CONDITION_WORD, word))
            elif word in self.action_words:
                tokens.append(Token(TokenType.ACTION_WORD, word))
            elif word in self.targeting_words:
                tokens.append(Token(TokenType.TARGETING_WORD, word))
            elif word in self.zone_references:
                tokens.append(Token(TokenType.ZONE_REFERENCE, word))
            elif word in self.timing_modifiers:
                tokens.append(Token(TokenType.TIMING_MODIFIER, word))
            elif word in self.ability_keywords:
                tokens.append(Token(TokenType.ABILITY_KEYWORD, word))
            elif word in self.articles_indefinite:
                tokens.append(Token(TokenType.ARTICLE_INDEFINITE, word))
            elif word in self.articles_definite:
                tokens.append(Token(TokenType.ARTICLE_DEFINITE, word))
            elif word in self.pronouns_subject:
                tokens.append(Token(TokenType.PRONOUN_SUBJECT, word))
            elif word in self.pronouns_possessive:
                tokens.append(Token(TokenType.PRONOUN_POSSESSIVE, word))
            elif word in self.quantifiers:
                tokens.append(Token(TokenType.QUANTIFIER, word))
            elif word in self.verbs_control:
                tokens.append(Token(TokenType.VERB_CONTROL, word))
            elif word in self.verbs_state:
                tokens.append(Token(TokenType.VERB_STATE, word))
            elif word in self.verbs_be:
                tokens.append(Token(TokenType.VERB_BE, word))
            elif word in self.modal_verbs:
                tokens.append(Token(TokenType.MODAL_VERB, word))
            elif word in self.prepositions:
                tokens.append(Token(TokenType.PREPOSITION, word))
            elif word in self.temporal_modifiers:
                tokens.append(Token(TokenType.TEMPORAL_MODIFIER, word))
            elif word in self.noun_player_roles:
                tokens.append(Token(TokenType.NOUN_PLAYER_ROLE, word))
            elif word in self.resource_terms:
                tokens.append(Token(TokenType.RESOURCE_TERM, word))
            elif word in self.object_terms:
                tokens.append(Token(TokenType.OBJECT_TERM, word))
            elif word in self.effect_terms:
                tokens.append(Token(TokenType.EFFECT_TERM, word))
            elif word.isdigit() or word in self.quantifiers:
                tokens.append(Token(TokenType.NUMERIC, word, metadata={"value": word}))
            else:
                tokens.append(Token(TokenType.UNKNOWN, word))

            i += 1

        return tokens

    def clean_punctuation(self, text):
        return text.replace(",", "").replace(".", "").replace(";", "").replace(":", "").replace("!", "").replace("?", "")
