"""Centralized game state object for the engine.

This module defines :class:`GameState` which consolidates turn management,
phase progression, zone tracking and stack access.  It replaces the
former ``PhaseManager``, ``ZoneManager`` and ``StateBasedActions``
modules by providing a single object that the rest of the engine can
query and mutate.
"""

from typing import List, Dict, Any

from stack_system.Stack import Stack


class GameState:
    """Container object holding all mutable game information.

    Parameters
    ----------
    players:
        List of participating :class:`~game_core.Player` objects.
    stack:
        Optional :class:`~stack_system.Stack` instance.  If ``None`` a new
        stack is created.
    trigger_engine:
        Optional trigger engine used when moving cards to the battlefield.
    """

    phases = [
        "Untap",
        "Upkeep",
        "Draw",
        "Precombat Main",
        "Beginning of Combat",
        "Declare Attackers",
        "Declare Blockers",
        "Combat Damage",
        "End of Combat",
        "Postcombat Main",
        "End Step",
        "Cleanup",
    ]

    def __init__(self, players: List[Any] | None = None, stack: StackEngine | None = None, trigger_engine: Any | None = None) -> None:
        self.players: List[Any] = players or []
        self.stack: StackEngine = stack or StackEngine()
        self.trigger_engine = trigger_engine

        self.turn_index: int = 0
        self.phase_index: int = 0

        # Zones are stored per player and mirror the zone lists on the
        # player objects so that operations remain in sync.
        self.zones: Dict[Any, Dict[str, List[Any]]] = {}
        for p in self.players:
            self.register_player(p)

        # Rules for state based actions
        self._sba_rules = [
            {"condition": self._creature_with_zero_toughness, "action": self._destroy_creature},
            {"condition": self._creature_with_lethal_damage, "action": self._destroy_creature},
            {"condition": self._player_zero_life, "action": self._player_lose},
        ]

    # ------------------------------------------------------------------
    # Player and phase handling
    # ------------------------------------------------------------------
    def register_player(self, player: Any) -> None:
        """Add a new player to the game state.

        The player's existing zone lists will be used so that any
        mutations through :class:`GameState` remain visible on the
        player instance itself.
        """

        if player not in self.players:
            self.players.append(player)
        self.zones[player] = {
            "hand": player.hand,
            "library": player.library,
            "battlefield": player.battlefield,
            "graveyard": player.graveyard,
            "exile": player.exile,
        }

    def current_player(self) -> Any:
        """Return the player whose turn it currently is."""
        return self.players[self.turn_index]

    def current_phase(self) -> str:
        """Return the name of the current phase."""
        return self.phases[self.phase_index]

    def advance_phase(self) -> str:
        """Advance to the next phase and return its name."""
        self.phase_index = (self.phase_index + 1) % len(self.phases)
        return self.current_phase()

    def next_turn(self) -> Any:
        """Move to the next player's turn and return that player."""
        self.turn_index = (self.turn_index + 1) % len(self.players)
        self.phase_index = 0
        for p in self.players:
            if hasattr(p, "reset_land_play"):
                p.reset_land_play()
        return self.current_player()

    # ------------------------------------------------------------------
    # Zone helpers
    # ------------------------------------------------------------------
    def get_zone(self, player: Any, zone_type: str) -> List[Any]:
        """Return the requested zone list for ``player``."""
        if player not in self.zones:
            raise ValueError("Player not managed by this GameState")
        try:
            return self.zones[player][zone_type]
        except KeyError as exc:
            raise ValueError(f"Unknown zone: {zone_type}") from exc

    def move_card(self, card: Any, player: Any, new_zone: str, face_down: bool = False) -> str:
        """Move ``card`` to ``player``'s ``new_zone``.

        The card is removed from whatever zone currently contains it and
        appended to the target zone.  ``card.zone`` and ``card.controller``
        are updated as appropriate.  If the card enters the battlefield
        and the game state has a trigger engine, a placeholder ETB trigger
        will be registered automatically.
        """

        if player not in self.zones:
            raise ValueError("Player not managed by this GameState")
        if new_zone not in self.zones[player]:
            raise ValueError(f"Unknown zone: {new_zone}")

        # Remove from current zone, regardless of owner
        for zones in self.zones.values():
            for lst in zones.values():
                if card in lst:
                    lst.remove(card)

        card.zone = new_zone
        card.is_face_down = face_down
        card.controller = player

        self.zones[player][new_zone].append(card)

        if new_zone == "battlefield" and self.trigger_engine:
            oracle = getattr(card, "oracle_text", "").lower()
            if "enters the battlefield" in oracle:
                def effect():
                    return f"{card.name}'s ETB trigger resolves."
                self.trigger_engine.register(lambda state: True, effect, source=card.name)
        return f"{card.name} moves to {new_zone}."

    # ------------------------------------------------------------------
    # Stack interaction
    # ------------------------------------------------------------------
    def push_to_stack(self, item: Any) -> str:
        """Push a :class:`StackObject` onto the stack."""
        self.stack.push(item)
        name = getattr(item, "display_name", lambda: str(item))()
        return f"{name} added to stack."

    def resolve_stack(self) -> str:
        """Resolve the topmost object on the stack."""
        return self.stack.resolve_top(self)

    # ------------------------------------------------------------------
    # State based actions
    # ------------------------------------------------------------------
    def check_state_based_actions(self) -> List[str]:
        """Evaluate and apply all state-based action rules."""
        results: List[str] = []
        for rule in self._sba_rules:
            for player in list(self.players):
                for permanent in list(self.get_zone(player, "battlefield")):
                    if rule["condition"](permanent):
                        results.append(rule["action"](permanent, player))
                if rule["condition"](player):
                    results.append(rule["action"](player, None))
        return results

    # --- SBA rule helpers -------------------------------------------------
    @staticmethod
    def _creature_with_zero_toughness(obj: Any) -> bool:
        return getattr(obj, "type_line", "").lower().startswith("creature") and getattr(obj, "toughness", 1) <= 0

    @staticmethod
    def _creature_with_lethal_damage(obj: Any) -> bool:
        return getattr(obj, "type_line", "").lower().startswith("creature") and getattr(obj, "damage", 0) >= getattr(obj, "toughness", 1)

    def _destroy_creature(self, creature: Any, controller: Any) -> str:
        self.move_card(creature, controller, "graveyard")
        return f"{creature.name} is destroyed by SBA."

    @staticmethod
    def _player_zero_life(player: Any) -> bool:
        return hasattr(player, "life") and player.life <= 0

    @staticmethod
    def _player_lose(player: Any, _controller: Any) -> str:
        player.lose("life total is 0 or less")
        return f"{player.name} loses the game due to 0 life."
