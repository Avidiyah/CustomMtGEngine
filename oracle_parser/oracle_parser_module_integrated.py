
# oracle_parser_module_integrated.py — Integrated Oracle Text Parser

import re
from typing import List, Dict, Union, Any

def oracle_tokenizer(oracle_text: str) -> List[str]:
    tokens = re.findall(r'\b[\w\'/-]+\b|[.,:;()]', oracle_text)
    return tokens

phrase_patterns = {
    "draw_card": re.compile(r'draw (\\d+|a|X) card(s)?', re.IGNORECASE),
    "deal_damage": re.compile(r'deals? (\\d+|X) damage to (any target|target \\w+)', re.IGNORECASE),
    "gain_life": re.compile(r'gain (\\d+|X) life', re.IGNORECASE),
    "lose_life": re.compile(r'lose (\\d+|X) life', re.IGNORECASE),
    "modify_pt": re.compile(r'gets? [+-]\\d+/[+-]\\d+ until end of turn', re.IGNORECASE),
    "grant_ability": re.compile(r'gains? \\w+ until end of turn', re.IGNORECASE),
    "destroy_target": re.compile(r'destroy target \\w+', re.IGNORECASE),
    "exile_target": re.compile(r'exile target \\w+', re.IGNORECASE),
    "return_to_hand": re.compile(r'return target \\w+ to its owner\'s hand', re.IGNORECASE),
    "triggered_when": re.compile(r'whenever .*?,|when .*?,|at the beginning of .*?,', re.IGNORECASE),
    "conditional_if": re.compile(r'if .*?,', re.IGNORECASE),
    "zone_transfer": re.compile(r'put .*? onto the battlefield|search .*? library|shuffle .*? into', re.IGNORECASE)
}

def match_oracle_phrases(text: str) -> Dict[str, Union[str, List[str]]]:
    tokens = oracle_tokenizer(text)
    matches = {}
    for label, pattern in phrase_patterns.items():
        found = pattern.findall(text)
        if found:
            matches[label] = found
    return {"tokens": tokens, "matches": matches}

def parse_oracle_text_to_behavior_tree(text: str) -> Dict[str, Any]:
    from oracle_parser_to_ast import parse_phrases_to_ast
    from oracle_ast_compiler import compile_ast_to_behavior

    parsed = match_oracle_phrases(text)
    ast_nodes = parse_phrases_to_ast(text, parsed["matches"])
    return compile_ast_to_behavior(ast_nodes)
