# ui_simulator/MainRunner.py
from typing import List
from game_core import Player, GameManager, GameState
from stack_system import StackEngine, TriggerEngine, PriorityManager
from ui_simulator.Simulator import Simulator
from ui_simulator.GameUI import GameUI


def setup_game(mode: str):
    """
    Returns a runnable object depending on mode:
      - 'headless' -> Simulator (with .run(turns) available)
      - 'manual'   -> GameUI (with .run() interactive loop)
    """
    players: List[Player] = [Player("Alice"), Player("Bob")]

    if mode == "headless":
        # Simulator already wires players + stack + triggers + game_state internally.
        return Simulator(players=players)

    # --- manual mode ---
    stack = StackEngine()
    triggers = TriggerEngine()
    priority = PriorityManager(num_players=len(players))

    game_state = GameState(players=players, stack=stack, trigger_engine=triggers)
    manager = GameManager(
        players=players,
        stack=stack,
        trigger_engine=triggers,
        priority_manager=priority,
        headless=False,
    )
    return GameUI(manager=manager, game_state=game_state)


def main():
    mode = input("Choose mode: [manual] or [headless]: ").strip().lower()
    if mode not in ("manual", "headless"):
        print("Invalid choice; defaulting to headless.")
        mode = "headless"

    game = setup_game(mode)

    # Unify launch:
    if mode == "headless":
        # Run a short demo game; user can change the turn count here or via prompt.
        try:
            turns_str = input("Headless: how many turns to simulate? [default 3]: ").strip()
            turns = int(turns_str) if turns_str else 3
        except Exception:
            turns = 3
        game.run(turns=turns)
    else:
        # Manual text UI (no GameManager.run loop).
        game.run()


if __name__ == "__main__":
    main()
