# -*- coding: utf-8 -*-
"""Combat resolution engine.

This module centralizes combat-phase logic for the simulator.  It
replaces the former ``CombatEngine`` implementations spread across
``effect_execution`` and ``stack_system``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

from data_layer.CardEntities import Card
from game_core.GameState import GameState
from game_core.Player import Player


@dataclass
class CombatEngine:
    """Handle combat flow according to MTG rules 506â€“510."""

    attackers: Dict[Card, Any] = field(default_factory=dict)
    blockers: Dict[Card, List[Card]] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Declaration helpers
    # ------------------------------------------------------------------
    def declare_attackers(
        self,
        game_state: GameState,
        attacking_player: Player,
        attacker_assignments: List[Tuple[Card, Any]],
    ) -> List[str]:
        """Declare attackers for ``attacking_player``.

        Parameters
        ----------
        game_state:
            The current :class:`GameState`.  ``game_state.combat`` will be
            populated with attacker information.
        attacking_player:
            The active player for the declare attackers step.
        attacker_assignments:
            List of ``(creature, defender)`` pairs where ``defender`` may be a
            :class:`Player` or planeswalker permanent.

        Returns
        -------
        list[str]
            Log messages describing each declaration.

        Notes
        -----
        Legality checks follow CR 508.1â€“508.4.  Actual prevention effects
        ("canâ€™t attack") will be layered in later using static abilities.
        """

        log: List[str] = []
        if game_state.current_phase() != "Declare Attackers":
            return ["Attackers may only be declared during the Declare Attackers step."]

        if not hasattr(game_state, "combat"):
            game_state.combat = {"attackers": {}, "blockers": {}}

        for creature, defender in attacker_assignments:
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

            # TODO: inject effects like "must attack" or "can't attack" here

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
        blocker_assignments: List[Tuple[Card, Card]],
    ) -> List[str]:
        """Declare blockers for ``defending_player``.

        Parameters
        ----------
        game_state:
            Current :class:`GameState` instance.
        defending_player:
            Player whose creatures will block this combat.
        blocker_assignments:
            List of ``(blocker, attacker)`` tuples.  A blocker may appear
            multiple times to block multiple attackers.

        Returns
        -------
        list[str]
            Log messages describing declarations.

        Notes
        -----
        Legality follows CR 509.1â€“509.2.  Static effects preventing blocks or
        forcing blocks will be processed later.
        """

        log: List[str] = []
        if game_state.current_phase() != "Declare Blockers":
            return ["Blockers may only be declared during the Declare Blockers step."]

        if not hasattr(game_state, "combat") or not game_state.combat.get("attackers"):
            return ["No attackers have been declared."]

        for blocker, attacker in blocker_assignments:
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
            if attacker not in self.attackers:
                log.append(f"{attacker.name} is not attacking {defending_player.name}.")
                continue

            # TODO: apply evasion rules (flying, menace, etc.) via TargetingSystem

            self.blockers.setdefault(blocker, []).append(attacker)
            game_state.combat.setdefault("blockers", {}).setdefault(blocker, []).append(attacker)
            blocker.status = "blocking"
            log.append(f"{blocker.name} blocks {attacker.name}.")

        return log

    # ------------------------------------------------------------------
    # Damage assignment
    # ------------------------------------------------------------------
    def assign_combat_damage(self, game_state: GameState) -> List[str]:
        """Resolve combat damage for the current combat step.

        This method assigns damage after blockers have been declared.  It does
        not process state-based actions or triggers.  Those hooks will be added
        in higher level managers.
        """

        log: List[str] = []
        if not hasattr(game_state, "combat"):
            return log

        # TODO: implement APNAP ordering when multiple players assign damage
        for attacker, defender in list(self.attackers.items()):
            blockers = [b for b, att_list in self.blockers.items() if attacker in att_list]
            if not blockers:
                if hasattr(defender, "life"):
                    defender.life -= attacker.power
                log.append(f"{attacker.name} deals {attacker.power} damage to {defender.name}.")
                continue

            remaining = attacker.power
            for blocker in blockers:
                dmg = 1 if getattr(attacker, "deathtouch", False) else min(remaining, blocker.toughness - getattr(blocker, "damage", 0))
                blocker.damage = getattr(blocker, "damage", 0) + dmg
                remaining -= dmg
                log.append(f"{attacker.name} deals {dmg} damage to {blocker.name}.")
                if remaining <= 0:
                    break

            if remaining > 0 and getattr(attacker, "trample", False):
                if hasattr(defender, "life"):
                    defender.life -= remaining
                log.append(f"{attacker.name} deals {remaining} trample damage to {defender.name}.")

            for blocker in blockers:
                dmg = 1 if getattr(blocker, "deathtouch", False) else blocker.power
                attacker.damage = getattr(attacker, "damage", 0) + dmg
                log.append(f"{blocker.name} deals {dmg} damage to {attacker.name}.")

        # TODO: raise triggers like "whenever this creature deals combat damage"
        # TODO: post-combat cleanup will be handled by StateBasedActions
        return log


__all__ = ["CombatEngine"]
