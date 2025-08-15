# ui_simulator/Simulator.py
from __future__ import annotations

from typing import Any, List, Optional

# --- Fixed imports: import concrete modules, not packages ------------------
from game_core.Player import Player
from game_core.GameState import GameState
from stack_system.StackEngine import StackEngine
from stack_system.TriggerEngine import TriggerEngine
from data_layer.CardEntities import Card, CardDataManager
from effect_execution.EffectEngine import EffectEngine

# CombatEngine location: prefer root-level CombatEngine.py; fall back if needed.
try:
    from CombatEngine import CombatEngine  # root-level file
except ImportError:  # optional fallback if your tree uses a package folder
    from combat_engine.CombatEngine import CombatEngine
# -------------------------------------------------------------------------


class Simulator:
    """
    Lightweight headless driver for quick sanity tests.
    Wires a full, minimal game environment and provides run(turns).
    """
    def __init__(self, players: Optional[List[Player]] = None):
        self.players: List[Player] = players or [Player("Alice"), Player("Bob")]
        self.stack = StackEngine()
        self.triggers = TriggerEngine()
        self.game_state = GameState(players=self.players, stack=self.stack, trigger_engine=self.triggers)
        self.combat = CombatEngine()
        self.effect_engine = EffectEngine()
        self.card_cache = CardDataManager()

    def load_deck(self, player_index: int, deck_list: List[str]) -> None:
        """Very basic library loader using CardEntities.Card + CardDataManager."""
        player = self.players[player_index]
        player.library.clear()

        for name in deck_list:
            data = self.card_cache.get_card_data(name)

            # Prefer commonly available Scryfall-style fields:
            type_line = str(data.get("type_line", ""))
            oracle_text = str(data.get("oracle_text", ""))

            # Coerce P/T safely (handles str, None, etc.)
            power = _to_int(data.get("power"), default=0)
            toughness = _to_int(data.get("toughness"), default=0)

            # Construct Card defensively to match whatever constructor your Card has.
            # Try most complete signature first, then gracefully degrade.
            card = None
            try:
                # Common modern signature
                card = Card(
                    name=data.get("name", name),
                    type_line=type_line,
                    oracle_text=oracle_text,
                    power=power,
                    toughness=toughness,
                )
            except TypeError:
                try:
                    # Older/lean signatures without P/T in __init__
                    card = Card(
                        name=data.get("name", name),
                        type_line=type_line,
                        oracle_text=oracle_text,
                    )
                    # Set P/T if attributes exist
                    if hasattr(card, "power"):
                        setattr(card, "power", power)
                    if hasattr(card, "toughness"):
                        setattr(card, "toughness", toughness)
                except TypeError:
                    # Minimal fallback (name only), then set attributes if present
                    card = Card(name=data.get("name", name))
                    if hasattr(card, "type_line"):
                        setattr(card, "type_line", type_line)
                    if hasattr(card, "oracle_text"):
                        setattr(card, "oracle_text", oracle_text)
                    if hasattr(card, "power"):
                        setattr(card, "power", power)
                    if hasattr(card, "toughness"):
                        setattr(card, "toughness", toughness)

            # If your Card uses 'types' instead of 'type_line' and data provides it
            if hasattr(card, "types") and "types" in data:
                try:
                    setattr(card, "types", list(data["types"]))
                except Exception:
                    pass

            player.library.append(card)
        # Simple shuffle omitted for determinism in smoke runs.

    def simulate_phase(self, phase: str) -> None:
        """
        Minimal, side-effectful phase step to sanity-check state transitions.
        Not exhaustive; just enough to keep headless runs consistent.
        """
        # Sync phase on GameState if the phase name is recognized
        if hasattr(self.game_state, "phases") and phase in getattr(self.game_state, "phases", []):
            self.game_state.phase_index = self.game_state.phases.index(phase)

        # Very small sample of automatic phase behaviors:
        active = self.players[self.game_state.turn_index]

        if phase == "Untap":
            for card in getattr(active, "battlefield", []):
                if getattr(card, "tapped", False):
                    card.tapped = False

        elif phase == "Draw":
            active.draw(1)

        elif phase == "Combat":
            # No attackers by default; ensure combat structures reset if your CombatEngine uses hooks.
            pass

        # Resolve one stack object (if any), then SBA + triggers:
        if not self.stack.is_empty():
            self.game_state.resolve_stack()
        self.game_state.check_state_based_actions()
        if self.triggers:
            self.triggers.check_and_push(self.game_state, self.stack)

    def run_test_game(self, turns: int = 3) -> None:
        for _ in range(turns):
            # very simple turn structure
            for phase in ("Untap", "Upkeep", "Draw", "Main1", "Combat", "Main2", "End", "Cleanup"):
                self.simulate_phase(phase)
            # Next turn
            self.game_state.next_turn()

    # .run() so MainRunner can just call it.
    def run(self, turns: int = 3) -> None:
        print(f"[Simulator] Running {turns} turn(s) headlessly.")
        self.run_test_game(turns=turns)
        print("[Simulator] Done.")


def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default
