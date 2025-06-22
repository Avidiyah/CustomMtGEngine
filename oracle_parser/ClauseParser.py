"""Clause parsing utilities for Oracle text.

This module provides standalone helper functions to interpret common
clauses found in Magic: the Gathering Oracle text.  It merges the logic
from the old ``TriggerClauseParser``, ``ConditionClauseParser`` and
``PatternLayer`` modules.  The utilities here are used by
:class:`OracleParser` but are otherwise self contained.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .Tokenizer import Tokenizer, TokenType, Token, TokenGroup


@dataclass
class ClauseBlock:
    """Structured representation of an Oracle text clause."""

    raw: str
    clause_type: str
    effect_ir: Dict[str, Any]
    trigger: Dict[str, Any] | None = None
    condition: Dict[str, Any] | None = None
    cost: Dict[str, Any] | None = None
    source_index: int = 0
    cr_tag: str | None = None
    referents: List[str] = field(default_factory=list)

_tokenizer = Tokenizer()


# ---------------------------------------------------------------------------
# Trigger parsing
# ---------------------------------------------------------------------------

def _parse_subject(tokens: List[Token]) -> Dict[str, Any]:
    """Interpret a list of tokens that describe the event subject."""
    subject: Dict[str, Any] = {
        "amount": None,
        "controller": None,
        "type": None,
        "modifiers": [],
    }
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.text in ["each", "any", "one", "up to"]:
            subject["amount"] = token.text
        elif token.text == "a":
            subject["amount"] = 1
        elif token.text in ["you", "your"]:
            if i + 1 < len(tokens) and tokens[i + 1].text in ["control", "controls"]:
                subject["controller"] = "you"
                i += 1
            else:
                subject["controller"] = "you"
        elif token.text == "opponent":
            if i + 1 < len(tokens) and tokens[i + 1].text in ["control", "controls"]:
                subject["controller"] = "opponent"
                i += 1
            else:
                subject["controller"] = "opponent"
        elif token.type == TokenType.TARGETING_WORD or token.text in [
            "creature",
            "land",
            "planeswalker",
            "artifact",
            "enchantment",
            "spell",
            "permanent",
        ]:
            if subject["type"]:
                if isinstance(subject["type"], list):
                    subject["type"].append(token.text)
                else:
                    subject["type"] = [subject["type"], token.text]
            else:
                subject["type"] = token.text
        i += 1
    return subject


def _parse_trigger_tokens(tokens: List[Token], start_index: int) -> Tuple[Dict[str, Any], int]:
    """Parse tokens beginning with a trigger word into a structured dict."""
    trigger_type = tokens[start_index].text
    i = start_index + 1

    subject_tokens: List[Token] = []
    action_tokens: List[Token] = []
    condition_tokens: List[Token] = []

    in_condition = False
    delayed = False
    zone_change: Dict[str, str] | None = None

    while i < len(tokens):
        token = tokens[i]
        if token.text in [",", "then"]:
            break
        if token.type == TokenType.CONDITION_WORD:
            in_condition = True
        if in_condition:
            condition_tokens.append(token)
        else:
            if token.type in (TokenType.ACTION_WORD, TokenType.ABILITY_KEYWORD):
                action_tokens.append(token)
            else:
                subject_tokens.append(token)
        i += 1

    combined_subject = " ".join(t.text for t in subject_tokens).lower()
    combined_action = " ".join(t.text for t in action_tokens).lower()

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

    subject = _parse_subject(subject_tokens)

    trigger_node = {
        "trigger": {
            "type": trigger_type,
            "event": {
                "subject": subject,
                "action": " ".join(t.text for t in action_tokens) or None,
                "condition": " ".join(t.text for t in condition_tokens) if condition_tokens else None,
                "zone_change": zone_change,
            },
            "delayed": delayed,
        }
    }

    return trigger_node, i


def parse_trigger_clause(text: str) -> Dict[str, Any]:
    """Public helper that parses ``text`` as a trigger clause."""
    tokens = _tokenizer.tokenize(text)
    node, _ = _parse_trigger_tokens(tokens, 0)
    return node["trigger"]


# ---------------------------------------------------------------------------
# Condition parsing
# ---------------------------------------------------------------------------

def _parse_condition_subject(tokens: List[Token]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {
        "controller": None,
        "type": None,
        "subtype": None,
        "count": None,
        "raw": " ".join(token.text for token in tokens),
    }
    for i, token in enumerate(tokens):
        if token.text in ["you", "your"]:
            parsed["controller"] = "you"
        elif token.text == "opponent":
            parsed["controller"] = "opponent"
        elif token.text in ["creature", "artifact", "permanent", "spell"]:
            parsed["type"] = token.text
        elif token.text and token.text[0].isupper() and i > 0:
            parsed["subtype"] = token.text
        elif token.text in ["another", "a", "one", "two"]:
            parsed["count"] = ">=1"
    return parsed


def _parse_condition_tokens(tokens: List[Token], start_index: int) -> Tuple[Dict[str, Any], int]:
    condition_tokens: List[Token] = []
    i = start_index + 1
    while i < len(tokens):
        token = tokens[i]
        if token.text in [",", "then"]:
            i += 1
            break
        condition_tokens.append(token)
        i += 1
    parsed = _parse_condition_subject(condition_tokens)
    return parsed, i


def parse_condition_clause(text: str) -> Dict[str, Any]:
    """Parse ``text`` describing a conditional clause."""
    tokens = _tokenizer.tokenize(text)
    parsed, _ = _parse_condition_tokens(tokens, 0)
    return parsed


def parse_token_group(group: TokenGroup) -> ClauseBlock:
    """Convert a :class:`TokenGroup` into a :class:`ClauseBlock`."""
    tokens = group.tokens
    trigger = None
    condition = None
    cost = None
    clause_type = "action"
    i = 0
    if tokens and tokens[0].type == TokenType.TRIGGER_WORD:
        node, i = _parse_trigger_tokens(tokens, 0)
        trigger = node.get("trigger")
        clause_type = "trigger"
    if i < len(tokens) and tokens[i].type == TokenType.CONDITION_WORD:
        condition, i = _parse_condition_tokens(tokens, i)
        if not trigger:
            clause_type = "condition"
    action_text = " ".join(t.text for t in tokens[i:])
    action = {"action": action_text} if action_text else None
    effect_ir = {
        "trigger": trigger,
        "condition": condition,
        "action": action,
    }
    return ClauseBlock(
        raw=group.raw,
        clause_type=clause_type,
        effect_ir=effect_ir,
        trigger=trigger,
        condition=condition,
        cost=cost,
    )


# ---------------------------------------------------------------------------
# Pattern segmentation
# ---------------------------------------------------------------------------

def segment_and_tag_patterns(text: str) -> List[Tuple[str, str]]:
    """Break ``text`` into tagged segments using simple token patterns."""
    tokens = _tokenizer.tokenize(text)
    segments: List[Tuple[str, str]] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == TokenType.TRIGGER_WORD:
            _, next_i = _parse_trigger_tokens(tokens, i)
            segment_text = " ".join(t.text for t in tokens[i:next_i])
            segments.append((segment_text, "TRIGGER"))
            i = next_i
            continue
        if token.type == TokenType.CONDITION_WORD:
            _, next_i = _parse_condition_tokens(tokens, i)
            segment_text = " ".join(t.text for t in tokens[i:next_i])
            segments.append((segment_text, "CONDITION"))
            i = next_i
            continue
        if token.type == TokenType.COST_WORD:
            j = i + 1
            while j < len(tokens) and tokens[j].type not in (
                TokenType.TRIGGER_WORD,
                TokenType.CONDITION_WORD,
            ):
                j += 1
            segment_text = " ".join(t.text for t in tokens[i:j])
            segments.append((segment_text, "COST"))
            i = j
            continue
        # Default: treat as part of an action clause
        j = i
        while j < len(tokens) and tokens[j].type not in (
            TokenType.TRIGGER_WORD,
            TokenType.CONDITION_WORD,
        ):
            j += 1
        segment_text = " ".join(t.text for t in tokens[i:j])
        if segment_text:
            segments.append((segment_text, "ACTION"))
        i = j
    return segments


__all__ = [
    "ClauseBlock",
    "parse_trigger_clause",
    "parse_condition_clause",
    "parse_token_group",
    "segment_and_tag_patterns",
]

