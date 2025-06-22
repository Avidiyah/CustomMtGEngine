Tokenizer utilities for Oracle text parsing.

from dataclasses import dataclass
from typing import List

# Token types
class TokenType
    TRIGGER_WORD = trigger_word
    CONDITION_WORD = condition_word
    ACTION_WORD = action_word
    COST_WORD = cost_word
    TARGETING_WORD = targeting_word
    ZONE_REFERENCE = zone_reference
    TIMING_MODIFIER = timing_modifier
    NUMERIC = numeric
    ABILITY_KEYWORD = ability_keyword
    ARTICLE_INDEFINITE = article_indefinite
    ARTICLE_DEFINITE = article_definite
    PRONOUN_SUBJECT = pronoun_subject
    PRONOUN_POSSESSIVE = pronoun_possessive
    QUANTIFIER = quantifier
    VERB_CONTROL = verb_control
    VERB_STATE = verb_state
    VERB_BE = verb_be
    MODAL_VERB = modal_verb
    PREPOSITION = preposition
    TEMPORAL_MODIFIER = temporal_modifier
    NOUN_PLAYER_ROLE = noun_player_role

    RESOURCE_TERM = resource_term
    OBJECT_TERM = object_term
    EFFECT_TERM = effect_term

    UNKNOWN = unknown

# Token object
@dataclass
class Token
    Simple token with associated classification type.

    text str
    type str

    def __repr__(self) - str  # pragma no cover - repr debugging
        return fToken(text={self.text!r}, type={self.type})


@dataclass
class TokenGroup
    Grouping of tokens that originated from the same clause.

    raw str
    tokens List[Token]

# Tokenizer class
from .RuleLexicon import (
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


class Tokenizer
    def __init__(self)
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

    def tokenize(self, text)
        text = text.lower()
        text = self.clean_punctuation(text)
        words = text.split()

        tokens = []
        i = 0
        while i  len(words)
            word = words[i]

            # Handle multi-word phrases first
            phrase_4 =  .join(words[ii+5])
            phrase_3 =  .join(words[ii+4])
            phrase_2 =  .join(words[ii+3])
            phrase_1 =  .join(words[ii+2])

            if phrase_4 in self.trigger_words or phrase_4 in self.timing_modifiers
                tokens.append(Token(phrase_4, TokenType.TRIGGER_WORD))
                i += 5
                continue
            elif phrase_3 in self.trigger_words or phrase_3 in self.timing_modifiers
                tokens.append(Token(phrase_3, TokenType.TRIGGER_WORD))
                i += 4
                continue
            elif phrase_2 in self.trigger_words or phrase_2 in self.timing_modifiers
                tokens.append(Token(phrase_2, TokenType.TRIGGER_WORD))
                i += 3
                continue
            elif phrase_1 in self.trigger_words or phrase_1 in self.timing_modifiers
                tokens.append(Token(phrase_1, TokenType.TRIGGER_WORD))
                i += 2
                continue

            # Single-word classification
            if word in self.trigger_words
                tokens.append(Token(word, TokenType.TRIGGER_WORD))
            elif word in self.condition_words
                tokens.append(Token(word, TokenType.CONDITION_WORD))
            elif word in self.action_words
                tokens.append(Token(word, TokenType.ACTION_WORD))
            elif word in self.targeting_words
                tokens.append(Token(word, TokenType.TARGETING_WORD))
            elif word in self.zone_references
                tokens.append(Token(word, TokenType.ZONE_REFERENCE))
            elif word in self.timing_modifiers
                tokens.append(Token(word, TokenType.TIMING_MODIFIER))
            elif word in self.ability_keywords
                tokens.append(Token(word, TokenType.ABILITY_KEYWORD))
            elif word in self.articles_indefinite
                tokens.append(Token(word, TokenType.ARTICLE_INDEFINITE))
            elif word in self.articles_definite
                tokens.append(Token(word, TokenType.ARTICLE_DEFINITE))
            elif word in self.pronouns_subject
                tokens.append(Token(word, TokenType.PRONOUN_SUBJECT))
            elif word in self.pronouns_possessive
                tokens.append(Token(word, TokenType.PRONOUN_POSSESSIVE))
            elif word in self.quantifiers
                tokens.append(Token(word, TokenType.QUANTIFIER))
            elif word in self.verbs_control
                tokens.append(Token(word, TokenType.VERB_CONTROL))
            elif word in self.verbs_state
                tokens.append(Token(word, TokenType.VERB_STATE))
            elif word in self.verbs_be
                tokens.append(Token(word, TokenType.VERB_BE))
            elif word in self.modal_verbs
                tokens.append(Token(word, TokenType.MODAL_VERB))
            elif word in self.prepositions
                tokens.append(Token(word, TokenType.PREPOSITION))
            elif word in self.temporal_modifiers
                tokens.append(Token(word, TokenType.TEMPORAL_MODIFIER))
            elif word in self.noun_player_roles
                tokens.append(Token(word, TokenType.NOUN_PLAYER_ROLE))
            elif word in self.resource_terms
                tokens.append(Token(word, TokenType.RESOURCE_TERM))
            elif word in self.object_terms
                tokens.append(Token(word, TokenType.OBJECT_TERM))
            elif word in self.effect_terms
                tokens.append(Token(word, TokenType.EFFECT_TERM))
            elif word.isdigit() or word in self.quantifiers
                tokens.append(Token(word, TokenType.NUMERIC))
            else
                tokens.append(Token(word, TokenType.UNKNOWN))

            i += 1

        return tokens

    def clean_punctuation(self, text)
        return text.replace(,, ).replace(., ).replace(;, ).replace(, ).replace(!, ).replace(, )


_default_tokenizer = Tokenizer()


def tokenize_clause(clause str) - TokenGroup
    Tokenize a single Oracle text clause into a class`TokenGroup`.
    tokens_raw = _default_tokenizer.tokenize(clause)
    # ``tokenize`` already returns class`Token` objects but we wrap them in a
    # class`TokenGroup` for downstream parsing.
    return TokenGroup(raw=clause, tokens=list(tokens_raw))
