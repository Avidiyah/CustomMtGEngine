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
    """Handle combat flow according to MTG rules 506–510."""

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
        """Declare attackers for ``attacking_player``."""
        log: List[str] = []
        if game_state.current_phase() != "Declare Attackers":
            return ["Attackers may only be declared during the Declare Attackers step."]

        if not hasattr(game_state, "combat"):
            game_state.combat = {"attackers": {}, "blockers": {}}

        for creature, defender in attacker_assignments:
            # Runtime-safe reads
            zone = getattr(creature, "zone", None)
            controller = getattr(creature, "controller", None)
            type_line = getattr(creature, "type_line", "")
            tapped = getattr(creature, "tapped", False)
            summoning_sick = getattr(creature, "summoning_sick", False)
            haste = getattr(creature, "haste", False)

            if zone != "battlefield":
                log.append(f"{creature.name} is not on the battlefield.")
                continue
            if controller is not attacking_player:
                log.append(f"{creature.name} is not controlled by {attacking_player.name}.")
                continue
            if "creature" not in type_line.lower():
                log.append(f"{creature.name} is not a creature.")
                continue
            if tapped:
                log.append(f"{creature.name} is tapped and can't attack.")
                continue
            if summoning_sick and not haste:
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
            setattr(creature, "tapped", True)
            setattr(creature, "status", "attacking")
            log.append(f"{creature.name} attacks {getattr(defender, 'name', str(defender))}.")

        return log

    def declare_blockers(
        self,
        game_state: GameState,
        defending_player: Player,
        blocker_assignments: List[Tuple[Card, Card]],
    ) -> List[str]:
        """Declare blockers for ``defending_player``."""
        log: List[str] = []
        if game_state.current_phase() != "Declare Blockers":
            return ["Blockers may only be declared during the Declare Blockers step."]

        if not hasattr(game_state, "combat") or not game_state.combat.get("attackers"):
            return ["No attackers have been declared."]

        for blocker, attacker in blocker_assignments:
            # Runtime-safe reads
            zone = getattr(blocker, "zone", None)
            controller = getattr(blocker, "controller", None)
            type_line = getattr(blocker, "type_line", "")
            tapped = getattr(blocker, "tapped", False)

            if zone != "battlefield":
                log.append(f"{blocker.name} is not on the battlefield.")
                continue
            if controller is not defending_player:
                log.append(f"{blocker.name} is not controlled by {defending_player.name}.")
                continue
            if "creature" not in type_line.lower():
                log.append(f"{blocker.name} is not a creature.")
                continue
            if tapped:
                log.append(f"{blocker.name} is tapped and can't block.")
                continue
            if attacker not in self.attackers:
                log.append(f"{attacker.name} is not attacking {defending_player.name}.")
                continue

            # TODO: apply evasion rules (flying, menace, etc.) via TargetingSystem

            self.blockers.setdefault(blocker, []).append(attacker)
            game_state.combat.setdefault("blockers", {}).setdefault(blocker, []).append(attacker)
            setattr(blocker, "status", "blocking")
            log.append(f"{blocker.name} blocks {attacker.name}.")

        return log

    # ------------------------------------------------------------------
    # Damage assignment
    # ------------------------------------------------------------------
    def assign_combat_damage(self, game_state: GameState) -> List[str]:
        """Resolve combat damage for the current combat step."""
        log: List[str] = []
        if not hasattr(game_state, "combat"):
            return log

        # TODO: implement APNAP ordering when multiple players assign damage
        for attacker, defender in list(self.attackers.items()):
            # Safe reads
            a_power = int(getattr(attacker, "power", 0) or 0)
            a_deathtouch = bool(getattr(attacker, "deathtouch", False))
            a_trample = bool(getattr(attacker, "trample", False))

            blockers = [b for b, att_list in self.blockers.items() if attacker in att_list]
            if not blockers:
                if hasattr(defender, "life"):
                    defender.life -= a_power
                log.append(f"{attacker.name} deals {a_power} damage to {getattr(defender, 'name', str(defender))}.")
                continue

            remaining = a_power
            for blocker in blockers:
                b_tough = int(getattr(blocker, "toughness", 0) or 0)
                b_damage = int(getattr(blocker, "damage", 0) or 0)
                dmg = 1 if a_deathtouch else max(0, min(remaining, b_tough - b_damage))
                setattr(blocker, "damage", b_damage + dmg)
                remaining -= dmg
                log.append(f"{attacker.name} deals {dmg} damage to {blocker.name}.")
                if remaining <= 0:
                    break

            if remaining > 0 and a_trample:
                if hasattr(defender, "life"):
                    defender.life -= remaining
                log.append(f"{attacker.name} deals {remaining} trample damage to {getattr(defender, 'name', str(defender))}.")

            for blocker in blockers:
                b_power = int(getattr(blocker, "power", 0) or 0)
                b_deathtouch = bool(getattr(blocker, "deathtouch", False))
                dealt = 1 if b_deathtouch else b_power
                a_damage = int(getattr(attacker, "damage", 0) or 0)
                setattr(attacker, "damage", a_damage + dealt)
                log.append(f"{blocker.name} deals {dealt} damage to {attacker.name}.")

        # TODO: triggers like "whenever this creature deals combat damage"
        # TODO: post-combat cleanup handled by StateBasedActions
        return log


__all__ = ["CombatEngine"]
