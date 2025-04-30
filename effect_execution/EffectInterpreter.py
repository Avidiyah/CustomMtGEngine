# === EffectInterpreter.py ===
# Oracle-Dominant Card Execution System (v2.7+)

from .EffectExecutor import EffectExecutor
from .DynamicReferenceManager import DynamicReferenceManager

class EffectInterpreter:
    def __init__(self):
        self.executor = EffectExecutor()
        self.reference_manager = DynamicReferenceManager()

    def execute(self, card, controller, game_state):
        """
        Primary execution entry point for any Card's behavior.
        """
        if hasattr(card, "behavior_tree") and card.behavior_tree:
            print(f"[EffectInterpreter] Executing parsed behavior for {card.name}.")
            return self.interpret_tree(card.behavior_tree, controller, game_state)
        else:
            print(f"[EffectInterpreter] WARNING: No behavior tree found for {card.name}. No effect executed.")
            return "No behavior tree to execute."

    def interpret_tree(self, tree, controller, game_state):
        if isinstance(tree, list):
            for node in tree:
                self.interpret_tree(node, controller, game_state)
            return

        if isinstance(tree, dict):
            # Conditional Execution
            if tree.get("type") == "conditional":
                condition = tree.get("condition")
                if self._evaluate_condition(condition, controller, game_state):
                    self.interpret_tree(tree.get("then"), controller, game_state)
                elif "else" in tree:
                    self.interpret_tree(tree.get("else"), controller, game_state)
                return

            # Modal Choices
            if tree.get("modal_choices"):
                options = tree["modal_choices"]
                count = tree.get("choose_count", 1)
                selected = options[:count] if isinstance(count, int) else options
                for choice in selected:
                    self.interpret_tree(choice, controller, game_state)
                return

            # Repeat Effects
            if tree.get("repeat"):
                print("[EffectInterpreter] Executing repeated effect once (placeholder).")
                for item in tree.get("effect_chain", []):
                    self.interpret_tree(item, controller, game_state)
                return

            # Effect Chain Execution
            if tree.get("effect_chain"):
                for effect in tree["effect_chain"]:
                    self.interpret_tree(effect, controller, game_state)
                return

            # Leaf Action Node
            if tree.get("action"):
                # Reference resolution (Phase 2.9 fallback logic)
                reference_tag = tree.get("reference_tag")
                referenced_obj = None
                if reference_tag:
                    referenced_obj = self.reference_manager.get_reference(reference_tag)
                    if not referenced_obj and hasattr(game_state.get("manager"), "memory_tracker"):
                        referenced_obj = game_state["manager"].memory_tracker.get_reference_by_tag(reference_tag)
                    if referenced_obj:
                        print(f"[EffectInterpreter] Resolved reference '{reference_tag}' to object {referenced_obj}.")
                        tree["target_resolved"] = referenced_obj

                self.executor.execute([tree], game_state)
                return

            print(f"[EffectInterpreter] Unrecognized node: {tree}")

    def _evaluate_condition(self, condition, controller, game_state):
        """
        Placeholder: Evaluates a structured condition object.
        """
        if isinstance(condition, dict):
            if condition.get("controller") == "you" and condition.get("type"):
                return True
        elif isinstance(condition, str):
            return True
        return False

    def register_reference(self, tag, obj):
        """
        Exposes ability to register dynamic references externally.
        """
        self.reference_manager.set_reference(tag, obj)
