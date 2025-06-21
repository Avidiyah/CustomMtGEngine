"""Game simulation backend utilities.

This module provides a :class:`Simulator` that can be used by manual
or automated tests to drive the engine without requiring UI prompts.
The class offers helper methods for setting up a game state, loading
decks and iterating through phases.  No gameplay logic is implemented
here; it simply orchestrates calls to the existing engine modules.
"""

from __future__ import annotations

from typing import List, Sequence

from data_layer.card_entities import Card, CardDataManager
from game_core import GameState, Player
from stack_system import StackEngine, TriggerEngine
from runtime.combat_engine import CombatEngine
from effect_execution import EffectEngine
from oracle_parser import OracleParser
class Simulator:
    """Backend driver for headless or scripted simulations."""

    def __init__(self, player_names: Sequence[str]) -> None:
        """Create a new ``GameState`` with players named in ``player_names``."""
        self.players: List[Player] = [Player(name) for name in player_names]
        self.stack = StackEngine()
        self.triggers = TriggerEngine()
        self.state = GameState(self.players, stack=self.stack, trigger_engine=self.triggers)
        self.combat = CombatEngine()
        self.effect_engine = EffectEngine()
        self.parser = OracleParser()

    # ------------------------------------------------------------------
    # Deck/zone management
    # ------------------------------------------------------------------
    def load_deck(self, player_index: int, deck_list: Sequence[str]) -> None:
        """Populate ``player_index``'s library with cards from ``deck_list``."""
        manager = CardDataManager()
        player = self.players[player_index]
        player.library.clear()
        for name in deck_list:
            data = manager.get_card_data(name) or {}
            card = Card(name)
            card.oracle_text = data.get("oracle_text", "")
            card.type_line = data.get("type_line", "")
            card.mana_cost = data.get("mana_cost", "")
            player.library.append(card)

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------
    def simulate_phase(self, phase: str) -> List[str]:
        """Execute a single phase step and return log messages."""
        logs: List[str] = []
        self.state.phase_index = self.state.phases.index(phase)
        active = self.state.current_player()

        if phase == "Untap":
            active.untap_all()
        elif phase == "Draw":
            active.draw(1)

        if phase == "Declare Attackers":
            if hasattr(self.state, "combat"):
                self.state.combat.clear()
            logs.extend(self.combat.declare_attackers(self.state, active, []))

        # Resolve triggers and stack if needed
        self.triggers.check_and_push(self.state, self.stack)
        if not self.stack.is_empty():
            logs.append(self.stack.resolve_top(self.state))

        logs.extend(self.state.check_state_based_actions())
        return logs

    def run_test_game(self, turns: int = 1) -> List[str]:
        """Run a very small scripted game for ``turns`` turns."""
        log: List[str] = []
        for _ in range(turns):
            for phase in self.state.phases:
                log.extend(self.simulate_phase(phase))
            self.state.next_turn()
        return log
        return False

    @staticmethod
    def event_matches_trigger(trigger_text, event_text):
        return event_text in trigger_text or trigger_text in event_text
