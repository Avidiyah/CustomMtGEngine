# ui_simulator/GameUI.py
from __future__ import annotations

from game_core.GameManager import GameManager
from game_core.GameState import GameState
from game_core.Player import Player
from stack_system.StackEngine import Spell


class GameUI:
    """
    Minimal text UI that operates independently of GameManager.run().
    It uses the provided GameManager and GameState, but the loop here
    drives simple actions to avoid getting stuck in priority loops.
    """
    def __init__(self, manager: GameManager, game_state: GameState):
        self.manager = manager
        self.game_state = game_state

    def _show_hand(self, player: Player):
        print(f"\n{player.name}'s hand:")
        for i, card in enumerate(player.hand):
            print(f"  [{i}] {getattr(card, 'name', 'Unknown')}")
        if not player.hand:
            print("  (empty)")

    def _cast_from_hand_by_index(self, player: Player, idx: int):
        if idx < 0 or idx >= len(player.hand):
            print("Invalid card index.")
            return
        card = player.hand[idx]
        # In a richer engine, costs must be paid; here we push directly for manual smoke tests
        spell = Spell(source=card, controller=player, effect_ir=getattr(card, "behavior_tree", None))
        self.game_state.stack.push(spell)
        print(f"{player.name} casts {getattr(card, 'name', 'a spell')}.")

        # Resolve immediately for interactive smoothness:
        self.game_state.resolve_stack()
        self.game_state.check_state_based_actions()

    def run(self):
        print("Manual UI started. Commands: pass | cast <index> | help | quit")
        while True:
            active = self.manager.players[self.manager.turn_player_index]
            phase = self.game_state.current_phase()
            print(f"\n=== {active.name}'s {phase} ===")

            # Show quick status
            for p in self.manager.players:
                print(f"{p.name}: {p.life} life, Hand={len(p.hand)}, BF={len(p.battlefield)}")

            # Simple auto-behaviors for common phases
            if phase == "Untap":
                active.untap_all()
            elif phase == "Draw":
                active.draw(1)

            # Only prompt during main phases for simplicity
            if phase in ("Main1", "Main2"):
                self._show_hand(active)
                cmd = input("> ").strip()

                if cmd == "quit":
                    print("Exiting manual UI.")
                    break
                if cmd == "help":
                    print("Commands:\n  pass\n  cast <index>\n  quit")
                    continue
                if cmd.startswith("cast "):
                    try:
                        idx = int(cmd.split()[1])
                        self._cast_from_hand_by_index(active, idx)
                    except Exception:
                        print("Usage: cast <index>")
                        continue
                elif cmd == "pass":
                    pass
                else:
                    print("Unknown command. Type 'help'.")

            # End-of-phase housekeeping
            if not self.game_state.stack.is_empty():
                self.game_state.resolve_stack()

            # Safe trigger check (in case manager doesn't expose trigger_engine/stack)
            trig = getattr(self.manager, "trigger_engine", None)
            mgr_stack = getattr(self.manager, "stack", None)
            if trig and mgr_stack:
                trig.check_and_push(self.game_state, mgr_stack)

            self.game_state.check_state_based_actions()

            # Advance phase; roll turn on Cleanup
            # RUNTIME FIX: SimplePhaseManager.next_phase() expects no arguments
            self.manager.phase_manager.next_phase()
            if phase == "Cleanup":
                # Next player's turn
                self.manager.turn_player_index = (self.manager.turn_player_index + 1) % len(self.manager.players)
                self.game_state.next_turn()
