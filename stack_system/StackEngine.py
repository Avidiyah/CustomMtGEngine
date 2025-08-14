# stack_system/StackEngine.py
from dataclasses import dataclass
from typing import Any, List, Optional

from effect_execution.EffectEngine import EffectEngine, EffectContext
# expose card/player types as Any to avoid import cycles at import-time
# Runners supply real Card/Player instances at runtime.


# ------- Safe default narrator (prevents NameError) -------
class _NullNarrator:
    def log(self, event: Any):
        # Swallow logs silently; replace by injecting your own .log(event) later if desired.
        pass


narrator = _NullNarrator()


# ------- Stack Object Types -------
@dataclass
class StackObject:
    source: Any
    controller: Any
    effect_ir: Any
    name: Optional[str] = None

    def label(self) -> str:
        return self.name or getattr(self.source, "name", "Spell/Ability")


@dataclass
class Spell(StackObject):
    pass


@dataclass
class ActivatedAbility(StackObject):
    pass


@dataclass
class TriggeredAbility(StackObject):
    pass


# ------- Engine -------
class StackEngine:
    def __init__(self):
        self._stack: List[StackObject] = []

    def push(self, obj: StackObject):
        self._stack.append(obj)

    # compatibility shim for older trigger code that tried to call add_trigger(...)
    def add_trigger(self, obj: StackObject):
        self.push(obj)

    def pop(self) -> Optional[StackObject]:
        if not self._stack:
            return None
        return self._stack.pop()

    def peek(self) -> Optional[StackObject]:
        if not self._stack:
            return None
        return self._stack[-1]

    def is_empty(self) -> bool:
        return not self._stack

    def resolve_top(self, game_state: Any):
        """Pop and resolve the top object using EffectEngine."""
        obj = self.pop()
        if obj is None:
            return

        effect_engine = EffectEngine()
        context = EffectContext(
            source_card=obj.source,
            controller=obj.controller,
            targets=[],
        )
        # Execute and narrate; failures are swallowed to avoid halting the run
        try:
            effect_engine.execute(obj.effect_ir, context, game_state)
            narrator.log({"type": "stack_resolve", "label": obj.label(), "controller": getattr(obj.controller, "name", str(obj.controller))})
        except Exception as exc:
            narrator.log({"type": "stack_error", "label": obj.label(), "error": repr(exc)})

    # Convenience for GameState wrappers
    def __len__(self) -> int:
        return len(self._stack)

    def __bool__(self) -> bool:
        return not self.is_empty()
