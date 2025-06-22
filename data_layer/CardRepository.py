from __future__ import annotations

"""Card data repository and metadata definitions.

This module introduces a new architecture for card information management.
It separates immutable card metadata from in-game card instances and
replaces the old ``CardDataManager`` global with a repository object that
handles cache lookup and Oracle parsing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import json

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

from oracle_parser.OracleParser import OracleParser
from oracle_parser.RuleLexicon import STATIC_KEYWORDS


@dataclass
class ClauseBlock:
    """Minimal representation of a parsed Oracle clause."""

    raw: str
    effect_ir: Any
    trigger: Optional[Dict[str, Any]] = None
    condition: Optional[Dict[str, Any]] = None


@dataclass
class CardMetadata:
    """Static card metadata parsed from Scryfall's Oracle information."""

    name: str
    oracle_text: str = ""
    type_line: str = ""
    mana_cost: str = ""
    supertypes: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)
    oracle_clauses: List[ClauseBlock] = field(default_factory=list)
    static_abilities: List[str] = field(default_factory=list)
    behavior_tree: List[Any] = field(default_factory=list)
    oracle_hash: str = ""
    card_fingerprint: str = ""

    def __post_init__(self) -> None:
        self._parse_type_line()

        parser = OracleParser()
        ir_list = parser.parse(self.oracle_text)

        lines = [l.strip() for l in self.oracle_text.split("\n") if l.strip()]
        self.oracle_clauses = [
            ClauseBlock(
                raw=line,
                effect_ir=ir.action,
                trigger=ir.trigger,
                condition=ir.condition,
            )
            for line, ir in zip(lines, ir_list)
        ]

        self.behavior_tree = [ir.action for ir in ir_list]

        text_lower = self.oracle_text.lower()
        self.static_abilities = [kw for kw in STATIC_KEYWORDS if kw in text_lower]

        self.oracle_hash = hashlib.sha1(self.oracle_text.encode()).hexdigest()
        fingerprint_str = f"{self.name}|{self.mana_cost}|{self.type_line}"
        self.card_fingerprint = hashlib.sha1(fingerprint_str.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_type_line(self) -> None:
        """Break ``type_line`` into super, card and sub types."""
        if not self.type_line:
            return
        parts = [p.strip() for p in self.type_line.split("—")]
        main = parts[0]
        subtypes: List[str] = []
        if len(parts) > 1:
            subtypes = [s.strip() for s in parts[1].split()] if parts[1] else []
        words = main.split()
        supertypes: List[str] = []
        types: List[str] = []
        for w in words:
            if w in [
                "Basic",
                "Legendary",
                "Snow",
                "World",
                "Ongoing",
            ]:
                supertypes.append(w)
            else:
                types.append(w)
        self.supertypes = supertypes
        self.types = types
        self.subtypes = subtypes


@dataclass
class GameCard:
    """In-game representation of a card instance."""

    metadata: CardMetadata
    owner: Any | None = None
    controller: Any | None = None
    zone: str = "library"
    tapped: bool = False
    damage: int = 0
    is_token: bool = False
    is_face_down: bool = False

    def display_name(self) -> str:
        return self.metadata.name

    def is_creature(self) -> bool:
        return "Creature" in self.metadata.types


class CardRepository:
    """Cache-backed provider of :class:`CardMetadata` objects."""

    def __init__(self, cache_file: str = "card_cache.json") -> None:
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    # ------------------------------------------------------------------
    # Cache file helpers
    # ------------------------------------------------------------------
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self) -> None:
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def import_cache(self, path: str) -> None:
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.cache.update(data)
            self._save_cache()
            print(f"[INFO] Imported card cache from {path}")
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"[WARNING] Failed to import cache {path}: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_card_data(self, name: str) -> Dict[str, Any] | None:
        key = name.lower()
        if key in self.cache:
            return self.cache[key]
        fetched = self._fetch_from_scryfall(name)
        if fetched:
            self.cache[key] = fetched
            self._save_cache()
            return fetched
        return None

    def load_card(self, name: str) -> CardMetadata | None:
        data = self.get_card_data(name)
        if not data:
            return None
        return CardMetadata(name=name, **data)

    # ------------------------------------------------------------------
    # Scryfall access (optional)
    # ------------------------------------------------------------------
    def _fetch_from_scryfall(self, name: str) -> Dict[str, Any] | None:
        url = f"https://api.scryfall.com/cards/named?exact={name}"
        if requests is None:
            return None
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                card = resp.json()
                return {
                    "oracle_text": card.get("oracle_text", ""),
                    "type_line": card.get("type_line", ""),
                    "mana_cost": card.get("mana_cost", ""),
                }
        except Exception as exc:  # pragma: no cover - network errors
            print(f"[ERROR] Failed to fetch card from Scryfall: {exc}")
        return None

__all__ = [
    "CardMetadata",
    "GameCard",
    "CardRepository",
    "ClauseBlock",
]
