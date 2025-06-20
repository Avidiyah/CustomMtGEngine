"""Combat and Targeting subsystem for CustomMtGEngine.

This module merges the legacy ``CombatEngine`` from ``stack_system`` and the
``TargetingSystem`` from ``effect_execution``.  It provides a single
interface for handling combat declaration and combat damage as well as
utilities for determining legal targets for spells and abilities.

Both classes here are intentionally lightweight.  They rely on the
:class:`GameState` object to query players, zones and tracked combat
assignments.  State based actions such as creature destruction are
expected to be processed elsewhere after damage has been assigned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from data_layer.card_entities import Card
from game_core.GameState import GameState
from game_core.Player import Player


@dataclass
class CombatEngine:
    """Manage combat steps according to MTG rules 506â€“509."""

    attackers: Dict[Card, Any] = field(default_factory=dict)
    blockers: Dict[Card, List[Card]] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Declaration helpers
    # ------------------------------------------------------------------
    def declare_attackers(
        self,
        game_state: GameState,
        attacking_player: Player,
        declared_attackers: List[Tuple[Card, Any]],
    ) -> List[str]:
        """Declare attackers for ``attacking_player``.

        Parameters
        ----------
        game_state:
            Current :class:`GameState` instance providing phase information.
        attacking_player:
            The player whose turn it is.
        declared_attackers:
            List of ``(creature, defender)`` pairs.  ``defender`` may be a
            :class:`Player` or a planeswalker permanent that player controls.

        Returns
        -------
        list[str]
            Human readable log messages for each declaration attempt.

        Notes
        -----
        This method enforces rule 508 from the Comprehensive Rules.  Creatures
        must be untapped, be creatures on the battlefield and either have been
        under the player's control since the start of the turn or possess
        ``haste``.  Illegal declarations are ignored and reported.
        """

        log: List[str] = []
        if game_state.current_phase() != "Declare Attackers":
            return ["Attackers may only be declared during the Declare Attackers step."]

        # ensure combat dictionary exists on the game state
        if not hasattr(game_state, "combat"):
            game_state.combat = {"attackers": {}, "blockers": {}}

        for creature, defender in declared_attackers:
            if creature.zone != "battlefield":
                log.append(f"{creature.name} is not on the battlefield.")
                continue
            if creature.controller is not attacking_player:
                log.append(f"{creature.name} is not controlled by {attacking_player.name}.")
                continue
            if "creature" not in getattr(creature, "type_line", "").lower():
                log.append(f"{creature.name} is not a creature.")
                continue
            if getattr(creature, "tapped", False):
                log.append(f"{creature.name} is tapped and can't attack.")
                continue
            if getattr(creature, "summoning_sick", False) and not getattr(creature, "haste", False):
                log.append(f"{creature.name} has summoning sickness.")
                continue
            if hasattr(creature, "can_attack") and not creature.can_attack:
                log.append(f"{creature.name} can't attack.")
                continue

            # verify defender
            legal_defender = False
            if isinstance(defender, Player) and defender in game_state.players and defender is not attacking_player:
                legal_defender = True
            elif getattr(defender, "controller", None) in game_state.players:
                legal_defender = True
            if not legal_defender:
                log.append(f"{getattr(defender, 'name', str(defender))} is not a legal defender.")
                continue

            self.attackers[creature] = defender
            game_state.combat["attackers"][creature] = defender
            creature.tapped = True
            creature.status = "attacking"
            log.append(f"{creature.name} attacks {getattr(defender, 'name', str(defender))}.")

        return log

    def declare_blockers(
        self,
        game_state: GameState,
        defending_player: Player,
        declared_blockers: List[Tuple[Card, Card]],
    ) -> List[str]:
        """Declare blockers for ``defending_player``.

        Parameters
        ----------
        game_state:
            Current :class:`GameState` instance providing phase information.
        defending_player:
            Player whose creatures are blocking this combat.
        declared_blockers:
            List of ``(blocker, attacker)`` tuples.  Multiple tuples may reference
            the same attacker allowing double or triple blocks.

        Returns
        -------
        list[str]
            Log messages describing the results of each declaration.
        """

        log: List[str] = []
        if game_state.current_phase() != "Declare Blockers":
            return ["Blockers may only be declared during the Declare Blockers step."]

        if not hasattr(game_state, "combat") or not game_state.combat.get("attackers"):
            return ["No attackers have been declared."]

        for blocker, attacker in declared_blockers:
            if blocker.zone != "battlefield":
                log.append(f"{blocker.name} is not on the battlefield.")
                continue
            if blocker.controller is not defending_player:
                log.append(f"{blocker.name} is not controlled by {defending_player.name}.")
                continue
            if "creature" not in getattr(blocker, "type_line", "").lower():
                log.append(f"{blocker.name} is not a creature.")
                continue
            if getattr(blocker, "tapped", False):
                log.append(f"{blocker.name} is tapped and can't block.")
                continue
            if blocker in self.blockers:
                log.append(f"{blocker.name} has already been declared as a blocker.")
                continue
            if attacker not in self.attackers:
                log.append(f"{attacker.name} is not attacking {defending_player.name}.")
                continue
            # Basic evasion checks
            if getattr(attacker, "flying", False) and not getattr(blocker, "flying", False) and not getattr(blocker, "reach", False):
                log.append(f"{blocker.name} can't block {attacker.name} (flying).")
                continue
            if getattr(attacker, "shadow", False) and not getattr(blocker, "shadow", False):
                log.append(f"{blocker.name} can't block {attacker.name} (shadow).")
                continue

            self.blockers.setdefault(blocker, []).append(attacker)
            game_state.combat.setdefault("blockers", {}).setdefault(blocker, []).append(attacker)
            blocker.status = "blocking"
            log.append(f"{blocker.name} blocks {attacker.name}.")

        return log

    # ------------------------------------------------------------------
    # Damage assignment
    # ------------------------------------------------------------------
    def assign_damage(self, game_state: GameState) -> List[str]:
        """Assign combat damage for the current combat step.

        This resolves combat damage for all creatures currently declared as
        attackers or blockers following APNAP order.  Damage is marked on
        creatures but destruction of lethal creatures is handled by state
        based actions outside this class.
        """

        log: List[str] = []
        if not hasattr(game_state, "combat"):
            return log

        for attacker, defender in list(self.attackers.items()):
            blockers = [b for b, att_list in self.blockers.items() if attacker in att_list]
            if not blockers:
                if hasattr(defender, "life"):
                    defender.life -= attacker.power
                log.append(f"{attacker.name} deals {attacker.power} damage to {defender.name}.")
                if hasattr(game_state, "manager") and hasattr(game_state.manager, "memory_tracker"):
                    game_state.manager.memory_tracker.log_combat_event(attacker, defender, damage=attacker.power, blocked=False)
                continue

            remaining = attacker.power
            for blocker in blockers:
                damage = 1 if getattr(attacker, "deathtouch", False) else min(remaining, blocker.toughness - getattr(blocker, "damage", 0))
                blocker.damage = getattr(blocker, "damage", 0) + damage
                remaining -= damage
                log.append(f"{attacker.name} deals {damage} damage to {blocker.name}.")
                if hasattr(game_state, "manager") and hasattr(game_state.manager, "memory_tracker"):
                    game_state.manager.memory_tracker.log_combat_event(attacker, blocker, damage=damage, blocked=True)
                if remaining <= 0:
                    break

            if remaining > 0 and getattr(attacker, "trample", False):
                if hasattr(defender, "life"):
                    defender.life -= remaining
                log.append(f"{attacker.name} deals {remaining} trample damage to {defender.name}.")
                if hasattr(game_state, "manager") and hasattr(game_state.manager, "memory_tracker"):
                    game_state.manager.memory_tracker.log_combat_event(attacker, defender, damage=remaining, blocked=True)

            for blocker in blockers:
                dmg = 1 if getattr(blocker, "deathtouch", False) else blocker.power
                attacker.damage = getattr(attacker, "damage", 0) + dmg
                log.append(f"{blocker.name} deals {dmg} damage to {attacker.name}.")
                if hasattr(game_state, "manager") and hasattr(game_state.manager, "memory_tracker"):
                    game_state.manager.memory_tracker.log_combat_event(blocker, attacker, damage=dmg, blocked=True)

        return log


class TargetingSystem:
    """Determine all legal targets for a given effect node."""

    def get_legal_targets(self, effect_ir: Dict[str, Any], game_state: GameState) -> List[Any]:
        """Return a list of objects that satisfy ``effect_ir`` restrictions.

        Parameters
        ----------
        effect_ir:
            Parsed effect node containing at least a ``"targets"`` field and
            optionally ``"zones"`` and ``"controller"`` entries.
        game_state:
            Current :class:`GameState` used to query zones and players.
        """

        required_types = effect_ir.get("targets", [])
        zones = effect_ir.get("zones", ["battlefield"])
        controller = effect_ir.get("controller")
        legal: List[Any] = []

        def player_matches(p: Player) -> bool:
            if controller == "you":
                return p is game_state.current_player()
            if controller == "opponent":
                return p is not game_state.current_player()
            return True

        # Players as potential targets
        if any(t.lower() == "player" for t in required_types):
            for p in game_state.players:
                if player_matches(p):
                    legal.append(p)

        # Permanents and cards in zones
        for p in game_state.players:
            if not player_matches(p):
                continue
            for zone in zones:
                try:
                    objects = game_state.get_zone(p, zone)
                except ValueError:
                    continue
                for obj in objects:
                    if required_types:
                        match = False
                        for t in required_types:
                            if t.lower() == "player":
                                continue
                            if t.lower() in getattr(obj, "type_line", "").lower():
                                match = True
                        if not match:
                            continue
                    if getattr(obj, "shroud", False):
                        continue
                    if getattr(obj, "hexproof", False) and obj.controller is not game_state.current_player():
                        continue
                    legal.append(obj)

        return legal


__all__ = ["CombatEngine", "TargetingSystem"]
