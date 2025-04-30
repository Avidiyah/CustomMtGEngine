# === EffectExecutor.py ===
# Executes parsed effect nodes on the game state

class EffectExecutor:
    def __init__(self):
        pass

    def execute(self, behavior_tree, game_state):
        print(f"Executing: {behavior_tree}")

        if behavior_tree.get("repeat", False):
            for _ in game_state.get("players", []):
                self._execute_chain(behavior_tree.get("effect_chain", []), game_state)
            return "Repeated execution complete."

        if "conditions" in behavior_tree and behavior_tree["conditions"]:
            condition_passed = all(self.evaluate_condition(cond, game_state)
                                   for cond in behavior_tree["conditions"])
            if condition_passed:
                return self._execute_chain(behavior_tree.get("effect_chain", []), game_state)
            elif "fallback_chain" in behavior_tree:
                return self._execute_chain(behavior_tree.get("fallback_chain", []), game_state)
            else:
                print("[INFO] Condition failed, no fallback.")
                return "Condition failed. No effect."

        return self._execute_chain(behavior_tree.get("effect_chain", []), game_state)

    def _execute_chain(self, chain, game_state):
        output_log = []
        stack = game_state.get("stack")
        targets = []
        if stack and hasattr(stack, "peek"):
            top_item = stack.peek()
            if top_item and isinstance(top_item, dict):
                targets = top_item.get("targets", [])

        for effect in chain:
            action = effect.get("action", "unknown_effect")
            value = effect.get("amount", 0)
            target = effect.get("target_resolved") or effect.get("target", None)

            if action == "draw_card":
                for p in game_state.get("players", []):
                    if hasattr(p, "draw"):
                        p.draw(1)
                        output_log.append(f"{p.name} draws a card.")

            elif action == "gain_life":
                for p in game_state.get("players", []):
                    if hasattr(p, "gain_life"):
                        p.gain_life(1)
                        output_log.append(f"{p.name} gains 1 life.")

            elif action == "deal_damage":
                for tgt in targets:
                    if hasattr(tgt, "life"):
                        tgt.life -= value
                        output_log.append(f"{tgt.name} takes {value} damage (life).")
                    elif hasattr(tgt, "damage"):
                        tgt.damage += value
                        output_log.append(f"{tgt.name} takes {value} damage (marked).")
                    elif hasattr(tgt, "loyalty"):
                        tgt.loyalty -= value
                        output_log.append(f"{tgt.name} loses {value} loyalty.")

            elif action == "grant_keyword":
                output_log.append(f"Keyword granted: {effect.get('keyword')}")

            elif action == "create_token":
                output_log.append(f"Token created: {effect.get('token')}")

            elif action == "apply_pt_modifier":
                output_log.append(f"Applied P/T modifier: {effect.get('mod')} until end of turn")

            elif action == "search_library":
                output_log.append(f"Searching library (reveal: {effect.get('reveal')})")

            elif action == "discard_cards":
                output_log.append(f"Discarding {effect.get('amount')} cards")

            elif action == "exile_from_hand":
                output_log.append("Exiling card from opponent's hand")

            elif action == "multi_player_discard":
                output_log.append(f"Each opponent discards a card")

            elif action == "untap_permanents":
                output_log.append(f"Untapping up to {effect.get('amount', 1)} permanents")

            elif action == "put_into_library_depth":
                output_log.append(f"Put into library {effect.get('position')} from top")

            elif action == "destroy_target":
                output_log.append(f"Destroying target: {target}")

            elif action == "conditional_fallback":
                output_log.append(f"[INFO] Conditional fallback detected")

            else:
                output_log.append("[UNKNOWN EFFECT]")
                output_log.append(f"  Action: {effect.get('action', '<none>')}")
                output_log.append(f"  Raw Text: {effect.get('raw_text', '<missing raw_text>')}")
                output_log.append(f"  Full Effect: {effect}")

        return "\n".join(output_log)

    def evaluate_condition(self, condition, game_state):
        condition = condition.lower()
        if "if you do" in condition or "if you discarded" in condition:
            return True
        if "if they can't" in condition:
            return True
        if "you control a nissa" in condition:
            return True
        return False
