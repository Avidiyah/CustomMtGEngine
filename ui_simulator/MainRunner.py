
from ui_simulator import Simulator
from game_core import Player, GameManager, PriorityManager
from stack_system import StackEngine, TriggerEngine



def initialize_players():
    print("Initializing players...")
    return [Player("Alice"), Player("Bob")]

def setup_game(headless=False):
    players = initialize_players()
    if headless:
        return Simulator(headless=True)
    else:
        stack = StackEngine()
        trigger_engine = TriggerEngine()
        priority_manager = PriorityManager(players[0], players[1])
               return GameManager(players, stack, None, trigger_engine, priority_manager, None, headless=False)
def main():
    print("Launching Magic: The Gathering engine...")
    mode = input("Select mode: [manual] or [headless] > ").strip().lower()
    headless = (mode == "headless")
    game = setup_game(headless=headless)
    game.run()

if __name__ == "__main__":
    main()
