# === TriggerEngine ===
class TriggerEngine:
    def __init__(self):
        self.registered_cards = []
        self.pending_triggers = []

    def register_trigger_reference(self, trigger_info, triggering_object, game_state):
        """
        Registers a dynamic reference when a trigger fires based on event context.
        Example: If a creature dies and the trigger says 'return that creature', store the creature.
        """
        if 'expected_reference' in trigger_info:
            tag = trigger_info['expected_reference']
            if hasattr(game_state.get('manager'), 'memory_tracker'):
                game_state['manager'].memory_tracker.tag_reference(tag, triggering_object)
                print(f"[TriggerEngine] Registered dynamic reference: {tag} -> {triggering_object}")

    def register_card(self, card):
        pass  # Placeholder (real registration logic occurs elsewhere)

    def register(self, condition_fn, effect_fn, source=""):
        self.registered_cards.append((condition_fn, effect_fn, source))

    def check_and_push(self, game_state, stack):
        """Phase-based automatic trigger resolution attempt."""
        if self.pending_triggers:
            for card, effect in self.pending_triggers:
                stack.add_trigger(card, effect)
            self.pending_triggers.clear()
