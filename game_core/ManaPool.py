import re

# === ManaPool ===
class ManaPool:
    def __init__(self):
        self.pool = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}

    def add(self, color, amount=1):
        if color in self.pool:
            self.pool[color] += amount

    def spend(self, color, amount=1):
        if self.pool.get(color, 0) >= amount:
            self.pool[color] -= amount
            return True
        return False

    def reset(self):
        for color in self.pool:
            self.pool[color] = 0

    def total(self):
        return sum(self.pool.values())

    def __str__(self):
        return str(self.pool)

    def parse_cost(self, mana_cost):
        cost = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0, "generic": 0}
        symbols = re.findall(r"{(.*?)}", mana_cost)
        for sym in symbols:
            if sym.isdigit():
                cost["generic"] += int(sym)
            elif sym in cost:
                cost[sym] += 1
        return cost

    def can_pay(self, mana_cost):
        cost = self.parse_cost(mana_cost)
        available = self.pool.copy()
        total_available = sum(available.values())
        for color in "WUBRGC":
            if available[color] < cost[color]:
                return False
            total_available -= cost[color]
        return total_available >= cost["generic"]

    def pay(self, mana_cost):
        cost = self.parse_cost(mana_cost)
        for color in "WUBRGC":
            for _ in range(cost[color]):
                self.spend(color)
        generic_needed = cost["generic"]
        for color in "WUBRGC":
            while generic_needed > 0 and self.pool[color] > 0:
                self.spend(color)
                generic_needed -= 1
