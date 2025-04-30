# === CombatEngine ===
from game_core import PhaseManager, PriorityManager, StateBasedActions
from stack_system import TriggerEngine
class CombatEngine:
    def __init__(self, phase_manager, priority_manager, sba_engine, trigger_engine):
        self.phase_manager = phase_manager
        self.priority_manager = priority_manager
        self.sba_engine = sba_engine
        self.trigger_engine = trigger_engine
        self.attackers = {}
        self.blockers = {}

    def declare_attackers(self, player, attacker_dict, game_state):
        results = []
        if self.phase_manager.current_phase() != "Declare Attackers":
            return ["Not the correct phase for declaring attackers."]
        for attacker, target in attacker_dict.items():
            if attacker.zone != "battlefield":
                results.append(f"{attacker.name} is not on the battlefield.")
                continue
            if getattr(attacker, 'tapped', False):
                results.append(f"{attacker.name} is tapped and can't attack.")
                continue
            if getattr(attacker, 'summoning_sick', False):
                results.append(f"{attacker.name} has summoning sickness.")
                continue
            if not hasattr(attacker, 'controller') or attacker.controller != player:
                results.append(f"{attacker.name} does not belong to the active player.")
                continue
            self.attackers[attacker] = target
            attacker.status = 'attacking'
            attacker.tapped = True
            results.append(f"{attacker.name} attacks {target}.")
        return results

    def declare_blockers(self, defending_player, blocker_dict):
        results = []
        if self.phase_manager.current_phase() != "Declare Blockers":
            return ["Not the correct phase for declaring blockers."]
        for blocker, targets in blocker_dict.items():
            if blocker.zone != "battlefield":
                results.append(f"{blocker.name} is not on the battlefield.")
                continue
            if getattr(blocker, 'tapped', False):
                results.append(f"{blocker.name} is tapped and can't block.")
                continue
            if not hasattr(blocker, 'controller') or blocker.controller != defending_player:
                results.append(f"{blocker.name} does not belong to the defending player.")
                continue
            legal_targets = [a for a in targets if a in self.attackers and self.attackers[a] == defending_player]
            if not legal_targets:
                results.append(f"{blocker.name} has no legal attackers to block.")
                continue
            self.blockers[blocker] = [legal_targets[0]]
            blocker.status = 'blocking'
            results.append(f"{blocker.name} blocks {legal_targets[0].name}.")
        return results

    def assign_combat_damage(self, game_state):
        log = []
        for attacker, defender in self.attackers.items():
            blocked = any(attacker in blockers for blockers in self.blockers.values())
            if not blocked:
                if hasattr(defender, 'life'):
                    defender.life -= attacker.power
                    log.append(f"{attacker.name} deals {attacker.power} damage to {defender.name}.")
                else:
                    log.append(f"{attacker.name} hits unblocked, but {defender} has no life total.")
        for blocker, attackers in self.blockers.items():
            attacker = attackers[0]
            blocker.damage = getattr(blocker, 'damage', 0) + attacker.power
            attacker.damage = getattr(attacker, 'damage', 0) + blocker.power
            log.append(f"{attacker.name} and {blocker.name} deal damage to each other.")
            if 'manager' in game_state and hasattr(game_state['manager'], 'memory_tracker'):
                game_state['manager'].memory_tracker.log_combat_event(attacker, blocker, damage=attacker.power, blocked=True)

        if self.sba_engine:
            log += self.sba_engine.check_and_apply(game_state)
        return log
