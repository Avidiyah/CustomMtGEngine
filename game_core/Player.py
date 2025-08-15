from game_core.ManaPool import ManaPool
from stack_system.StackEngine import Spell

class Player:
    def __init__(self, name):
        self.name = name
        self.life = 20
        self.hand = []
        self.library = []
        self.graveyard = []
        self.exile = []
        self.battlefield = []
        self.mana_pool = ManaPool()
        self.lands_played_this_turn = 0

    def can_play_land(self):
        return self.lands_played_this_turn < 1

    def play_land(self, card, game_state):
        if not self.can_play_land():
            return f"{self.name} has already played a land this turn."
        if card not in self.hand:
            return f"{card.name} is not in hand."
        self.hand.remove(card)
        self.lands_played_this_turn += 1
        game_state.move_card(card, self, "battlefield")
        return f"{self.name} plays {card.name} as a land."

    def reset_land_play(self):
        self.lands_played_this_turn = 0

    def draw(self, count=1):
        drawn = []
        for _ in range(count):
            if not self.library:
                self.lose("tried to draw from empty library")
                return drawn
            card = self.library.pop(0)
            self.hand.append(card)
            drawn.append(card)
        print(f"{self.name} draws {len(drawn)} card(s): {[c.name for c in drawn]}")
        return drawn

    def gain_life(self, amount):
        self.life += amount
        print(f"{self.name} gains {amount} life. (Total: {self.life})")

    def lose_life(self, amount):
        self.life -= amount
        print(f"{self.name} loses {amount} life. (Total: {self.life})")

    def untap_all(self):
        for permanent in self.battlefield:
            if hasattr(permanent, "tapped"):
                permanent.tapped = False

    def discard_to_limit(self, limit=7):
        excess = len(self.hand) - limit
        if excess > 0:
            discarded = self.hand[-excess:]
            self.graveyard.extend(discarded)
            self.hand = self.hand[:-excess]
            return discarded
        return []

    def lose(self, reason=""):
        print(f"{self.name} loses the game. {reason}")
        self.life = 0

    def add_mana(self, color, amount=1):
        self.mana_pool.add(color, amount)

    def reset_mana_pool(self):
        self.mana_pool.reset()

    def can_pay_cost(self, mana_cost):
        return self.mana_pool.can_pay(mana_cost)

    def pay_cost(self, mana_cost):
        self.mana_pool.pay(mana_cost)

    # === Dummy Player Automation Helpers ===

    def has_untapped_lands(self):
        return any(not p.tapped and "Land" in p.type_line for p in self.battlefield)

    def tap_land_for_mana(self):
        for perm in self.battlefield:
            if "Land" in perm.type_line and not perm.tapped:
                perm.tapped = True
                self.add_mana("U")
                print(f"{self.name} taps {perm.name} for U mana.")
                return True
        return False

    def can_cast_spell(self):
        return any(card for card in self.hand if "land" not in card.type_line.lower() and self.can_pay_cost(card.mana_cost))

    def cast_random_spell(self, game_state):
        for card in self.hand:
            if "land" not in card.type_line.lower() and self.can_pay_cost(card.mana_cost):
                self.pay_cost(card.mana_cost)
                spell = Spell(source=card, controller=self, effect_ir=getattr(card, "behavior_tree", {}))
                game_state.stack.push(spell)
                self.hand.remove(card)
                print(f"{self.name} casts {card.name}.")
                return True
        return False
