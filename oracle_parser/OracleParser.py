from __future__ import annotations

"""High level Oracle text parser for the engine.

This parser converts raw Oracle text into a structured intermediate
representation (IR) of effects without mutating any game state.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .Tokenizer import tokenize_clause, Tokenizer
from .ClauseParser import parse_token_group, ClauseBlock

@dataclass
class EffectIR:
    """Simplified effect representation returned by :class:`OracleParser`."""

    trigger: Optional[Dict[str, Any]] = None
    condition: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None



class OracleParser:
    """Parses Oracle text into a list of :class:`ClauseBlock` objects."""

    def __init__(self,
        tokenizer: Optional[Tokenizer] = None) -> None:
        self.tokenizer = tokenizer or Tokenizer()
        self.oracle_clauses: List[ClauseBlock] = []
        self.behavior_tree: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def parse(self, card: Any | str) -> List[ClauseBlock]:
        """Parse ``card``'s Oracle text into :class:`ClauseBlock` objects."""
        text = card if isinstance(card, str) else getattr(card, "oracle_text", "")
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        self.oracle_clauses = []
        self.behavior_tree = []

        for idx, line in enumerate(lines):
            group = tokenize_clause(line)
            clause = parse_token_group(group)
            clause.source_index = idx
            self.oracle_clauses.append(clause)
            self.behavior_tree.append(clause.effect_ir)
            
        return self.oracle_clauses

__all__ = ["OracleParser", "EffectIR", "ClauseBlock"]
