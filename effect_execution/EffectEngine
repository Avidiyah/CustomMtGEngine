# === effect_engine.py ===
"""Unified effect execution engine for the MTG simulator.

This module merges the functionality previously spread across
``EffectExecutor.py``, ``EffectInterpreter.py`` and
``DynamicReferenceManager.py``.  It exposes :class:`EffectEngine`
with a single :py:meth:`EffectEngine.execute` entry point as well as
an :class:`EffectContext` that stores resolution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class DynamicReferenceManager:
    """Manage dynamic references used by pronouns in Oracle text."""

    def __init__(self) -> None:
        self._refs: Dict[str, Any] = {}

    def set_reference(self, tag: str, obj: Any) -> None:
        """Store ``obj`` under ``tag`` for later resolution."""
        self._refs[tag] = obj

    def resolve(self, tag: str) -> Any | None:
        """Return the object stored for ``tag`` if present."""
        return self._refs.get(tag)

    def clear(self) -> None:
        """Remove all stored references."""
        self._refs.clear()


@dataclass
class EffectContext:
    """Container for per-resolution state.

    Parameters
    ----------
    source:
        Card or ability that produced the effect.
    controller:
        Player currently controlling the effect.
    targets:
        List of resolved target objects used by the effect.
    dynamic_refs:
        Map of temporary reference tags (e.g. ``"that creature"``) to objects.
    flags:
        Arbitrary flags and selections made while resolving the spell.
    zone_changes:
        Pending zone transitions created by the effect.
    game_state:
        Optional :class:`GameState` instance for direct state manipulation.
    """

    source: Any
    controller: Any
    targets: List[Any] = field(default_factory=list)
    dynamic_refs: DynamicReferenceManager = field(default_factory=DynamicReferenceManager)
    flags: Dict[str, Any] = field(default_factory=dict)
    zone_changes: List[Dict[str, Any]] = field(default_factory=list)
    game_state: Any | None = None


class EffectEngine:
    """Interpret and execute parsed effect representations."""

    def __init__(self) -> None:
        self.ref_manager = DynamicReferenceManager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def execute(self, effect_ir: Any, context: EffectContext) -> str:
        """Execute ``effect_ir`` using ``context``.

        ``effect_ir`` may be a single action node or a nested behavior tree
        consisting of lists and dictionaries.  The engine walks the
        structure recursively and applies game state mutations.
        Returns a human readable summary of the actions performed.
        """
        return self._walk(effect_ir, context)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _walk(self, node: Any, context: EffectContext) -> str:
        if node is None:
            return ""

        if isinstance(node, list):
            logs = [self._walk(child, context) for child in node]
            return "\n".join(l for l in logs if l)

        if isinstance(node, dict):
            # Conditional branches
            if node.get("type") == "conditional":
                condition = node.get("condition", "")
                if self._evaluate_condition(condition, context):
                    return self._walk(node.get("then"), context)
                return self._walk(node.get("else"), context)

            # Modal choices
            if node.get("modal_choices"):
                index = context.flags.get("modal_choice", 0)
                choices = node.get("modal_choices", [])
                if 0 <= index < len(choices):
                    return self._walk(choices[index], context)
                return ""

            # Repeat structures
            if node.get("repeat"):
                repeat_logs: List[str] = []
                players: List[Any] = []
                if context.game_state and hasattr(context.game_state, "players"):
                    players = context.game_state.players
                if not players:
                    players = [context.controller]
                for _ in players:
                    for child in node.get("effect_chain", []):
                        repeat_logs.append(self._walk(child, context))
                return "\n".join(l for l in repeat_logs if l)

            # Effect chains
            if node.get("effect_chain") is not None:
                logs = [self._walk(eff, context) for eff in node.get("effect_chain", [])]
                return "\n".join(l for l in logs if l)

            # Single action
            if node.get("action"):
                return self._apply_action(node, context)

        return ""

    def _apply_action(self, effect: Dict[str, Any], context: EffectContext) -> str:
        action = effect.get("action", "unknown_effect")
        amount = effect.get("amount", 0)

        # Resolve dynamic reference tags
        if "reference_tag" in effect and "target_resolved" not in effect:
            ref_obj = context.dynamic_refs.resolve(effect["reference_tag"])
            if ref_obj is not None:
                effect["target_resolved"] = ref_obj

        target = effect.get("target_resolved") or effect.get("target")
        targets = target if isinstance(target, list) else [target] if target else []

        logs: List[str] = []
        gs = context.game_state

        if action == "draw_card":
            if hasattr(context.controller, "draw"):
                count = effect.get("amount", 1)
                context.controller.draw(count)
                logs.append(f"{context.controller.name} draws {count} card(s).")

        elif action == "gain_life":
            if hasattr(context.controller, "gain_life"):
                amt = effect.get("amount", 1)
                context.controller.gain_life(amt)
                logs.append(f"{context.controller.name} gains {amt} life.")

        elif action == "lose_life":
            if hasattr(context.controller, "lose_life"):
                amt = effect.get("amount", 1)
                context.controller.lose_life(amt)
                logs.append(f"{context.controller.name} loses {amt} life.")

        elif action == "deal_damage":
            for tgt in targets:
                if tgt is None:
                    continue
                if hasattr(tgt, "life"):
                    tgt.life -= amount
                    logs.append(f"{tgt.name} takes {amount} damage (life).")
                elif hasattr(tgt, "damage"):
                    tgt.damage += amount
                    logs.append(f"{tgt.name} takes {amount} damage (marked).")
                elif hasattr(tgt, "loyalty"):
                    tgt.loyalty -= amount
                    logs.append(f"{tgt.name} loses {amount} loyalty.")

        elif action == "grant_keyword":
            logs.append(f"Keyword granted: {effect.get('keyword')}")

        elif action == "create_token":
            logs.append(f"Token created: {effect.get('token')}")
            if tag := effect.get("store_as"):
                context.dynamic_refs.set_reference(tag, effect.get("token"))

        elif action == "apply_pt_modifier":
            logs.append(f"Applied P/T modifier: {effect.get('mod')} until end of turn")

        elif action == "search_library":
            logs.append(f"Searching library (reveal: {effect.get('reveal')})")

        elif action == "discard_cards":
            logs.append(f"Discarding {effect.get('amount')} cards")

        elif action == "exile_from_hand":
            logs.append("Exiling card from opponent's hand")

        elif action == "multi_player_discard":
            logs.append("Each opponent discards a card")

        elif action == "untap_permanents":
            logs.append(f"Untapping up to {effect.get('amount', 1)} permanents")

        elif action == "put_into_library_depth":
            logs.append(f"Put into library {effect.get('position')} from top")

        elif action == "destroy_target":
            for tgt in targets:
                if tgt is None:
                    continue
                if gs and hasattr(gs, "move_card"):
                    owner = getattr(tgt, "controller", context.controller)
                    gs.move_card(tgt, owner, "graveyard")
                logs.append(f"Destroying target: {getattr(tgt, 'name', tgt)}")

        elif action == "conditional_fallback":
            logs.append("[INFO] Conditional fallback detected")

        else:
            logs.append("[UNKNOWN EFFECT]")
            logs.append(f"  Action: {action}")
            logs.append(f"  Raw Text: {effect.get('raw_text', '<missing raw_text>')}")
            logs.append(f"  Full Effect: {effect}")

        return "\n".join(logs)

    def _evaluate_condition(self, condition: str, _context: EffectContext) -> bool:
        condition = condition.lower()
        if "if you do" in condition or "if you discarded" in condition:
            return True
        if "if they can't" in condition:
            return True
        if "you control a nissa" in condition:
            return True
        return False


__all__ = ["EffectEngine", "EffectContext", "DynamicReferenceManager"]
