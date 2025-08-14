# testing_tools/Test_Run.py
import os
import sys
import unittest

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# -------------------------------------------------------------
# Minimal imports from the engine for smoke testing
# -------------------------------------------------------------
from game_core import Player, GameState
from stack_system import StackEngine, TriggerEngine, Spell
from effect_execution.EffectEngine import EffectContext, EffectEngine

# Simulator is optional for headless runs; tests adapt if not present
try:
    from ui_simulator.Simulator import Simulator
    HAS_SIMULATOR = True
except Exception:
    HAS_SIMULATOR = False


class SmokeImportsAndCoreConstruction(unittest.TestCase):
    """Sanity check: core types import and basic objects construct."""

    def test_imports_and_construction(self):
        p1, p2 = Player("Alice"), Player("Bob")
        stack = StackEngine()
        triggers = TriggerEngine()
        state = GameState(players=[p1, p2], stack=stack, trigger_engine=triggers)

        # Basic invariants
        self.assertEqual(len(state.players), 2)
        self.assertTrue(stack.is_empty())
        self.assertIs(state.trigger_engine, triggers)

        # No-op SBA pass should not raise
        state.check_state_based_actions()


class SmokeSimulatorHeadless(unittest.TestCase):
    """Headless run for 1–2 turns to ensure nothing crashes."""

    @unittest.skipUnless(HAS_SIMULATOR, "Simulator not available in this build")
    def test_headless_one_turn(self):
        sim = Simulator()
        # Prefer .run if available; else fallback to .run_test_game
        runner = getattr(sim, "run", None) or getattr(sim, "run_test_game", None)
        self.assertIsNotNone(runner, "Simulator has no run or run_test_game method")

        start_turn = sim.game_state.turn_index
        runner(turns=1)
        # Turn index should advance by at least 1 modulo player count (robust to modulo wrap)
        self.assertNotEqual(sim.game_state.turn_index, start_turn)


class SmokeTriggerEnginePath(unittest.TestCase):
    """Queue a trivial trigger and ensure it can be pushed and resolved."""

    def test_trigger_queue_and_push(self):
        p1, p2 = Player("Alice"), Player("Bob")
        stack = StackEngine()
        triggers = TriggerEngine()
        state = GameState(players=[p1, p2], stack=stack, trigger_engine=triggers)

        # Queue a trivial no-op effect IR and push it
        triggers.fire_now(effect_ir={}, source=p1)
        # Should not raise
        triggers.check_and_push(state, stack)

        # If a trigger was pushed, resolve it; otherwise this is a no-op smoke check
        if not stack.is_empty():
            # Resolve top; ensure it doesn't raise
            stack.resolve_top(state)
            self.assertTrue(stack.is_empty())


class SmokeStackResolution(unittest.TestCase):
    """Resolve a minimal spell with a do-nothing effect IR."""

    class _DummyCard:
        def __init__(self, name="Test Spell"):
            self.name = name

    def test_resolve_noop_spell(self):
        p1, p2 = Player("Alice"), Player("Bob")
        stack = StackEngine()
        state = GameState(players=[p1, p2], stack=stack, trigger_engine=TriggerEngine())

        # Minimal no-op effect: most EffectEngine implementations will ignore/handle unknown actions
        dummy_effect_ir = {}
        spell = Spell(source=self._DummyCard(), controller=p1, effect_ir=dummy_effect_ir)
        stack.push(spell)

        # Resolution should not raise and should empty the stack
        stack.resolve_top(state)
        self.assertTrue(stack.is_empty())

        # Also ensure EffectEngine can be called directly in a no-op context without error
        ee = EffectEngine()
        ctx = EffectContext(source_card=spell.source, controller=p1, targets=[])
        # Should not raise even if effect_ir is empty
        ee.execute(dummy_effect_ir, ctx, state)


if __name__ == '__main__':
    unittest.main(verbosity=2)