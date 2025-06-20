"""Centralized rule keyword and phrase registry for Oracle parsing.

This module consolidates keyword groups and simple phrase mappings used
throughout the engine.  It provides a single source of truth for the
Tokenizer, ClauseParsers and EffectRegistry so that all components share
the same vocabulary.  No game state logic or token classes are defined
here.
"""

# ---------------------------------------------------------------------------
# Keyword groups
# ---------------------------------------------------------------------------

# Words that typically start triggered abilities.
TRIGGER_WORDS = frozenset({
    "when",
    "whenever",
    "at the beginning of",
    "at end of combat",
    "at the start of your upkeep",
    "at the end of your turn",
    "at your end step",
})

# Words that introduce conditional clauses.
CONDITION_WORDS = frozenset({
    "if",
    "unless",
    "as long as",
    "until",
    "during",
    "instead",
    "after",
    "before",
    "whilst",
})

# Common action verbs found in Oracle text.
ACTION_WORDS = frozenset({
    "draw", "discard", "destroy", "exile", "tap", "untap", "create",
    "gain", "lose", "search", "reveal", "return", "counter", "sacrifice",
    "sacrifices", "pay", "cast", "attack", "block", "equip", "enchant",
    "flip", "mill", "venture", "explore", "investigate", "amass",
    "fight", "adapt", "proliferate", "scry", "connive",
})

# Targeting indicators and common object descriptors.
TARGETING_WORDS = frozenset({
    "target", "choose", "each", "any", "up to", "each opponent",
    "each player", "each creature", "opponent", "player",
    "planeswalker", "artifact", "enchantment", "creature", "land",
    "spell", "permanent", "nonland", "nontoken", "noncreature",
    "nonartifact",
})

# Zones referenced within card text.
ZONE_WORDS = frozenset({
    "battlefield", "graveyard", "exile", "library", "hand",
    "stack", "command zone",
})

# Timing restrictions or clauses.
TIMING_WORDS = frozenset({
    "only as a sorcery", "instant speed", "during your upkeep",
    "during combat", "end of turn", "before damage",
    "after blockers are declared", "at any time",
})

# Static ability keywords recognised by the engine.
STATIC_KEYWORDS = frozenset({
    "flying", "first strike", "double strike", "deathtouch", "lifelink",
    "vigilance", "trample", "hexproof", "menace", "ward", "indestructible",
    "protection", "haste", "reach",
})

# Cost-related verbs and phrases.
COST_WORDS = frozenset({"sacrifice", "discard", "pay"})

# Articles and pronouns used for simple grammatical tagging.
ARTICLES_INDEFINITE = frozenset({"a", "an"})
ARTICLES_DEFINITE = frozenset({"the"})
PRONOUNS_SUBJECT = frozenset({"you", "they"})
PRONOUNS_POSSESSIVE = frozenset({"your", "their"})

# Quantifiers including common numeric words.
QUANTIFIERS = frozenset({
    "each", "any", "one", "all", "up to", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten", "x", "any number",
    "at least", "no more than",
})

# Miscellaneous verb groups used for tagging.
VERBS_CONTROL = frozenset({"control", "controls"})
VERBS_STATE = frozenset({"has", "have"})
VERBS_BE = frozenset({"is", "are", "was", "were"})
MODAL_VERBS = frozenset({"choose", "may", "must", "can", "shall", "could"})
PREPOSITIONS = frozenset({"of", "with", "without"})
TEMPORAL_MODIFIERS = frozenset({"during", "before", "after"})
NOUN_PLAYER_ROLES = frozenset({"opponent", "player"})
RESOURCE_TERMS = frozenset({"life", "mana", "damage", "counter", "token"})
OBJECT_TERMS = frozenset({"card", "spell", "permanent", "player", "ability", "emblem"})
EFFECT_TERMS = frozenset({"gain", "lose", "prevent", "add", "remove", "create", "destroy"})

# ---------------------------------------------------------------------------
# Phrase groupings and tag mappings
# ---------------------------------------------------------------------------

# Rule modifying static abilities mapped to structured descriptors.
STATIC_RULE_MODIFIERS = {
    "players can't cast more than one spell each turn": {
        "rule": "cast_limit_per_turn",
        "value": 1,
        "applies_to": "player",
    },
    "creatures can't attack you unless their controller pays": {
        "rule": "attack_tax",
        "cost": "{2}",
        "target": "you",
    },
    "can't attack or block unless": {"rule": "combat_restriction"},
    "must attack each combat if able": {"rule": "must_attack"},
}

# Conditional keywords mapped to simple tags.
CONDITIONALS = {
    "if": "conditional_start",
    "as long as": "sustained_condition",
    "unless": "negated_condition",
    "while": "state_condition",
}

# Modal phrases that alter how choices are made.
MODAL_KEYWORDS = {
    "choose one": ["mode"],
    "choose two": ["mode"],
    "you may": ["optional"],
}

# Simple reverse lookup patterns used by the effect tagger.
TAGGED_PATTERNS = {
    "deal damage": "ACTION",
    "draw a card": "ACTION",
    "beginning of your upkeep": "TRIGGER",
}

__all__ = [
    "TRIGGER_WORDS",
    "CONDITION_WORDS",
    "ACTION_WORDS",
    "TARGETING_WORDS",
    "ZONE_WORDS",
    "TIMING_WORDS",
    "STATIC_KEYWORDS",
    "COST_WORDS",
    "ARTICLES_INDEFINITE",
    "ARTICLES_DEFINITE",
    "PRONOUNS_SUBJECT",
    "PRONOUNS_POSSESSIVE",
    "QUANTIFIERS",
    "VERBS_CONTROL",
    "VERBS_STATE",
    "VERBS_BE",
    "MODAL_VERBS",
    "PREPOSITIONS",
    "TEMPORAL_MODIFIERS",
    "NOUN_PLAYER_ROLES",
    "RESOURCE_TERMS",
    "OBJECT_TERMS",
    "EFFECT_TERMS",
    "STATIC_RULE_MODIFIERS",
    "CONDITIONALS",
    "MODAL_KEYWORDS",
    "TAGGED_PATTERNS",
]
