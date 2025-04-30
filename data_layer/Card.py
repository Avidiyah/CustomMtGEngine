from .CardDataManager import CardDataManager

_card_data_manager = CardDataManager()
_card_data_manager.import_cache("card_cache.json")  # Ensure cache is loaded

class Card:
    def __init__(self, name):
        self.name = name
        self.oracle_text = ""
        self.type_line = ""
        self.mana_cost = ""
        self.behavior_tree = {}
        self.static_ability_tags = []

        # Pull from cache, or fetch from Scryfall if not found
        card_data = _card_data_manager.get_card(name)
        if not card_data:
            card_data = _card_data_manager.fetch_from_scryfall(name)

        self.data = card_data or {}

        if card_data:
            self.oracle_text = card_data.get("oracle_text", "")
            self.type_line = card_data.get("type_line", "")
            self.mana_cost = card_data.get("mana_cost", "")
        else:
            print(f"[WARNING] Failed to load card data for: {name}")
