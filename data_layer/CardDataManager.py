# === CardDataManager.py ===
# Handles caching, fetching, and importing Magic card data

import json
import requests

class CardDataManager:
    def get_card_by_name(self, name):
        from .Card import Card
        return Card(name)

    def __init__(self, cache_file='card_cache.json'):
        """Initialize CardDataManager with a default cache file."""
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        """Load local card cache from disk."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self):
        """Save current card cache to disk."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def import_cache(self, cache_file):
        """Import an external cache file into the current cache."""
        try:
            with open(cache_file, 'r') as f:
                external_cache = json.load(f)
                self.cache.update(external_cache)
                self.save_cache()
                print(f"[INFO] Successfully imported card cache from {cache_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARNING] Failed to import cache from {cache_file}: {e}")

    def get_card(self, card_name):
        """Legacy alias to maintain compatibility with older engine modules."""
        return self.get_card_data(card_name)

    def get_card_data(self, card_name):
        """Retrieve card data from cache or fetch from Scryfall if missing."""
        if card_name in self.cache:
            return self.cache[card_name]

        card_data = self.fetch_from_scryfall(card_name)
        if card_data:
            self.cache[card_name] = card_data
            self.save_cache()
            return card_data
        else:
            lower_name = card_name.lower()
            if not (lower_name.startswith("dummy") or lower_name == "unknown card"):
                print(f"[ERROR] Scryfall could not find card: {card_name}")
                print(f"[WARNING] Failed to load card data for: {card_name}")
            return None

    def fetch_from_scryfall(self, card_name):
        """Attempt to fetch card data from the Scryfall API."""
        url = f"https://api.scryfall.com/cards/named?exact={card_name}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                card_info = response.json()
                return {
                    "oracle_text": card_info.get("oracle_text", ""),
                    "type_line": card_info.get("type_line", ""),
                    "mana_cost": card_info.get("mana_cost", ""),
                }
            else:
                return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch card from Scryfall: {e}")
            return None
    @staticmethod
    def load_card(name):
        """Static method to fetch a single card using default manager."""
        instance = CardDataManager()
        return instance.get_card_data(name)
