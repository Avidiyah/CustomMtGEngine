import os
import sys
import unittest
from dataclasses import dataclass
from typing import Any, Dict, List

# Ensure repository root is on sys.path
# This test file lives in ``testing_tools`` at the repository root, so the
# parent directory contains ``data_layer``.  Avoid walking up directories that
# may inadvertently select another engine version when multiple copies exist.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# -------------------------------------------------------------
# Imports from the engine
# -------------------------------------------------------------
from data_layer.CardRepository import CardRepository, CardMetadata, GameCard
from oracle_parser.OracleParser import OracleParser
from oracle_parser.Tokenizer import Token, TokenGroup, tokenize_clause
from oracle_parser.ClauseParser import parse_token_group, ClauseBlock
from oracle_parser.RuleLexicon import STATIC_KEYWORDS


class OraclePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cache_path = os.path.join(REPO_ROOT, 'data_layer', 'card_cache.json')
        cls.repo = CardRepository(cache_file=cache_path)
        cls.glory = cls.repo.load_card('glorybringer')
        cls.bolt = cls.repo.load_card('lightning bolt')
        cls.angel = cls.repo.load_card('serra angel')
        cls.gamecard = GameCard(metadata=cls.glory)
        cls.parser = OracleParser()

    # ------------------------------------------------------------------
    # Phase 1.1 tests
    # ------------------------------------------------------------------
    def test_repository_load(self):
        self.assertIsInstance(self.glory, CardMetadata)
        self.assertIsInstance(self.bolt, CardMetadata)

    def test_metadata_fields(self):
        md = self.glory
        self.assertIn('Creature', md.types)
        self.assertIn('Dragon', md.subtypes)
        self.assertIn('flying', md.static_abilities)
        self.assertIn('haste', md.static_abilities)
        self.assertTrue(md.oracle_hash)
        self.assertTrue(md.card_fingerprint)
        print('\nOracle Hash:', md.oracle_hash)
        print('Card Fingerprint:', md.card_fingerprint)
        print('Static Abilities:', md.static_abilities)

    def test_gamecard_wrapper(self):
        gc = self.gamecard
        self.assertEqual(gc.zone, 'library')
        self.assertTrue(gc.is_creature())

    # ------------------------------------------------------------------
    # Phase 1.2 tests
    # ------------------------------------------------------------------
    def test_oracle_clauses_structure(self):
        clauses = self.parser.parse(self.bolt.oracle_text)
        lines = [l.strip() for l in self.bolt.oracle_text.split('\n') if l.strip()]
        self.assertEqual(len(clauses), len(lines))
        for c in clauses:
            self.assertIsInstance(c, ClauseBlock)
            self.assertIsInstance(c.effect_ir, dict)
            self.assertTrue(c.clause_type)
            print('ClauseBlock:', c.clause_type, c.raw, c.effect_ir)

    def test_behavior_tree_population(self):
        clauses = self.parser.parse(self.bolt.oracle_text)
        tree = self.parser.behavior_tree
        self.assertEqual(len(tree), len(clauses))
        self.assertTrue(all(isinstance(node, dict) for node in tree))
        print('Behavior Tree:', tree)

    # ------------------------------------------------------------------
    # Phase 1.3 tests
    # ------------------------------------------------------------------
    def test_tokenizer_typing(self):
        clause = 'Whenever another creature enters, you gain 1 life.'
        group = tokenize_clause(clause)
        self.assertIsInstance(group, TokenGroup)
        types = [t.type for t in group.tokens]
        print('Tokens:', [(t.text, t.type) for t in group.tokens])
        self.assertIn('trigger_word', types)
        self.assertIn('action_word', types)

    def test_clause_parser_semantics(self):
        clause = 'Whenever another creature enters, you gain 1 life.'
        group = tokenize_clause(clause)
        block = parse_token_group(group)
        self.assertEqual(block.clause_type, 'trigger')
        self.assertIsNotNone(block.effect_ir.get('trigger'))
        self.assertIn('trigger', block.effect_ir)
        print('Parsed Clause:', block)


