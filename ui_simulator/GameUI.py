# GameUI.py — Updated for Dummy Input System and Manual Mode
from stack_system import Spell

class GameUI:
    def __init__(self, game_manager, game_state, dummy_mode=False):
        self.game_manager = game_manager
        self.game_state = game_state
        self.dummy_mode = dummy_mode
        self.targeting_system = game_state.get("targeting_system", None)

    def run(self):
        while True:
            current_player = self.game_manager.priority_manager.current_player()
            phase = self.game_manager.phase_manager.current_phase()

            if self.dummy_mode:
                self.auto_action(current_player)
                continue

            print(f"== {phase} ==")
            print(f"--- {current_player.name}'s Turn ---")
            print(f"Hand: {[card.name for card in current_player.hand]}")

            if phase == "Untap":
                for player in self.game_state["players"]:
                    player.reset_mana_pool()
                current_player.untap_all()

            self.game_state["trigger_engine"].check_and_push(self.game_state, self.game_state["stack"])

            command = input("Enter an action: [play <card>] [activate <card>] [tap <land>] [pass]\nAction > ").strip().lower()

            if command == "pass":
                if self.game_manager.priority_manager.pass_priority():
                    self.game_manager.state_based_actions.check_and_apply(self.game_state)
                    self.game_manager.phase_manager.next_phase()
                    self.game_manager.priority_manager.reset()
                    if self.game_manager.phase_manager.current_phase() == "Cleanup":
                        self.game_manager.end_turn()
                        self.game_manager.start_next_turn()
                continue

            if command.startswith("play "):
                name = command[5:].strip().capitalize()
                for card in current_player.hand:
                    if card.name.lower() == name.lower():
                        if "land" in card.type_line.lower():
                            print(current_player.play_land(card, self.game_state))
                        else:
                            if not current_player.can_pay_cost(card.mana_cost):
                                print("Not enough mana.")
                                break
                            current_player.pay_cost(card.mana_cost)
                            spell = Spell(card=card, controller=current_player)
                            self.game_state["stack"].push(spell)
                            current_player.hand.remove(card)
                        break
                else:
                    print("Card not found in hand.")

            elif command.startswith("tap "):
                name = command[4:].strip().capitalize()
                for perm in current_player.battlefield:
                    if perm.name.lower() == name.lower():
                        if not perm.tapped:
                            perm.tapped = True
                            current_player.add_mana("U")
                            print(f"{perm.name} tapped for U mana.")
                        else:
                            print(f"{perm.name} is already tapped.")
                        break
                else:
                    print("Card not found on battlefield.")

            if phase == "Precombat Main" and not self.game_state["stack"].is_empty():
                print("Resolving stack...")
                print(self.game_state["stack"].resolve_top(self.game_state))

    def auto_action(self, current_player):
        if self.try_tap_land(current_player):
            return
        if self.try_cast_spell(current_player):
            return
        self.game_manager.priority_manager.pass_priority()

    def try_tap_land(self, current_player):
        for perm in current_player.battlefield:
            if "Land" in perm.type_line and not perm.tapped:
                perm.tapped = True
                current_player.add_mana("U")
                print(f"[AUTO] {perm.name} tapped for U.")
                return True
        return False

    def try_cast_spell(self, current_player):
        for card in current_player.hand:
            if "land" not in card.type_line.lower() and current_player.can_pay_cost(card.mana_cost):
                current_player.pay_cost(card.mana_cost)
                spell = Spell(card=card, controller=current_player)
                self.game_state["stack"].push(spell)
                current_player.hand.remove(card)
                print(f"[AUTO] Cast {card.name}.")
                return True
        return False
