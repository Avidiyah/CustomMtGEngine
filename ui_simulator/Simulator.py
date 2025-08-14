# ui_simulator/Simulator.py
from typing import List, Optional
from game_core import Player, GameState
from stack_system import StackEngine, TriggerEngine
from data_layer.CardEntities import Card, CardDataManager
from effect_execution.EffectEngine import EffectEngine
from combat_engine.CombatEngine import CombatEngine  # adjust path if your repo uses root-level CombatEngine.py


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

    def load_deck(self, player_index: int, deck_list: List[str]):
        """Very basic library loader using CardEntities.Card + CardDataManager."""
        player = self.players[player_index]
        player.library.clear()
        for name in deck_list:
            data = self.card_cache.get_card_data(name)
            player.library.append(Card(name=data.get("name", name), types=data.get("types", []),
                                       power=data.get("power", 0), toughness=data.get("toughness", 0)))
        # Simple shuffle omitted for determinism in smoke runs.

    def simulate_phase(self, phase: str):
        """
        Minimal, side-effectful phase step to sanity-check state transitions.
        Not exhaustive; just enough to keep headless runs consistent.
        """
        # Sync phase on GameState
        if phase in self.game_state.phases:
            self.game_state.phase_index = self.game_state.phases.index(phase)

        # Very small sample of automatic phase behaviors:
        active = self.players[self.game_state.turn_index]

        if phase == "Untap":
            for card in active.battlefield:
                if getattr(card, "tapped", False):
                    card.tapped = False

        elif phase == "Draw":
            active.draw(1)

        elif phase == "Combat":
            # No attackers by default; ensure combat structures reset if your CombatEngine uses game_state hooks.
            pass

        # Resolve one stack object (if any), then SBA + triggers:
        if not self.stack.is_empty():
            self.game_state.resolve_stack()
        self.game_state.check_state_based_actions()
        if self.triggers:
            self.triggers.check_and_push(self.game_state, self.stack)

    def run_test_game(self, turns: int = 3):
        for _ in range(turns):
            # very simple turn structure
            for phase in ("Untap", "Upkeep", "Draw", "Main1", "Combat", "Main2", "End", "Cleanup"):
                self.simulate_phase(phase)
            # Next turn
            self.game_state.next_turn()

    # NEW: .run() so MainRunner can just call it.
    def run(self, turns: int = 3):
        print(f"[Simulator] Running {turns} turn(s) headlessly.")
        self.run_test_game(turns=turns)
        print("[Simulator] Done.")