class PhaseOneTestSuite(unittest.TestCase):
    """Comprehensive tests validating the Phase 1 engine architecture."""

    @classmethod
    def setUpClass(cls):
        cache_path = os.path.join(REPO_ROOT, 'data_layer', 'card_cache.json')
        cls.repo = CardRepository(cache_file=cache_path)
        cls.serra = cls.repo.load_card('serra angel')
        cls.bolt = cls.repo.load_card('lightning bolt')
        cls.warden = cls.repo.load_card('soul warden')
        cls.parser = OracleParser()

    # ------------------------------------------------------------------
    # CARD DATA TESTS
    # ------------------------------------------------------------------
    def test_card_metadata_loading(self):
        md = self.serra
        self.assertEqual(md.name.lower(), 'serra angel')
        self.assertTrue(md.oracle_text)
        self.assertIn('Creature', md.types)
        self.assertTrue(md.mana_cost)
        self.assertTrue(md.oracle_hash)
        self.assertTrue(md.card_fingerprint)
        self.assertIn('flying', md.static_abilities)

    def test_oracle_hash_consistency(self):
        first = self.repo.load_card('soul warden')
        second = self.repo.load_card('soul warden')
        self.assertEqual(first.oracle_hash, second.oracle_hash)

    # ------------------------------------------------------------------
    # TOKENIZER TESTS
    # ------------------------------------------------------------------
    def test_token_classification(self):
        clause = 'Whenever another creature enters, you gain 1 life.'
        group = tokenize_clause(clause)
        roles = {t.text: t.type for t in group.tokens}
        self.assertEqual(roles.get('whenever'), 'trigger_word')
        self.assertEqual(roles.get('creature'), 'targeting_word')
        self.assertEqual(roles.get('gain'), 'action_word')
        self.assertEqual(roles.get('life'), 'resource_term')

    def test_token_group_preserves_raw_clause(self):
        clause = 'Whenever another creature enters, you gain 1 life.'
        group = tokenize_clause(clause)
        self.assertEqual(group.raw, clause)

    # ------------------------------------------------------------------
    # PARSER + CLAUSEBLOCK TESTS
    # ------------------------------------------------------------------
    def test_clauseblock_structure(self):
        clauses = self.parser.parse(self.serra.oracle_text)
        self.assertTrue(all(isinstance(c, ClauseBlock) for c in clauses))
        for c in clauses:
            self.assertTrue(c.raw)
            self.assertIsInstance(c.effect_ir, dict)

    def test_effect_ir_presence(self):
        clauses = self.parser.parse(self.glory_text())
        for cl in clauses:
            self.assertIsInstance(cl.effect_ir, dict)
            self.assertTrue(cl.effect_ir)

    # ------------------------------------------------------------------
    # STATIC ABILITIES + KEYWORD TESTS
    # ------------------------------------------------------------------
    def test_static_keyword_detection(self):
        self.assertIn('flying', self.serra.static_abilities)
        self.assertIn('vigilance', self.serra.static_abilities)

    # ------------------------------------------------------------------
    # FINGERPRINT + INTEGRITY TESTS
    # ------------------------------------------------------------------
    def test_clause_fingerprint_uniqueness(self):
        fp1 = self.serra.card_fingerprint
        fp2 = self.bolt.card_fingerprint
        self.assertNotEqual(fp1, fp2)

    def test_token_consistency_on_retokenization(self):
        clause = 'Lightning Bolt deals 3 damage to any target.'
        t1 = tokenize_clause(clause)
        t2 = tokenize_clause(clause)
        seq1 = [(tok.text, tok.type) for tok in t1.tokens]
        seq2 = [(tok.text, tok.type) for tok in t2.tokens]
        self.assertEqual(seq1, seq2)

    # ------------------------------------------------------------------
    # EDGE CASE TESTS
    # ------------------------------------------------------------------
    def test_tokenizer_with_punctuation(self):
        clause = 'Destroy target creature, then draw a card!'
        group = tokenize_clause(clause)
        texts = [t.text for t in group.tokens]
        self.assertIn('destroy', texts)
        self.assertIn('draw', texts)

    def test_unknown_tokens_are_tagged(self):
        clause = 'Blorbity blorb deals 2 damage to floofs!'
        group = tokenize_clause(clause)
        unknown_tokens = [t for t in group.tokens if t.text in {'blorbity', 'blorb', 'floofs'}]
        self.assertTrue(all(t.type == 'unknown' for t in unknown_tokens))

    # Helper to reuse Glorybringer text for effect IR checks
    def glory_text(self):
        glory = self.repo.load_card('glorybringer')
        return glory.oracle_text



if __name__ == '__main__':
    unittest.main(verbosity=2)
