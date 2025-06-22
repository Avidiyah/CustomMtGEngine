import os
import sys
import types
import unittest
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Ensure repository root is on sys.path. We may be invoked from ``testing_tools``
# or the repo root, so walk upward until ``data_layer`` is found.
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
while not os.path.exists(os.path.join(REPO_ROOT, "data_layer")):
    parent = os.path.dirname(REPO_ROOT)
    if parent == REPO_ROOT:
        break
    REPO_ROOT = parent
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# -------------------------------------------------------------
# Minimal stubs to avoid circular imports during tests
# -------------------------------------------------------------
# Stub oracle_parser.RuleLexicon
rulelex = types.ModuleType('oracle_parser.RuleLexicon')
rulelex.STATIC_KEYWORDS = {
    'flying', 'haste', 'first strike', 'double strike',
    'deathtouch', 'lifelink', 'vigilance', 'trample',
    'hexproof', 'menace', 'ward', 'indestructible',
    'protection', 'reach'
}
sys.modules['oracle_parser.RuleLexicon'] = rulelex

# Stub oracle_parser.OracleParser
oracle_mod = types.ModuleType('oracle_parser.OracleParser')
@dataclass
class EffectIR:
    trigger: Optional[Dict[str, Any]] = None
    condition: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None

class OracleParser:
    """Very small stub that splits text on newlines."""
    def parse(self, text: str) -> List[EffectIR]:
        clauses = [c.strip() for c in text.split('\n') if c.strip()]
        return [EffectIR(action={'action': 'noop'}) for _ in clauses]

oracle_mod.EffectIR = EffectIR
oracle_mod.OracleParser = OracleParser
sys.modules['oracle_parser.OracleParser'] = oracle_mod

# Create package entry so imports succeed
oracle_pkg = types.ModuleType('oracle_parser')
sys.modules['oracle_parser'] = oracle_pkg

# -------------------------------------------------------------
from data_layer.CardRepository import CardRepository, GameCard, CardMetadata

class CardRepositoryPhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cache_path = os.path.join(REPO_ROOT, 'data_layer', 'card_cache.json')
        cls.repo = CardRepository(cache_file=cache_path)
        cls.metadata = cls.repo.load_card('glorybringer')
        cls.gamecard = GameCard(metadata=cls.metadata)

    def test_metadata_parsing(self):
        md = self.metadata
        self.assertIsInstance(md, CardMetadata)
        self.assertIn('Creature', md.types)
        self.assertIn('Dragon', md.subtypes)
        self.assertIn('flying', md.static_abilities)
        self.assertGreater(len(md.oracle_clauses), 0)
        self.assertTrue(md.oracle_hash)
        self.assertTrue(md.card_fingerprint)
        print('\nCard Fingerprint:', md.card_fingerprint)
        print('Supertypes:', md.supertypes)
        print('Types:', md.types)
        print('Subtypes:', md.subtypes)
        print('Static Abilities:', md.static_abilities)
        for i, clause in enumerate(md.oracle_clauses, 1):
            print(f'Clause {i}:',
                  'trigger=', clause.trigger,
                  'condition=', clause.condition,
                  'effect=', clause.effect_ir)

    def test_gamecard_wrapper(self):
        gc = self.gamecard
        self.assertTrue(gc.is_creature())
        self.assertEqual(gc.zone, 'library')

    def test_repository_load(self):
        loaded = self.repo.load_card('glorybringer')
        self.assertIsInstance(loaded, CardMetadata)

if __name__ == '__main__':
    unittest.main(verbosity=2)
