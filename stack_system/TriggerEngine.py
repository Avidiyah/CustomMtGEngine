# stack_system/TriggerEngine.py
from typing import Any, Callable, List, Tuple
from stack_system.StackEngine import TriggeredAbility


class TriggerEngine:
    """
    Minimal trigger registry. For stability, we do not attempt full CR 603 integration here.
    - register(condition_fn, effect_ir_fn, source): store a trigger
    - fire_now(effect_ir, source): immediate push helper (used by simple ETB demos)
    - check_and_push(game_state, stack): push any pending triggers (no detection loop implemented)
    """
    def __init__(self):
        # Each entry: (condition_fn, effect_ir_fn, source)
        self.registered: List[Tuple[Callable[[Any], bool], Callable[[], Any], Any]] = []
        # Pending entries: (effect_ir, source)
        self.pending: List[Tuple[Any, Any]] = []

    def register(self, condition_fn: Callable[[Any], bool], effect_ir_fn: Callable[[], Any], source: Any):
        self.registered.append((condition_fn, effect_ir_fn, source))

    def fire_now(self, effect_ir: Any, source: Any):
        """Simple helper to queue a trigger for immediate stack push on next check."""
        self.pending.append((effect_ir, source))

    def check_and_push(self, game_state: Any, stack: Any):
        """
        Consume any pending triggers and push them to the stack as TriggeredAbility.
        (We do NOT do event detection here; just provide a safe path for modules that queue triggers.)
        """
        if not self.pending:
            return
        while self.pending:
            effect_ir, source = self.pending.pop(0)
            controller = getattr(source, "controller", None)
            stack.add_trigger(TriggeredAbility(source=source, controller=controller, effect_ir=effect_ir))
