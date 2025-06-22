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

    def test_clause_structure(self):
        md = self.metadata
        lines = [l.strip() for l in md.oracle_text.split('\n') if l.strip()]
        self.assertEqual(len(md.oracle_clauses), len(lines))
        for clause, line in zip(md.oracle_clauses, lines):
            self.assertEqual(clause.raw, line)
            self.assertIsInstance(clause.effect_ir, dict)
            # trigger/condition may be None in stub
            self.assertTrue(hasattr(clause, 'trigger'))
            self.assertTrue(hasattr(clause, 'condition'))
            print('Clause:', clause.raw, clause.effect_ir)

    def test_behavior_tree_population(self):
        md = self.metadata
        self.assertEqual(len(md.behavior_tree), len(md.oracle_clauses))
        self.assertTrue(all(isinstance(act, dict) for act in md.behavior_tree))
        print('Behavior Tree:', md.behavior_tree)

    def test_static_keyword_extraction(self):
        md = self.metadata
        text_lower = md.oracle_text.lower()
        expected = [kw for kw in rulelex.STATIC_KEYWORDS if kw in text_lower]
        for kw in expected:
            self.assertIn(kw, md.static_abilities)
        print('Extracted Static Abilities:', md.static_abilities)

    def test_hash_generation_consistency(self):
        md = self.metadata
        import hashlib
        oracle_hash = hashlib.sha1(md.oracle_text.encode()).hexdigest()
        fingerprint = hashlib.sha1(
            f"{md.name}|{md.mana_cost}|{md.type_line}".encode()
        ).hexdigest()
        self.assertEqual(md.oracle_hash, oracle_hash)
        self.assertEqual(md.card_fingerprint, fingerprint)
        print('Oracle Hash:', md.oracle_hash)
        print('Card Fingerprint:', md.card_fingerprint)


if __name__ == '__main__':
    unittest.main(verbosity=2)
