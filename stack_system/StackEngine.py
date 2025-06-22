"""Stack resolution system for the Custom MTG engine.

This module merges the old Stack, Spell and ActivatedAbility implementations
and introduces a unified object model for everything that can exist on the
Magic stack.  It provides a :class:`StackEngine` which resolves
:class:`StackObject` instances in a last-in, first-out manner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..event_system import (
    StackDeclinedEvent,
    StackFizzleEvent,
    StackResolutionEvent,
)

from ..data_layer.CardEntities import Card
from ..effect_execution import EffectEngine, EffectContext


@dataclass
class StackObject:
    """Base representation for any object that can be placed on the stack."""

    source: Any
    controller: Any
    targets: List[Any] = field(default_factory=list)
    effect_ir: Any = None
    name: str = ""
    zone_origin: str = ""
    resolved: bool = False
    engine: EffectEngine = field(default_factory=EffectEngine, init=False)
    
    # ------------------------------------------------------------------
    # Optional resolution helpers
    # ------------------------------------------------------------------
    @property
    def is_optional(self) -> bool:
        text = getattr(self.source, "oracle_text", "")
        return "you may" in text.lower()

    def controller_wants_to_resolve(self) -> bool:
        return True

    def has_legal_targets(self, game_state: Any) -> bool:
        if not self.targets:
            return True
        return any(self._is_target_legal(t) for t in self.targets)

    def resolve(self, game_state: Any) -> str:
        """Resolve this stack object using :class:`EffectEngine`."""

        legal_targets = [t for t in self.targets if self._is_target_legal(t)]
        if self.targets and not legal_targets:
            self.resolved = True
            return f"{self.display_name()} fizzles — all targets illegal."
        self.targets = legal_targets

        context = EffectContext(
            source=self.source,
            controller=self.controller,
            targets=self.targets,
            game_state=game_state,
        )
        result = self.engine.execute(self.effect_ir, context)
        self.resolved = True
        return result

    def _is_target_legal(self, target: Any) -> bool:
        if hasattr(target, "is_valid") and callable(target.is_valid):
            return target.is_valid()
        return True

    def display_name(self) -> str:
        return self.name or getattr(self.source, "name", "<object>")


@dataclass
class Spell(StackObject):
    """Concrete stack object representing a spell."""

    mana_cost: str = ""
    type_line: str = ""
    card: Optional[Card] = None

    def __post_init__(self) -> None:
        if self.card is not None:
            self.source = self.card
            self.name = self.card.name
            self.effect_ir = self.card.behavior_tree
            self.mana_cost = self.card.mana_cost
            self.type_line = self.card.type_line


@dataclass
class ActivatedAbility(StackObject):
    """Stack object created from an activated ability."""

    cost: Any = None
    choices: dict | None = None


@dataclass
class TriggeredAbility(StackObject):
    """Stack object created from a triggered ability."""

    memory: dict = field(default_factory=dict)


class StackEngine:
    """Manage and resolve :class:`StackObject` instances in LIFO order."""

    def __init__(self) -> None:
        self._stack: List[StackObject] = []

    # ------------------------------------------------------------------
    # Basic stack operations
    # ------------------------------------------------------------------
    def push(self, obj: StackObject) -> None:
        """Push ``obj`` onto the stack."""
        self._stack.append(obj)

    def pop(self) -> Optional[StackObject]:
        """Remove and return the top object, if any."""
        if self._stack:
            return self._stack.pop()
        return None

    def peek(self) -> Optional[StackObject]:
        """Return the top object without removing it."""
        if self._stack:
            return self._stack[-1]
        return None

    def is_empty(self) -> bool:
        return not self._stack

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------
    def resolve_top(self, game_state: Any) -> str:
        """Resolve the topmost object on the stack."""
        obj = self.pop()
        if obj is None:
            return "Stack is empty."
        if not obj.has_legal_targets(game_state):
            event = StackFizzleEvent(obj)
            narrator.log(event)
            obj.resolved = True
            return f"{obj.display_name()} fizzles — all targets illegal."

        if obj.is_optional and not obj.controller_wants_to_resolve():
            event = StackDeclinedEvent(obj)
            narrator.log(event)
            obj.resolved = True
            return f"{obj.display_name()} resolution declined."

        result = obj.resolve(game_state)
        event = StackResolutionEvent(obj, result)
        narrator.log(event)
        return result

__all__ = [
    "StackObject",
    "Spell",
    "ActivatedAbility",
    "TriggeredAbility",
    "StackEngine",
]
