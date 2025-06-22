"""Card entities and data management for the CustomMtGEngine.

This module consolidates card related classes including ``Card``,
``CardComponent`` and ``CardDataManager``. The manager handles loading
card information from ``card_cache.json`` and can fall back to
requesting data from the Scryfall API when needed.
"""

from __future__ import annotations

from typing import Any, Dict
from dataclasses import dataclass, field
import os
import json
try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None


class CardComponent:
    """Base class for modular card components such as abilities."""

    def on_play(self, game_state: Any) -> None:
        pass

    def activate(self, game_state: Any) -> None:
        pass


class CardDataManager:
    """Handle caching, fetching and providing card data."""

    def __init__(self, cache_file: str = "card_cache.json") -> None:
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = self.load_cache()

    def load_cache(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def import_cache(self, cache_file: str) -> None:
        try:
            with open(cache_file, "r") as f:
                external_cache = json.load(f)
            self.cache.update(external_cache)
            self.save_cache()
            print(f"[INFO] Successfully imported card cache from {cache_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARNING] Failed to import cache from {cache_file}: {e}")

    def get_card(self, card_name: str) -> Dict[str, Any] | None:
        return self.get_card_data(card_name)

    def get_card_data(self, card_name: str) -> Dict[str, Any] | None:
        if card_name in self.cache:
            return self.cache[card_name]

        card_data = self.fetch_from_scryfall(card_name)
        if card_data:
            self.cache[card_name] = card_data
            self.save_cache()
            return card_data

        lower_name = card_name.lower()
        if not (lower_name.startswith("dummy") or lower_name == "unknown card"):
            print(f"[ERROR] Scryfall could not find card: {card_name}")
            print(f"[WARNING] Failed to load card data for: {card_name}")
        return None

    def fetch_from_scryfall(self, card_name: str) -> Dict[str, Any] | None:
        url = f"https://api.scryfall.com/cards/named?exact={card_name}"
        if requests is None:
            raise RuntimeError(
                "The 'requests' package is required to fetch cards from Scryfall."
            )
        try:
            response = requests.get(url)
            if response.status_code == 200:
                card_info = response.json()
                return {
                    "oracle_text": card_info.get("oracle_text", ""),
                    "type_line": card_info.get("type_line", ""),
                    "mana_cost": card_info.get("mana_cost", ""),
                }
            return None
        except Exception as e:  # pragma: no cover - network errors
            print(f"[ERROR] Failed to fetch card from Scryfall: {e}")
            return None

    @staticmethod
    def load_card(name: str) -> Dict[str, Any] | None:
        instance = CardDataManager()
        return instance.get_card_data(name)

    def get_card_by_name(self, name: str) -> "Card":
        return Card(name)


# Global manager instance used by ``Card`` objects
_cache_file = os.path.join(os.path.dirname(__file__), "card_cache.json")
_card_data_manager = CardDataManager(cache_file=_cache_file)
_card_data_manager.import_cache(_cache_file)


@dataclass
class Card:
    """Representation of a Magic card and its parsed attributes."""

    name: str
    oracle_text: str = ""
    type_line: str = ""
    mana_cost: str = ""
    behavior_tree: Dict[str, Any] = field(default_factory=dict)
    static_ability_tags: list[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        card_data = _card_data_manager.get_card(self.name)
        if not card_data:
            card_data = _card_data_manager.fetch_from_scryfall(self.name)

        self.data = card_data or {}

        if card_data:
            self.oracle_text = card_data.get("oracle_text", "")
            self.type_line = card_data.get("type_line", "")
            self.mana_cost = card_data.get("mana_cost", "")
        else:
            print(f"[WARNING] Failed to load card data for: {self.name}")


__all__ = ["Card", "CardComponent", "CardDataManager"]
