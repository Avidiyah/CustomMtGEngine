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
from .rule_lexicon import (
    TRIGGER_WORDS,
    CONDITION_WORDS,
    ACTION_WORDS,
    TARGETING_WORDS,
    ZONE_WORDS,
    TIMING_WORDS,
    STATIC_KEYWORDS,
    ARTICLES_INDEFINITE,
    ARTICLES_DEFINITE,
    PRONOUNS_SUBJECT,
    PRONOUNS_POSSESSIVE,
    QUANTIFIERS,
    VERBS_CONTROL,
    VERBS_STATE,
    VERBS_BE,
    MODAL_VERBS,
    PREPOSITIONS,
    TEMPORAL_MODIFIERS,
    NOUN_PLAYER_ROLES,
    RESOURCE_TERMS,
    OBJECT_TERMS,
    EFFECT_TERMS,
)


class Tokenizer:
    def __init__(self):
        self.trigger_words = list(TRIGGER_WORDS)
        self.condition_words = list(CONDITION_WORDS)
        self.articles_indefinite = list(ARTICLES_INDEFINITE)
        self.articles_definite = list(ARTICLES_DEFINITE)
        self.pronouns_subject = list(PRONOUNS_SUBJECT)
        self.pronouns_possessive = list(PRONOUNS_POSSESSIVE)
        self.quantifiers = list(QUANTIFIERS)
        self.verbs_control = list(VERBS_CONTROL)
        self.verbs_state = list(VERBS_STATE)
        self.verbs_be = list(VERBS_BE)
        self.modal_verbs = list(MODAL_VERBS)
        self.prepositions = list(PREPOSITIONS)
        self.temporal_modifiers = list(TEMPORAL_MODIFIERS)
        self.noun_player_roles = list(NOUN_PLAYER_ROLES)
        self.resource_terms = list(RESOURCE_TERMS)
        self.object_terms = list(OBJECT_TERMS)
        self.effect_terms = list(EFFECT_TERMS)
        self.action_words = list(ACTION_WORDS)
        self.targeting_words = list(TARGETING_WORDS)
        self.zone_references = list(ZONE_WORDS)
        self.timing_modifiers = list(TIMING_WORDS)
        self.ability_keywords = list(STATIC_KEYWORDS)

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
