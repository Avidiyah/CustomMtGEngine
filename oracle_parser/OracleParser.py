from __future__ import annotations

"""High level Oracle text parser for the engine.

This parser converts raw Oracle text into a structured intermediate
representation (IR) of effects without mutating any game state.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from .Tokenizer import Tokenizer, TokenType
from .EffectRegistry import STANDARD_EFFECTS
from .ClauseParser import (
    _parse_trigger_tokens,
    _parse_condition_tokens,
)


@dataclass
class EffectIR:
    """Simplified effect representation returned by :class:`OracleParser`."""

    trigger: Optional[Dict[str, Any]] = None
    condition: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None


class OracleParser:
    """Parses Oracle text into a list of :class:`EffectIR` objects."""

    def __init__(self,
                 tokenizer: Optional[Tokenizer] = None,
                 effect_registry: Optional[Dict[str, Dict[str, Any]]] = None,
                 trigger_parser: Optional[callable] = None,
                 condition_parser: Optional[callable] = None) -> None:
        self.tokenizer = tokenizer or Tokenizer()
        self.effect_registry = effect_registry or STANDARD_EFFECTS
        self.trigger_parser = trigger_parser or _parse_trigger_tokens
        self.condition_parser = condition_parser or _parse_condition_tokens

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def parse(self, card: Any | str) -> List[EffectIR]:
        """Parse ``card``'s Oracle text into an IR list."""
        text = card if isinstance(card, str) else getattr(card, "oracle_text", "")
        clauses = self._split_clauses(text)
        ir_list: List[EffectIR] = []
        for clause in clauses:
            tokens = self.tokenizer.tokenize(clause)
            ir = self._parse_tokens(tokens)
            if ir:
                ir_list.append(ir)
        return ir_list

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _split_clauses(self, text: str) -> List[str]:
        """Naive clause splitting on periods and semicolons."""
        import re

        parts = re.split(r"\. |; |\n", text)
        return [p.strip() for p in parts if p.strip()]

    def _parse_tokens(self, tokens: List[Any]) -> Optional[EffectIR]:
        trigger: Optional[Dict[str, Any]] = None
        condition: Optional[Dict[str, Any]] = None

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == TokenType.TRIGGER_WORD:
                trig, new_i = self.trigger_parser(tokens, i)
                trigger = trig.get("trigger")
                i = new_i
                continue
            if token.type == TokenType.CONDITION_WORD:
                condition, new_i = self.condition_parser(tokens, i)
                i = new_i
                break
            i += 1

        action_tokens = tokens[i:]
        action_text = " ".join(t.value for t in action_tokens)
        action = self._match_action(action_text)
        if not action:
            action = {"action": "unparsed_effect", "raw_text": action_text}

        return EffectIR(trigger=trigger, condition=condition, action=action)

    def _match_action(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.lower()
        for entry in self.effect_registry.values():
            phrases = entry.get("phrases", [])
            if any(p in text for p in phrases):
                parse_fn = entry.get("parse")
                return parse_fn(text)
        return None

__all__ = ["OracleParser", "EffectIR"]
