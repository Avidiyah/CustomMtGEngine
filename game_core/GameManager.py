# === GameManager ===
from .PriorityManager import PriorityManager
from stack_system.TriggerEngine import TriggerEngine
from stack_system import StackEngine


from .StateMemoryTracker import StateMemoryTracker

class GameManager:
    def __init__(self, players, stack, phase_manager, trigger_engine, priority_manager=None, state_based_actions=None, headless=False):
        self.players = players
        self.phase_manager = phase_manager
        self.priority_manager = priority_manager or PriorityManager(players[0], players[1])
        self.trigger_engine = trigger_engine
        # TODO: implement StateBasedActions in a later phase
        self.state_based_actions = state_based_actions
        self.stack = stack
        self.turn_player_index = 0
        self.headless_mode = headless

    def resolve_stack(self) -> str:
        """Convenience wrapper to resolve the top of the stack."""
        return self.stack.resolve_top(self)

    def current_player(self):
        return self.players[self.turn_player_index]

    def next_turn(self):
        self.turn_player_index = (self.turn_player_index + 1) % len(self.players)
        self.phase_manager.current_index = 0

    def execute_phase(self, game_state):
        phase = self.phase_manager.current_phase()
        print(f"== {phase} ==")

        if phase == "Untap":
            self.current_player().untap_all()
        elif phase == "Draw":
            self.current_player().draw(1)

        self.trigger_engine.check_and_push(game_state, self.stack)
        self.state_based_actions.check_and_apply(game_state)

        if self.headless_mode:
            self.priority_manager.pass_priority()
            if self.priority_manager.both_players_passed():
                if not self.stack.is_empty():
                    print("Resolving top of stack...")
                    print(self.stack.resolve_top(game_state))
                    self.trigger_engine.check_and_push(game_state, self.stack)
                    self.state_based_actions.check_and_apply(game_state)
                    self.priority_manager.reset()
                    return
                else:
                    self.phase_manager.next_phase()
                    self.priority_manager.reset()
                    return
            return

        while True:
            if self.priority_manager.pass_priority():
                if not self.stack.is_empty():
                    print("Resolving top of stack...")
                    print(self.stack.resolve_top(game_state))
                    self.trigger_engine.check_and_push(game_state, self.stack)
                    self.state_based_actions.check_and_apply(game_state)
                    self.priority_manager.reset()
                    continue
                else:
                    self.phase_manager.next_phase()
                    self.priority_manager.reset()
                    break

    def execute_turn(self, game_state):
        while self.phase_manager.current_phase() != "Cleanup":
            self.execute_phase(game_state)
        self.phase_manager.next_phase()
        self.next_turn()
