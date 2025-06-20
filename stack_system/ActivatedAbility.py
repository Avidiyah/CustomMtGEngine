# === ActivatedAbility ===

from ..data_layer import CardComponent

class ActivatedAbility(CardComponent):
    def __init__(self, cost, effect):
        self.cost = cost
        self.effect = effect

    def activate(self, game_state):
        print(f"Activating ability: {self.effect}")
