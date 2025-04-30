# === Simulator.py ===

from data_layer import Card
from oracle_parser import OracleParserPipeline
from stack_system import TriggerEngine, Stack
from game_core import PhaseManager, Player, GameManager, PriorityManager, StateBasedActions, ZoneManager
from ui_simulator import GameUI


class Simulator:
    def __init__(self, headless=False):
        self.headless = headless
        self.stack = Stack()
        self.phase_manager = PhaseManager()
        self.trigger_engine = TriggerEngine()
        self.players = [Player(name="Player 1"), Player(name="Player 2")]
        self.priority_manager = PriorityManager(self.players[0], self.players[1])
        self.state_based_actions = StateBasedActions()
        self.zone_manager = ZoneManager()

        self.game_state = {
            "players": self.players,
            "stack": self.stack,
            "phase_manager": self.phase_manager,
            "trigger_engine": self.trigger_engine,
            "priority_manager": self.priority_manager,
            "state_based_actions": self.state_based_actions,
            "zone_manager": self.zone_manager
        }

        self.game_manager = GameManager(
            players=self.players,
            stack=self.stack,
            phase_manager=self.phase_manager,
            trigger_engine=self.trigger_engine,
            priority_manager=self.priority_manager,
            state_based_actions=self.state_based_actions,
            headless=True
        )

        if not self.headless:
            self.ui = GameUI(self.game_manager, self.game_state, dummy_mode=False)
        else:
            self.ui = None  # No GameUI in headless

    def run(self):
        if self.headless:
            self.run_headless()
        else:
            self.run_manual()

    def run_manual(self):
        print("\n=== Manual Simulation ===")
        card_name = input("\nEnter the name of the card you want to simulate: ").strip()

        card = Card(name=card_name)
        parser = OracleParserPipeline()

        oracle_text = card.data.get("oracle_text", "")
        parser.parse_oracle_text(card, oracle_text)

        print("\n=== CARD DATA ===")
        print(f"[Name] {card.name}")
        print(f"[Type Line] {card.data.get('type_line', 'Unknown')}")
        print(f"[Mana Cost] {card.data.get('mana_cost', 'Unknown')}")
        print(f"[Oracle Text] {oracle_text}")

        print("\n=== PARSING RESULTS ===")
        print(f"[Static Abilities Detected] {card.static_ability_tags}")
        print("\n[Behavior Tree Effects]")
        has_unknown = False
        for effect in card.behavior_tree:
            if effect.get("action") == "unknown_effect":
                print(f"  ❌ [UNMATCHED EFFECT]: {effect.get('raw_text', '<no raw_text>')}")
                has_unknown = True
            else:
                print(f"  ✅ [Matched Effect]: {effect}")
        if not has_unknown:
            print("\n✅ No unmatched effects detected.")

        self.trigger_engine.register_card(card)

        print("\n=== TRIGGER REGISTRATION ===")
        print(f"[Registered Triggers for {card.name}]")
        for reg_card, reg_effect in self.trigger_engine.registered_cards:
            print(f"  - {reg_effect.get('raw_text', '')}")

        game_event = input("\nEnter an event to simulate (example: 'creature enters'): ").strip()
        print(f"[Simulated Event] {game_event}")

        self.trigger_engine.pending_triggers.clear()
        for reg_card, reg_effect in self.trigger_engine.registered_cards:
            if self.event_matches_trigger(reg_effect.get('raw_text', "").lower(), game_event.lower()):
                self.trigger_engine.pending_triggers.append((reg_card, reg_effect))

        print("\n[Pending Triggers Detected]")
        if self.trigger_engine.pending_triggers:
            for pend_card, pend_effect in self.trigger_engine.pending_triggers:
                print(f"  - {pend_card.name} trigger: {pend_effect.get('raw_text', '')}")
        else:
            print("  - None")

        print("\n=== PRIORITY PASS ===")
        self.phase_manager.pass_priority(self.game_state)

        print("\n[Stack after Priority Pass]")
        print(self.stack.log())

        print("\n=== SIMULATION COMPLETE ===")

    def run_headless(self):
        print("\n=== Headless Simulation Starting ===")
        self.setup_full_game()

        while not self.is_game_over():
            self.game_manager.execute_turn(self.game_state)
            print("[INFO] Headless Turn completed.")
        print("\n=== Headless Simulation Complete ===")

    def setup_full_game(self):
        from data_layer.Card import Card  # Correct local import

        for player in self.players:
            # Add 20 Islands
            for _ in range(20):
                island = Card(name="Island")
                island.type_line = "Basic Land — Island"
                island.mana_cost = ""
                player.library.append(island)

            # Add 20 Test Creatures
            for _ in range(20):
                creature = Card(name="Test Creature")
                creature.type_line = "Creature — Dummy"
                creature.mana_cost = "{1}{U}"  # 2 mana: 1 generic, 1 blue
                creature.power = 2
                creature.toughness = 2
                player.library.append(creature)

            # Shuffle library
            import random
            random.shuffle(player.library)

            # Draw 7 card opening hand
            player.draw(7)

    def is_game_over(self):
        for player in self.players:
            if player.life <= 0 or len(player.library) == 0:
                return True
        return False

    @staticmethod
    def event_matches_trigger(trigger_text, event_text):
        return event_text in trigger_text or trigger_text in event_text
